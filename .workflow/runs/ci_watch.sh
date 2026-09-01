#!/usr/bin/env bash
# Watch CI for a PR until all checks complete. Usage: ci_watch.sh <pr-number>
# Detached; log in .workflow/logs/ci_watch_pr<N>.log. Exit code of `gh pr checks --watch` is recorded.
set -u
cd /home/barami/projects/industrial-opportunity-resolution-mvp || exit 1
PR="${1:?pr number required}"
echo "=== CI WATCH PR #$PR START $(date -Is) ==="
gh pr view "$PR" --json number,url,headRefOid,state 2>&1
echo "=== watching ==="
gh pr checks "$PR" --watch --interval 20 2>&1
WATCH_EXIT=$?
echo "WATCH_EXIT=$WATCH_EXIT"
echo "=== final checks ==="
gh pr checks "$PR" 2>&1
echo "=== runs for head ==="
HEAD_SHA="$(gh pr view "$PR" --json headRefOid -q .headRefOid)"
gh run list --commit "$HEAD_SHA" --json databaseId,name,status,conclusion,url,headSha 2>&1
echo "=== CI WATCH PR #$PR END $(date -Is) ==="
