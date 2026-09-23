"""Authority and public/Class-D executive isolation contracts."""

from __future__ import annotations

from ior_mvp.config import PROJECT_ROOT
from ior_mvp.executive.service import (
    build_executive_case,
    build_executive_summary,
    clear_executive_caches,
)

CORE = PROJECT_ROOT / "docs" / "core"


def test_authority_pins_separate_vectors_datasets_evsi_and_claims() -> None:
    requirements = (CORE / "01_PRODUCT_AND_REQUIREMENTS.md").read_text(
        encoding="utf-8"
    )
    model = (CORE / "04_CANONICAL_DATA_MODEL.md").read_text(
        encoding="utf-8"
    )
    engine = (CORE / "07_DETERMINISTIC_ENGINE_SPEC.md").read_text(
        encoding="utf-8"
    )
    acceptance = (
        CORE / "09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md"
    ).read_text(encoding="utf-8")

    assert "contains no combined score or ordinal rank" in requirements
    assert "never assigned to a public dataset kind" in requirements
    assert "An unknown exact code is retained as `UNMAPPED`" in model
    assert "No first-row fallback is allowed" in " ".join(engine.split())
    assert "The unmodified violation count is calculated as zero" in acceptance
    assert (
        "graph identity and projection bytes change only because governed "
        "Core and engine input hashes change"
    ) in " ".join(acceptance.split())
    assert (
        "all 112 WebPs are expected to remain byte-identical"
    ) in " ".join(acceptance.split())


def test_public_dataset_and_vector_branches_exclude_class_d_evsi() -> None:
    clear_executive_caches()
    summary = build_executive_summary().model_dump(mode="json")
    case = build_executive_case("SAU-H0-721049").model_dump(mode="json")

    public_rows = str(summary["public_dataset_unlocks"])
    vectors = str(case["vectors"])
    assert "EVSI" not in public_rows.upper()
    assert "SIMULATED" not in public_rows.upper()
    assert "approximate_evsi" not in vectors.lower()
    assert case["decisions"]["public"]["synthetic_flag"] is False
    assert case["decisions"]["public"]["scenario_id"] is None
