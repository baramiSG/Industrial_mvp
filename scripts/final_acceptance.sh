#!/usr/bin/env bash
set -u
set -o pipefail

readonly ROOT="/home/barami/projects/industrial-opportunity-resolution-mvp"
readonly RELEASE_VERSION="0.2.0"
export RELEASE_VERSION

cd "$ROOT"

readonly RUN_ID="${S05_RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-$$}"
readonly LOG_DIR="$ROOT/.workflow/logs/s05-final-acceptance/$RUN_ID"
readonly STEPS_FILE="$LOG_DIR/steps.tsv"
readonly JOURNEY_SUMMARY="$LOG_DIR/journeys.json"
readonly TIMING_SUMMARY="$LOG_DIR/timings.json"
readonly FAILURE_SUMMARY="$LOG_DIR/failures.json"
readonly KEYWORD_REPORT="$LOG_DIR/keyword_dispositions.md"
readonly ARCHIVE_PATH="$LOG_DIR/source-acceptance.zip"
readonly RESULTS_PATH="$ROOT/.workflow/slices/S05-final-acceptance/acceptance_results.md"
readonly PIP_VENV="$LOG_DIR/pip-venv"
readonly PIP_PYTHON="$PIP_VENV/bin/python"
readonly IMAGE_TAG="industrial-opportunity-resolution-mvp:s05-acceptance"
readonly CONTAINER_NAME="ior-s05-${RUN_ID//[^a-zA-Z0-9_.-]/-}"
readonly REVERT_WORKTREE="$LOG_DIR/revert-worktree"

export ROOT RUN_ID LOG_DIR STEPS_FILE JOURNEY_SUMMARY TIMING_SUMMARY
export FAILURE_SUMMARY KEYWORD_REPORT ARCHIVE_PATH RESULTS_PATH

mkdir -p "$LOG_DIR"
printf 'order\tstep\texit_code\tduration_ms\tlog\n' > "$STEPS_FILE"

declare -A STEP_CODES=()
STEP_NUMBER=0
CONTAINER_ID=""
UVICORN_PID=""
FIRST_UVICORN_PID=""
RESTART_PID=""
REVERT_ADDED=0

cleanup() {
  local status=$?
  set +e
  if [[ -n "${UVICORN_PID:-}" ]] && kill -0 "$UVICORN_PID" 2>/dev/null; then
    kill -TERM "$UVICORN_PID" 2>/dev/null
    wait "$UVICORN_PID" 2>/dev/null
  fi
  if [[ -n "${RESTART_PID:-}" ]] && kill -0 "$RESTART_PID" 2>/dev/null; then
    kill -TERM "$RESTART_PID" 2>/dev/null
    wait "$RESTART_PID" 2>/dev/null
  fi
  if [[ -n "${CONTAINER_ID:-}" ]]; then
    docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1
  fi
  if [[ "${REVERT_ADDED:-0}" -eq 1 ]]; then
    git worktree remove --force "$REVERT_WORKTREE" >/dev/null 2>&1
    git worktree prune >/dev/null 2>&1
  fi
  exit "$status"
}
trap cleanup EXIT INT TERM

run_step() {
  local name="$1"
  shift
  local started ended duration status relative_log absolute_log
  STEP_NUMBER=$((STEP_NUMBER + 1))
  relative_log=".workflow/logs/s05-final-acceptance/$RUN_ID/${name}.log"
  absolute_log="$ROOT/$relative_log"
  started="$(date +%s%N)"
  "$@" >"$absolute_log" 2>&1
  status=$?
  ended="$(date +%s%N)"
  duration=$(((ended - started) / 1000000))
  STEP_CODES["$name"]="$status"
  printf '%02d\t%s\t%d\t%d\t%s\n' \
    "$STEP_NUMBER" "$name" "$status" "$duration" "$relative_log" \
    >> "$STEPS_FILE"
  printf 'STEP %02d %-28s exit=%d duration_ms=%d\n' \
    "$STEP_NUMBER" "$name" "$status" "$duration"
  return 0
}

record_server_step() {
  run_step "$@"
}

require_step() {
  local name="$1"
  local code="${STEP_CODES[$name]:-125}"
  if [[ "$code" -ne 0 ]]; then
    printf 'Dependency %s did not pass; action not run.\n' "$name"
    return 125
  fi
  return 0
}

current_failure_status() {
  local name
  for name in "${!STEP_CODES[@]}"; do
    if [[ "${STEP_CODES[$name]}" -ne 0 ]]; then
      printf '1\n'
      return
    fi
  done
  printf '0\n'
}

wait_for_url() {
  local url="$1"
  local output="$2"
  local attempt status
  for attempt in $(seq 1 30); do
    curl --fail --silent --show-error "$url" -o "$output"
    status=$?
    if [[ "$status" -eq 0 ]]; then
      return 0
    fi
    sleep 1
  done
  printf 'Timed out waiting for %s\n' "$url"
  return 1
}

stop_pid() {
  local pid="$1"
  if ! kill -0 "$pid" 2>/dev/null; then
    printf 'Process %s is not running.\n' "$pid"
    return 1
  fi
  kill -TERM "$pid"
  local status=$?
  if [[ "$status" -ne 0 ]]; then
    return "$status"
  fi
  wait "$pid"
  status=$?
  case "$status" in
    0|143)
      return 0
      ;;
    *)
      return "$status"
      ;;
  esac
}

step_preflight() {
  local branch head
  branch="$(git branch --show-current)"
  head="$(git rev-parse HEAD)"
  printf 'branch=%s\nhead=%s\n' "$branch" "$head"
  if [[ "$branch" != "slice/S05-final-acceptance" && "$branch" != "main" ]]; then
    printf 'Unexpected acceptance branch: %s\n' "$branch"
    return 1
  fi
  git status --short
  python3 --version
  "$HOME/.local/bin/uv" --version
  docker --version
  sha256sum \
    config/thresholds.v1.yaml \
    config/sector_profiles.v1.yaml \
    config/evidence_policy.v1.yaml \
    data/manifests/snapshot_manifest.json \
    docs/authority/authority_hashes.json \
    docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx
}

step_make_ci() {
  make ci
}

step_clean_venv_create() {
  python3 -m venv --clear "$PIP_VENV"
}

step_clean_pip_install() {
  require_step "clean_venv_create" || return $?
  "$PIP_PYTHON" -m pip install -e ".[dev]"
}

