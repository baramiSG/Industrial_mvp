#!/usr/bin/env bash
# S00 bootstrap. Launched detached (nohup); all output goes to .workflow/logs/s00_bootstrap.log.
# Proof gate: git steps run only if integrity, pytest and smoke all exit 0 on the imported tree.
set -u
cd /home/barami/projects/industrial-opportunity-resolution-mvp || exit 1
echo "=== S00 START $(date -Is) ==="

step() { echo; echo "=== STEP $1: $2 ==="; }
fail() { echo "$1"; echo "=== S00 END FAILED $(date -Is) ==="; exit 1; }

step 2 "venv + pip install (documented path)"
if [[ ! -d .venv ]]; then python3 -m venv .venv || fail "VENV_CREATE_FAILED"; fi
. .venv/bin/activate
python -m pip install --upgrade pip 2>&1 | tail -n 2
python -m pip install -e '.[dev]' 2>&1 | tail -n 8
python -c 'import fastapi, uvicorn, yaml, pytest, httpx; print("deps-ok", fastapi.__version__, yaml.__version__, pytest.__version__)' || fail "STEP2_DEPS_FAILED"

step 3 "baseline proof commands"
PYTHONPATH=src python3 scripts/verify_integrity.py; EI=$?
echo "EXIT_INTEGRITY=$EI"
PYTHONPATH=src pytest -q; EP=$?
echo "EXIT_PYTEST=$EP"
PYTHONPATH=src python3 scripts/demo_smoke.py; ES=$?
echo "EXIT_SMOKE=$ES"
if [[ $EI -ne 0 || $EP -ne 0 || $ES -ne 0 ]]; then fail "PROOF_FAILED"; fi

step 4 "git init and stage"
git init -b main || fail "GIT_INIT_FAILED"
git add -A
echo "tracked_count=$(git ls-files | wc -l)"
if git ls-files | grep -Ei 'zone\.identifier|^\.venv/|^\.env$|__pycache__|\.pyc$|^\.workflow/logs/'; then
  fail "PROHIBITED_FILES_STAGED"
fi
echo "prohibited_check=clean"

step 5 "commit"
git -c user.name='Salim Al-Barami' -c user.email='baramidata@gmail.com' commit -q -F - <<'MSG' || fail "COMMIT_FAILED"
Import IOR MVP v0.1.0 package with build-control records

Baseline import of the delivered Industrial Opportunity Resolution Engine
MVP/POC (CHANGELOG 0.1.0) plus Supervisor build-control documents
(docs/BUILD_ROADMAP.md, BUILD_PROGRESS.md, REQUIREMENTS_TRACEABILITY.md,
ARCHITECTURE_DECISIONS.md, KNOWN_LIMITATIONS.md, .workflow/). Windows
Zone.Identifier sidecar files removed and ignored. No engine, config,
data or test file altered (ADR-001 bootstrap exception).
MSG
git log --oneline -n 3
echo "HEAD=$(git rev-parse HEAD)"

step 6 "remote and push (active gh account baramiSG)"
gh auth status 2>&1 | grep -E 'Logged in|Active account' | sed 's/Token:.*/Token: [REDACTED]/'
git remote add origin https://github.com/baramiSG/Industrial_mvp.git
if ! git push -u origin main 2>&1; then
  echo "push failed once; configuring gh credential helper and retrying"
  gh auth setup-git && git push -u origin main 2>&1
fi
echo "EXIT_PUSH=$?"

step 7 "verify remote state"
git remote -v
git branch -vv
gh repo view baramiSG/Industrial_mvp --json name,visibility,defaultBranchRef,isEmpty,pushedAt 2>&1
echo "=== S00 END OK $(date -Is) ==="
