"""Fail-closed graph query service for the S17 API contract."""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Any

from ior_mvp.acquisition.contracts import OfflineGuardViolation

from .engine_feed import shared_enabler_queue_rows
if TYPE_CHECKING:
    from .loader import ConnectionSpec
    from .projection import GraphProjection
else:
    ConnectionSpec = Any


class GraphDriverUnavailable(RuntimeError):
    """Raised when the optional graph driver cannot serve a view."""


class GraphConnectionError(RuntimeError):
    """Raised when the live graph cannot serve a view."""


class GraphNotFound(LookupError):
    """Typed unknown view or opportunity state."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


StatusReader = Callable[[ConnectionSpec], dict[str, Any]]
ViewReader = Callable[
    [ConnectionSpec, str, str, str, str],
    list[dict[str, Any]],
]


def _default_status_reader(spec: ConnectionSpec) -> dict[str, Any]:
    from .loader import (
        GraphConnectionFailure,
        GraphDriverNotInstalled,
        live_status,
    )

    try:
        return live_status(spec)
    except GraphDriverNotInstalled as exc:
        raise GraphDriverUnavailable from exc
    except GraphConnectionFailure as exc:
        raise GraphConnectionError from exc


def _default_view_reader(
    spec: ConnectionSpec,
    view_id: str,
    opportunity_id: str,
    mode: str,
    scenario_id: str,
) -> list[dict[str, Any]]:
    from .loader import (
        GraphConnectionFailure,
        GraphDriverNotInstalled,
        execute_view,
    )

    try:
        return execute_view(
            spec,
            view_id,
            opportunity_id=opportunity_id,
            mode=mode,
            scenario_id=scenario_id,
        )
    except GraphDriverNotInstalled as exc:
        raise GraphDriverUnavailable from exc
    except GraphConnectionFailure as exc:
        raise GraphConnectionError from exc


class GraphService:
    """Serve live graph reads only when the mirror matches the artifact."""

    def __init__(
        self,
        spec: ConnectionSpec | None,
        *,
        artifact_projection_id: str,
        projection: GraphProjection | None = None,
        status_reader: StatusReader = _default_status_reader,
        view_reader: ViewReader = _default_view_reader,
    ) -> None:
        self.spec = spec
        self.artifact_projection_id = artifact_projection_id
        self.projection = projection
        self._status_reader = status_reader
        self._view_reader = view_reader

    @classmethod
    def from_environment(
        cls,
        projection: GraphProjection,
        env: Mapping[str, str] | None = None,
    ) -> "GraphService":
        """Construct a service without reading any dotenv file."""
        values = os.environ if env is None else env
        target = values.get("IOR_GRAPH_TARGET")
        if not target:
            return cls(
                None,
                artifact_projection_id=projection.projection_id,
                projection=projection,
            )
        from .loader import GraphSafetyError, resolve_target

        try:
            spec = resolve_target(
                target,
                values,
                confirm_instance=values.get("AURA_INSTANCEID")
                if target == "aura"
                else None,
            )
        except GraphSafetyError:
            service = cls(
                None,
                artifact_projection_id=projection.projection_id,
                projection=projection,
            )
            service._configuration_reason = "INSTANCE_MISMATCH"
            return service
        return cls(
            spec,
            artifact_projection_id=projection.projection_id,
            projection=projection,
        )

    def _unavailable_status(self, reason_code: str) -> dict[str, Any]:
        return {
            "graph_status": "GRAPH_UNAVAILABLE",
            "reason_code": reason_code,
            "target": self.spec.target if self.spec is not None else None,
            "artifact_projection_id": self.artifact_projection_id,
            "live_projection_id": None,
            "counts": None,
            "synthetic_partition": None,
        }

    def status(self) -> dict[str, Any]:
        """Return AVAILABLE only for an equal live projection."""
        if self.spec is None:
            return self._unavailable_status(
                getattr(self, "_configuration_reason", "NOT_CONFIGURED")
            )
        try:
            live = self._status_reader(self.spec)
        except OfflineGuardViolation:
            raise
        except GraphDriverUnavailable:
            return self._unavailable_status("DRIVER_NOT_INSTALLED")
        except (GraphConnectionError, OSError, TimeoutError):
            return self._unavailable_status("CONNECTION_FAILED")
        if live.get("projection_id") != self.artifact_projection_id:
            result = self._unavailable_status("PROJECTION_MISMATCH")
            result["live_projection_id"] = live.get("projection_id")
            return result
        return {
            "graph_status": "AVAILABLE",
            "reason_code": None,
            "target": self.spec.target,
            "artifact_projection_id": self.artifact_projection_id,
            "live_projection_id": live.get("projection_id"),
            "counts": live.get("counts"),
            "synthetic_partition": live.get("synthetic_partition"),
        }

    def _scenario_id(self, opportunity_id: str, mode: str) -> str:
        if mode == "public":
            return "PUBLIC"
        if self.projection is None:
            return "UNAVAILABLE"
        scenarios = sorted(
            node.id
            for node in self.projection.nodes
            if node.label == "Scenario"
            and node.properties.get("opportunity_id") == opportunity_id
        )
        if len(scenarios) != 1:
            raise GraphNotFound("OPPORTUNITY_NOT_FOUND")
        return scenarios[0]

    def _element_payload(self, identity: str) -> dict[str, Any]:
        if self.projection is None:
            return {
                "id": identity,
                "label": "Evidence",
                "catalogue_key": "node.evidence",
                "name_en": None,
                "name_ar": None,
                "properties": {},
                "provenance": {},
                "derived": False,
            }
        node = next(
            (row for row in self.projection.nodes if row.id == identity),
            None,
        )
        if node is None:
            raise GraphNotFound("OPPORTUNITY_NOT_FOUND")
        properties = dict(node.properties)
        provenance = {
            key: properties[key]
            for key in (
                "evidence_id",
                "as_of",
                "evidence_class",
                "synthetic_flag",
                "scenario_id",
            )
        }
        payload = {
            "id": node.id,
            "label": node.label,
            "catalogue_key": f"node.{node.label.casefold()}",
            "name_en": properties.get("name_en")
            or properties.get("primary_name_en"),
            "name_ar": properties.get("name_ar")
            or properties.get("primary_name_ar"),
            "properties": {
                key: value
                for key, value in properties.items()
                if key
                not in {
                    "evidence_id",
                    "as_of",
                    "evidence_class",
                    "synthetic_flag",
                    "scenario_id",
                    "display_label",
                    "display_label_ar",
                }
            },
            "provenance": provenance,
            "derived": properties.get("derived") is True,
        }
        if properties.get("synthetic_flag") is True:
            payload["display_labels"] = {
                "en": properties["display_label"],
                "ar": properties["display_label_ar"],
            }
        return payload

    def _edge_payload(self, edge: Any) -> dict[str, Any]:
        properties = dict(edge.properties)
        provenance = {
            key: properties[key]
            for key in (
                "evidence_id",
                "as_of",
                "evidence_class",
                "synthetic_flag",
                "scenario_id",
            )
        }
        payload = {
            "id": edge.key,
            "type": edge.type,
            "source": edge.source,
            "target": edge.target,
            "properties": {
                key: value
                for key, value in properties.items()
                if key
                not in {
                    "key",
                    "evidence_id",
                    "as_of",
                    "evidence_class",
                    "synthetic_flag",
                    "scenario_id",
                    "display_label",
                    "display_label_ar",
                }
            },
            "provenance": provenance,
            "derived": properties.get("derived") is True,
        }
        if properties.get("synthetic_flag") is True:
            payload["display_labels"] = {
                "en": properties["display_label"],
                "ar": properties["display_label_ar"],
            }
        return payload

    def _view_elements(
        self,
        view_id: str,
        opportunity_id: str,
        mode: str,
        scenario_id: str,
        rows: list[dict[str, Any]],
        focus_id: str | None = None,
        requirement_item_id: str | None = None,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        if self.projection is None:
            return [], []
        selected_edges = []
        if view_id == "adjacency":
            producer_ids = {
                str(row["producer_id"])
                for row in rows
                if isinstance(row.get("producer_id"), str)
            }
            selected_edges = [
                edge
                for edge in self.projection.edges
                if edge.type == "ADJACENT_TO"
                and edge.source in producer_ids
                and edge.target == opportunity_id
                and (
                    edge.properties.get("scenario_id") == "PUBLIC"
                    if mode == "public"
                    else edge.properties.get("scenario_id") == scenario_id
                )
            ]
            if mode == "public":
                source_membership = {
                    edge.source: set(edge.properties.get("evidence_ids", []))
                    for edge in selected_edges
                }
                selected_edges.extend(
                    edge for edge in self.projection.edges
                    if edge.properties.get("scenario_id") == "PUBLIC"
                    and edge.properties.get("synthetic_flag") is False
                    and (
                        (edge.type == "PRODUCED_BY"
                         and edge.source == opportunity_id
                         and edge.target in producer_ids)
                        or (edge.type in {"USES_PROCESS", "CERTIFIED_TO"}
                            and edge.source in producer_ids
                            and bool(edge.properties.get("evidence_ids"))
                            and set(edge.properties["evidence_ids"])
                            <= source_membership.get(edge.source, set()))
                    )
                )
            if focus_id is not None and mode == "simulated":
                focus = next(node for node in self.projection.nodes if node.id == focus_id)
                selected_edges.extend(
                    edge for edge in self.projection.edges
                    if edge.properties.get("scenario_id") == scenario_id
                    and edge.properties.get("attribution_scope") in {
                        "CANDIDATE_DISCOVERY", "LINE_DIAGNOSTIC"
                    }
                    and (
                        (edge.type == "SUPPORTED_BY_EVIDENCE" and edge.source == focus_id)
                        or (edge.type == "HAS_LINE" and (
                            edge.source == focus_id or edge.target == focus_id
                        ))
                        or (edge.type == "HAS_CAPABILITY"
                            and focus.label == "ProductionLine"
                            and edge.source == opportunity_id
                            and edge.properties.get("canonical_entity_id")
                            == focus.properties.get("canonical_entity_id")
                            and (requirement_item_id is None or
                                 edge.properties.get("requirement_item_id")
                                 == requirement_item_id))
                    )
                )
        elif view_id == "route_blocking":
            pairs = {
                (str(row["intervention_id"]), str(row["capability_id"]))
                for row in rows
            }
            selected_edges = [
                edge
                for edge in self.projection.edges
                if edge.type == "CONSTRAINED_BY"
                and (edge.source, edge.target) in pairs
                and edge.properties.get("reason_code")
                in {
                    row.get("reason_code")
                    for row in rows
                    if row.get("intervention_id") == edge.source
                    and row.get("capability_id") == edge.target
                }
            ]
        elif view_id == "shared_enabler":
            applicable = [
                row
                for row in rows
                if opportunity_id in row.get("dependent_opportunity_ids", [])
            ]
            pairs = {
                (str(dependent), str(row["enabler_id"]))
                for row in applicable
                for dependent in row.get("dependent_opportunity_ids", [])
            }
            selected_edges = [
                edge
                for edge in self.projection.edges
                if edge.type == "UNLOCKED_BY"
                and (edge.source, edge.target) in pairs
                and (
                    edge.properties.get("synthetic_flag") is False
                    if mode == "public"
                    else edge.properties.get("synthetic_flag") is True
                )
            ]
        else:
            pairs = {
                (str(row["decision_id"]), str(row["target_id"]))
                for row in rows
            }
            selected_edges = [
                edge
                for edge in self.projection.edges
                if edge.type == "CONSTRAINED_BY"
                and (edge.source, edge.target) in pairs
                and edge.properties.get("need_code")
                in {
                    row.get("need_code")
                    for row in rows
                    if row.get("decision_id") == edge.source
                    and row.get("target_id") == edge.target
                }
            ]
            evidence_ids = {
                str(value)
                for row in rows
                for value in row.get("evidence_ids", [])
            }
            targets = {target for _source, target in pairs}
            selected_edges.extend(
                edge
                for edge in self.projection.edges
                if edge.type == "SUPPORTED_BY_EVIDENCE"
                and edge.source in targets
                and edge.target in evidence_ids
                and (
                    (
                        edge.properties.get("synthetic_flag") is False
                        and edge.properties.get("scenario_id") == "PUBLIC"
                    )
                    or (
                        mode == "simulated"
                        and edge.properties.get("synthetic_flag") is True
                        and edge.properties.get("scenario_id") == scenario_id
                    )
                )
            )
        selected_edges.sort(
            key=lambda edge: (
                edge.type,
                edge.source,
                edge.target,
                edge.key,
            )
        )
        node_ids = {opportunity_id}
        if focus_id is not None:
            node_ids.add(focus_id)
        for edge in selected_edges:
            node_ids.add(edge.source)
            node_ids.add(edge.target)
        nodes = [
            self._element_payload(identity)
            for identity in sorted(node_ids)
            if any(
                node.id == identity for node in self.projection.nodes
            )
        ]
        return nodes, [
            self._edge_payload(edge) for edge in selected_edges
        ]

    def _focus_id(
        self, opportunity_id: str, mode: str, scenario_id: str,
        context: Mapping[str, str | None] | None,
    ) -> str | None:
        if not context or not any(context.values()):
            return None
        if mode != "simulated" or self.projection is None:
            raise GraphNotFound("GRAPH_CONTEXT_NOT_FOUND")
        company = context.get("company_id")
        plant = context.get("plant_id")
        line = context.get("line_id")
        requirement = context.get("requirement_item_id")
        if not company or (line and not plant) or (plant and not company):
            raise GraphNotFound("GRAPH_CONTEXT_NOT_FOUND")
        scoped = {
            node.properties.get("canonical_entity_id"): node
            for node in self.projection.nodes
            if node.properties.get("scenario_id") == scenario_id
            and node.properties.get("opportunity_id") == opportunity_id
            and node.properties.get("attribution_scope") == "CANDIDATE_DISCOVERY"
            and node.label in {"Company", "Plant", "ProductionLine"}
        }
        company_node = scoped.get(company)
        plant_node = scoped.get(plant) if plant else None
        line_node = scoped.get(line) if line else None
        if company_node is None or company_node.label != "Company":
            raise GraphNotFound("GRAPH_CONTEXT_NOT_FOUND")
        if plant and (plant_node is None or plant_node.label != "Plant"
                      or plant_node.properties.get("company_id") != company):
            raise GraphNotFound("GRAPH_CONTEXT_NOT_FOUND")
        if line and (line_node is None or line_node.label != "ProductionLine"
                     or line_node.properties.get("plant_id") != plant
                     or line_node.properties.get("company_id") != company):
            raise GraphNotFound("GRAPH_CONTEXT_NOT_FOUND")
        focus = line_node or plant_node or company_node
        if requirement and requirement not in focus.properties.get("finding_item_ids", []):
            raise GraphNotFound("GRAPH_CONTEXT_NOT_FOUND")
        return focus.id

    def view(
        self,
        view_id: str,
        opportunity_id: str,
        mode: str,
        context: Mapping[str, str | None] | None = None,
    ) -> dict[str, Any]:
        """Execute a fixed live query and return a typed fail-closed payload."""
        if view_id not in {
            "adjacency",
            "route_blocking",
            "shared_enabler",
            "evidence_to_change",
        }:
            raise GraphNotFound("GRAPH_VIEW_NOT_FOUND")
        if mode not in {"public", "simulated"}:
            raise GraphNotFound("GRAPH_VIEW_NOT_FOUND")
        if self.projection is not None and opportunity_id not in {
            node.id for node in self.projection.nodes if node.label == "Product"
        }:
            raise GraphNotFound("OPPORTUNITY_NOT_FOUND")
        scenario_id = self._scenario_id(opportunity_id, mode)
        focus_id = self._focus_id(opportunity_id, mode, scenario_id, context)
        selection = {
            key: context.get(key) if context else None
            for key in ("company_id", "plant_id", "line_id", "requirement_item_id")
        }
        state = self.status()
        if state["graph_status"] != "AVAILABLE":
            return {
                "view_id": view_id,
                "opportunity_id": opportunity_id,
                "mode": mode,
                "graph_status": "GRAPH_UNAVAILABLE",
                "reason_code": state["reason_code"],
                "projection_id": self.artifact_projection_id,
                "synthetic_flag": False,
                "display_labels": None,
                "nodes": [],
                "edges": [],
                "explanation": None,
                "drilldown": [],
                "context": selection,
                "focus_element_id": focus_id,
            }
        assert self.spec is not None
        try:
            rows = self._view_reader(
                self.spec,
                view_id,
                opportunity_id,
                mode,
                scenario_id,
            )
        except OfflineGuardViolation:
            raise
        except GraphDriverUnavailable:
            reason_code = "DRIVER_NOT_INSTALLED"
        except (GraphConnectionError, OSError, TimeoutError):
            reason_code = "CONNECTION_FAILED"
        else:
            reason_code = None
        if reason_code is not None:
            return {
                "view_id": view_id,
                "opportunity_id": opportunity_id,
                "mode": mode,
                "graph_status": "GRAPH_UNAVAILABLE",
                "reason_code": reason_code,
                "projection_id": self.artifact_projection_id,
                "synthetic_flag": False,
                "display_labels": None,
                "nodes": [],
                "edges": [],
                "explanation": None,
                "drilldown": [],
                "context": selection,
                "focus_element_id": focus_id,
            }
        nodes, edges = self._view_elements(
            view_id,
            opportunity_id,
            mode,
            scenario_id,
            rows,
            focus_id,
            selection["requirement_item_id"],
        )
        elements = [*nodes, *edges]
        synthetic = any(
            element.get("provenance", {}).get("synthetic_flag") is True
            for element in elements
        )
        labels = (
            next(
                (
                    element["display_labels"]
                    for element in elements
                    if element.get("provenance", {}).get("synthetic_flag") is True
                    and "display_labels" in element
                ),
                None,
            )
            if synthetic
            else None
        )
        return {
            "view_id": view_id,
            "opportunity_id": opportunity_id,
            "mode": mode,
            "graph_status": "AVAILABLE",
            "reason_code": None,
            "projection_id": self.artifact_projection_id,
            "synthetic_flag": synthetic,
            "display_labels": labels,
            "nodes": nodes,
            "edges": edges,
            "explanation": {
                "catalogue_key": f"view.{view_id}.explanation",
                "values": {"row_count": len(rows)},
            },
            "drilldown": [
                {
                    "element_id": node["id"],
                    "evidence_ids": node["properties"].get(
                        "evidence_ids", []
                    ),
                    "document_addresses": node["properties"].get(
                        "document_addresses", []
                    ),
                }
                for node in elements
            ],
            "context": selection,
            "focus_element_id": focus_id,
        }

    def shared_enablers(self, mode: str) -> dict[str, Any]:
        """Return typed portfolio rows after live-projection equality."""
        state = self.status()
        if state["graph_status"] != "AVAILABLE":
            return {
                "mode": mode,
                "graph_status": "GRAPH_UNAVAILABLE",
                "reason_code": state["reason_code"],
                "projection_id": self.artifact_projection_id,
                "rows": [],
            }
        if self.projection is None:
            rows: list[dict[str, Any]] = []
        elif mode == "public":
            assert self.spec is not None
            artifact_rows = shared_enabler_queue_rows(
                self.projection,
                branch="public",
            )
            try:
                rows = self._view_reader(
                    self.spec,
                    "shared_enabler",
                    "",
                    "public",
                    "PUBLIC",
                )
            except OfflineGuardViolation:
                raise
            except GraphDriverUnavailable:
                return {
                    "mode": mode,
                    "graph_status": "GRAPH_UNAVAILABLE",
                    "reason_code": "DRIVER_NOT_INSTALLED",
                    "projection_id": self.artifact_projection_id,
                    "rows": [],
                }
            except (GraphConnectionError, OSError, TimeoutError):
                return {
                    "mode": mode,
                    "graph_status": "GRAPH_UNAVAILABLE",
                    "reason_code": "CONNECTION_FAILED",
                    "projection_id": self.artifact_projection_id,
                    "rows": [],
                }
            if rows != artifact_rows:
                return {
                    "mode": mode,
                    "graph_status": "GRAPH_UNAVAILABLE",
                    "reason_code": "PROJECTION_MISMATCH",
                    "projection_id": self.artifact_projection_id,
                    "rows": [],
                }
        else:
            assert self.spec is not None
            scenario_ids = sorted(
                node.id
                for node in self.projection.nodes
                if node.label == "Scenario"
            )
            artifact_rows = [
                row
                for scenario_id in scenario_ids
                for row in shared_enabler_queue_rows(
                    self.projection,
                    branch=("simulated", scenario_id),
                )
            ]
            artifact_rows = list(
                {
                    row["enabler_id"]: row
                    for row in artifact_rows
                }.values()
            )
            rows = []
            for scenario_id in scenario_ids:
                try:
                    rows.extend(
                        self._view_reader(
                            self.spec,
                            "shared_enabler",
                            "",
                            "simulated",
                            scenario_id,
                        )
                    )
                except OfflineGuardViolation:
                    raise
                except GraphDriverUnavailable:
                    return {
                        "mode": mode,
                        "graph_status": "GRAPH_UNAVAILABLE",
                        "reason_code": "DRIVER_NOT_INSTALLED",
                        "projection_id": self.artifact_projection_id,
                        "rows": [],
                    }
                except (GraphConnectionError, OSError, TimeoutError):
                    return {
                        "mode": mode,
                        "graph_status": "GRAPH_UNAVAILABLE",
                        "reason_code": "CONNECTION_FAILED",
                        "projection_id": self.artifact_projection_id,
                        "rows": [],
                    }
            rows = list(
                {
                    row["enabler_id"]: row
                    for row in rows
                }.values()
            )
            if rows != artifact_rows:
                return {
                    "mode": mode,
                    "graph_status": "GRAPH_UNAVAILABLE",
                    "reason_code": "PROJECTION_MISMATCH",
                    "projection_id": self.artifact_projection_id,
                    "rows": [],
                }
        return {
            "mode": mode,
            "graph_status": "AVAILABLE",
            "reason_code": None,
            "projection_id": self.artifact_projection_id,
            "rows": rows,
        }
