#!/usr/bin/env bash
# Generic slice gate: stage all, audit, commit, push, open PR. Supervisor-authorised per slice.
# Usage: slice_commit_push_pr.sh <branch> <slice-dir> <commit-msg-file> <pr-title> [allowed-governed-regex]
# Log: .workflow/logs/<slice>_pr.log (caller redirects).
set -u
cd /home/barami/projects/industrial-opportunity-resolution-mvp || exit 1
BRANCH="${1:?branch}"; SLICE_DIR="${2:?slice dir}"; MSG_FILE="${3:?commit msg file}"; TITLE="${4:?pr title}"
ALLOWED_GOVERNED="${5:-^$}"   # regex of governed paths this slice is authorised to change; default none
UV="$HOME/.local/bin/uv"
echo "=== PR GATE START $(date -Is) branch=$BRANCH ==="
fail() { echo "$1"; echo "=== PR GATE END FAILED $(date -Is) ==="; exit 1; }

[[ "$(git branch --show-current)" == "$BRANCH" ]] || fail "WRONG_BRANCH:$(git branch --show-current)"

echo "=== stage all (gitignore respected) ==="
git add -A
git status --short

echo "=== governed-path audit (allowed: $ALLOWED_GOVERNED) ==="
GOVERNED_CHANGED="$(git diff --cached --name-only | grep -E '^(config/|data/|docs/core/|docs/authority/)' || true)"
if [[ -n "$GOVERNED_CHANGED" ]]; then
  echo "$GOVERNED_CHANGED"
  UNAUTH="$(echo "$GOVERNED_CHANGED" | grep -Ev "$ALLOWED_GOVERNED" || true)"
  [[ -z "$UNAUTH" ]] || { echo "UNAUTHORISED:"; echo "$UNAUTH"; fail "UNAUTHORISED_GOVERNED_CHANGE"; }
fi
echo "governed_audit=ok"

echo "=== scanners over staged set ==="
PYTHONPATH=src "$UV" run --locked --extra dev python scripts/check_prohibited_files.py || fail "PROHIBITED_SCAN_FAILED"
if [[ -f scripts/check_threshold_literals.py ]]; then
  PYTHONPATH=src "$UV" run --locked --extra dev python scripts/check_threshold_literals.py || fail "THRESHOLD_SCAN_FAILED"
fi
git diff --cached --check || fail "WHITESPACE"

echo "=== integrity on staged tree ==="
PYTHONPATH=src "$UV" run --locked --extra dev python scripts/verify_integrity.py || fail "INTEGRITY_FAILED"

echo "=== commit ==="
git -c user.name='Salim Al-Barami' -c user.email='baramidata@gmail.com' commit -q -F "$MSG_FILE" || fail "COMMIT_FAILED"
git log --oneline -n 3
echo "HEAD=$(git rev-parse HEAD)"

echo "=== push ==="
git push -u origin "$BRANCH" 2>&1 || fail "PUSH_FAILED"

echo "=== pr create ==="
gh pr create --base main --head "$BRANCH" --title "$TITLE" --body-file "$SLICE_DIR/pr_record.md" 2>&1 || fail "PR_CREATE_FAILED"
gh pr view "$BRANCH" --json number,url,headRefOid,baseRefName 2>&1
echo "=== PR GATE END OK $(date -Is) ==="
