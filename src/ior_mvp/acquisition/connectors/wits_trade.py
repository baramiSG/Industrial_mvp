"""WITS trade connector."""

from __future__ import annotations

import json
import re
from datetime import date
from html import unescape
from typing import Any

from ..contracts import (
    PageMeta,
    QualityCheck,
    QualityReport,
    RawArtifact,
    SourceContractRecord,
    TariffLine,
    TradeObservation,
    UNAVAILABLE,
)
from ..harmonise import trade_observation_from_row
from .base import BaseConnector

_ROW_PATTERN = re.compile(
    r"<tr\s+class='(?:odd|even)'>"
    r".*?<td[^>]*>\s*(Import|Export)\s*</td>"
    r".*?<td[^>]*>\s*(\d{6})\s*</td>"
    r".*?<td[^>]*>\s*(\d{4})\s*</td>"
    r".*?partner/[^>]+>\s*([^<]+?)\s*</a></td>"
    r".*?<td[^>]*>\s*([\d,\.]+)\s*</td>"
    r".*?<td[^>]*>\s*([\d,\.]+)\s*</td>"
    r".*?<td[^>]*>\s*([^<]+?)\s*</td>",
    re.DOTALL | re.IGNORECASE,
)


class WitsTradeConnector(BaseConnector):
    source_id = "wits_trade"
    snapshot_kinds = frozenset({"universe", "partners"})

    def page_meta(self, payload: bytes, content_type: str) -> PageMeta:
        text = payload.decode("utf-8", errors="replace")
        rows = len(_ROW_PATTERN.findall(text))
        return PageMeta(
            page_index=1,
            pages_expected=1,
            next_page_token_present=False,
            rows_in_page=rows if rows else UNAVAILABLE,
            enumerated_children=None,
        )

    def validate(self, raw: RawArtifact) -> QualityReport:
        checks: list[QualityCheck] = []
        contract = raw.contract
        checks.append(
            QualityCheck(
                "reporter_is_SAU",
                "PASS" if contract.reporter == "SAU" else "FAIL",
                contract.reporter,
            )
        )
        payload = self.store.read_payload(contract)
        rows = self.parse_rows(payload, contract.content_type)
        checks.append(
            QualityCheck(
                "rows_present",
                "PASS" if rows else "FAIL",
                f"{len(rows)} rows",
            )
        )
        for index, row in enumerate(rows):
            try:
                valid_year = int(row.get("year", 0)) > 0
            except (ValueError, TypeError):
                valid_year = False
            hs6 = str(row.get("hs6", ""))
            shape_valid = valid_year and len(hs6) == 6 and hs6.isdigit() and row.get("flow") in {"imports", "exports"}
            checks.append(QualityCheck(f"row_{index}_shape", "PASS" if shape_valid else "FAIL", "year, HS6 and flow"))
            checks.append(QualityCheck(f"row_{index}_reporter", "PASS" if row.get("reporter") == contract.reporter else "FAIL", "row reporter matches contract"))
        status = "PASS" if all(c.result == "PASS" for c in checks) else "FAIL"
        return QualityReport(
            source_id=contract.source_id,
            query_hash=contract.query_hash,
            run_id=contract.run_id,
            status=status,
            checks=tuple(checks),
        )

    def normalize(
        self, raw: RawArtifact
    ) -> list[TradeObservation] | list[TariffLine]:
        payload = self.store.read_payload(raw.contract)
        rows = self.parse_rows(payload, raw.contract.content_type)
        if not rows:
            return []
        evidence_id = f"{raw.contract.query_hash[:12]}-p{raw.contract.page_index:04d}"
        observations: list[TradeObservation] = []
        for row in rows:
            observations.append(
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
                    valuation_by_flow={
                        "imports": "CIF",
                        "exports": "FOB",
                    },
                )
            )
        return observations

    def _parse_rows(
        self,
        payload: bytes,
        contract: SourceContractRecord | None = None,
    ) -> list[dict[str, Any]]:
        text = payload.decode("utf-8", errors="replace")
        rows: list[dict[str, Any]] = []

        for match in _ROW_PATTERN.finditer(text):
            flow_raw, hs6, year, partner, value_text, weight_text, weight_unit = (
                match.groups()
            )
            flow = "imports" if flow_raw.lower().startswith("import") else "exports"
            value_clean = value_text.replace(",", "")
            weight_clean = weight_text.replace(",", "")
            rows.append(
                {
                    "year": int(year),
                    "reporter": "SAU",
                    "partner": unescape(partner.strip()),
                    "flow": flow,
                    "hs6": hs6,
                    "trade_value": value_text,
                    "trade_value_value": float(value_clean) * 1000.0,
                    "net_weight": weight_text,
                    "net_weight_value": float(weight_clean),
                    "weight_unit": weight_unit.strip(),
                    "currency": "USD",
                }
            )

        if rows:
            return rows

        try:
            data = json.loads(text)
        except (UnicodeError, json.JSONDecodeError):
            return []
        if isinstance(data, dict):
            dataset = data.get("dataset", data)
            if isinstance(dataset, dict):
                for item in dataset.get("data", []):
                    if isinstance(item, dict):
                        rows.append(item)
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
            {
                "sources": {self.source_id: self.source_config},
                "metadata": {"version": self.config_version},
            },
            __import__(
                "ior_mvp.acquisition.connectors.base",
                fromlist=["default_registry"],
            ).default_registry(),
            source_id=self.source_id,
        )
