#!/usr/bin/env bash
# S01: final staged audit, commit, push, PR create. Supervisor-authorised. Detached; log in .workflow/logs/s01_pr.log
set -u
cd /home/barami/projects/industrial-opportunity-resolution-mvp || exit 1
UV="$HOME/.local/bin/uv"
echo "=== S01 PR START $(date -Is) ==="
fail() { echo "$1"; echo "=== S01 PR END FAILED $(date -Is) ==="; exit 1; }

echo "=== branch ==="
git branch --show-current
[[ "$(git branch --show-current)" == "slice/S01-ci-and-toolchain" ]] || fail "WRONG_BRANCH"

echo "=== stage all (gitignore respected) ==="
git add -A
git status --short

echo "=== protected-path audit ==="
if git diff --cached --name-only | grep -E '^(src/|config/|data/|docs/core/|docs/authority/|Dockerfile$|START_DEMO_WSL.sh$|\.gitignore$)'; then
  fail "PROTECTED_PATH_STAGED"
fi
echo "protected_paths=clean"

echo "=== prohibited-file scan over staged set ==="
PYTHONPATH=src "$UV" run --locked --extra dev python scripts/check_prohibited_files.py || fail "SCAN_FAILED"

echo "=== whitespace check ==="
git diff --cached --check || fail "WHITESPACE"

echo "=== commit ==="
git -c user.name='Salim Al-Barami' -c user.email='baramidata@gmail.com' commit -q -F - <<'MSG' || fail "COMMIT_FAILED"
S01: add CI pipeline, prohibited-file scanner, local gates and uv toolchain

GitHub Actions now verifies every push/PR to main on uv/Python 3.12,
uv/Python 3.14 and the documented pip path (scan, compile, node --check,
verify_integrity, pytest, demo_smoke) plus an independent Docker image
build. Adds scripts/check_prohibited_files.py (tracked-path and secret
scan, fail-closed), tests for scanner and workflow contract, make ci /
uv-sync / lock targets, uv.lock, DEVELOPMENT_GUIDE and slice records.

No domain, config, data, core or authority file changed; hashes untouched.
Reviews: Supervisor plan approval (2 rounds), implementation review,
independent Grok review APPROVE after one fix round. 72 tests pass.
MSG
git log --oneline -n 3
echo "HEAD=$(git rev-parse HEAD)"

echo "=== push ==="
git push -u origin slice/S01-ci-and-toolchain 2>&1 || fail "PUSH_FAILED"

echo "=== pr create ==="
gh pr create --base main --head slice/S01-ci-and-toolchain \
  --title "S01: CI pipeline, prohibited-file scanner, local gates and uv toolchain" \
  --body-file .workflow/slices/S01-ci-and-toolchain/pr_record.md 2>&1 || fail "PR_CREATE_FAILED"
gh pr view slice/S01-ci-and-toolchain --json number,url,headRefOid,baseRefName 2>&1
echo "=== S01 PR END OK $(date -Is) ==="