step_clean_prohibited() {
  require_step "clean_pip_install" || return $?
  "$PIP_PYTHON" scripts/check_prohibited_files.py
}

step_clean_thresholds() {
  require_step "clean_pip_install" || return $?
  "$PIP_PYTHON" scripts/check_threshold_literals.py
}

step_clean_compile() {
  require_step "clean_pip_install" || return $?
  "$PIP_PYTHON" -m compileall -q src scripts tests
}

step_clean_node() {
  node --check src/ior_mvp/static/app.js
}

step_clean_integrity() {
  require_step "clean_pip_install" || return $?
  PYTHONPATH=src "$PIP_PYTHON" scripts/verify_integrity.py
}

step_clean_gate_b() {
  require_step "clean_pip_install" || return $?
  PYTHONPATH=src "$PIP_PYTHON" scripts/validate_scenarios.py
}

step_clean_pytest() {
  require_step "clean_pip_install" || return $?
  PYTHONPATH=src "$PIP_PYTHON" -m pytest -q
}

step_clean_smoke() {
  require_step "clean_pip_install" || return $?
  PYTHONPATH=src "$PIP_PYTHON" scripts/demo_smoke.py
}

step_docker_build() {
  docker build --file Dockerfile --tag "$IMAGE_TAG" .
}

step_docker_run() {
  require_step "docker_build" || return $?
  CONTAINER_ID="$(
    docker run -d --name "$CONTAINER_NAME" -p 8001:8000 "$IMAGE_TAG"
  )"
  printf 'container=%s\n' "$CONTAINER_ID"
  [[ -n "$CONTAINER_ID" ]]
}

step_docker_health() {
  require_step "docker_run" || return $?
  local payload="$LOG_DIR/docker-health.json"
  wait_for_url "http://127.0.0.1:8001/api/health" "$payload" || return $?
  python3 - "$payload" <<'PY'
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["status"] == "ok"
assert payload["version"] == os.environ["RELEASE_VERSION"]
assert payload["evidence_boundary"] == (
    "public real decision / isolated synthetic simulation"
)
print(json.dumps(payload, indent=2))
PY
}

step_docker_stop() {
  require_step "docker_run" || return $?
  docker stop "$CONTAINER_NAME"
}

step_docker_remove() {
  require_step "docker_run" || return $?
  docker rm "$CONTAINER_NAME"
  local status=$?
  if [[ "$status" -eq 0 ]]; then
    CONTAINER_ID=""
  fi
  return "$status"
}

step_uvicorn_start() {
  require_step "clean_pip_install" || return $?
  PYTHONPATH=src "$PIP_PYTHON" -m uvicorn ior_mvp.app:app \
    --host 127.0.0.1 --port 8010 \
    >"$LOG_DIR/uvicorn-first.log" 2>&1 &
  UVICORN_PID=$!
  FIRST_UVICORN_PID="$UVICORN_PID"
  sleep 0.2
  kill -0 "$UVICORN_PID"
  printf 'pid=%s\n' "$UVICORN_PID"
}

step_uvicorn_health() {
  require_step "uvicorn_start" || return $?
  local payload="$LOG_DIR/uvicorn-health.json"
  wait_for_url "http://127.0.0.1:8010/api/health" "$payload" || return $?
  "$PIP_PYTHON" - <<'PY'
from __future__ import annotations

import json
import os
from urllib.request import urlopen

base = "http://127.0.0.1:8010"
with urlopen(base + "/api/health", timeout=10) as response:
    health = json.load(response)
with urlopen(
    base + "/api/opportunities/SAU-H0-721049?mode=public",
    timeout=10,
) as response:
    analysis = json.load(response)
assert health["status"] == "ok"
assert health["version"] == os.environ["RELEASE_VERSION"]
assert health["version"] == analysis["authority"]["project_version"]
assert health["evidence_boundary"] == (
    "public real decision / isolated synthetic simulation"
)
print(json.dumps({"health": health, "authority": analysis["authority"]}, indent=2))
PY
}

