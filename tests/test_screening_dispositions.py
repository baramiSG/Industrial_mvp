"""Typed screening disposition tests."""

from __future__ import annotations


def _ledger(*fired, disabled_r0=False):
    ids = ("R0", "R1-D", "R2", "R3", "R4-D", "R5", "R9-S", "R10", "R11")
    return [
        {
            "rule_id": rule_id,
            "execution": "DISABLED" if rule_id == "R0" and disabled_r0 else "FULL",
            "fired": rule_id in fired,
            "metrics": {},
            "result_code": "TEST",
            "decision_effect_code": "TEST_EFFECT",
        }
        for rule_id in ids
    ]


def _classify(ledger=None, *, imports=True, exclusion=False, warnings=None):
    from ior_mvp.screening.dispositions import classify

    return classify(
        {
            "ledger": ledger or _ledger(),
            "case": {
                "trade": [{"imports_usd_m": 1}] if imports else [],
                "hard_exclusion_inputs": {},
            },
            "exclusions": (
                [{"code": "X", "status": "SATISFIED", "reason_code": "X", "evidence_ids": []}]
                if exclusion
                else []
            ),
            "warnings": warnings or {},
            "partner_evidence_ids": ["P1"],
        }
    )


def test_no_trigger_is_no_candidate_no_trigger_fired():
    result = _classify()
    assert result["screening_disposition"] == "NO_CANDIDATE"
    assert result["disposition_reason_code"] == "NO_TRIGGER_FIRED"


def test_malformed_identity_is_no_candidate_identity_unresolved():
    result = _classify(_ledger(disabled_r0=True))
    assert result["disposition_reason_code"] == "IDENTITY_UNRESOLVED"


def test_no_import_rows_is_no_candidate_no_import_observations():
    result = _classify(imports=False)
    assert result["disposition_reason_code"] == "NO_IMPORT_OBSERVATIONS"


def test_exclusion_satisfied_is_screened_out_reject_indication():
    result = _classify(_ledger("R2"), exclusion=True)
    assert result["screening_disposition"] == "SCREENED_OUT"
    assert result["indicated_state"] == "REJECT"


def test_r11_full_fired_is_screened_out_generic_capacity_contradicted():
    result = _classify(_ledger("R11"))
    assert result["disposition_reason_code"] == "GENERIC_CAPACITY_CONTRADICTED"


def test_r3_only_is_candidate_with_monitor_indication_and_named_trigger():
    result = _classify(_ledger("R3"))
    assert result["indicated_state"] == "MONITOR"
    assert result["monitor_trigger"]["domain"] == "supplier_concentration"


def test_material_trigger_is_candidate_with_investigate_indication():
    result = _classify(_ledger("R2"))
    assert result["indicated_state"] == "INVESTIGATE"
    assert result["disposition_reason_code"] == "MATERIAL_TRIGGER_FIRED"


def test_r4d_only_is_candidate_without_indication():
    result = _classify(_ledger("R4-D"))
    assert result["screening_disposition"] == "CANDIDATE"
    assert result["indicated_state"] is None


def test_record_never_carries_formal_state_or_route_or_advance():
    result = _classify(_ledger("R2"))
    assert not {"state", "route_code", "d_star"} & set(result)
    assert "ADVANCE" not in str(result)


def test_evidence_need_codes_from_governed_vocabulary():
    from ior_mvp.screening.config import screening_config

    result = _classify(_ledger("R2"))
    allowed = set(screening_config()["vocabularies"]["evidence_need_codes"])
    assert {need["code"] for need in result["evidence_needs"]} <= allowed
