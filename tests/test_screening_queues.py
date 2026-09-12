"""Route-specific queue membership and deterministic Pareto ordering."""

from __future__ import annotations

import copy


def _record(hs6="721049", fired=("R1-D",), material=(), warning=False, continuity="NONE"):
    return {
        "hs6": hs6,
        "screening_disposition": "CANDIDATE",
        "indicated_state": "INVESTIGATE" if material else None,
        "fired_signal_rule_ids": list(fired),
        "material_trigger_rule_ids": list(material),
        "ledger": [
            {"rule_id": rule, "execution": "FULL", "fired": True, "metrics": {}}
            for rule in fired
        ],
        "warnings": {
            "export_import_ratio_warning": warning,
            "price_led_growth": False,
            "classification_continuity": {"pattern": continuity},
        },
        "metrics": {
            "imports_usd_m_latest": 10,
            "quantity_cagr": 0.1,
            "qualifying_signal_count": len(fired),
            "largest_supplier_share_value": 0.6,
            "export_import_value_ratio": 1,
            "fired_signal_count": len(fired),
        },
    }


def _assign(records, config=None):
    from ior_mvp.screening.config import screening_config
    from ior_mvp.screening.queues import assign_queues

    return assign_queues(records, config or screening_config())


def test_robust_requires_min_signals_full_signal_no_warning_continuous():
    queues, _ = _assign([_record(fired=("R2", "R5"), material=("R2", "R5"))])
    assert queues["robust_public_finding"]["entries"]


def test_injected_minimum_signals_changes_membership():
    from ior_mvp.screening.config import screening_config
    config = copy.deepcopy(screening_config())
    config["queues"]["robust_public_finding"]["minimum_fired_material_signals"] = 3
    queues, _ = _assign([_record(fired=("R2", "R5"), material=("R2", "R5"))], config)
    assert not queues["robust_public_finding"]["entries"]


def test_incumbent_upgrade_requires_r9s_and_other_material_trigger():
    queues, _ = _assign([_record(fired=("R9-S", "R2"), material=("R9-S", "R2"))])
    assert queues["incumbent_upgrade_investigation"]["entries"]


def test_resilience_requires_r3():
    queues, _ = _assign([_record(fired=("R3",))])
    assert queues["resilience_case"]["entries"]


def test_likely_false_positive_from_ratio_warning_price_led_or_discontinuity():
    queues, _ = _assign([_record(warning=True)])
    assert queues["likely_false_positive"]["entries"]


def test_high_evsi_is_r2_full_not_elsewhere_with_evsi_not_calculable():
    record = _record(fired=("R2",), material=("R2",))
    queues, _ = _assign([record])
    entry = queues["high_evsi_evidence_investigation"]["entries"][0]
    assert entry["evsi_status"] == "NOT_CALCULABLE"


def test_persistence_only_is_unqueued_and_counted():
    queues, meta = _assign([_record()])
    assert all(not queue["entries"] for queue in queues.values())
    assert meta["unqueued_candidates"] == 1


def test_multi_queue_membership_allowed_and_no_global_rank_field():
    queues, _ = _assign([_record(fired=("R2", "R3"), material=("R2",), warning=True)])
    assert sum(bool(q["entries"]) for q in queues.values()) > 1
    assert "rank" not in _record()


def test_pareto_ranks_non_dominated_sorting_known_answers():
    from ior_mvp.screening.queues import pareto_ranks

    assert pareto_ranks([(3, 3), (2, 2), (3, 1), (1, 3)]) == [1, 2, 2, 2]


def test_ordering_deterministic_by_rank_then_hs6():
    records = [_record("721050", fired=("R3",)), _record("721049", fired=("R3",))]
    queues, _ = _assign(records)
    assert [entry["hs6"] for entry in queues["resilience_case"]["entries"]] == ["721049", "721050"]


def test_methodology_queue_mapping_records_8_2_c_not_calculable():
    _, meta = _assign([])
    assert meta["methodology_queue_mapping"]["§8.2(c)"]["status"] == "NOT_CALCULABLE"
    assert meta["methodology_queue_mapping"]["§8.2(c)"]["queue_id"] is None
