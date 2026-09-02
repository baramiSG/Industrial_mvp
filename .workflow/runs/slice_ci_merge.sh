#!/usr/bin/env bash
# Generic CI watch + conditional squash merge for a slice PR. Merges ONLY if every check passes (ADR-007).
# Usage: slice_ci_merge.sh <pr-number> <merge-subject>
set -u
cd /home/barami/projects/industrial-opportunity-resolution-mvp || exit 1
PR="${1:?pr number}"; SUBJECT="${2:?merge subject}"
echo "=== CI+MERGE START PR #$PR $(date -Is) ==="
fail() { echo "$1"; echo "=== CI+MERGE END FAILED $(date -Is) ==="; exit 1; }

gh pr view "$PR" --json number,url,headRefOid,state 2>&1
sleep 15
gh pr checks "$PR" --watch --interval 15 2>&1
WATCH_EXIT=$?
echo "WATCH_EXIT=$WATCH_EXIT"
gh pr checks "$PR" 2>&1
HEAD_SHA="$(gh pr view "$PR" --json headRefOid -q .headRefOid)"
gh run list --commit "$HEAD_SHA" --json databaseId,status,conclusion,url 2>&1
[[ $WATCH_EXIT -eq 0 ]] || fail "CI_NOT_GREEN"

PASS_COUNT="$(gh pr checks "$PR" 2>/dev/null | awk -F'\t' '$2=="pass"' | wc -l)"
TOTAL_COUNT="$(gh pr checks "$PR" 2>/dev/null | wc -l)"
echo "checks_pass=$PASS_COUNT total=$TOTAL_COUNT"
[[ "$TOTAL_COUNT" -eq 4 && "$PASS_COUNT" -eq 4 ]] || fail "CHECK_COUNT_MISMATCH"

echo "=== squash merge ==="
gh pr merge "$PR" --squash --delete-branch --subject "$SUBJECT" 2>&1 || fail "MERGE_FAILED"
git checkout main 2>&1
git pull --ff-only 2>&1
echo "MAIN_HEAD=$(git rev-parse HEAD)"
git log --oneline -n 3
gh pr view "$PR" --json state,mergedAt,mergeCommit 2>&1
echo "=== post-merge integrity on main ==="
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev python scripts/verify_integrity.py 2>&1
echo "=== CI+MERGE END OK $(date -Is) ==="
