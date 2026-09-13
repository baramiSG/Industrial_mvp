"""Safe idempotent loading and verification of Neo4j projection mirrors."""

from __future__ import annotations

import json
import os
import secrets
import stat
import time
from collections import defaultdict
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ior_mvp.acquisition.contracts import OfflineGuardViolation
from ior_mvp.config import PROJECT_ROOT

from .artifact import validate_projection
from .cypher import (
    CONSTRAINT_QUERIES,
    INDEX_QUERIES,
    VERIFY_QUERIES,
    VIEW_QUERIES,
    edge_merge_query,
    node_merge_query,
)
from .model import LABELS
from .projection import GraphProjection


class GraphSafetyError(RuntimeError):
    """Raised before any connection when an operator confirmation is invalid."""


class GraphDriverNotInstalled(RuntimeError):
    """Raised when the optional graph dependency is unavailable."""


class GraphConnectionFailure(RuntimeError):
    """Raised with a sanitized message when the mirror cannot be reached."""


class GraphVerificationError(RuntimeError):
    """Raised when the live mirror differs from the governed artifact."""


def ensure_credential(path: Path) -> str:
    """Create one opaque local Neo4j auth file without ever returning its value."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        descriptor = os.open(
            path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
    except FileExistsError:
        mode = stat.S_IMODE(path.stat().st_mode)
        if mode != 0o600:
            raise GraphSafetyError("NEO4J_AUTH_FILE_MODE_INVALID")
        _read_auth_file(path)
        return "CREDENTIAL_PRESENT"
    value = f"neo4j/{secrets.token_hex(16)}\n".encode("utf-8")
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(value)
    return "CREDENTIAL_CREATED"


@dataclass(frozen=True)
class ConnectionSpec:
    """Resolved target connection with the credential excluded from repr."""

    target: str
    uri: str
    username: str
    password: str = field(repr=False)
    database: str = "neo4j"
    instance_id: str | None = None
    clear_identity: str = ""


@dataclass(frozen=True)
class LoadReport:
    """Sanitized counters from one idempotent projection load."""

    target: str
    projection_id: str
    nodes_created: int
    relationships_created: int
    properties_set: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VerifyReport:
    """Sanitized mirror-equality report."""

    target: str
    projection_id: str
    node_count: int
    edge_count: int
    provenance_complete: bool
    partition_valid: bool
    counts_by_label: dict[str, int]
    counts_by_type: dict[str, int]
    synthetic_partition: dict[str, int]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_auth_file(path: Path) -> tuple[str, str]:
    try:
        value = path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError) as exc:
        raise GraphSafetyError("NEO4J_AUTH_FILE_UNAVAILABLE") from exc
    if "/" not in value:
        raise GraphSafetyError("NEO4J_AUTH_FILE_INVALID")
    username, password = value.split("/", maxsplit=1)
    if not username or not password:
        raise GraphSafetyError("NEO4J_AUTH_FILE_INVALID")
    return username, password


def _required_env(env: Mapping[str, str], name: str) -> str:
    value = env.get(name)
    if not isinstance(value, str) or not value:
        raise GraphSafetyError(f"{name}_REQUIRED")
    return value


def resolve_target(
    target: str,
    env: Mapping[str, str] | None = None,
    *,
    confirm_instance: str | None = None,
) -> ConnectionSpec:
    """Resolve a connection without importing or creating a driver."""
    values = os.environ if env is None else env
    database = values.get("NEO4J_DATABASE") or "neo4j"
    if target == "compose":
        auth_path = Path(
            values.get("NEO4J_AUTH_FILE")
            or PROJECT_ROOT / ".secrets/neo4j_auth.txt"
        )
        username, password = _read_auth_file(auth_path)
        return ConnectionSpec(
            target="compose",
            uri="bolt://localhost:7688",
            username=username,
            password=password,
            database=database,
            clear_identity="industrial-mvp-neo4j",
        )
    if target == "ci":
        return ConnectionSpec(
            target="ci",
            uri="bolt://localhost:7688",
            username=values.get("NEO4J_USERNAME") or "neo4j",
            password=_required_env(values, "NEO4J_PASSWORD"),
            database=database,
            clear_identity="neo4j-ci",
        )
    if target != "aura":
        raise GraphSafetyError("GRAPH_TARGET_INVALID")

    instance_id = _required_env(values, "AURA_INSTANCEID")
    if confirm_instance != instance_id:
        raise GraphSafetyError("INSTANCE_MISMATCH")
    uri = _required_env(values, "NEO4J_URI")
    parsed = urlparse(uri)
    host = parsed.hostname or ""
    host_prefix = host.split(".", maxsplit=1)[0]
    if (
        parsed.scheme != "neo4j+s"
        or not host.endswith(".databases.neo4j.io")
        or host_prefix != instance_id
    ):
        raise GraphSafetyError("INSTANCE_MISMATCH")
    return ConnectionSpec(
        target="aura",
        uri=uri,
        username=_required_env(values, "NEO4J_USERNAME"),
        password=_required_env(values, "NEO4J_PASSWORD"),
        database=database,
        instance_id=instance_id,
        clear_identity=instance_id,
    )


def primitive_properties(properties: Mapping[str, Any]) -> dict[str, Any]:
    """Encode Neo4j properties as primitives or homogeneous primitive arrays."""
    result: dict[str, Any] = {}
    for key, value in properties.items():
        if value is None:
            continue
        if isinstance(value, (str, bool, int, float)):
            result[key] = value
            continue
        if isinstance(value, list):
            if not value:
                result[key] = []
                continue
            primitive_types = {
                bool if isinstance(item, bool) else type(item)
                for item in value
            }
            if (
                all(isinstance(item, (str, bool, int, float)) for item in value)
                and len(primitive_types) == 1
            ):
                result[key] = list(value)
                continue
        result[key] = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    return result


def _default_driver_factory(spec: ConnectionSpec):
    try:
        from neo4j import GraphDatabase
    except ImportError as exc:
        raise GraphDriverNotInstalled from exc
    try:
        return GraphDatabase.driver(
            spec.uri,
            auth=(spec.username, spec.password),
            connection_timeout=2.0,
            connection_acquisition_timeout=2.0,
            max_transaction_retry_time=0.0,
        )
    except OfflineGuardViolation:
        raise
    except Exception as exc:
        # Driver construction errors are sanitized; no credential text escapes.
        raise GraphConnectionFailure("Neo4j driver creation failed") from exc


DriverFactory = Callable[[ConnectionSpec], Any]


def _execute(
    driver: Any,
    spec: ConnectionSpec,
    query: str,
    parameters: Mapping[str, Any] | None = None,
) -> Any:
    try:
        return driver.execute_query(
            query,
            parameters_=dict(parameters or {}),
            database_=spec.database,
        )
    except OfflineGuardViolation:
        raise
    except Exception as exc:
        raise GraphConnectionFailure("Neo4j query failed") from exc


def _records(result: Any) -> list[dict[str, Any]]:
    raw = result.records if hasattr(result, "records") else result[0]
    rows: list[dict[str, Any]] = []
    for record in raw:
        if hasattr(record, "data"):
            rows.append(dict(record.data()))
        else:
            rows.append(dict(record))
    return rows


def _summary(result: Any) -> Any:
    return result.summary if hasattr(result, "summary") else result[1]


def _counter(summary: Any, name: str) -> int:
    counters = getattr(summary, "counters", None)
    return int(getattr(counters, name, 0)) if counters is not None else 0


def load(
    spec: ConnectionSpec,
    projection: GraphProjection,
    *,
    driver_factory: DriverFactory = _default_driver_factory,
) -> LoadReport:
    """MERGE a validated projection by governed ids."""
    validate_projection(projection)
    driver = driver_factory(spec)
    nodes_created = 0
    relationships_created = 0
    properties_set = 0
    try:
        existing_node_count = int(
            _single_value(
                driver,
                spec,
                "MATCH (n) RETURN count(n) AS count",
                "count",
            )
        )
        existing_projection_ids = (
            _single_value(
                driver,
                spec,
                VERIFY_QUERIES["projection_ids"],
                "projection_ids",
            )
            if existing_node_count
            else []
        )
        if existing_projection_ids not in (
            [],
            [projection.projection_id],
        ):
            raise GraphVerificationError(
                "Neo4j projection identity differs; explicit clear required"
            )
        for query in CONSTRAINT_QUERIES:
            _execute(driver, spec, query)
        for query in INDEX_QUERIES:
            _execute(driver, spec, query)

        by_label: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for node in projection.nodes:
            properties = primitive_properties(node.properties)
            properties["id"] = node.id
            by_label[node.label].append(
                {"id": node.id, "properties": properties}
            )
        for label in LABELS:
            rows = sorted(by_label.get(label, []), key=lambda row: row["id"])
            if not rows:
                continue
            result = _execute(
                driver,
                spec,
                node_merge_query(label),
                {"rows": rows},
            )
            summary = _summary(result)
            nodes_created += _counter(summary, "nodes_created")
            properties_set += _counter(summary, "properties_set")

        labels_by_id = {node.id: node.label for node in projection.nodes}
        grouped_edges: dict[
            tuple[str, str, str], list[dict[str, Any]]
        ] = defaultdict(list)
        for edge in projection.edges:
            properties = primitive_properties(edge.properties)
            properties["key"] = edge.key
            grouped_edges[
                (
                    edge.type,
                    labels_by_id[edge.source],
                    labels_by_id[edge.target],
                )
            ].append(
                {
                    "source": edge.source,
                    "target": edge.target,
                    "key": edge.key,
                    "properties": properties,
                }
            )
        for (edge_type, source_label, target_label), rows in sorted(
            grouped_edges.items()
        ):
            result = _execute(
                driver,
                spec,
                edge_merge_query(
                    edge_type,
                    source_label,
                    target_label,
                ),
                {
                    "rows": sorted(
                        rows,
                        key=lambda row: (
                            row["source"],
                            row["target"],
                            row["key"],
                        ),
                    )
                },
            )
            summary = _summary(result)
            relationships_created += _counter(
                summary, "relationships_created"
            )
            properties_set += _counter(summary, "properties_set")
    finally:
        driver.close()
    return LoadReport(
        target=spec.target,
        projection_id=projection.projection_id,
        nodes_created=nodes_created,
        relationships_created=relationships_created,
        properties_set=properties_set,
    )


def _single_value(
    driver: Any,
    spec: ConnectionSpec,
    query: str,
    key: str,
) -> Any:
    rows = _records(_execute(driver, spec, query))
    if len(rows) != 1 or key not in rows[0]:
        raise GraphVerificationError("Neo4j verification result is invalid")
    return rows[0][key]


def live_status(
    spec: ConnectionSpec,
    *,
    driver_factory: DriverFactory = _default_driver_factory,
) -> dict[str, Any]:
    """Read sanitized mirror status for the fail-closed service."""
    driver = driver_factory(spec)
    try:
        projection_ids = _single_value(
            driver,
            spec,
            VERIFY_QUERIES["projection_ids"],
            "projection_ids",
        )
        node_count = _single_value(
            driver,
            spec,
            "MATCH (n) RETURN count(n) AS count",
            "count",
        )
        edge_count = _single_value(
            driver,
            spec,
            "MATCH ()-[r]->() RETURN count(r) AS count",
            "count",
        )
        partition_rows = _records(
            _execute(
                driver,
                spec,
                VERIFY_QUERIES["synthetic_partition"],
            )
        )
    finally:
        driver.close()
    projection_identity = (
        projection_ids[0]
        if isinstance(projection_ids, list) and len(projection_ids) == 1
        else None
    )
    partition = (
        partition_rows[0]
        if len(partition_rows) == 1
        else {"public_nodes": 0, "synthetic_nodes": 0}
    )
    return {
        "projection_id": projection_identity,
        "counts": {
            "nodes": int(node_count),
            "edges": int(edge_count),
        },
        "synthetic_partition": {
            "public_nodes": int(partition["public_nodes"]),
            "synthetic_nodes": int(partition["synthetic_nodes"]),
        },
    }


def verify(
    spec: ConnectionSpec,
    projection: GraphProjection,
    *,
    driver_factory: DriverFactory = _default_driver_factory,
) -> VerifyReport:
    """Compare all live counts, provenance, and partition to the artifact."""
    driver = driver_factory(spec)
    try:
        counts_by_label = {
            label: int(
                _single_value(
                    driver,
                    spec,
                    f"MATCH (n:`{label}`) RETURN count(n) AS count",
                    "count",
                )
            )
            for label in LABELS
        }
        counts_by_type = {
            edge_type: int(
                _single_value(
                    driver,
                    spec,
                    f"MATCH ()-[r:`{edge_type}`]->() RETURN count(r) AS count",
                    "count",
                )
            )
            for edge_type in projection.counts["edges_by_type"]
        }
        missing_nodes = int(
            _single_value(
                driver,
                spec,
                VERIFY_QUERIES["node_provenance_missing"],
                "count",
            )
        )
        missing_edges = int(
            _single_value(
                driver,
                spec,
                VERIFY_QUERIES["edge_provenance_missing"],
                "count",
            )
        )
        partition_violations = int(
            _single_value(
                driver,
                spec,
                VERIFY_QUERIES["partition_violations"],
                "count",
            )
        )
        projection_ids = _single_value(
            driver,
            spec,
            VERIFY_QUERIES["projection_ids"],
            "projection_ids",
        )
        partition = _records(
            _execute(
                driver,
                spec,
                VERIFY_QUERIES["synthetic_partition"],
            )
        )[0]
    finally:
        driver.close()
    expected_labels = {
        label: int(projection.counts["nodes_by_label"].get(label, 0))
        for label in LABELS
    }
    expected_types = {
        edge_type: int(count)
        for edge_type, count in projection.counts["edges_by_type"].items()
    }
    if counts_by_label != expected_labels or counts_by_type != expected_types:
        raise GraphVerificationError("Neo4j counts differ from projection")
    if missing_nodes or missing_edges:
        raise GraphVerificationError("Neo4j provenance is incomplete")
    if partition_violations:
        raise GraphVerificationError("Neo4j public/Class-D partition is invalid")
    if projection_ids != [projection.projection_id]:
        raise GraphVerificationError("Neo4j projection identity differs")
    return VerifyReport(
        target=spec.target,
        projection_id=projection.projection_id,
        node_count=projection.counts["nodes"],
        edge_count=projection.counts["edges"],
        provenance_complete=True,
        partition_valid=True,
        counts_by_label=counts_by_label,
        counts_by_type=counts_by_type,
        synthetic_partition={
            "public_nodes": int(partition["public_nodes"]),
            "synthetic_nodes": int(partition["synthetic_nodes"]),
        },
    )


def execute_view(
    spec: ConnectionSpec,
    view_id: str,
    *,
    opportunity_id: str,
    mode: str,
    scenario_id: str,
    driver_factory: DriverFactory = _default_driver_factory,
) -> list[dict[str, Any]]:
    """Execute one fixed governed view query."""
    if view_id not in VIEW_QUERIES:
        raise ValueError(f"Unknown graph view: {view_id}")
    driver = driver_factory(spec)
    try:
        rows = _records(
            _execute(
                driver,
                spec,
                VIEW_QUERIES[view_id],
                {
                    "opportunity_id": opportunity_id,
                    "mode": mode,
                    "scenario_id": scenario_id,
                },
            )
        )
    finally:
        driver.close()
    if view_id == "shared_enabler":
        normalized: list[dict[str, Any]] = []
        for row in rows:
            unlock_value = float(row["unlock_value_m_sar"])
            evidence_ids = sorted(
                {
                    str(value)
                    for nested in row.pop("nested_evidence_ids", [])
                    for value in nested
                }
            )
            label_en = row.pop("label_en", None)
            label_ar = row.pop("label_ar", None)
            normalized.append(
                {
                    **row,
                    "label": {"en": label_en, "ar": label_ar},
                    "status": (
                        "POSITIVE"
                        if unlock_value > 0
                        else "NONPOSITIVE"
                    ),
                    "evidence_ids": evidence_ids,
                }
            )
        return normalized
    return rows


def clear(
    spec: ConnectionSpec,
    *,
    confirm: str,
    driver_factory: DriverFactory = _default_driver_factory,
) -> None:
    """Clear a mirror only after exact target-scoped confirmation."""
    if confirm != spec.clear_identity:
        raise GraphSafetyError("CLEAR_CONFIRMATION_MISMATCH")
    driver = driver_factory(spec)
    try:
        _execute(driver, spec, "MATCH (n) DETACH DELETE n")
    finally:
        driver.close()


def wait(
    spec: ConnectionSpec,
    timeout_s: float,
    *,
    driver_factory: DriverFactory = _default_driver_factory,
) -> None:
    """Wait for a mirror without exposing connection details."""
    deadline = time.monotonic() + timeout_s
    while True:
        driver = None
        try:
            driver = driver_factory(spec)
            driver.verify_connectivity()
            return
        except (GraphDriverNotInstalled, GraphSafetyError):
            raise
        except OfflineGuardViolation:
            raise
        except Exception as exc:
            if time.monotonic() >= deadline:
                raise GraphConnectionFailure(
                    "Neo4j readiness timeout"
                ) from exc
            time.sleep(0.5)
        finally:
            if driver is not None:
                driver.close()
