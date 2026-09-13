"""UN Comtrade connector."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from ..contracts import (
    CompletenessBasis,
    PageMeta,
    QualityCheck,
    QualityReport,
    RawArtifact,
    TariffLine,
    TradeObservation,
    UNAVAILABLE,
    UnavailableReason,
    Stage,
)
from ..harmonise import trade_observation_from_row
from .base import BaseConnector


class UnComtradeConnector(BaseConnector):
    source_id = "un_comtrade"
    snapshot_kinds = frozenset({"universe", "partners"})
    documented_record_cap = 100_000

    def single_response_completeness_basis(self) -> CompletenessBasis:
        return (
            CompletenessBasis.PROVIDER_COUNT_MATCH_BELOW_DOCUMENTED_CAP_100000
        )

    def coverage_stop_reason(
        self, raw: RawArtifact
    ) -> UnavailableReason | None:
        payload = self.store.read_payload(raw.contract)
        envelope = (
            self._envelope(payload)
            if self._json_content_type(raw.contract.content_type)
            else None
        )
        if envelope is None:
            return UnavailableReason.COVERAGE_INDETERMINATE
        dataset = envelope.get("data")
        count = envelope.get("count")
        if (
            isinstance(count, int)
            and not isinstance(count, bool)
            and count >= self.documented_record_cap
        ):
            return UnavailableReason.RECORD_CAP_REACHED
        if (
            isinstance(dataset, list)
            and isinstance(count, int)
            and not isinstance(count, bool)
            and count != len(dataset)
        ):
            return UnavailableReason.COUNT_MISMATCH
        report = self.validate(raw)
        if report.status == "PASS":
            return None
        failed = {
            check.check_id for check in report.checks if check.result != "PASS"
        }
        if "reporter_682_all_rows" in failed:
            return UnavailableReason.REPORTER_MISMATCH
        if failed == {"partner_desc_present_for_non_world_rows"}:
            return UnavailableReason.PARTNER_DESCRIPTIONS_UNAVAILABLE
        return UnavailableReason.COVERAGE_INDETERMINATE

    @staticmethod
    def _json_content_type(content_type: str) -> bool:
        media_type = content_type.split(";", 1)[0].strip().casefold()
        return media_type == "application/json" or media_type.endswith(
            "+json"
        )

    @staticmethod
    def _envelope(payload: bytes) -> dict[str, Any] | None:
        try:
            value = json.loads(payload.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            return None
        return value if isinstance(value, dict) else None

    @staticmethod
    def _error_is_clear(envelope: dict[str, Any]) -> bool:
        return envelope.get("error") in (None, "", [], {})

    @staticmethod
    def _decimal_scale(value: str) -> int:
        decimal = Decimal(value)
        return max(0, -decimal.as_tuple().exponent)

    def _universe_reference(
        self,
        *,
        flow: str,
        period: str,
        hs6: str,
    ) -> str | None:
        selected = self.store.latest_runs(
            source_id=self.source_id,
            stage=Stage.UNIVERSE.value,
        ).get((flow, period))
        if selected is None or selected[0].status != "COMPLETE":
            return None
        coverage = selected[0]
        for contract in self.store.pages_for(
            self.source_id,
            coverage.query_hash,
            coverage.run_id,
        ):
            try:
                envelope = json.loads(
                    self.store.read_payload(contract).decode("utf-8"),
                    parse_float=str,
                )
            except (UnicodeError, json.JSONDecodeError):
                return None
            rows = envelope.get("data") if isinstance(envelope, dict) else None
            if not isinstance(rows, list):
                return None
            for row in rows:
                if (
                    isinstance(row, dict)
                    and str(row.get("cmdCode")) == hs6
                    and row.get("primaryValue") is not None
                ):
                    return str(row["primaryValue"])
        return None

    def _aggregate_reconciliation(
        self,
        *,
        payload: bytes,
        query: Any,
    ) -> tuple[bool, str]:
        reference_text = self._universe_reference(
            flow=query.flow,
            period=query.periods[0] if query.periods else "",
            hs6=query.product_codes[0] if query.product_codes else "",
        )
        if reference_text is None:
            return False, "reference unavailable"
        try:
            envelope = json.loads(payload.decode("utf-8"), parse_float=str)
            rows = envelope.get("data") if isinstance(envelope, dict) else None
            if not isinstance(rows, list):
                return False, "partner rows unavailable"
            reference = Decimal(reference_text)
            non_world = [
                str(row["primaryValue"])
                for row in rows
                if isinstance(row, dict)
                and str(row.get("partnerCode")) != "0"
                and row.get("primaryValue") is not None
            ]
            if len(non_world) != sum(
                isinstance(row, dict)
                and str(row.get("partnerCode")) != "0"
                for row in rows
            ):
                return False, "non-World primaryValue unavailable"
            values = [Decimal(value) for value in non_world]
            world_values = [
                str(row["primaryValue"])
                for row in rows
                if isinstance(row, dict)
                and str(row.get("partnerCode")) == "0"
                and row.get("primaryValue") is not None
            ]
            scale = max(
                [self._decimal_scale(reference_text)]
                + [self._decimal_scale(value) for value in non_world]
                + [self._decimal_scale(value) for value in world_values]
            )
            unit = Decimal(10) ** -scale
            total = sum(values, Decimal(0))
            tolerance = Decimal(len(values)) * unit / 2
            difference = abs(total - reference)
            world_ok = all(
                abs(Decimal(value) - reference) <= unit / 2
                for value in world_values
            )
            passed = difference <= tolerance and world_ok
            return (
                passed,
                (
                    f"S={total}; R={reference}; diff={difference}; "
                    f"s={scale}; tolerance={tolerance}; world_match={world_ok}"
                ),
            )
        except (InvalidOperation, KeyError, TypeError, ValueError):
            return False, "numeric token unavailable"

    def page_meta(self, payload: bytes, content_type: str) -> PageMeta:
        rows = UNAVAILABLE
        pages_expected: int | str = UNAVAILABLE
        envelope = (
            self._envelope(payload)
            if self._json_content_type(content_type)
            else None
        )
        if envelope is not None:
            dataset = envelope.get("data")
            count = envelope.get("count")
            if isinstance(dataset, list):
                rows = len(dataset)
                if (
                    isinstance(count, int)
                    and not isinstance(count, bool)
                    and count == rows
                    and count < self.documented_record_cap
                    and self._error_is_clear(envelope)
                ):
                    pages_expected = 1
        return PageMeta(
            page_index=1,
            pages_expected=pages_expected,
            next_page_token_present=False,
            rows_in_page=rows,
            enumerated_children=None,
        )

    def classify_page(
        self,
        payload: bytes,
        content_type: str,
        stage: Stage,
    ) -> tuple[str, str | None]:
        if stage is Stage.PARTNERS and self._json_content_type(content_type):
            envelope = self._envelope(payload)
            if (
                envelope is not None
                and envelope.get("count") == 0
                and envelope.get("data") == []
                and self._error_is_clear(envelope)
            ):
                return "NORMALIZED_EMPTY", "zero_rows_provider_count_0"
        return super().classify_page(payload, content_type, stage)

    def validate(self, raw: RawArtifact) -> QualityReport:
        contract = raw.contract
        payload = self.store.read_payload(contract)
        content_type_json = self._json_content_type(contract.content_type)
        envelope = self._envelope(payload) if content_type_json else None
        dataset = envelope.get("data") if envelope is not None else None
        count = envelope.get("count") if envelope is not None else None
        rows = dataset if isinstance(dataset, list) else []
        query = contract.query_contract
        expected_reporter = str(
            self.source_config.get("parameters", {}).get(
                "reporter_token",
                "682",
            )
        )
        expected_flow = str(
            self.source_config.get("parameters", {})
            .get("flow_tokens", {})
            .get(query.flow, query.flow)
        )
        expected_period = query.periods[0] if query.periods else ""
        partner_stage = query.stage is Stage.PARTNERS
        zero_envelope = (
            partner_stage
            and envelope is not None
            and count == 0
            and dataset == []
            and self._error_is_clear(envelope)
        )
        aggregate_ok, aggregate_detail = self._aggregate_reconciliation(
            payload=payload,
            query=query,
        ) if partner_stage else (True, "not applicable")
        reporter_ok = bool(rows) and all(
            str(item.get("reporterCode")) == expected_reporter
            for item in rows
            if isinstance(item, dict)
        ) and all(isinstance(item, dict) for item in rows)
        period_ok = bool(rows) and all(
            str(item.get("period")) == expected_period
            for item in rows
            if isinstance(item, dict)
        ) and all(isinstance(item, dict) for item in rows)
        flow_ok = bool(rows) and all(
            str(item.get("flowCode")) == expected_flow
            for item in rows
            if isinstance(item, dict)
        ) and all(isinstance(item, dict) for item in rows)
        if zero_envelope:
            reporter_ok = period_ok = flow_ok = True
        if query.stage.value == "UNIVERSE":
            partner_ok = bool(rows) and all(
                isinstance(item, dict)
                and str(item.get("partnerCode")) == "0"
                for item in rows
            )
        else:
            partner_ok = zero_envelope or (
                bool(rows)
                and any(
                    isinstance(item, dict)
                    and str(item.get("partnerCode")) != "0"
                    for item in rows
                )
            )
        hs6_values = [
            str(item.get("cmdCode", ""))
            for item in rows
            if isinstance(item, dict)
        ]
        hs6_ok = (
            len(hs6_values) == len(rows)
            and bool(hs6_values)
            and all(len(value) == 6 and value.isdigit() for value in hs6_values)
        )
        if query.product_scope.value == "EXPLICIT":
            hs6_ok = hs6_ok and all(
                value in query.product_codes for value in hs6_values
            )
        classifications = [
            str(item.get("classificationCode", ""))
            for item in rows
            if isinstance(item, dict)
        ]
        classification_ok = (
            len(classifications) == len(rows)
            and bool(classifications)
            and all(classifications)
            and len(set(classifications)) == 1
        )
        if zero_envelope:
            hs6_ok = classification_ok = True
        duplicate_ok = len(set(hs6_values)) == len(hs6_values)
        common_checks = (
            QualityCheck(
                "content_type_json",
                "PASS" if content_type_json else "FAIL",
                contract.content_type,
            ),
            QualityCheck(
                "envelope_shape",
                "PASS"
                if envelope is not None
                and isinstance(dataset, list)
                and isinstance(count, int)
                and not isinstance(count, bool)
                else "FAIL",
                "count integer and data list required",
            ),
            QualityCheck(
                "no_error_field",
                "PASS"
                if envelope is not None and self._error_is_clear(envelope)
                else "FAIL",
                "error must be absent, null, or empty",
            ),
            QualityCheck(
                "count_matches_rows",
                "PASS"
                if isinstance(count, int)
                and not isinstance(count, bool)
                and count == len(rows)
                else "FAIL",
                f"count={count!r}; stored_rows={len(rows)}",
            ),
        )
        if not partner_stage:
            checks = common_checks + (
            QualityCheck(
                "rows_present",
                "PASS" if rows else "FAIL",
                f"{len(rows)} rows",
            ),
            QualityCheck(
                "reporter_682_all_rows",
                "PASS" if reporter_ok else "FAIL",
                f"expected reporterCode={expected_reporter}",
            ),
            QualityCheck(
                "period_matches_contract",
                "PASS" if period_ok else "FAIL",
                f"expected period={expected_period}",
            ),
            QualityCheck(
                "flow_matches_contract",
                "PASS" if flow_ok else "FAIL",
                f"expected flowCode={expected_flow}",
            ),
            QualityCheck(
                "partner_matches_stage",
                "PASS" if partner_ok else "FAIL",
                query.stage.value,
            ),
            QualityCheck(
                "cmd_code_hs6_all_rows",
                "PASS" if hs6_ok else "FAIL",
                "six-digit HS6 required",
            ),
            QualityCheck(
                "single_classification_code_per_unit",
                "PASS" if classification_ok else "FAIL",
                f"classification_codes={sorted(set(classifications))}",
            ),
            QualityCheck(
                "no_duplicate_hs6_per_unit",
                "PASS" if duplicate_ok else "FAIL",
                query.stage.value,
            ),
            )
        else:
            partner_pairs = [
                (str(item.get("cmdCode", "")), str(item.get("partnerCode", "")))
                for item in rows
                if isinstance(item, dict)
            ]
            pair_unique = (
                zero_envelope
                or (
                    len(partner_pairs) == len(rows)
                    and len(set(partner_pairs)) == len(partner_pairs)
                )
            )
            secondary_fields = ("partner2Code", "motCode", "customsCode")
            secondary_ok = zero_envelope or all(
                not any(field in item for item in rows if isinstance(item, dict))
                or (
                    all(
                        isinstance(item, dict) and field in item
                        for item in rows
                    )
                    and len(
                        {
                            str(item[field])
                            for item in rows
                            if isinstance(item, dict)
                        }
                    )
                    == 1
                )
                for field in secondary_fields
            )
            partner_desc_ok = zero_envelope or all(
                str(item.get("partnerCode")) == "0"
                or (
                    isinstance(item.get("partnerDesc"), str)
                    and bool(item["partnerDesc"].strip())
                    and item["partnerDesc"] != UNAVAILABLE
                )
                for item in rows
                if isinstance(item, dict)
            )
            non_world_descs = [
                item["partnerDesc"].strip()
                for item in rows
                if isinstance(item, dict)
                and str(item.get("partnerCode")) != "0"
                and isinstance(item.get("partnerDesc"), str)
                and item["partnerDesc"].strip()
                and item["partnerDesc"] != UNAVAILABLE
            ]
            partner_desc_unique = (
                len(non_world_descs) == len(set(non_world_descs))
            )
            checks = common_checks + (
                QualityCheck(
                    "count_below_documented_cap",
                    "PASS"
                    if isinstance(count, int)
                    and not isinstance(count, bool)
                    and count < self.documented_record_cap
                    else "FAIL",
                    f"count={count!r}; cap={self.documented_record_cap}",
                ),
                QualityCheck(
                    "rows_or_zero_envelope",
                    "PASS" if rows or zero_envelope else "FAIL",
                    f"{len(rows)} rows; zero_envelope={zero_envelope}",
                ),
                QualityCheck(
                    "reporter_682_all_rows",
                    "PASS" if reporter_ok else "FAIL",
                    f"expected reporterCode={expected_reporter}",
                ),
                QualityCheck(
                    "period_matches_contract",
                    "PASS" if period_ok else "FAIL",
                    f"expected period={expected_period}",
                ),
                QualityCheck(
                    "flow_matches_contract",
                    "PASS" if flow_ok else "FAIL",
                    f"expected flowCode={expected_flow}",
                ),
                QualityCheck(
                    "partner_matches_stage",
                    "PASS" if partner_ok else "FAIL",
                    query.stage.value,
                ),
                QualityCheck(
                    "cmd_code_hs6_all_rows",
                    "PASS" if hs6_ok else "FAIL",
                    "six-digit explicit HS6 required",
                ),
                QualityCheck(
                    "single_classification_code_per_unit",
                    "PASS" if classification_ok else "FAIL",
                    f"classification_codes={sorted(set(classifications))}",
                ),
                QualityCheck(
                    "partner_rows_unique_per_unit",
                    "PASS" if pair_unique else "FAIL",
                    "(cmdCode, partnerCode) must be unique",
                ),
                QualityCheck(
                    "secondary_dimensions_single_valued",
                    "PASS" if secondary_ok else "FAIL",
                    "present partner2Code/motCode/customsCode fields",
                ),
                QualityCheck(
                    "partner_desc_present_for_non_world_rows",
                    "PASS" if partner_desc_ok else "FAIL",
                    "non-World rows require partnerDesc",
                ),
                QualityCheck(
                    "aggregate_reconciles",
                    "PASS" if aggregate_ok else "FAIL",
                    aggregate_detail,
                ),
                QualityCheck(
                    "partner_desc_unique_for_non_world_rows",
                    "PASS" if partner_desc_unique else "FAIL",
                    "non-empty non-World partnerDesc values must be unique",
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
                    hs_revision=row["classification_code"],
                    source_evidence_id=evidence_id,
                    valuation_by_flow={
                        "imports": "CIF",
                        "exports": "FOB",
                    },
                )
            )
        return observations

    def _parse_rows(self, payload: bytes) -> list[dict[str, Any]]:
        try:
            data = json.loads(payload.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            return []
        rows: list[dict[str, Any]] = []
        if isinstance(data, dict) and isinstance(data.get("data"), list):
            for item in data["data"]:
                if not isinstance(item, dict):
                    continue
                flow_code = str(item.get("flowCode", ""))
                partner_code = str(item.get("partnerCode", ""))
                partner = (
                    "World"
                    if partner_code == "0"
                    else str(item.get("partnerDesc", UNAVAILABLE))
                )
                rows.append(
                    {
                        "year": int(item.get("period", 0)),
                        "reporter": "SAU",
                        "reporter_code": str(item.get("reporterCode", "")),
                        "partner": partner,
                        "partner_code": partner_code,
                        "flow": {
                            "M": "imports",
                            "X": "exports",
                        }.get(flow_code, UNAVAILABLE),
                        "flow_code": flow_code,
                        "hs6": str(item.get("cmdCode", "")),
                        "classification_code": str(
                            item.get("classificationCode", "")
                        ),
                        "trade_value": (
                            ""
                            if item.get("primaryValue") is None
                            else str(item.get("primaryValue"))
                        ),
                        "trade_value_value": item.get("primaryValue"),
                        "net_weight": (
                            ""
                            if item.get("netWgt") is None
                            else str(item.get("netWgt"))
                        ),
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
