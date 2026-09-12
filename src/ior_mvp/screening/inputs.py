"""Offline assembly and evidence-bound plant-family links."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SIGNAL_TYPES = frozenset(
    {
        "matching_feedstock",
        "core_process",
        "equipment",
        "adjacent_output",
        "relevant_certification",
        "imported_inputs",
    }
)
ENTRY_KEYS = frozenset(
    {
        "link_id",
        "entity_id",
        "family_id",
        "signal_type",
        "evidence_class",
        "evidence",
        "reviewer_status",
    }
)


@dataclass(frozen=True)
class ScreeningInputs:
    universe: dict[str, Any] | None
    partners: dict[str, Any] | None
    tariff: dict[str, Any] | None
    entities: dict[str, Any] | None
    family_links: dict[str, Any]
    inputs_block: dict[str, Any]
    unavailable_reasons: tuple[str, ...]


def _json_pointer(record: Any, pointer: str) -> Any:
    if not pointer.startswith("/"):
        raise ValueError("snapshot json_pointer must start with /")
    value = record
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def validate_family_links(
    record: dict[str, Any],
    entities: dict[str, Any],
    documents: dict[str, Any],
    snapshots: dict[str, Any],
) -> None:
    if set(record) != {"schema_version", "list_id", "recorded_on", "entries"}:
        raise ValueError("plant-family link-list keys mismatch")
    if record["schema_version"] != "1.0.0" or record["list_id"] != "plant-family-links-v1":
        raise ValueError("plant-family link-list identity mismatch")
    plants = {
        entity["entity_id"]
        for entity in entities.get("entities", [])
        if entity.get("entity_type") == "PLANT"
    }
    ids: set[str] = set()
    for entry in record["entries"]:
        if set(entry) != ENTRY_KEYS:
            raise ValueError("plant-family link entry keys mismatch")
        if entry["link_id"] in ids:
            raise ValueError("duplicate plant-family link")
        ids.add(entry["link_id"])
        if entry["entity_id"] not in plants:
            raise ValueError("link entity must be an existing PLANT")
        if entry["signal_type"] not in SIGNAL_TYPES:
            raise ValueError("unknown plant-family signal_type")
        if entry["evidence_class"] != "C":
            raise ValueError("plant-family link evidence must be Class C")
        if entry["reviewer_status"] != "agent_authored_pending_domain_review":
            raise ValueError("invalid plant-family reviewer status")
        if not entry["evidence"]:
            raise ValueError("plant-family link requires evidence")
        for evidence in entry["evidence"]:
            if evidence.get("kind") == "document_line":
                document = documents[evidence["document_id"]]
                line = document["pages"][evidence["page_index"]]["lines"][
                    evidence["line_index"]
                ]
                if evidence["verbatim_span"] not in line:
                    raise ValueError("document verbatim span mismatch")
            elif evidence.get("kind") == "snapshot_value":
                observed = _json_pointer(
                    snapshots[evidence["snapshot_id"]],
                    evidence["json_pointer"],
                )
                if observed != evidence["value"]:
                    raise ValueError("snapshot value mismatch")
            else:
                raise ValueError("unknown plant-family evidence kind")


def write_family_links(record: dict[str, Any], root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / "plant-family-links-v1.json"
    content = json.dumps(
        record, ensure_ascii=False, sort_keys=True, indent=2
    ) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != content:
            raise ValueError("plant-family link write conflict")
        return path
    path.write_text(content, encoding="utf-8")
    return path


def _identity(
    path: Path,
    *,
    identity: str,
    repo_root: Path,
) -> dict[str, str]:
    resolved_root = repo_root.resolve()
    resolved_path = path.resolve()
    try:
        relative = resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(
            f"screening input path outside repository root: {path}"
        ) from exc
    manifest_path = relative.as_posix()
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or not relative.parts
        or relative.parts[0] not in {"data", "config"}
    ):
        raise ValueError(
            f"screening input path is not a manifest key: {manifest_path}"
        )
    return {
        "path": manifest_path,
        "sha256": hashlib.sha256(resolved_path.read_bytes()).hexdigest(),
        "id": identity,
    }


def latest_universe_attempt_reason(data_root: Path, source_id: str) -> str:
    coverage = sorted((data_root / "raw" / source_id).glob("**/coverage.json"))
    if not coverage:
        return "NO_UNIVERSE_SNAPSHOT"
    latest = max(
        coverage,
        key=lambda path: json.loads(path.read_text(encoding="utf-8")).get(
            "run_id", ""
        ),
    )
    reason = json.loads(latest.read_text(encoding="utf-8")).get("stop_reason")
    return reason or "NO_UNIVERSE_SNAPSHOT"


def assemble_inputs(data_root: Path, *, source_id: str) -> ScreeningInputs:
    """Load newest governed inputs for the offline builder."""
    from ior_mvp.acquisition import repository

    repo_root = data_root.resolve().parent

    universe_values = repository.acquired_snapshots(
        "universe", data_root=data_root
    )
    partner_values = {
        key: value
        for key, value in repository.acquired_snapshots(
            "partners", data_root=data_root
        ).items()
        if value.get("source_id") == source_id
    }
    tariff_values = repository.acquired_snapshots(
        "tariff", data_root=data_root
    )
    universe = max(
        universe_values.values(),
        key=lambda row: (row["as_of_date"], row["snapshot_id"]),
        default=None,
    )
    partners = max(
        partner_values.values(),
        key=lambda row: (row["as_of_date"], row["snapshot_id"]),
        default=None,
    )
    tariff = max(
        tariff_values.values(),
        key=lambda row: (row["as_of_date"], row["snapshot_id"]),
        default=None,
    )
    links_path = data_root / "screening" / "lists" / "plant-family-links-v1.json"
    links = (
        json.loads(links_path.read_text(encoding="utf-8"))
        if links_path.exists()
        else {
            "schema_version": "1.0.0",
            "list_id": "plant-family-links-v1",
            "recorded_on": "2026-09-12",
            "entries": [],
        }
    )
    reasons = (
        ()
        if universe is not None
        else (latest_universe_attempt_reason(data_root, source_id),)
    )
    entity_paths = sorted((data_root / "entities" / "resolution").glob("*.json"))
    entity_path = entity_paths[-1] if entity_paths else None
    entities = (
        json.loads(entity_path.read_text(encoding="utf-8"))
        if entity_path is not None
        else None
    )

    def snapshot_identity(
        kind: str, record: dict[str, Any] | None
    ) -> list[dict[str, str]]:
        if record is None:
            return []
        path = data_root / "snapshots" / kind / f"{record['snapshot_id']}.json"
        return [
            _identity(
                path,
                identity=record["snapshot_id"],
                repo_root=repo_root,
            )
        ]

    config_paths = (
        ("config/screening.v1.yaml", "1.0.0"),
        ("config/product_families.v1.yaml", "1.0.0"),
        ("config/thresholds.v1.yaml", "1.2.0"),
        ("config/acquisition_sources.v1.yaml", "1.3.0"),
    )
    block: dict[str, Any] = {
        "universe_snapshots": snapshot_identity("universe", universe),
        "partner_snapshots": snapshot_identity("partners", partners),
        "tariff_snapshots": snapshot_identity("tariff", tariff),
        "entity_artifacts": (
            [
                _identity(
                    entity_path,
                    identity=entities.get("artifact_id", entity_path.stem),
                    repo_root=repo_root,
                )
            ]
            if entity_path is not None and entities is not None
            else []
        ),
        "plant_family_links": [
            _identity(
                links_path,
                identity=links["list_id"],
                repo_root=repo_root,
            )
        ] if links_path.exists() else [],
        "configs": [
            {
                "path": relative,
                "sha256": hashlib.sha256(
                    (repo_root / relative).read_bytes()
                ).hexdigest(),
                "version": version,
            }
            for relative, version in config_paths
        ],
    }
    return ScreeningInputs(
        universe, partners, tariff, entities, links, block, reasons
    )
