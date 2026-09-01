#!/usr/bin/env bash
# S01: evidence-promotion commit, push, CI watch, and squash merge ONLY if every check passes.
# Supervisor-authorised (zero findings recorded; first CI run green). Log: .workflow/logs/s01_merge.log
set -u
cd /home/barami/projects/industrial-opportunity-resolution-mvp || exit 1
UV="$HOME/.local/bin/uv"
echo "=== S01 PROMOTE+MERGE START $(date -Is) ==="
fail() { echo "$1"; echo "=== S01 PROMOTE+MERGE END FAILED $(date -Is) ==="; exit 1; }

[[ "$(git branch --show-current)" == "slice/S01-ci-and-toolchain" ]] || fail "WRONG_BRANCH"

echo "=== promote traceability ==="
python3 .workflow/runs/s01_promote.py || fail "PROMOTE_FAILED"

echo "=== focused gates on docs-only change ==="
PYTHONPATH=src "$UV" run --locked --extra dev pytest tests/test_ci_contract.py tests/test_prohibited_files.py -q 2>&1 | tail -n 3
git add -A
PYTHONPATH=src "$UV" run --locked --extra dev python scripts/check_prohibited_files.py || fail "SCAN_FAILED"
git diff --cached --check || fail "WHITESPACE"
if git diff --cached --name-only | grep -E '^(src/|config/|data/|docs/core/|docs/authority/)'; then fail "PROTECTED_PATH_STAGED"; fi
git status --short

echo "=== commit + push ==="
git -c user.name='Salim Al-Barami' -c user.email='baramidata@gmail.com' commit -q -m "S01: record CI evidence, promote traceability rows to TESTED, close KL-09 pending merge" || fail "COMMIT_FAILED"
echo "HEAD=$(git rev-parse HEAD)"
git push 2>&1 || fail "PUSH_FAILED"

echo "=== CI watch on promotion head ==="
sleep 20
gh pr checks 1 --watch --interval 15 2>&1
WATCH_EXIT=$?
echo "WATCH_EXIT=$WATCH_EXIT"
gh pr checks 1 2>&1
HEAD_SHA="$(git rev-parse HEAD)"
gh run list --commit "$HEAD_SHA" --json databaseId,status,conclusion,url 2>&1
[[ $WATCH_EXIT -eq 0 ]] || fail "CI_NOT_GREEN"

echo "=== verify every check on head passed (gate) ==="
PASS_COUNT="$(gh pr checks 1 2>/dev/null | awk -F'\t' '$2=="pass"' | wc -l)"
TOTAL_COUNT="$(gh pr checks 1 2>/dev/null | wc -l)"
echo "checks_pass=$PASS_COUNT total=$TOTAL_COUNT"
[[ "$TOTAL_COUNT" -eq 4 && "$PASS_COUNT" -eq 4 ]] || fail "CHECK_COUNT_MISMATCH"

echo "=== squash merge ==="
gh pr merge 1 --squash --delete-branch --subject "S01: CI pipeline, prohibited-file scanner, local gates and uv toolchain (#1)" 2>&1 || fail "MERGE_FAILED"
git checkout main 2>&1
git pull --ff-only 2>&1
echo "MAIN_HEAD=$(git rev-parse HEAD)"
git log --oneline -n 3
gh pr view 1 --json state,mergedAt,mergeCommit 2>&1
echo "=== S01 PROMOTE+MERGE END OK $(date -Is) ==="
