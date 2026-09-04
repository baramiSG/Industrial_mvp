"""CEPII BACI bulk connector — raw-only in S11."""

from __future__ import annotations

import json
from datetime import date
from typing import Any

from ..contracts import (
    AcquisitionUnavailable,
    PageMeta,
    QualityCheck,
    QualityReport,
    RawArtifact,
    TariffLine,
    TradeObservation,
    UNAVAILABLE,
    UnavailableReason,
)
from .base import BaseConnector


class BaciCepiiConnector(BaseConnector):
    source_id = "baci_cepii"
    snapshot_kinds: frozenset[str] = frozenset()

    def page_meta(self, payload: bytes, content_type: str) -> PageMeta:
        return PageMeta(
            page_index=1,
            pages_expected=1,
            next_page_token_present=False,
            rows_in_page=UNAVAILABLE,
            enumerated_children=None,
        )

    def validate(self, raw: RawArtifact) -> QualityReport:
        contract = raw.contract
        payload = self.store.read_payload(contract)
        checks = (
            QualityCheck(
                "bulk_payload_present",
                "PASS" if payload else "FAIL",
                f"{len(payload)} bytes",
            ),
        )
        return QualityReport(
            source_id=contract.source_id,
            query_hash=contract.query_hash,
            run_id=contract.run_id,
            status="PASS" if payload else "FAIL",
            checks=checks,
        )

    def normalize(
        self, raw: RawArtifact
    ) -> list[TradeObservation] | list[TariffLine]:
        payload = self.store.read_payload(raw.contract)
        if payload[:2] == b"PK":
            return []
        try:
            text = payload.decode("utf-8", errors="replace")
            if text.strip().startswith("{"):
                json.loads(text)
        except json.JSONDecodeError:
            return []
        return []

    def snapshot(
        self,
        observations: list[Any],
        as_of_date: date,
    ) -> dict[str, Any]:
        raise AcquisitionUnavailable(
            UnavailableReason.OUT_OF_SCOPE_CONTENT,
            {"detail": "RAW_ONLY_NO_SNAPSHOT_KIND"},
        )