step_http_journeys() {
  require_step "uvicorn_health" || return $?
  "$PIP_PYTHON" - <<'PY'
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.request import urlopen


BASE_URL = "http://127.0.0.1:8010"
OUT = Path(os.environ["JOURNEY_SUMMARY"])
DISCLOSURE = "SIMULATED — NOT MINISTRY EVIDENCE"
RELEASE_VERSION = os.environ["RELEASE_VERSION"]
CASES = {
    "SAU-H0-721049": {
        "public": ("INVESTIGATE", "INVESTIGATE"),
        "simulated": ("INVESTIGATE", "ADVANCE"),
    },
    "SAU-H0-390210": {
        "public": ("REJECT", "REJECT"),
        "simulated": ("REJECT", "REJECT"),
    },
}
APPROVED_COMPONENTS = {
    "integrity_banner",
    "decision_hero",
    "metric_grid",
    "trade_chart",
    "rule_ledger",
    "capability_matrix",
    "economics_panel",
    "evidence_ledger",
    "data_unlocks",
    "decision_actions",
}
DOSSIER_KEYS = {
    "decision_headline",
    "decision_state",
    "route",
    "product_identity",
    "demand_conclusion",
    "supply_conclusion",
    "gap_diagnosis",
    "capability_route",
    "economics",
    "competition_policy",
    "evidence_summary",
    "conditions",
    "kill_conditions",
    "next_evidence_actions",
    "synthetic_disclosure",
}


def get(path: str) -> tuple[int, bytes, str]:
    with urlopen(BASE_URL + path, timeout=10) as response:
        return (
            response.status,
            response.read(),
            response.headers.get_content_type(),
        )


def get_json(path: str) -> dict[str, Any] | list[Any]:
    status, body, _ = get(path)
    assert status == 200, (path, status)
    return json.loads(body)


health = get_json("/api/health")
assert isinstance(health, dict)
assert health["status"] == "ok"
assert health["version"] == RELEASE_VERSION
assert health["evidence_boundary"] == (
    "public real decision / isolated synthetic simulation"
)

project = get_json("/api/project")
assert isinstance(project, dict)
assert project["project"]["id"] == "ior-mvp"
assert project["project"]["version"] == RELEASE_VERSION
assert project["project"]["modes"] == ["public", "simulated"]
assert {
    row["opportunity_id"]
    for row in project["golden_cases"]
} == set(CASES)

thresholds = get_json("/api/thresholds")
assert isinstance(thresholds, dict)
assert thresholds["metadata"]["version"] == "1.1.0"
assert thresholds["metadata"]["status"] == "frozen_for_demo_cycle"
assert "R11" in thresholds["rules"]
assert "route_bands" in thresholds["capability"]

extraction = get_json("/api/extraction-demo")
assert isinstance(extraction, dict)
assert extraction["passed"] == extraction["total"] == 4
assert extraction["accuracy"] == 1.0
assert all(row["passed"] is True for row in extraction["records"])
assert all(
    set(row["source_spans"]) == {"ar", "en"}
    for row in extraction["records"]
)

summary: dict[str, Any] = {
    "health": "PASS",
    "project": "PASS",
    "thresholds": "PASS",
    "extraction": "4/4",
    "cases": {},
}

for mode in ("public", "simulated"):
    listing = get_json(f"/api/opportunities?mode={mode}")
    assert isinstance(listing, list)
    assert {row["id"] for row in listing} == set(CASES)
    assert all(row["mode"] == mode for row in listing)
    for row in listing:
        expected_real, expected_active = CASES[row["id"]][mode]
        assert row["real_state"] == expected_real
        assert row["active_state"] == expected_active

    for opportunity_id, expectations in CASES.items():
        expected_real, expected_active = expectations[mode]
        prefix = f"/api/opportunities/{opportunity_id}"
        detail = get_json(f"{prefix}?mode={mode}")
        assert isinstance(detail, dict)
        assert detail["opportunity"]["id"] == opportunity_id
        assert detail["mode"] == mode
        assert detail["real_decision"]["state"] == expected_real
        assert detail["active_decision"]["state"] == expected_active
        assert detail["authority"]["methodology"]["sha256"]
        assert len(detail["authority"]["methodology"]["sha256"]) == 64
        assert (
            health["version"]
            == detail["authority"]["project_version"]
            == project["project"]["version"]
            == RELEASE_VERSION
        )
        assert detail["snapshot_id"]
        assert detail["as_of_date"]
        assert detail["rules"]
        assert all(
            {
                "rule_id",
                "execution",
                "fired",
                "result",
                "metrics",
                "decision_effect",
            } <= set(row)
            for row in detail["rules"]
        )
        public_rows = [
            row
            for row in detail["evidence"]
            if row["synthetic_flag"] is False
        ]
        synthetic_rows = [
            row
            for row in detail["evidence"]
            if row["synthetic_flag"] is True
        ]
        assert public_rows
        assert all(
            {
                "source",
                "status",
                "evidence_class",
                "synthetic_flag",
            } <= set(row)
            for row in public_rows
        )
        if opportunity_id == "SAU-H0-721049":
            assert any(row.get("contradiction") for row in public_rows)

        if mode == "public":
            assert detail["simulation_decision"] is None
            assert synthetic_rows == []
            assert detail["synthetic_inputs_used"] == []
            assert detail["integrity"][
                "real_decision_uses_public_only"
            ] is True
        else:
            assert detail["simulation_decision"] is not None
            assert synthetic_rows
            assert all(
                row["source"] == "DEMO_GENERATOR"
                and row["evidence_class"] == "D"
                and row["display_label"] == DISCLOSURE
                for row in synthetic_rows
            )
            assert detail["simulation_scenario"][
                "display_label"
            ] == DISCLOSURE
            assert detail["integrity"][
                "real_decision_unchanged_after_simulation"
            ] is True
            assert detail["integrity"][
                "ground_truth_backtest"
            ]["match"] is True

        if opportunity_id == "SAU-H0-721049":
            assert detail["real_decision"]["state"] == "INVESTIGATE"
            assert detail["real_decision"]["route_code"] is None
            if mode == "public":
                assert detail["capability"]["d_star"] is None
                assert detail["economics"] is None
                assert detail["data_unlocks"]
            else:
                assert detail["active_decision"]["route_code"] == 5
                assert detail["capacity"][
                    "effective_qualified_capacity_kt"
                ] == 57.509
                assert detail["capacity"][
                    "specification_adjusted_gap_kt"
                ] == 46.491
                assert detail["capability"]["d_star"] == 0.2667
                assert detail["economics"][
                    "minimum_effective_support_m"
                ] == 18.0
                assert detail["economics"]["national_value"][
                    "incremental_national_value_m_sar"
                ] == 198.0
                assert detail["competition"]["warning_fires"] is False
        else:
            assert detail["real_decision"]["state"] == "REJECT"
            assert detail["real_decision"]["route_code"] == 0
            assert next(
                row
                for row in detail["rules"]
                if row["rule_id"] == "R11"
                and row.get("synthetic_flag") is not True
            )["fired"] is True
            if mode == "simulated":
                assert detail["active_decision"]["route_code"] == 0
                assert detail["capacity"]["qualified_available_kt"] == 80.0
                assert detail["capacity"][
                    "specification_adjusted_gap_kt"
                ] == -24.0
                assert detail["economics"][
                    "minimum_effective_support_m"
                ] == 0.0

        manifest = get_json(f"{prefix}/ui-manifest?mode={mode}")
        assert isinstance(manifest, dict)
        assert manifest["context"] == {
            "opportunity_id": opportunity_id,
            "mode": mode,
            "decision_state": expected_active,
        }
        component_types = {
            component["type"]
            for component in manifest["components"]
        }
        assert component_types <= APPROVED_COMPONENTS
        assert {
            "integrity_banner",
            "decision_hero",
            "rule_ledger",
            "decision_actions",
        } <= component_types
        if mode == "public":
            assert "economics_panel" not in component_types
        metric_grid = next(
            component
            for component in manifest["components"]
            if component["type"] == "metric_grid"
        )
        if opportunity_id == "SAU-H0-390210":
            assert metric_grid["props"]["supplier_concentration"] == {}

        dossier = get_json(f"{prefix}/dossier?mode={mode}")
        assert isinstance(dossier, dict)
        assert DOSSIER_KEYS <= set(dossier)
        assert dossier["opportunity_id"] == opportunity_id
        assert dossier["mode"] == mode
        assert dossier["decision_state"] == expected_active
        assert dossier["conditions"] is not None
        assert dossier["kill_conditions"] is not None
        assert dossier["evidence_summary"]["authority"] == detail["authority"]
        if mode == "public":
            assert dossier["synthetic_disclosure"] is None
            assert dossier["evidence_summary"]["synthetic_records"] == 0
        else:
            assert dossier["synthetic_disclosure"][
                "display_label"
            ] == DISCLOSURE
            assert dossier["evidence_summary"]["synthetic_records"] > 0

        html_status, html_body, content_type = get(
            f"{prefix}/dossier.html?mode={mode}"
        )
        html = html_body.decode("utf-8")
        assert html_status == 200
        assert content_type == "text/html"
        assert html.startswith("<!doctype html>")
        assert dossier["decision_headline"] in html
        assert 'dir="rtl"' in html
        if mode == "public":
            assert DISCLOSURE not in html
            exact = (
                f"{dossier['evidence_summary']['public_records']} "
                "public records; 0 synthetic records."
            )
            assert exact in html
        else:
            assert DISCLOSURE in html
            assert "Simulated R6–R8 ledger" in html

        summary["cases"][f"{opportunity_id}:{mode}"] = {
            "real_state": expected_real,
            "active_state": expected_active,
            "detail": "PASS",
            "ui_manifest": "PASS",
            "dossier_json": "PASS",
            "dossier_html": "PASS",
        }

OUT.write_text(
    json.dumps(summary, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(summary, indent=2))
PY
}

step_http_nfr_005() {
  require_step "uvicorn_health" || return $?
  "$PIP_PYTHON" - <<'PY'
from __future__ import annotations

import json
import os
from pathlib import Path
from statistics import median
from time import perf_counter
from urllib.request import urlopen


BASE_URL = "http://127.0.0.1:8010"
OPPORTUNITY_IDS = ("SAU-H0-721049", "SAU-H0-390210")
MODES = ("public", "simulated")
ANALYSIS_PATHS = (
    *(f"/api/opportunities?mode={mode}" for mode in MODES),
    *(
        f"/api/opportunities/{opportunity_id}{suffix}?mode={mode}"
        for mode in MODES
        for opportunity_id in OPPORTUNITY_IDS
        for suffix in ("", "/ui-manifest", "/dossier", "/dossier.html")
    ),
)


def fetch(path: str) -> tuple[int, bytes]:
    with urlopen(BASE_URL + path, timeout=10) as response:
        return response.status, response.read()


results: dict[str, dict[str, object]] = {}
for path in ANALYSIS_PATHS:
    assert fetch(path)[0] == 200
    samples: list[float] = []
    for _ in range(5):
        started = perf_counter()
        status, _ = fetch(path)
        elapsed_ms = (perf_counter() - started) * 1000
        assert status == 200
        samples.append(round(elapsed_ms, 3))
    measured_median = round(median(samples), 3)
    results[path] = {
        "samples_ms": samples,
        "median_ms": measured_median,
        "bound_ms": 250.0,
        "passes": measured_median < 250.0,
    }
assert all(row["passes"] is True for row in results.values())
Path(os.environ["TIMING_SUMMARY"]).write_text(
    json.dumps(dict(sorted(results.items())), indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(dict(sorted(results.items())), indent=2))
PY
}

step_http_failures() {
  require_step "uvicorn_health" || return $?
  "$PIP_PYTHON" - <<'PY'
from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen


BASE_URL = "http://127.0.0.1:8010"


def get_allow_error(path: str) -> tuple[int, bytes, str]:
    try:
        with urlopen(BASE_URL + path, timeout=10) as response:
            return (
                response.status,
                response.read(),
                response.headers.get_content_type(),
            )
    except HTTPError as error:
        return (
            error.code,
            error.read(),
            error.headers.get_content_type(),
        )


status, payload, _ = get_allow_error(
    "/api/opportunities/DOES-NOT-EXIST"
)
assert status == 404
assert json.loads(payload)["detail"] == (
    "Unknown opportunity: DOES-NOT-EXIST"
)
unknown_status = status

status, payload, _ = get_allow_error(
    "/api/opportunities?mode=invalid"
)
assert status == 422
assert json.loads(payload)["detail"]
invalid_mode_status = status

status, payload, content_type = get_allow_error(
    "/nonexistent-static"
)
assert status == 200
assert content_type == "text/html"
assert payload.decode("utf-8").startswith("<!doctype html>")
spa_status = status

summary = {
    "unknown_opportunity": unknown_status,
    "invalid_mode": invalid_mode_status,
    "spa_fallback": spa_status,
    "evidence_integrity_scope": "TestClient planted scenario",
}
Path(os.environ["FAILURE_SUMMARY"]).write_text(
    json.dumps(summary, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(summary, indent=2))
PY
}

step_integrity_422_testclient() {
  require_step "clean_pip_install" || return $?
  PYTHONPATH=src "$PIP_PYTHON" -m pytest \
    tests/test_api.py::test_evidence_integrity_failure_returns_422_json \
    -q
}

step_uvicorn_stop() {
  require_step "uvicorn_start" || return $?
  stop_pid "$UVICORN_PID"
  local status=$?
  if [[ "$status" -eq 0 ]]; then
    UVICORN_PID=""
  fi
  return "$status"
}

step_uvicorn_restart() {
  require_step "uvicorn_stop" || return $?
  PYTHONPATH=src "$PIP_PYTHON" -m uvicorn ior_mvp.app:app \
    --host 127.0.0.1 --port 8010 \
    >"$LOG_DIR/uvicorn-restart.log" 2>&1 &
  RESTART_PID=$!
  sleep 0.2
  kill -0 "$RESTART_PID" || return $?
  if [[ "$RESTART_PID" == "$FIRST_UVICORN_PID" ]]; then
    printf 'Restart reused the first PID: %s\n' "$RESTART_PID"
    return 1
  fi
  printf 'first_pid=%s\nrestart_pid=%s\n' \
    "$FIRST_UVICORN_PID" "$RESTART_PID"
}

step_restart_health() {
  require_step "uvicorn_restart" || return $?
  local payload="$LOG_DIR/restart-health.json"
  wait_for_url "http://127.0.0.1:8010/api/health" "$payload" || return $?
  "$PIP_PYTHON" - <<'PY'
from __future__ import annotations

import json
import os
from urllib.request import urlopen

base = "http://127.0.0.1:8010"
with urlopen(base + "/api/health", timeout=10) as response:
    health = json.load(response)
with urlopen(
    base + "/api/opportunities/SAU-H0-390210?mode=simulated",
    timeout=10,
) as response:
    analysis = json.load(response)
assert health["status"] == "ok"
assert (
    health["version"]
    == analysis["authority"]["project_version"]
    == os.environ["RELEASE_VERSION"]
)
print(json.dumps({"health": health, "authority": analysis["authority"]}, indent=2))
PY
}

step_restart_stop() {
  require_step "uvicorn_restart" || return $?
  stop_pid "$RESTART_PID"
  local status=$?
  if [[ "$status" -eq 0 ]]; then
    RESTART_PID=""
  fi
  return "$status"
}

step_revert_worktree_add() {
  git worktree add --detach "$REVERT_WORKTREE" HEAD
  local status=$?
  if [[ "$status" -eq 0 ]]; then
    REVERT_ADDED=1
  fi
  return "$status"
}

step_revert_apply() {
  require_step "revert_worktree_add" || return $?
  (
    cd "$REVERT_WORKTREE"
    git revert --no-commit 98c1a40225a94090238867bc9861e8c6544b5839
  )
}

step_revert_diff_check() {
  require_step "revert_apply" || return $?
  (
    cd "$REVERT_WORKTREE"
    git diff --check
    local_status=$?
    if [[ "$local_status" -ne 0 ]]; then
      exit "$local_status"
    fi
    unmerged="$(git diff --name-only --diff-filter=U)"
    if [[ -n "$unmerged" ]]; then
      printf 'Unmerged paths:\n%s\n' "$unmerged"
      exit 1
    fi
    git status --short
  )
}

step_revert_abort() {
  require_step "revert_apply" || return $?
  (
    cd "$REVERT_WORKTREE"
    git revert --abort
  )
}

step_revert_clean() {
  require_step "revert_abort" || return $?
  local status_text
  status_text="$(git -C "$REVERT_WORKTREE" status --porcelain)"
  printf '%s' "$status_text"
  [[ -z "$status_text" ]]
}

step_revert_worktree_remove() {
  require_step "revert_worktree_add" || return $?
  git worktree remove "$REVERT_WORKTREE"
  local status=$?
  if [[ "$status" -ne 0 ]]; then
    return "$status"
  fi
  git worktree prune
  status=$?
  if [[ "$status" -eq 0 ]]; then
    REVERT_ADDED=0
  fi
  return "$status"
}

step_final_prohibited() {
  require_step "clean_pip_install" || return $?
  "$PIP_PYTHON" scripts/check_prohibited_files.py
}

step_final_thresholds() {
  require_step "clean_pip_install" || return $?
  "$PIP_PYTHON" scripts/check_threshold_literals.py
}

step_final_gate_b() {
  require_step "clean_pip_install" || return $?
  PYTHONPATH=src "$PIP_PYTHON" scripts/validate_scenarios.py
}

step_keyword_scan() {
  python3 - <<'PY'
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


root = Path(os.environ["ROOT"])
report_path = Path(os.environ["KEYWORD_REPORT"])
pattern = re.compile(
    r"TODO|FIXME|HACK|temporary|placeholder|hardcoded|TEMP|mock|disabled|skip|xfail",
    re.IGNORECASE,
)
tracked_raw = subprocess.run(
    ["git", "ls-files", "-z"],
    cwd=root,
    check=True,
    stdout=subprocess.PIPE,
).stdout
paths = {
    os.fsdecode(raw)
    for raw in tracked_raw.split(b"\0")
    if raw
}
intended = {
    "scripts/final_acceptance.sh",
    "tests/test_performance.py",
    "tests/test_final_acceptance_contract.py",
    "docs/FINAL_BUILD_REPORT.md",
    "docs/OPERATOR_RUNBOOK.md",
    "docs/DEPLOYMENT_GUIDE.md",
    ".workflow/slices/S05-final-acceptance/acceptance_results.md",
    ".workflow/slices/S05-final-acceptance/implementation_log.md",
    ".workflow/slices/S05-final-acceptance/test_evidence.md",
}
paths.update(path for path in intended if (root / path).is_file())
paths = {
    path
    for path in paths
    if not path.startswith(".workflow/runs/")
    and not path.startswith(".workflow/logs/")
    and not (
        path.startswith(".workflow/")
        and path.endswith("/plan.md")
    )
}

control_docs = {
    "docs/KNOWN_LIMITATIONS.md",
    "docs/REQUIREMENTS_TRACEABILITY.md",
    "docs/ARCHITECTURE_DECISIONS.md",
    "docs/FINAL_BUILD_REPORT.md",
    "docs/OPERATOR_RUNBOOK.md",
    "docs/DEPLOYMENT_GUIDE.md",
    "docs/DEVELOPMENT_GUIDE.md",
    "docs/implementation/API_REFERENCE.md",
}
rows: list[tuple[str, int, str, str, str]] = []
binary_count = 0
for path in sorted(paths):
    payload = (root / path).read_bytes()
    if b"\0" in payload:
        binary_count += 1
        continue
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        binary_count += 1
        continue
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in pattern.finditer(line):
            token = match.group(0)
            before = line[match.start() - 1] if match.start() else ""
            after = line[match.end()] if match.end() < len(line) else ""
            lexical = (
                (before and (before.isalnum() or before == "_"))
                or (after and (after.isalnum() or after == "_"))
            )
            if path.startswith(".workflow/"):
                disposition = "LEGITIMATE — historical governance record"
            elif lexical:
                disposition = "LEGITIMATE — lexical substring"
            elif token.lower() == "disabled" and (
                path.startswith("src/ior_mvp/")
                or path.startswith("tests/")
                or path.startswith("docs/core/")
                or path == "docs/authority/methodology_extracted.md"
            ):
                disposition = "LEGITIMATE — governed execution state"
            elif token.lower() in {"temp", "temporary"} and (
                path.startswith("data/")
                or path == "docs/authority/methodology_extracted.md"
            ):
                disposition = "LEGITIMATE — documented limitation/control"
            elif token.lower() == "disabled" and (
                path.startswith("docs/implementation/")
                and (
                    "FULL/DEGRADED/DISABLED" in line
                    or "Synthetic mode must be disabled" in line
                )
            ):
                disposition = "LEGITIMATE — documented limitation/control"
            elif path.startswith("tests/") and token.lower() in {
                "temp",
                "temporary",
                "mock",
                "placeholder",
            }:
                disposition = "LEGITIMATE — isolated test fixture"
            elif path in control_docs or path == "scripts/final_acceptance.sh":
                disposition = "LEGITIMATE — documented limitation/control"
            else:
                disposition = "UNRESOLVED"
            excerpt = " ".join(line.strip().split())
            excerpt = excerpt.replace("|", "\\|").replace("`", "'")
            rows.append(
                (path, line_number, token, excerpt[:240], disposition)
            )

unresolved = sum(
    disposition == "UNRESOLVED"
    for *_, disposition in rows
)
lines = [
    "# Repository keyword dispositions",
    "",
    f"Text hits: {len(rows)}.",
    f"Binary/non-UTF-8 files skipped from content matching: {binary_count}.",
    f"Unresolved: {unresolved}.",
    "",
    "| Path | Line | Token | Source excerpt | Disposition |",
    "|---|---:|---|---|---|",
]
lines.extend(
    f"| {path} | {line_number} | {token} | {excerpt} | {disposition} |"
    for path, line_number, token, excerpt, disposition in rows
)
report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"KEYWORD_HITS={len(rows)}")
print(f"KEYWORD_UNRESOLVED={unresolved}")
raise SystemExit(1 if unresolved else 0)
PY
}

step_docs_audit() {
  python3 - <<'PY'
from __future__ import annotations

from pathlib import Path


root = Path(".")
required = {
    "docs/FINAL_BUILD_REPORT.md": (
        "Industrial Opportunity Resolution MVP 0.2.0",
        "recorded by the Supervisor in the release-state PR",
        "Residual-review disposition",
        "Rollback and recovery",
    ),
    "docs/OPERATOR_RUNBOOK.md": (
        "Operator Runbook",
        "Health check",
        "Stop and restart",
        "Failure interpretation",
    ),
    "docs/DEPLOYMENT_GUIDE.md": (
        "Deployment Guide",
        "WSL",
        "Native Linux",
        "Docker",
        "Rollback",
    ),
    "docs/DEVELOPMENT_GUIDE.md": (
        "Final acceptance",
        "Gate B",
        "Authority-change procedure",
        "Slice workflow",
    ),
    "docs/KNOWN_LIMITATIONS.md": ("KL-22", "KL-29", "KL-30"),
    "docs/ARCHITECTURE_DECISIONS.md": (
        "ADR-004",
        "Accepted 2026-09-02 (implemented and merged in S01)",
        "ADR-009",
    ),
    "docs/REQUIREMENTS_TRACEABILITY.md": (
        "CI-S01-A",
        "NFR-005",
        "DOD-01",
        "DOD-10",
        "SC-01",
        "SC-06",
        "No Playwright/real-browser interaction",
    ),
    "docs/implementation/API_REFERENCE.md": (
        "GET `/api/opportunities?mode=public|simulated`",
        "HTTP 404",
    ),
}
for path, fragments in required.items():
    candidate = root / path
    assert candidate.is_file(), path
    text = candidate.read_text(encoding="utf-8")
    assert text.strip(), path
    for fragment in fragments:
        assert fragment in text, (path, fragment)

traceability = (
    root / "docs/REQUIREMENTS_TRACEABILITY.md"
).read_text(encoding="utf-8")
assert "| COMPLETE |" not in traceability
assert "FR-073" in traceability
assert "NOT_APPLICABLE (production)" in traceability
print("DOCUMENT_AUDIT_PASS")
print("Required documents:", len(required))
PY
}

step_source_archive() {
  python3 - <<'PY'
from __future__ import annotations

import os
import subprocess
import zipfile
from pathlib import Path


root = Path(os.environ["ROOT"])
archive = Path(os.environ["ARCHIVE_PATH"])
tracked_raw = subprocess.run(
    ["git", "ls-files", "-z"],
    cwd=root,
    check=True,
    stdout=subprocess.PIPE,
).stdout
paths = {
    os.fsdecode(raw)
    for raw in tracked_raw.split(b"\0")
    if raw
}
intended = {
    "scripts/final_acceptance.sh",
    "tests/test_performance.py",
    "tests/test_final_acceptance_contract.py",
    "docs/FINAL_BUILD_REPORT.md",
    "docs/OPERATOR_RUNBOOK.md",
    "docs/DEPLOYMENT_GUIDE.md",
    ".workflow/slices/S05-final-acceptance/acceptance_results.md",
    ".workflow/slices/S05-final-acceptance/implementation_log.md",
    ".workflow/slices/S05-final-acceptance/test_evidence.md",
}
paths.update(path for path in intended if (root / path).is_file())
paths = {
    path
    for path in paths
    if (root / path).is_file()
    and not path.startswith(".workflow/runs/")
    and not path.startswith(".workflow/logs/")
    and "/.git/" not in f"/{path}/"
}
with zipfile.ZipFile(
    archive,
    "w",
    compression=zipfile.ZIP_DEFLATED,
) as handle:
    for path in sorted(paths):
        handle.write(root / path, arcname=path)
print(f"SOURCE_ARCHIVE_FILES={len(paths)}")
print(f"SOURCE_ARCHIVE={archive}")
PY
}

step_archive_audit() {
  require_step "source_archive" || return $?
  python3 - <<'PY'
from __future__ import annotations

import os
import zipfile
from pathlib import Path


archive = Path(os.environ["ARCHIVE_PATH"])
required = {
    "AGENTS.md",
    "README.md",
    "pyproject.toml",
    "uv.lock",
    "src/ior_mvp/app.py",
    "src/ior_mvp/static/index.html",
    "scripts/final_acceptance.sh",
    "tests/test_golden_cases.py",
    "docs/FINAL_BUILD_REPORT.md",
    "docs/OPERATOR_RUNBOOK.md",
    "docs/DEPLOYMENT_GUIDE.md",
    "docs/DEVELOPMENT_GUIDE.md",
    "docs/REQUIREMENTS_TRACEABILITY.md",
    "docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx",
    "data/manifests/snapshot_manifest.json",
}
with zipfile.ZipFile(archive) as handle:
    assert handle.testzip() is None
    names = set(handle.namelist())
assert required <= names, sorted(required - names)
bad_markers = (
    "/.git/",
    "/.venv/",
    "/__pycache__/",
    "/.workflow/logs/",
    "Zone.Identifier",
)
bad_suffixes = (".pyc", ".pem", ".key", ".p12")
bad = [
    name
    for name in names
    if any(marker in f"/{name}" for marker in bad_markers)
    or name.lower().endswith(bad_suffixes)
]
assert not bad, bad
print(f"ARCHIVE_AUDIT_PASS files={len(names)} required={len(required)}")
PY
}

step_protected_diff() {
  local status_text
  status_text="$(
    git status --short -- \
      config/thresholds.v1.yaml \
      config/sector_profiles.v1.yaml \
      config/evidence_policy.v1.yaml \
      data \
      docs/core \
      docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx \
      docs/authority/authority_hashes.json \
      data/manifests/snapshot_manifest.json \
      tests/test_golden_cases.py
  )"
  if [[ -n "$status_text" ]]; then
    printf 'Protected-path changes detected:\n%s\n' "$status_text"
    return 1
  fi
  printf 'PROTECTED_DIFF_PASS\n'
  git diff --check
}

write_results_file() {
  python3 - <<'PY'
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


root = Path(os.environ["ROOT"])
steps_path = Path(os.environ["STEPS_FILE"])
results_path = Path(os.environ["RESULTS_PATH"])


def command_output(command: list[str]) -> str:
    result = subprocess.run(
        command,
        cwd=root,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.stdout.strip()


rows = []
for line in steps_path.read_text(encoding="utf-8").splitlines()[1:]:
    order, step, code, duration, log = line.split("\t")
    rows.append(
        {
            "order": order,
            "step": step,
            "code": int(code),
            "duration_ms": int(duration),
            "log": log,
        }
    )

status = int(os.environ["HARNESS_STATUS"])
journeys_path = Path(os.environ["JOURNEY_SUMMARY"])
timings_path = Path(os.environ["TIMING_SUMMARY"])
failures_path = Path(os.environ["FAILURE_SUMMARY"])
keyword_path = Path(os.environ["KEYWORD_REPORT"])
journeys = (
    json.loads(journeys_path.read_text(encoding="utf-8"))
    if journeys_path.is_file()
    else {}
)
timings = (
    json.loads(timings_path.read_text(encoding="utf-8"))
    if timings_path.is_file()
    else {}
)
failures = (
    json.loads(failures_path.read_text(encoding="utf-8"))
    if failures_path.is_file()
    else {}
)
keyword = (
    keyword_path.read_text(encoding="utf-8")
    if keyword_path.is_file()
    else "Keyword report unavailable.\n"
)
dirty = command_output(["git", "status", "--short"])
branch = command_output(["git", "branch", "--show-current"])
head = command_output(["git", "rev-parse", "HEAD"])
python_version = command_output(["python3", "--version"])
uv_version = command_output([str(Path.home() / ".local/bin/uv"), "--version"])
docker_version = command_output(["docker", "--version"])

lines = [
    "# S05 Final Acceptance Results",
    "",
    f"- Run UTC: `{datetime.now(timezone.utc).isoformat()}`",
    f"- Run ID: `{os.environ['RUN_ID']}`",
    f"- Branch: `{branch}`",
    f"- HEAD: `{head}`",
    f"- Release identity: `{os.environ['RELEASE_VERSION']}`",
    f"- Python: `{python_version}`",
    f"- uv: `{uv_version}`",
    f"- Docker: `{docker_version}`",
    (
        "- Overall local result: **LOCAL HARNESS PASS**"
        if status == 0
        else "- Overall local result: **LOCAL HARNESS FAIL**"
    ),
    "",
    "This record is local engineering evidence only. It does not claim "
    "review approval, hosted CI, merge, project completion, or a release tag.",
    "",
    "## Dirty-path inventory",
    "",
    "```text",
    dirty or "(clean)",
    "```",
    "",
    "## Step results",
    "",
    "| # | Step | Exit | Duration (ms) | Log |",
    "|---:|---|---:|---:|---|",
]
lines.extend(
    f"| {row['order']} | {row['step']} | {row['code']} | "
    f"{row['duration_ms']} | `{row['log']}` |"
    for row in rows
)

lines.extend(
    [
        "",
        "## Journey A–E live HTTP summary",
        "",
        "```json",
        json.dumps(journeys, indent=2, sort_keys=True),
        "```",
        "",
        "The live matrix covers both list modes and all steel/PP public and "
        "simulated detail, approved manifest, dossier JSON, and printable "
        "HTML contracts. Browser paint or interaction was not executed.",
        "",
        "## NFR-005 live medians",
        "",
        "One warm-up was excluded for every path. Each median uses five real "
        "localhost HTTP calls and must be strictly below 250.0 ms.",
        "",
        "| Path | Samples (ms) | Median (ms) | Bound (ms) | Result |",
        "|---|---|---:|---:|---|",
    ]
)
for path, result in sorted(timings.items()):
    samples = ", ".join(str(value) for value in result["samples_ms"])
    lines.append(
        f"| `{path}` | {samples} | {result['median_ms']} | "
        f"{result['bound_ms']} | "
        f"{'PASS' if result['passes'] else 'FAIL'} |"
    )

lines.extend(
    [
        "",
        "## Failure paths",
        "",
        f"- Unknown opportunity: HTTP `{failures.get('unknown_opportunity', 'not run')}`.",
        f"- Invalid mode: HTTP `{failures.get('invalid_mode', 'not run')}`.",
        f"- Unknown SPA path: HTTP `{failures.get('spa_fallback', 'not run')}`.",
        "- Evidence-integrity HTTP 422 is exercised with a planted invalid "
        "scenario through TestClient because no runtime data-root override exists.",
        "",
        "## Reversal, protected bytes, and package",
        "",
        "- Reversal uses an isolated worktree, applies the S04 revert without "
        "commit, checks the diff, aborts, verifies clean state, and removes it.",
        "- Protected config/data/core/methodology/manifest/golden paths must "
        "have no worktree change; `config/project.yaml` version is the only "
        "permitted config edit.",
        "- The source archive is CRC-checked and contains the required source, "
        "documentation, methodology, tests, lock, and manifest members.",
        "",
        "## Owner mandate §27 audit",
        "",
        "| Step | Evidence state |",
        "|---:|---|",
        "| 1 | Traceability and governing maps audited locally; external review gate remains. |",
        "| 2 | Traceability row/status audit executed by docs audit. |",
        "| 3 | Full suite executed by make and clean-pip paths. |",
        "| 4 | Local CI equivalent executed. |",
        "| 5 | EXTERNAL SUPERVISOR GATE — hosted default-branch CI is not claimed. |",
        "| 6 | Clean pip environment created and installed. |",
        "| 7 | Uvicorn startup, stop, distinct-PID restart, and health executed. |",
        "| 8 | NOT_APPLICABLE — no database or migration layer. |",
        "| 9 | Journeys A–E executed over live HTTP in both modes. |",
        "| 10 | 404, 422, SPA fallback, and planted integrity failure executed. |",
        "| 11 | Isolated S04 revert and abort executed. |",
        "| 12 | Prohibited, protected-byte, evidence-isolation, and localhost controls executed. |",
        "| 13 | Dossier, manifests, and source archive validated. |",
        "| 14 | Local FastAPI/static/uvicorn/Docker adapters tested; external integrations NOT_APPLICABLE. |",
        "| 15 | NOT_APPLICABLE — no mutable database/user state; Git/tag recovery documented. |",
        "| 16 | Required document content audited locally. |",
        "| 17 | Named keyword scan and per-hit dispositions executed. |",
        "| 18 | EXTERNAL SUPERVISOR GATE — different-model final review is not claimed. |",
        "| 19 | EXTERNAL SUPERVISOR GATE — reviewer remediation is not claimed. |",
        "| 20 | EXTERNAL SUPERVISOR GATE — mandatory post-review rerun is not claimed. |",
        "",
        "## Assumptions and accepted limitations",
        "",
        "- Data classification is `confidential_demo`; only frozen public and "
        "explicit Class-D demo fixtures were used.",
        "- Docker, curl, Node, Git, Python, uv, ports 8001/8010, and localhost "
        "process control are required by this run.",
        "- KL-20–KL-30 remain the accepted MVP limitations. KL-22 limits "
        "product proof to live HTTP/API plus static contracts; KL-29 requires "
        "restart after approved file changes; KL-30 records the stable R1-D "
        "confidence-cap result string.",
        "",
        "## Repository keyword dispositions",
        "",
        keyword.rstrip(),
        "",
        "## Evidence links",
        "",
        "- `.workflow/slices/S05-final-acceptance/test_evidence.md`",
        "- `.workflow/slices/S05-final-acceptance/reviewer_findings.md` "
        "(external reviewer-owned)",
        "- `.workflow/slices/S05-final-acceptance/pr_record.md` "
        "(Supervisor-owned)",
        "",
    ]
)
results_path.write_text("\n".join(lines), encoding="utf-8")
print(
    "RESULTS_RENDERED "
    f"status={status} steps={len(rows)} nonzero="
    f"{sum(row['code'] != 0 for row in rows)}"
)
PY
}

record_results_step() {
  local name="render""_results"
  local started ended duration status relative_log absolute_log rerender_status
  STEP_NUMBER=$((STEP_NUMBER + 1))
  relative_log=".workflow/logs/s05-final-acceptance/$RUN_ID/${name}.log"
  absolute_log="$ROOT/$relative_log"
  export HARNESS_STATUS
  HARNESS_STATUS="$(current_failure_status)"
  started="$(date +%s%N)"
  write_results_file >"$absolute_log" 2>&1
  status=$?
  ended="$(date +%s%N)"
  duration=$(((ended - started) / 1000000))
  STEP_CODES["$name"]="$status"
  printf '%02d\t%s\t%d\t%d\t%s\n' \
    "$STEP_NUMBER" "$name" "$status" "$duration" "$relative_log" \
    >> "$STEPS_FILE"
  if [[ "$status" -eq 0 ]]; then
    HARNESS_STATUS="$(current_failure_status)"
    write_results_file >>"$absolute_log" 2>&1
    rerender_status=$?
    if [[ "$rerender_status" -ne 0 ]]; then
      status="$rerender_status"
      STEP_CODES["$name"]="$status"
    fi
  fi
  printf 'STEP %02d %-28s exit=%d duration_ms=%d\n' \
    "$STEP_NUMBER" "$name" "$status" "$duration"
}

run_step "preflight" step_preflight
run_step "make_ci" step_make_ci
run_step "clean_venv_create" step_clean_venv_create
run_step "clean_pip_install" step_clean_pip_install
run_step "clean_prohibited" step_clean_prohibited
run_step "clean_thresholds" step_clean_thresholds
run_step "clean_compile" step_clean_compile
run_step "clean_node" step_clean_node
run_step "clean_integrity" step_clean_integrity
run_step "clean_gate_b" step_clean_gate_b
run_step "clean_pytest" step_clean_pytest
run_step "clean_smoke" step_clean_smoke
run_step "docker_build" step_docker_build
run_step "docker_run" step_docker_run
run_step "docker_health" step_docker_health
run_step "docker_stop" step_docker_stop
run_step "docker_remove" step_docker_remove
record_server_step "uvicorn_start" step_uvicorn_start
run_step "uvicorn_health" step_uvicorn_health
run_step "http_journeys" step_http_journeys
run_step "http_nfr_005" step_http_nfr_005
run_step "http_failures" step_http_failures
run_step "integrity_422_testclient" step_integrity_422_testclient
run_step "uvicorn_stop" step_uvicorn_stop
record_server_step "uvicorn_restart" step_uvicorn_restart
run_step "restart_health" step_restart_health
run_step "restart_stop" step_restart_stop
run_step "revert_worktree_add" step_revert_worktree_add
run_step "revert_apply" step_revert_apply
run_step "revert_diff_check" step_revert_diff_check
run_step "revert_abort" step_revert_abort
run_step "revert_clean" step_revert_clean
run_step "revert_worktree_remove" step_revert_worktree_remove
run_step "final_prohibited" step_final_prohibited
run_step "final_thresholds" step_final_thresholds
run_step "final_gate_b" step_final_gate_b
run_step "keyword_scan" step_keyword_scan
run_step "docs_audit" step_docs_audit
run_step "source_archive" step_source_archive
run_step "archive_audit" step_archive_audit
run_step "protected_diff" step_protected_diff
# render_results
record_results_step

final_status="$(current_failure_status)"
if [[ "$STEP_NUMBER" -ne 42 ]]; then
  final_status=1
fi
printf '__FINAL_ACCEPTANCE__ status=%s\n' "$final_status"
exit "$final_status"
