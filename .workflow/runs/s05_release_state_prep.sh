#!/usr/bin/env bash
# S05 release-state prep: verify default-branch CI for the S05 implementation merge, create the release-state branch.
set -u
cd /home/barami/projects/industrial-opportunity-resolution-mvp || exit 1
echo "=== RELEASE-STATE PREP START $(date -Is) ==="
git checkout main -q && git pull --ff-only -q
echo "MAIN_HEAD=$(git rev-parse HEAD)"
MERGE_SHA="55304dbfbd49f69d567406faddcc308aea65c804"
RUN_ID="$(gh run list --branch main --commit "$MERGE_SHA" --workflow CI --limit 1 --json databaseId --jq '.[0].databaseId')"
echo "MAIN_RUN_ID=$RUN_ID"
if [[ -n "$RUN_ID" ]]; then
  gh run watch "$RUN_ID" --exit-status >/dev/null 2>&1
  echo "MAIN_RUN_WATCH_EXIT=$?"
  gh run view "$RUN_ID" --json conclusion,headSha,event,status,url
fi
git checkout -b slice/S05-release-state && echo "BRANCH=$(git branch --show-current)"
echo "TESTED_ROWS=$(grep -c '| TESTED |' docs/REQUIREMENTS_TRACEABILITY.md)"
echo "IMPLEMENTED_ROWS=$(grep -c '| IMPLEMENTED' docs/REQUIREMENTS_TRACEABILITY.md)"
echo "=== FINAL_BUILD_REPORT headings ==="
grep -n '^## ' docs/FINAL_BUILD_REPORT.md
echo "=== RELEASE-STATE PREP END $(date -Is) ==="
