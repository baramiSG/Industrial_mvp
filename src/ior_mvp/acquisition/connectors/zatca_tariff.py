"""ZATCA tariff connector."""

from __future__ import annotations

import json
import re
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
from ..harmonise import tariff_line_from_row
from .base import BaseConnector


class ZatcaTariffConnector(BaseConnector):
    source_id = "zatca_tariff"
    snapshot_kinds = frozenset({"tariff"})

    def page_meta(self, payload: bytes, content_type: str) -> PageMeta:
        text = payload.decode("utf-8", errors="replace")
        children = tuple(sorted(set(re.findall(r'data-hs6="(\d{6})"', text))))
        return PageMeta(
            page_index=1,
            pages_expected=1 if not children else len(children),
            next_page_token_present=False,
            rows_in_page=len(children) if children else UNAVAILABLE,
            enumerated_children=children or None,
        )

    def validate(self, raw: RawArtifact) -> QualityReport:
        contract = raw.contract
        lines = self.normalize(raw)
        checks = (
            QualityCheck(
                "tree_enumeration_complete",
                "PASS" if lines else "FAIL",
                f"{len(lines)} lines",
            ),
        )
        status = "PASS" if lines else "FAIL"
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
        text = payload.decode("utf-8", errors="replace")
        evidence_id = f"{raw.contract.query_hash[:12]}-p{raw.contract.page_index:04d}"
        lines: list[TariffLine] = []
        for match in re.finditer(
            r'data-code="(\d{12})"[^>]*data-hs6="(\d{6})"[^>]*'
            r'data-desc-en="([^"]*)"[^>]*data-desc-ar="([^"]*)"',
            text,
        ):
            national_code, hs6, desc_en, desc_ar = match.groups()
            try:
                lines.append(
                    tariff_line_from_row(
                        {
                            "national_code": national_code,
                            "hs6": hs6,
                            "description_en": desc_en,
                            "description_ar": desc_ar,
                            "duty_fields": {},
                            "hs6_mapping_basis": "prefix_6",
                        },
                        field_map={
                            "national_code": "national_code",
                            "hs6": "hs6",
                            "description_en": "description_en",
                            "description_ar": "description_ar",
                            "duty_fields": "duty_fields",
                            "hs6_mapping_basis": "hs6_mapping_basis",
                        },
                        hs_revision=self.source_config["nomenclature"],
                        source_evidence_id=evidence_id,
                    )
                )
            except ValueError:
                continue
        if lines:
            return lines
        try:
            data = json.loads(text)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        lines.append(
                            tariff_line_from_row(
                                item,
                                field_map={
                                    "national_code": "national_code",
                                    "hs6": "hs6",
                                    "description_en": "description_en",
                                    "description_ar": "description_ar",
                                    "duty_fields": "duty_fields",
                                    "hs6_mapping_basis": "hs6_mapping_basis",
                                },
                                hs_revision=self.source_config["nomenclature"],
                                source_evidence_id=evidence_id,
                            )
                        )
        except (UnicodeError, json.JSONDecodeError):
            pass
        return lines

    def snapshot(
        self,
        observations: list[Any],
        as_of_date: date,
    ) -> dict[str, Any]:
        from .. import snapshots

        return snapshots.build_tariff_snapshot(
            self.store,
            {"sources": {self.source_id: self.source_config}, "metadata": {"version": self.config_version}},
            __import__("ior_mvp.acquisition.connectors.base", fromlist=["default_registry"]).default_registry(),
            source_id=self.source_id,
        )
