"""S04 post-merge evidence promotion: traceability rows -> TESTED; KL-07/08 -> Closed; ADR-006 Accepted check."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACE = ROOT / "docs" / "REQUIREMENTS_TRACEABILITY.md"
KL = ROOT / "docs" / "KNOWN_LIMITATIONS.md"
ADR = ROOT / "docs" / "ARCHITECTURE_DECISIONS.md"
CI = "CI run 33584437086 (PR #4, head bd72207): uv 3.12, uv 3.14, pip 3.12, Docker all pass; merged 98c1a40"


def promote_status(text: str, row_id: str) -> str:
    prefix = f"| {row_id} |"
    lines = text.splitlines(keepends=True)
    hits = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    if len(hits) != 1:
        raise SystemExit(f"{row_id}: expected one row, found {len(hits)}")
    cells = lines[hits[0]].rstrip("\n").split(" | ")
    status_idx = len(cells) - 2
    if not cells[status_idx].strip().startswith("IMPLEMENTED"):
        raise SystemExit(f"{row_id}: status is {cells[status_idx]!r}, expected IMPLEMENTED*")
    cells[status_idx] = "TESTED"
    cells[3] = cells[3] + f"; {CI}"
    lines[hits[0]] = " | ".join(cells) + "\n"
    return "".join(lines)


def main() -> None:
    text = TRACE.read_text(encoding="utf-8")
    for row_id in ("FR-020", "FR-021", "FR-052", "FR-054", "TL-07", "INV-02"):
        text = promote_status(text, row_id)
    TRACE.write_text(text, encoding="utf-8")

    kl = KL.read_text(encoding="utf-8")
    lines = kl.splitlines(keepends=True)
    kept = [line for line in lines if not (line.startswith("| KL-07 |") or line.startswith("| KL-08 |"))]
    if len(lines) - len(kept) != 2:
        raise SystemExit(f"expected to remove 2 open KL rows, removed {len(lines) - len(kept)}")
    kl = "".join(kept)
    anchor = "| KL-09 | No CI workflow; proof commands run manually only (*pre-existing*)."
    if kl.count(anchor) != 1:
        raise SystemExit("KL-09 anchor not found")
    closed = (
        "| KL-07 | Simulated ledger repeated the public R6/R7/R8 `DISABLED` rows instead of re-evaluating with labelled synthetic inputs (*pre-existing*). | `rules.evaluate_simulated_rules` appends Class-D labelled R6/R7/R8 rows in simulated mode (FULL/DEGRADED/DISABLED with `NOT_CALCULABLE` metrics); public ledger carries none; UI and dossier disclose them. | `.workflow/slices/S04-simulation-fidelity/test_evidence.md`; CI run 33584437086 on PR #4 — 4/4 pass. | Squash merge of S04 (PR #4, `98c1a40`). |\n"
        "| KL-08 | Steel/PP branch dispatch and decision narrative hard-coded in engine code; scenarios carried no ground truth (*pre-existing*). | Generic `_simulate` (Core 07 §7.4 → §7.3 → INVESTIGATE); scenarios 1.1.0 carry `ground_truth` and `decision_narrative`; runtime and Gate B back-test fail closed. | Same evidence as KL-07; Gate B back-tests PASS for both scenarios. | Squash merge of S04 (PR #4, `98c1a40`). |\n"
    )
    idx = kl.index(anchor)
    kl = kl[:idx] + closed + kl[idx:]
    KL.write_text(kl, encoding="utf-8")

    adr = ADR.read_text(encoding="utf-8")
    match = re.search(r"## ADR-006[^\n]*\n\n\*\*Status:\*\* ([^\n]*)", adr)
    status = match.group(1) if match else "<not found>"
    print(f"ADR-006 status: {status}")
    print("PROMOTED S04: 6 traceability rows -> TESTED; KL-07/08 closed")


if __name__ == "__main__":
    main()
