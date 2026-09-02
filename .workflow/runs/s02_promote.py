"""S02 post-merge evidence promotion: traceability rows -> TESTED; KL-01..03 -> Closed.

Supervisor-authored; each replacement must match exactly once.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACE = ROOT / "docs" / "REQUIREMENTS_TRACEABILITY.md"
KL = ROOT / "docs" / "KNOWN_LIMITATIONS.md"
CI = "CI run 33573669072 (PR #2, head 1da6a0e): uv 3.12, uv 3.14, pip 3.12, Docker all pass; merged c438370"


def promote_status(text: str, row_id: str, old_status: str, new_status: str) -> str:
    prefix = f"| {row_id} |"
    lines = text.splitlines(keepends=True)
    hits = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    if len(hits) != 1:
        raise SystemExit(f"{row_id}: expected one row, found {len(hits)}")
    line = lines[hits[0]]
    cells = line.rstrip("\n").split(" | ")
    # status is the second-to-last cell (before the slice cell)
    status_idx = len(cells) - 2
    if cells[status_idx].strip() != old_status:
        raise SystemExit(f"{row_id}: status is {cells[status_idx]!r}, expected {old_status!r}")
    cells[status_idx] = new_status
    # append CI evidence to the test/evidence cell (third from last for A/B tables, varies) -> append to implementation cell safely
    cells[3] = cells[3] + f"; {CI}"
    lines[hits[0]] = " | ".join(cells) + "\n"
    return "".join(lines)


def main() -> None:
    text = TRACE.read_text(encoding="utf-8")
    for row_id in ("FR-002", "FR-025", "FR-033", "FR-034", "FR-044", "INV-07", "TL-03", "TL-08", "GATE-C"):
        text = promote_status(text, row_id, "IMPLEMENTED", "TESTED")
    TRACE.write_text(text, encoding="utf-8")

    kl = KL.read_text(encoding="utf-8")
    open_rows = [
        "| KL-01 | S02 implementation removes the pre-existing threshold literals and adds an AST guard; closure remains pending independent review, CI and merge. | AGENTS.md #7; Core 07 §9 | S02 |\n",
        "| KL-02 | S02 implementation compares like-for-like R3 measures and reports missing largest-supplier share as `NOT_CALCULABLE`; closure remains pending independent review, CI and merge. | Methodology §4 R3 | S02 |\n",
        "| KL-03 | S02 implementation adds below/equal/above threshold tests; closure remains pending independent review, CI and merge. | Core 09 §3 | S02 |\n",
    ]
    for row in open_rows:
        if kl.count(row) != 1:
            raise SystemExit(f"KL row not found exactly once: {row[:40]}")
        kl = kl.replace(row, "")
    closed_anchor = "| KL-09 | No CI workflow; proof commands run manually only (*pre-existing*)."
    if kl.count(closed_anchor) != 1:
        raise SystemExit("KL-09 closed row anchor not found")
    new_closed = (
        "| KL-01 | Threshold literals `0.40`, `1.25`, `50` embedded in engine code (*pre-existing*). | Config-sourced predicates (`rules.py`, `decision_engine.py`), thresholds 1.1.0 R11 key, `scripts/check_threshold_literals.py` guard in CI and `make ci`. | `.workflow/slices/S02-threshold-governance/test_evidence.md`; CI run 33573669072 on PR #2 — 4/4 pass. | Squash merge of S02 (PR #2, `c438370`). |\n"
        "| KL-02 | R3 compared `top_two_value_share` with the largest-supplier threshold (*pre-existing*). | `rules.r3_fires` uses `largest_supplier_share` only; absent → `NOT_CALCULABLE` in metrics. | Same evidence as KL-01; `test_r3_does_not_substitute_top_two_share_for_largest_supplier`. | Squash merge of S02 (PR #2, `c438370`). |\n"
        "| KL-03 | No threshold boundary tests (*pre-existing*). | `tests/test_threshold_boundaries.py` (R1-D, R2, R3, R11, Kmin, D\\* bands, competition; below/equal/above). | Same evidence as KL-01. | Squash merge of S02 (PR #2, `c438370`). |\n"
    )
    idx = kl.index(closed_anchor)
    kl = kl[:idx] + new_closed + kl[idx:]
    KL.write_text(kl, encoding="utf-8")
    print("PROMOTED S02: 9 traceability rows -> TESTED; KL-01..03 closed")


if __name__ == "__main__":
    main()
