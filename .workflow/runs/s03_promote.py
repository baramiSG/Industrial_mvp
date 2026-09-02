"""S03 post-merge evidence promotion: traceability rows -> TESTED; KL-04..06 -> Closed; ADR-008 Accepted."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACE = ROOT / "docs" / "REQUIREMENTS_TRACEABILITY.md"
KL = ROOT / "docs" / "KNOWN_LIMITATIONS.md"
ADR = ROOT / "docs" / "ARCHITECTURE_DECISIONS.md"
CI = "CI run 33579923763 (PR #3, head f6ef33b): uv 3.12, uv 3.14, pip 3.12, Docker all pass; merged ddf905d"


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
    for row_id in ("FR-001", "FR-004", "INV-03", "INV-04", "TL-09", "GATE-B", "GATE-F"):
        text = promote_status(text, row_id)
    TRACE.write_text(text, encoding="utf-8")

    kl = KL.read_text(encoding="utf-8")
    lines = kl.splitlines(keepends=True)
    kept: list[str] = []
    removed = 0
    for line in lines:
        if line.startswith("| KL-04 |") or line.startswith("| KL-05 |") or line.startswith("| KL-06 |"):
            removed += 1
            continue
        kept.append(line)
    if removed != 3:
        raise SystemExit(f"expected to remove 3 open KL rows, removed {removed}")
    kl = "".join(kept)
    anchor = "| KL-09 | No CI workflow; proof commands run manually only (*pre-existing*)."
    if kl.count(anchor) != 1:
        raise SystemExit("KL-09 anchor not found")
    closed = (
        "| KL-04 | Evidence policy did not require `display_label`; a scenario missing it raised `KeyError` (*pre-existing*). | `evidence_policy.v1.yaml` 1.1.0 requires all Core 06 §4 fields plus class/source/label; `validate_synthetic_scenario` raises typed `EvidenceIntegrityError`; repository loader delegates. | `.workflow/slices/S03-evidence-isolation-hardening/test_evidence.md`; CI run 33579923763 on PR #3 — 4/4 pass. | Squash merge of S03 (PR #3, `ddf905d`). |\n"
        "| KL-05 | No validator reconciled synthetic scenarios to public marginals (*pre-existing*). | `evidence.reconcile_synthetic_scenario` (demand, nameplate, factors, qualified availability; INFORMATIONAL demand layers; NOT_APPLICABLE allocation) blocks simulation on FAIL; `scripts/validate_scenarios.py` Gate B in CI and `make ci`. | Same evidence as KL-04; Gate B `SCENARIO VALIDATION PASS (2 scenarios)`. | Squash merge of S03 (PR #3, `ddf905d`). |\n"
        "| KL-06 | Analysis response did not expose methodology/config versions per case (*pre-existing*). | `config.authority_summary` in every analysis, banner and dossier (FR-001). | Same evidence as KL-04; `tests/test_authority_disclosure.py`. | Squash merge of S03 (PR #3, `ddf905d`). |\n"
    )
    idx = kl.index(anchor)
    kl = kl[:idx] + closed + kl[idx:]
    KL.write_text(kl, encoding="utf-8")

    adr = ADR.read_text(encoding="utf-8")
    old = "**Status:** Proposed for S03."
    if adr.count(old) != 1:
        raise SystemExit("ADR-008 status line not found exactly once")
    ADR.write_text(adr.replace(old, "**Status:** Accepted 2026-09-02."), encoding="utf-8")
    print("PROMOTED S03: 7 traceability rows -> TESTED; KL-04..06 closed; ADR-008 Accepted")


if __name__ == "__main__":
    main()
