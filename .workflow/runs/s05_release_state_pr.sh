#!/usr/bin/env bash
# Release-state PR: run promotion, then the generic gate (stage/audit/scan/integrity/commit/push/PR) with a custom body file.
set -u
cd /home/barami/projects/industrial-opportunity-resolution-mvp || exit 1
echo "=== RELEASE-STATE PR START $(date -Is) ==="
[[ "$(git branch --show-current)" == "slice/S05-release-state" ]] || { echo WRONG_BRANCH; exit 1; }
python3 .workflow/runs/s05_release_state_promote.py || { echo PROMOTE_FAILED; exit 1; }
python3 .workflow/runs/strip_trailing_ws.py docs/FINAL_BUILD_REPORT.md docs/REQUIREMENTS_TRACEABILITY.md docs/BUILD_PROGRESS.md
echo "TESTED_LEFT=$(grep -c '| TESTED |' docs/REQUIREMENTS_TRACEABILITY.md)"
echo "COMPLETE_ROWS=$(grep -c '| COMPLETE |' docs/REQUIREMENTS_TRACEABILITY.md)"
# temporarily point the generic gate at the release-state body by copying it over pr_record.md's expected path
cp .workflow/slices/S05-final-acceptance/release_state_pr.md .workflow/logs/release_state_body.md
mkdir -p .workflow/logs/release_state_slice && cp .workflow/logs/release_state_body.md .workflow/logs/release_state_slice/pr_record.md
bash .workflow/runs/slice_commit_push_pr.sh slice/S05-release-state .workflow/logs/release_state_slice .workflow/slices/S05-final-acceptance/release_state_commit_message.txt 'S05 release state: COMPLETE promotions, final facts, state COMPLETE' '^$'
echo "=== RELEASE-STATE PR END $(date -Is) ==="
