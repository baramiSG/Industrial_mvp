"""Write-once storage primitives for entity mention lists and artifacts."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from ...config import PROJECT_ROOT
from ..contracts import (
    RawStoreIntegrityError,
    SnapshotWriteConflict,
    canonical_dumps,
)
from ..harmonise import PIPELINE_VERSION
from ..raw_store import _PATH_UNSAFE
from ..snapshots import ReconstructionResult
from .ids import ENTITY_ID_PATTERN
from .mentions import (
    LIST_ID_PATTERN,
    MentionList,
    load_mention_list,
    mention_list_sha256,
    verify_mentions,
)
from .resolver import ResolutionResult, resolve
from .rules import (
    ENTITY_RULES_PATH,
    EntityResolutionError,
    EntityRules,
    load_entity_rules,
    rules_sha256,
)

ARTIFACT_SCHEMA_VERSION = "1.0.0"
ARTIFACT_ID_SCHEME = "ENTITY_ARTIFACT_ID_V1"
ENTITY_CONFIG_VERSION = "1.0.0"
ARTIFACT_ID_PATTERN = re.compile(r"^ENTITIES-\d{4}-\d{2}-\d{2}-[0-9a-f]{12}$")
LINK_ID_PATTERN = re.compile(r"^L-[0-9]{3}$")

_TOP_KEYS = {
    "schema_version",
    "artifact_id",
    "artifact_id_scheme",
    "kind",
    "source_boundary",
    "synthetic_flag",
    "as_of_date",
    "id_scheme",
    "normalisation",
    "inputs",
    "entities",
    "links",
    "passport_links",
    "observation_links",
    "ownership_records",
    "name_change_records",
    "merge_records",
    "documents_without_mentions",
    "counts",
    "transformation_record",
    "quality_summary",
}
_ENTITY_KEYS = {
    "entity_id",
    "entity_type",
    "canonical_key",
    "primary_name_en",
    "primary_name_ar",
    "jurisdiction",
    "granularity",
    "parent",
    "locality_token",
    "names",
    "identifiers",
    "attributes_unresolved",
    "merged_into",
    "first_observed_as_of",
    "evidence_mention_ids",
}
_LINK_KEYS = {
    "link_id",
    "mention_id",
    "entity_type",
    "link_status",
    "precedence_rank",
    "rule_applied",
    "entity_id",
    "candidate_entity_ids",
    "unresolved_reason",
    "evidence",
}
_STATUSES = (
    "DETERMINISTIC_IDENTIFIER",
    "EXACT_DOCUMENT_EVIDENCE",
    "PROPOSED_PENDING_REVIEW",
    "UNRESOLVED",
)


@dataclass(frozen=True)
class DocumentInput:
    document_id: str
    path: Path
    sha256: str
    record: dict[str, Any]

    @classmethod
    def from_path(
        cls, document_id: str, path: Path, record: dict[str, Any]
    ) -> "DocumentInput":
        return cls(document_id, path, hashlib.sha256(path.read_bytes()).hexdigest(), record)


@dataclass(frozen=True)
class SnapshotInput:
    snapshot_id: str
    path: Path
    sha256: str
    record: dict[str, Any]

    @classmethod
    def from_path(
        cls, snapshot_id: str, path: Path, record: dict[str, Any]
    ) -> "SnapshotInput":
        return cls(snapshot_id, path, hashlib.sha256(path.read_bytes()).hexdigest(), record)


@dataclass(frozen=True)
class EntityBuildReport:
    artifact_id: str
    artifact_path: str
    entities_by_type: dict[str, int]
    links_by_status: dict[str, int]
    passport_links_by_status: dict[str, int]
    documents_without_mentions: tuple[str, ...]


def artifact_id(recorded_on: str, mention_list_hash: str) -> str:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", recorded_on):
        raise EntityResolutionError("recorded_on must be an ISO date")
    if not re.fullmatch(r"[0-9a-f]{64}", mention_list_hash):
        raise EntityResolutionError("mention_list_sha256 must be a SHA-256 hex digest")
    return f"ENTITIES-{recorded_on}-{mention_list_hash[:12]}"


def _relative_path(path: Path, data_root: Path) -> str:
    resolved = path.resolve()
    for base in (data_root.resolve(), PROJECT_ROOT.resolve()):
        try:
            return resolved.relative_to(base).as_posix()
        except ValueError:
            continue
    return resolved.as_posix()


def _resolve_input_path(value: str, data_root: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    under_data_root = data_root / value
    if under_data_root.exists():
        return under_data_root
    if value.startswith(("data/", "config/")):
        return PROJECT_ROOT / value
    return under_data_root


def default_document_loader(
    data_root: Path, *, allow_test_double: bool = False
) -> dict[str, DocumentInput]:
    from ..documents.store import DocumentStore, validate_document_record

    loaded: dict[str, DocumentInput] = {}
    for path, record in DocumentStore(data_root / "documents").iter_records():
        validate_document_record(record, allow_test_double=allow_test_double)
        document_id = record["document_id"]
        loaded[document_id] = DocumentInput.from_path(document_id, path, record)
    return loaded


def default_snapshot_loader(data_root: Path) -> dict[str, SnapshotInput]:
    from ...public_snapshot import validate_public_snapshot

    loaded: dict[str, SnapshotInput] = {}
    for path in sorted((data_root / "snapshots" / "public").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        validate_public_snapshot(record, path=path, root=data_root.parent)
        snapshot_id = record.get("snapshot_id", path.stem)
        loaded[snapshot_id] = SnapshotInput.from_path(snapshot_id, path, record)
    return loaded


class EntityStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self._reject_forbidden_roots()

    def _reject_forbidden_roots(self) -> None:
        repo_data = PROJECT_ROOT / "data"
        forbidden = (repo_data / "snapshots" / "public", repo_data / "synthetic")
        for path in forbidden:
            try:
                self.root.resolve().relative_to(path.resolve())
            except ValueError:
                continue
            raise RawStoreIntegrityError(f"Entity store root may not be under {path}")

    @staticmethod
    def _segment(value: str, label: str) -> str:
        if not isinstance(value, str) or not value or _PATH_UNSAFE.search(value):
            raise RawStoreIntegrityError(
                f"Invalid {label} for entity store path: {value!r}"
            )
        return value

    def mention_list_path(self, list_id: str) -> Path:
        if not isinstance(list_id, str) or LIST_ID_PATTERN.fullmatch(list_id) is None:
            raise RawStoreIntegrityError(f"Invalid entity mention list_id: {list_id!r}")
        self._segment(list_id, "list_id")
        return self.root / "mentions" / f"{list_id}.json"

    def artifact_path(self, artifact_id: str) -> Path:
        self._segment(artifact_id, "artifact_id")
        return self.root / "resolution" / f"{artifact_id}.json"

    def _under_repository_data(self) -> bool:
        try:
            self.root.resolve().relative_to((PROJECT_ROOT / "data").resolve())
        except ValueError:
            return False
        return True

    @staticmethod
    def _contains_test_double(value: Any) -> bool:
        if isinstance(value, dict):
            for key, nested in value.items():
                if key == "recorded_by_seat" and nested == "TEST-DOUBLE":
                    return True
                if key == "list_id" and isinstance(nested, str) and nested.startswith(
                    "test-double"
                ):
                    return True
                if key == "document_id" and isinstance(
                    nested, str
                ) and "TEST-FIXTURE" in nested:
                    return True
                if key == "snapshot_id" and isinstance(nested, str) and nested.startswith(
                    ("FIX-", "TEST-")
                ):
                    return True
                if EntityStore._contains_test_double(nested):
                    return True
        elif isinstance(value, list):
            return any(EntityStore._contains_test_double(item) for item in value)
        return False

    def write_artifact(
        self, artifact: dict[str, Any], *, allow_test_double: bool = False
    ) -> Path:
        if not isinstance(artifact, dict):
            raise EntityResolutionError("Entity artifact must be an object")
        if (
            not allow_test_double
            and self._under_repository_data()
            and self._contains_test_double(artifact)
        ):
            raise RawStoreIntegrityError(
                "test doubles are not permitted under repository data/entities"
            )
        validate_entity_artifact(artifact, allow_test_double=allow_test_double)
        artifact_id = artifact.get("artifact_id")
        if not isinstance(artifact_id, str):
            raise EntityResolutionError("Entity artifact_id must be a string")
        path = self.artifact_path(artifact_id)
        payload = canonical_dumps(artifact)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            if path.read_text(encoding="utf-8") == payload:
                return path
            raise SnapshotWriteConflict(f"Entity artifact already exists: {path}")
        path.write_text(payload, encoding="utf-8")
        return path

    def iter_mention_lists(self) -> list[tuple[Path, dict[str, Any]]]:
        return [
            (path, json.loads(path.read_text(encoding="utf-8")))
            for path in sorted((self.root / "mentions").glob("*.json"))
        ]

    def iter_artifacts(self) -> list[tuple[Path, dict[str, Any]]]:
        return [
            (path, json.loads(path.read_text(encoding="utf-8")))
            for path in sorted((self.root / "resolution").glob("*.json"))
        ]


def _validate_status_link(link: dict[str, Any], field: str) -> None:
    status = link.get("link_status")
    if status not in _STATUSES:
        raise EntityResolutionError(f"{field}.link_status is not governed")
    entity_id_value = link.get("entity_id")
    candidates = link.get("candidate_entity_ids")
    reason = link.get("unresolved_reason")
    if not isinstance(candidates, list) or not all(
        isinstance(value, str) and ENTITY_ID_PATTERN.fullmatch(value)
        for value in candidates
    ):
        raise EntityResolutionError(f"{field}.candidate_entity_ids is invalid")
    if status in _STATUSES[:2]:
        if not isinstance(entity_id_value, str) or ENTITY_ID_PATTERN.fullmatch(
            entity_id_value
        ) is None:
            raise EntityResolutionError(f"{field} resolved link requires entity_id")
        if candidates or reason is not None:
            raise EntityResolutionError(f"{field} resolved link has pending fields")
    elif status == "PROPOSED_PENDING_REVIEW":
        if entity_id_value is not None or reason is not None or not candidates:
            raise EntityResolutionError(
                f"{field} pending link requires candidates and no entity_id"
            )
    else:
        if entity_id_value is not None or candidates:
            raise EntityResolutionError(f"{field} unresolved link has identity")
        if reason not in {
            "OUT_OF_SCOPE_ENTITY_TYPE",
            "COUNT_ONLY_NO_IDENTITY",
            "NO_MENTION_RECORDED",
            "LOCALITY_NOT_IN_TABLE",
            "NO_SUBJECT_ENTITY",
            "OWNER_UNNAMED",
        }:
            raise EntityResolutionError(f"{field}.unresolved_reason is not governed")


def _count_statuses(items: list[dict[str, Any]]) -> dict[str, int]:
    return {
        status: sum(item["link_status"] == status for item in items)
        for status in _STATUSES
    }


def validate_entity_artifact(
    artifact: dict[str, Any], *, allow_test_double: bool = False
) -> None:
    """Fail closed on EntityResolutionArtifact shape, identities and counts."""
    if not isinstance(artifact, dict) or set(artifact) != _TOP_KEYS:
        actual = set(artifact) if isinstance(artifact, dict) else set()
        raise EntityResolutionError(
            f"entity artifact has unexpected keys {sorted(actual - _TOP_KEYS)} "
            f"or missing keys {sorted(_TOP_KEYS - actual)}"
        )
    fixed = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_id_scheme": ARTIFACT_ID_SCHEME,
        "kind": "entity_resolution",
        "source_boundary": "public",
        "synthetic_flag": False,
        "quality_summary": "PASS",
    }
    for key, expected in fixed.items():
        if artifact[key] != expected:
            raise EntityResolutionError(f"{key} must be {expected!r}")
    if not isinstance(artifact["artifact_id"], str) or ARTIFACT_ID_PATTERN.fullmatch(
        artifact["artifact_id"]
    ) is None:
        raise EntityResolutionError("artifact_id is invalid")
    if artifact["id_scheme"] != {
        "name": "ENTITY_ID_V1",
        "hash": "sha256",
        "hex_length": 16,
    }:
        raise EntityResolutionError("id_scheme is invalid")
    if artifact["normalisation"] != {
        "method_id": "NAME_NORMALISATION_V1",
        "version": "1.0.0",
    }:
        raise EntityResolutionError("normalisation is invalid")
    entities = artifact["entities"]
    if not isinstance(entities, list):
        raise EntityResolutionError("entities must be a list")
    if entities != sorted(entities, key=lambda item: item.get("entity_id", "")):
        raise EntityResolutionError("entities must be sorted by entity_id")
    entity_ids: set[str] = set()
    for index, entity in enumerate(entities):
        if not isinstance(entity, dict) or set(entity) != _ENTITY_KEYS:
            raise EntityResolutionError(f"entities[{index}] has invalid keys")
        value = entity["entity_id"]
        if not isinstance(value, str) or ENTITY_ID_PATTERN.fullmatch(value) is None:
            raise EntityResolutionError(f"entities[{index}].entity_id is invalid")
        if value in entity_ids or not value.startswith(f"{entity['entity_type']}-"):
            raise EntityResolutionError("entity ids must be unique and type-prefixed")
        entity_ids.add(value)
        if entity["granularity"] not in {
            "LEGAL_ENTITY",
            "SITE_LOCALITY",
            "LINE_DESIGNATION",
        }:
            raise EntityResolutionError("entity granularity is invalid")
    links = artifact["links"]
    if not isinstance(links, list):
        raise EntityResolutionError("links must be a list")
    for index, link in enumerate(links):
        if not isinstance(link, dict) or set(link) != _LINK_KEYS:
            raise EntityResolutionError(f"links[{index}] has invalid keys")
        if LINK_ID_PATTERN.fullmatch(link["link_id"]) is None:
            raise EntityResolutionError(f"links[{index}].link_id is invalid")
        _validate_status_link(link, f"links[{index}]")
        if link["entity_id"] is not None and link["entity_id"] not in entity_ids:
            raise EntityResolutionError("link references unknown entity_id")
    for field in ("passport_links", "observation_links"):
        values = artifact[field]
        if not isinstance(values, list):
            raise EntityResolutionError(f"{field} must be a list")
        for index, value in enumerate(values):
            if not isinstance(value, dict):
                raise EntityResolutionError(f"{field}[{index}] must be an object")
            _validate_status_link(value, f"{field}[{index}]")
            if value["entity_id"] is not None and value["entity_id"] not in entity_ids:
                raise EntityResolutionError(f"{field}[{index}] references unknown entity")
    counts = artifact["counts"]
    expected_counts = {
        "entities_by_type": {
            entity_type: sum(
                entity["entity_type"] == entity_type for entity in entities
            )
            for entity_type in ("COMPANY", "PLANT", "LINE", "LICENCE_HOLDER")
        },
        "links_by_status": _count_statuses(links),
        "passport_links_by_status": _count_statuses(artifact["passport_links"]),
        "observation_links_by_status": _count_statuses(artifact["observation_links"]),
    }
    if counts != expected_counts:
        raise EntityResolutionError("artifact counts do not match content")
    inputs = artifact["inputs"]
    if not isinstance(inputs, dict) or set(inputs) != {
        "mention_list",
        "rule_table",
        "document_records",
        "public_snapshots",
    }:
        raise EntityResolutionError("inputs has invalid keys")
    if not allow_test_double and EntityStore._contains_test_double(artifact):
        raise RawStoreIntegrityError("test double entity artifact is refused")


def _input_rows(
    inputs: Mapping[str, DocumentInput | SnapshotInput],
    *,
    data_root: Path,
    id_field: str,
) -> list[dict[str, str]]:
    return [
        {
            id_field: getattr(value, id_field),
            "path": _relative_path(value.path, data_root),
            "sha256": value.sha256,
        }
        for _, value in sorted(inputs.items())
    ]


def _artifact_payload(
    *,
    mention_list: MentionList,
    mention_path: Path,
    mention_hash: str,
    rule_path: Path,
    rules: EntityRules,
    documents: Mapping[str, DocumentInput],
    snapshots: Mapping[str, SnapshotInput],
    result: ResolutionResult,
    data_root: Path,
) -> dict[str, Any]:
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_id": artifact_id(mention_list.recorded_on, mention_hash),
        "artifact_id_scheme": ARTIFACT_ID_SCHEME,
        "kind": "entity_resolution",
        "source_boundary": "public",
        "synthetic_flag": False,
        "as_of_date": mention_list.recorded_on,
        "id_scheme": {"name": "ENTITY_ID_V1", "hash": "sha256", "hex_length": 16},
        "normalisation": {
            "method_id": "NAME_NORMALISATION_V1",
            "version": "1.0.0",
        },
        "inputs": {
            "mention_list": {
                "path": _relative_path(mention_path, data_root),
                "sha256": mention_hash,
                "list_id": mention_list.list_id,
            },
            "rule_table": {
                "path": _relative_path(rule_path, data_root),
                "sha256": rules_sha256(rule_path),
                "version": rules.version,
            },
            "document_records": _input_rows(
                documents, data_root=data_root, id_field="document_id"
            ),
            "public_snapshots": _input_rows(
                snapshots, data_root=data_root, id_field="snapshot_id"
            ),
        },
        "entities": result.entities,
        "links": result.links,
        "passport_links": result.passport_links,
        "observation_links": result.observation_links,
        "ownership_records": result.ownership_records,
        "name_change_records": result.name_change_records,
        "merge_records": result.merge_records,
        "documents_without_mentions": result.documents_without_mentions,
        "counts": result.counts,
        "transformation_record": {
            "formula": "resolve_entities",
            "parameters": {
                "mention_list_id": mention_list.list_id,
                "id_scheme": "ENTITY_ID_V1",
                "normalisation_method_id": "NAME_NORMALISATION_V1",
                "normalisation_version": "1.0.0",
                "rule_table_version": rules.version,
            },
            "exclusions": [],
            "pipeline_version": PIPELINE_VERSION,
            "config_version": ENTITY_CONFIG_VERSION,
        },
        "quality_summary": "PASS",
    }


def build_entity_resolution(
    data_root: Path,
    *,
    mention_list_id: str,
    rules_path: Path = ENTITY_RULES_PATH,
    document_loader: Callable[..., Mapping[str, DocumentInput]] | None = None,
    snapshot_loader: Callable[[Path], Mapping[str, SnapshotInput]] | None = None,
    allow_test_double: bool = False,
) -> EntityBuildReport:
    """Verify every declared span, resolve deterministically, then write once."""
    store = EntityStore(data_root / "entities")
    mention_path = store.mention_list_path(mention_list_id)
    mention_list = load_mention_list(mention_path)
    if (
        not allow_test_double
        and store._under_repository_data()
        and (
            mention_list.list_id.startswith("test-double")
            or mention_list.recorded_by_seat == "TEST-DOUBLE"
        )
    ):
        raise RawStoreIntegrityError("test double mention list is refused")
    rules = load_entity_rules(rules_path)
    load_documents = document_loader or default_document_loader
    load_snapshots = snapshot_loader or default_snapshot_loader
    documents = dict(
        load_documents(data_root, allow_test_double=allow_test_double)
    )
    snapshots = dict(load_snapshots(data_root))
    verified = verify_mentions(
        mention_list,
        documents=documents,
        snapshots=snapshots,
        rules=rules,
    )
    result = resolve(
        verified,
        documents=documents,
        snapshots=snapshots,
        rules=rules,
    )
    mention_hash = mention_list_sha256(mention_path)
    artifact = _artifact_payload(
        mention_list=mention_list,
        mention_path=mention_path,
        mention_hash=mention_hash,
        rule_path=rules_path,
        rules=rules,
        documents=documents,
        snapshots=snapshots,
        result=result,
        data_root=data_root,
    )
    path = store.write_artifact(artifact, allow_test_double=allow_test_double)
    return EntityBuildReport(
        artifact_id=artifact["artifact_id"],
        artifact_path=str(path),
        entities_by_type=result.counts["entities_by_type"],
        links_by_status=result.counts["links_by_status"],
        passport_links_by_status=result.counts["passport_links_by_status"],
        documents_without_mentions=tuple(result.documents_without_mentions),
    )


def _reconstruction_failure(
    artifact: dict[str, Any],
    reason: str,
    *,
    expected: str = "",
    actual: str = "",
    verified: int = 0,
    path: str | None = None,
) -> ReconstructionResult:
    detail = {"reason": reason}
    if path is not None:
        detail["path"] = path
    return ReconstructionResult(
        False,
        expected,
        actual,
        verified,
        artifact.get("artifact_id", "UNKNOWN"),
        detail,
    )


def reconstruct_entity_artifact(
    path: Path,
    *,
    data_root: Path,
    rules_path: Path = ENTITY_RULES_PATH,
) -> ReconstructionResult:
    """Rebuild an entity artifact after checking every recorded input hash."""
    try:
        stored_bytes = path.read_bytes()
        artifact = json.loads(stored_bytes.decode("utf-8"))
        validate_entity_artifact(artifact, allow_test_double=True)
    except (OSError, UnicodeError, json.JSONDecodeError, EntityResolutionError) as exc:
        return ReconstructionResult(
            False, "", "", 0, path.stem, {"reason": "BYTE_MISMATCH", "detail": str(exc)}
        )
    canonical_stored = canonical_dumps(artifact).encode("utf-8")
    if stored_bytes != canonical_stored:
        return _reconstruction_failure(
            artifact,
            "BYTE_MISMATCH",
            expected=hashlib.sha256(canonical_stored).hexdigest(),
            actual=hashlib.sha256(stored_bytes).hexdigest(),
            path=str(path),
        )
    inputs = artifact["inputs"]
    mention_ref = inputs["mention_list"]
    mention_path = _resolve_input_path(mention_ref["path"], data_root)
    actual_mention_hash = (
        hashlib.sha256(mention_path.read_bytes()).hexdigest()
        if mention_path.exists()
        else ""
    )
    if actual_mention_hash != mention_ref["sha256"]:
        return _reconstruction_failure(
            artifact,
            "MENTION_LIST_HASH_MISMATCH",
            expected=mention_ref["sha256"],
            actual=actual_mention_hash,
            path=mention_ref["path"],
        )
    rule_ref = inputs["rule_table"]
    recorded_rule_path = _resolve_input_path(rule_ref["path"], data_root)
    selected_rule_path = rules_path if rules_path != ENTITY_RULES_PATH else recorded_rule_path
    actual_rule_hash = (
        hashlib.sha256(selected_rule_path.read_bytes()).hexdigest()
        if selected_rule_path.exists()
        else ""
    )
    if actual_rule_hash != rule_ref["sha256"]:
        return _reconstruction_failure(
            artifact,
            "RULE_TABLE_HASH_MISMATCH",
            expected=rule_ref["sha256"],
            actual=actual_rule_hash,
            path=rule_ref["path"],
        )
    documents: dict[str, DocumentInput] = {}
    snapshots: dict[str, SnapshotInput] = {}
    verified_count = 0
    for field, cls, id_field, target in (
        ("document_records", DocumentInput, "document_id", documents),
        ("public_snapshots", SnapshotInput, "snapshot_id", snapshots),
    ):
        for row in inputs[field]:
            input_path = _resolve_input_path(row["path"], data_root)
            actual_hash = (
                hashlib.sha256(input_path.read_bytes()).hexdigest()
                if input_path.exists()
                else ""
            )
            if actual_hash != row["sha256"]:
                return _reconstruction_failure(
                    artifact,
                    "INPUT_HASH_MISMATCH",
                    expected=row["sha256"],
                    actual=actual_hash,
                    verified=verified_count,
                    path=row["path"],
                )
            record = json.loads(input_path.read_text(encoding="utf-8"))
            identifier = row[id_field]
            target[identifier] = cls(identifier, input_path, actual_hash, record)
            verified_count += 1
    try:
        mention_list = load_mention_list(mention_path)
        rules = load_entity_rules(selected_rule_path)
        verified = verify_mentions(
            mention_list, documents=documents, snapshots=snapshots, rules=rules
        )
        result = resolve(
            verified, documents=documents, snapshots=snapshots, rules=rules
        )
        rebuilt = _artifact_payload(
            mention_list=mention_list,
            mention_path=mention_path,
            mention_hash=actual_mention_hash,
            rule_path=selected_rule_path,
            rules=rules,
            documents=documents,
            snapshots=snapshots,
            result=result,
            data_root=data_root,
        )
    except (OSError, ValueError, EntityResolutionError) as exc:
        return _reconstruction_failure(
            artifact,
            "BYTE_MISMATCH",
            verified=verified_count,
            path=str(path),
            actual=str(exc),
        )
    expected_bytes = canonical_dumps(artifact).encode("utf-8")
    actual_bytes = canonical_dumps(rebuilt).encode("utf-8")
    if actual_bytes != expected_bytes:
        return _reconstruction_failure(
            artifact,
            "BYTE_MISMATCH",
            expected=hashlib.sha256(expected_bytes).hexdigest(),
            actual=hashlib.sha256(actual_bytes).hexdigest(),
            verified=verified_count,
            path=str(path),
        )
    digest = hashlib.sha256(expected_bytes).hexdigest()
    return ReconstructionResult(
        True,
        digest,
        digest,
        verified_count,
        artifact["artifact_id"],
        {},
    )
