"""Release-state promotion: every TESTED traceability row -> COMPLETE; BC-08 -> COMPLETE; report final facts.

Supervisor-authored. Runs on branch slice/S05-release-state after the S05 implementation merge (55304db) and its
default-branch CI (run 33589819341) were observed green. Deterministic; fails on unexpected structure.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACE = ROOT / "docs" / "REQUIREMENTS_TRACEABILITY.md"
REPORT = ROOT / "docs" / "FINAL_BUILD_REPORT.md"

EVIDENCE = (
    "S05 implementation merge 55304dbfbd49f69d567406faddcc308aea65c804 (PR #5; PR CI run 33589765172; "
    "default-branch CI run 33589819341 success); acceptance run 20260902T040100Z-95877 42/42; 280 tests; "
    "final reviewer APPROVE"
)


def main() -> None:
    text = TRACE.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    promoted = 0
    for index, line in enumerate(lines):
        if not line.startswith("| ") or line.startswith("| ID |") or line.startswith("|---"):
            continue
        cells = line.rstrip("\n").split(" | ")
        if len(cells) < 4:
            continue
        status_idx = len(cells) - 2
        status = cells[status_idx].strip()
        row_id = cells[0].lstrip("| ").strip()
        if status == "TESTED":
            cells[status_idx] = "COMPLETE"
            promoted += 1
        elif row_id == "BC-08" and status == "IMPLEMENTED":
            cells[2] = (
                "Runner/tests/docs implemented; final holistic reviewer (cursor-grok-4.6-xhigh) APPROVE after one fix "
                "round; hosted CI green on PR #5 and on main; " + EVIDENCE
            )
            cells[status_idx] = "COMPLETE"
            promoted += 1
        else:
            continue
        lines[index] = " | ".join(cells) + "\n"
    TRACE.write_text("".join(lines), encoding="utf-8")

    report = REPORT.read_text(encoding="utf-8")
    marker = "## Final commit, tag, and release state"
    if report.count(marker) != 1:
        raise SystemExit("final section marker not found exactly once")
    head = report[: report.index(marker)]
    final_section = (
        "## Final commit, tag, and release state\n\n"
        "Recorded by the Supervisor from direct observation of `gh` output and git metadata.\n\n"
        "| Item | Value |\n|---|---|\n"
        "| S05 implementation PR | https://github.com/baramiSG/Industrial_mvp/pull/5 (head `80f4b1d`; PR CI run 33589765172, 4/4 pass) |\n"
        "| S05 implementation merge commit on `main` | `55304dbfbd49f69d567406faddcc308aea65c804` |\n"
        "| Default-branch CI for that merge | run 33589819341 — `conclusion: success`, `event: push` |\n"
        "| Post-merge integrity on `main` | `INTEGRITY PASS` |\n"
        "| Release-state PR | PR #6 (this branch `slice/S05-release-state`): docs/state-only — traceability `TESTED` → `COMPLETE`, "
        "`.workflow/state.json` `COMPLETE`, progress, S05 completion and PR records, this section |\n"
        "| Final commit | the squash-merge commit of PR #6 on `main` (verify with `git rev-parse main` / `git show --no-patch v0.2.0`) |\n"
        "| Release tag | `v0.2.0`, annotated, created by the Supervisor on the PR #6 merge commit after its four checks and default-branch CI are green |\n"
        "| Release identity | package/API/`config/project.yaml` version `0.2.0`; thresholds 1.1.0; sector profiles 1.0.0; evidence policy 1.1.0; scenarios 1.1.0 |\n\n"
        "Merged completion slices: S00 `0731ae5` (baseline import), S01 `432af8a` (PR #1), S02 `c438370` (PR #2), "
        "S03 `ddf905d` (PR #3), S04 `98c1a40` (PR #4), S05 `55304db` (PR #5). All PR CI runs green 4/4 "
        "(33569855956, 33570112914, 33573669072, 33579923763, 33584437086, 33589765172).\n\n"
        "### Owner action items\n\n"
        "- Rotate any credentials present in the local, git-ignored workspace `.env` as a precaution. It was never tracked, "
        "never packaged (packaging now archives tracked files only) and never read or printed by the Supervisor; an implementer "
        "reported it contains live-looking keys while verifying the packaging exclusion.\n"
        "- Consider a GitHub plan with rulesets so the four CI checks become required checks (ADR-007 currently enforces the gate procedurally).\n"
    )
    REPORT.write_text(head + final_section, encoding="utf-8")
    print(f"PROMOTED {promoted} rows -> COMPLETE; final report section written")


if __name__ == "__main__":
    main()
