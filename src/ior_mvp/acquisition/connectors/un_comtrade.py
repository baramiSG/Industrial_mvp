"""UN Comtrade connector."""

from __future__ import annotations

import json
from datetime import date
from typing import Any

from ..contracts import (
    PageMeta,
    QualityCheck,
    QualityReport,
    RawArtifact,
    TariffLine,
    TradeObservation,
    UNAVAILABLE,
)
from ..harmonise import trade_observation_from_row
from .base import BaseConnector


class UnComtradeConnector(BaseConnector):
    source_id = "un_comtrade"
    snapshot_kinds = frozenset({"universe", "partners"})

    def page_meta(self, payload: bytes, content_type: str) -> PageMeta:
        rows = UNAVAILABLE
        next_token = False
        try:
            data = json.loads(payload.decode("utf-8"))
            if isinstance(data, dict):
                dataset = data.get("data", [])
                if isinstance(dataset, list):
                    rows = len(dataset)
                next_token = bool(data.get("next"))
        except (UnicodeError, json.JSONDecodeError):
            pass
        return PageMeta(
            page_index=1,
            pages_expected=UNAVAILABLE,
            next_page_token_present=next_token,
            rows_in_page=rows,
            enumerated_children=None,
        )

    def validate(self, raw: RawArtifact) -> QualityReport:
        contract = raw.contract
        payload = self.store.read_payload(contract)
        rows = self.parse_rows(payload, contract.content_type)
        checks = (
            QualityCheck(
                "reporter_is_SAU",
                "PASS" if contract.reporter == "SAU" else "FAIL",
                contract.reporter,
            ),
            QualityCheck(
                "rows_present",
                "PASS" if rows else "FAIL",
                f"{len(rows)} rows",
            ),
        )
        status = "PASS" if all(c.result == "PASS" for c in checks) else "FAIL"
        return QualityReport(
            source_id=contract.source_id,
            query_hash=contract.query_hash,
            run_id=contract.run_id,
            status=status,
            checks=checks,
        )

    def normalize(
        self, raw: RawArtifact
    ) -> list[TradeObservation] | list[TariffLine]:
        payload = self.store.read_payload(raw.contract)
        rows = self.parse_rows(payload, raw.contract.content_type)
        if not rows:
            return []
        evidence_id = f"{raw.contract.query_hash[:12]}-p{raw.contract.page_index:04d}"
        return [
            trade_observation_from_row(
                row,
                field_map={
                    "year": "year",
                    "reporter": "reporter",
                    "partner": "partner",
                    "flow": "flow",
                    "hs6": "hs6",
                    "trade_value": "trade_value",
                    "trade_value_value": "trade_value_value",
                    "net_weight": "net_weight",
                    "net_weight_value": "net_weight_value",
                    "weight_unit": "weight_unit",
                    "currency": "currency",
                },
                reporter_expected="SAU",
                hs_revision=self.source_config["nomenclature"],
                source_evidence_id=evidence_id,
                valuation_by_flow={"imports": "CIF", "exports": "FOB"},
            )
            for row in rows
        ]

    def _parse_rows(self, payload: bytes) -> list[dict[str, Any]]:
        try:
            data = json.loads(payload.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            return []
        rows: list[dict[str, Any]] = []
        if isinstance(data, dict):
            for item in data.get("data", []):
                if isinstance(item, dict):
                    flow_code = str(item.get("flowCode", ""))
                    flow = "imports" if flow_code == "M" else "exports"
                    rows.append(
                        {
                            "year": int(item.get("period", 0)),
                            "reporter": "SAU",
                            "partner": str(item.get("partnerDesc", UNAVAILABLE)),
                            "flow": flow,
                            "hs6": str(item.get("cmdCode", ""))[:6],
                            "trade_value": str(item.get("primaryValue", "")),
                            "trade_value_value": item.get("primaryValue"),
                            "net_weight": str(item.get("netWgt", "")),
                            "net_weight_value": item.get("netWgt"),
                            "weight_unit": "kg",
                            "currency": "USD",
                        }
                    )
        return rows

    def parse_rows(self, payload: bytes, content_type: str) -> list[dict[str, Any]]:
        return self._parse_rows(payload)

    def snapshot(
        self,
        observations: list[Any],
        as_of_date: date,
    ) -> dict[str, Any]:
        from .. import snapshots

        return snapshots.build_universe_snapshot(
            self.store,
            {"sources": {self.source_id: self.source_config}, "metadata": {"version": self.config_version}},
            __import__("ior_mvp.acquisition.connectors.base", fromlist=["default_registry"]).default_registry(),
            source_id=self.source_id,
        )
