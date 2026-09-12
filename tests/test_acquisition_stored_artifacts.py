"""Stored artifact parametrized tests."""

from __future__ import annotations

import hashlib
import copy
import json
import shutil
from pathlib import Path
from typing import Any

import pytest
import yaml

from ior_mvp.acquisition.contracts import SourceContractRecord
from ior_mvp.acquisition.raw_store import RawStore
from ior_mvp.acquisition.source_config import acquisition_sources_config, configured_credential_env_var
from ior_mvp.config import PROJECT_ROOT

EXPECTED_SOURCE_IDS = frozenset(
    {"wits_trade", "un_comtrade", "baci_cepii", "zatca_tariff", "gastat",
     "ministry_of_industry", "modon", "saso_catalogue", "saber_registry"}
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _header_names(headers: list[dict[str, str]] | None) -> list[str]:
    if not headers:
        return []
    return [entry["name"].lower() for entry in headers if isinstance(entry, dict)]


def stored_evidence_problems(raw_root: Path, config: dict[str, Any]) -> list[str]:
    """Return deterministic problem strings for DD-23 (a)-(d) predicates."""
    problems: list[str] = []
    sources = config["sources"]
    source_ids = set(sources)
    if source_ids != EXPECTED_SOURCE_IDS:
        problems.append(
            f"configured source set mismatch: expected {sorted(EXPECTED_SOURCE_IDS)}, "
            f"got {sorted(source_ids)}"
        )

    deny = {name.lower() for name in config["offline_guard"]["header_denylist"]}
    allow = {name.lower() for name in config["offline_guard"]["header_allowlist"]}
    cred = {source_id: configured_credential_env_var(sources[source_id]) for source_id in source_ids}

    if not raw_root.exists():
        problems.append("raw store root missing")
        return problems

    seen_dirs = {path.name for path in raw_root.iterdir() if path.is_dir()}
    if "TEST-FIXTURE" in seen_dirs:
        problems.append("TEST-FIXTURE directory present under data/raw")
    missing_dirs = source_ids - seen_dirs
    if missing_dirs:
        problems.append(
            f"sources without artifact or attempt record: {sorted(missing_dirs)}"
        )

    json_files = sorted(raw_root.rglob("*.json"))
    if not json_files:
        problems.append("no raw JSON records")
        return problems

    records: list[tuple[Path, dict[str, Any], str]] = []
    for path in json_files:
        record = _load_json(path)
        source_dir = path.relative_to(raw_root).parts[0]
        record_source = record.get("source_id")
        if record_source != source_dir:
            problems.append(
                f"{path}: record source_id {record_source!r} outside partition {source_dir!r}"
            )
        if record.get("access_classification") == "test_double":
            problems.append(f"{path}: test_double access_classification under data/raw")
        records.append((path, record, source_dir))

    pages = [
        (path, record, sid)
        for path, record, sid in records
        if path.name.startswith("page-") and path.name.endswith(".contract.json")
    ]
    covs = [(path, record, sid) for path, record, sid in records if path.name == "coverage.json"]
    atts = [(path, record, sid) for path, record, sid in records if path.name == "attempt.json"]
    other = len(records) - len(pages) - len(covs) - len(atts)
    if other:
        problems.append(f"unexpected raw record kind count: {other}")

    header_entries: list[tuple[Path, list[str]]] = []
    for path, record, _sid in pages:
        header_entries.append((path, _header_names(record.get("response_headers_subset"))))
    for path, record, _sid in covs:
        observed = record.get("observed_stop") or {}
        header_entries.append((path, _header_names(observed.get("headers_subset"))))
    for path, record, _sid in atts:
        observed = record.get("observed_response") or {}
        header_entries.append((path, _header_names(observed.get("headers_subset"))))

    for path, names in header_entries:
        denied = set(names) & deny
        if denied:
            problems.append(
                f"{path}: deny-listed header in stored response metadata: {sorted(denied)}"
            )
        non_allowed = set(names) - allow
        if non_allowed:
            problems.append(
                f"{path}: non-allow-listed header in stored response metadata: "
                f"{sorted(non_allowed)}"
            )

    for path, record, sid in pages + atts:
        expected = cred[sid]
        if record.get("credential_env_var") != expected:
            problems.append(
                f"{path}: credential_env_var {record.get('credential_env_var')!r} "
                f"differs from configured {expected!r}"
            )
    for path, record, sid in pages:
        if cred[sid] is None and record.get("credential_used") is not False:
            problems.append(f"{path}: credential_used on uncredentialed source")
    for path, record, sid in atts:
        if cred[sid] is None and record.get("credential_present") is not False:
            problems.append(f"{path}: credential_present on uncredentialed source")

    absent = [(path, record, sid) for path, record, sid in atts if record.get("reason") == "CREDENTIAL_ABSENT"]
    for path, record, sid in absent:
        expected = cred[sid]
        if expected is None:
            problems.append(f"{path}: CREDENTIAL_ABSENT on source without credential_env_var")
            continue
        if record.get("credential_env_var") != expected:
            problems.append(f"{path}: CREDENTIAL_ABSENT credential_env_var mismatch")
        if record.get("credential_present") is not False:
            problems.append(f"{path}: CREDENTIAL_ABSENT with credential_present true")
        if record.get("observed_response") is not None:
            problems.append(f"{path}: CREDENTIAL_ABSENT with non-null observed_response")
        coverage = record.get("coverage")
        if not isinstance(coverage, dict):
            problems.append(f"{path}: CREDENTIAL_ABSENT missing embedded coverage")
            continue
        sibling = path.parent / "coverage.json"
        if not sibling.exists():
            problems.append(f"{path}: CREDENTIAL_ABSENT missing sibling coverage.json")
        elif _load_json(sibling) != coverage:
            problems.append(f"{path}: CREDENTIAL_ABSENT embedded coverage differs from sibling")
        if coverage.get("requests_made") != 0:
            problems.append(f"{path}: CREDENTIAL_ABSENT coverage requests_made != 0")
        if coverage.get("pages_fetched") != 0:
            problems.append(f"{path}: CREDENTIAL_ABSENT coverage pages_fetched != 0")
        if coverage.get("status") != "INCOMPLETE":
            problems.append(f"{path}: CREDENTIAL_ABSENT coverage status != INCOMPLETE")
        if coverage.get("stop_reason") != "CREDENTIAL_ABSENT":
            problems.append(f"{path}: CREDENTIAL_ABSENT coverage stop_reason mismatch")
        if list(path.parent.glob("page-*")):
            problems.append(f"{path}: CREDENTIAL_ABSENT run directory contains page artifacts")

    for sid, var in cred.items():
        if var is None:
            continue
        source_root = raw_root / sid
        if not source_root.exists():
            continue
        has_pages = any(source_root.rglob("page-*.contract.json"))
        if not has_pages:
            has_absent = any(
                _load_json(attempt).get("reason") == "CREDENTIAL_ABSENT"
                for attempt in source_root.rglob("attempt.json")
            )
            if not has_absent:
                problems.append(
                    f"{sid}: credentialed source without pages lacks CREDENTIAL_ABSENT record"
                )

    for path, _record, _sid in covs:
        rel_parts = path.relative_to(raw_root).parts
        if len(rel_parts) != 4:
            problems.append(
                f"{path}: coverage.json not at <source_id>/<query_hash>/<run_id>/"
            )

    return problems


def test_repository_raw_store_has_no_stored_evidence_problems() -> None:
    config = acquisition_sources_config()
    problems = stored_evidence_problems(PROJECT_ROOT / "data" / "raw", config)
    assert problems == []


def _copy_raw_tree(tmp_path: Path) -> Path:
    raw_copy = tmp_path / "raw"
    shutil.copytree(PROJECT_ROOT / "data" / "raw", raw_copy)
    return raw_copy


def _config() -> dict[str, Any]:
    return acquisition_sources_config()


def test_detector_meta_denylisted_header_in_attempt_observed_response(tmp_path: Path) -> None:
    raw = _copy_raw_tree(tmp_path)
    attempt = next(raw.rglob("attempt.json"))
    payload = _load_json(attempt)
    if payload.get("observed_response") is None:
        payload["observed_response"] = {
            "http_status": 500,
            "headers_subset": [],
            "body_sha256": None,
            "body_byte_count": None,
            "error_type": "HTTPError",
            "error_message_redacted": "HTTP 500",
        }
    payload["observed_response"]["headers_subset"] = [
        {"name": "set-cookie", "value": "session=abc"}
    ]
    attempt.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    problems = stored_evidence_problems(raw, _config())
    assert any("deny-listed header" in problem for problem in problems)


def test_detector_meta_denylisted_header_in_page_contract(tmp_path: Path) -> None:
    raw = _copy_raw_tree(tmp_path)
    contract = next(raw.rglob("page-*.contract.json"))
    payload = _load_json(contract)
    payload["response_headers_subset"] = [
        {"name": "authorization", "value": "Bearer secret"},
        {"name": "content-type", "value": "text/html"},
    ]
    contract.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    problems = stored_evidence_problems(raw, _config())
    assert any("deny-listed header" in problem for problem in problems)


def test_detector_meta_non_allowlisted_header(tmp_path: Path) -> None:
    raw = _copy_raw_tree(tmp_path)
    contract = next(raw.rglob("page-*.contract.json"))
    payload = _load_json(contract)
    payload["response_headers_subset"] = [
        {"name": "content-type", "value": "text/html"},
        {"name": "x-custom-header", "value": "1"},
    ]
    contract.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    problems = stored_evidence_problems(raw, _config())
    assert any("non-allow-listed header" in problem for problem in problems)


def test_detector_meta_credential_absent_credential_present_true(tmp_path: Path) -> None:
    raw = _copy_raw_tree(tmp_path)
    attempt = next(
        p for p in raw.rglob("attempt.json") if _load_json(p).get("reason") == "CREDENTIAL_ABSENT"
    )
    payload = _load_json(attempt)
    payload["credential_present"] = True
    attempt.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    problems = stored_evidence_problems(raw, _config())
    assert any("credential_present true" in problem for problem in problems)


def test_detector_meta_credential_absent_credential_env_var_changed(tmp_path: Path) -> None:
    raw = _copy_raw_tree(tmp_path)
    config = _config()
    # W1 permits only the exact missing-directory baseline until T7. Every
    # additional problem below must still be caused by this credential mutation.
    missing = set(config["sources"]) - {p.name for p in raw.iterdir() if p.is_dir()}
    assert missing <= {"gastat", "ministry_of_industry", "modon", "saso_catalogue", "saber_registry"}
    baseline = {f"sources without artifact or attempt record: {sorted(missing)}"} if missing else set()
    assert set(stored_evidence_problems(raw, config)) == baseline
    attempt = next(
        p for p in raw.rglob("attempt.json") if _load_json(p).get("reason") == "CREDENTIAL_ABSENT"
    )
    payload = _load_json(attempt)
    sid = payload["source_id"]
    configured = config["sources"][sid]["credential_env_var"]
    payload["credential_env_var"] = "NOT_THE_CONFIGURED_NAME"
    attempt.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    problems = stored_evidence_problems(raw, config)
    expected = {
        (
            f"{attempt}: credential_env_var 'NOT_THE_CONFIGURED_NAME' "
            f"differs from configured {configured!r}"
        ),
        f"{attempt}: CREDENTIAL_ABSENT credential_env_var mismatch",
    }
    assert set(problems) == expected | baseline


def test_detector_meta_sentinel_credential_in_stored_record_flagged(tmp_path: Path) -> None:
    raw = _copy_raw_tree(tmp_path)
    attempt = next((raw / "wits_trade").rglob("attempt.json"))
    payload = _load_json(attempt)
    payload["credential_env_var"] = "UNAVAILABLE"
    attempt.write_text(json.dumps(payload), encoding="utf-8")
    assert (
        f"{attempt}: credential_env_var 'UNAVAILABLE' differs from configured None"
        in stored_evidence_problems(raw, _config())
    )


def test_detector_sentinel_configured_source_is_uncredentialed(tmp_path: Path) -> None:
    raw = _copy_raw_tree(tmp_path)
    config = copy.deepcopy(_config())
    config["sources"]["wits_trade"]["credential_env_var"] = "UNAVAILABLE"
    missing = set(config["sources"]) - {p.name for p in raw.iterdir() if p.is_dir()}
    assert missing <= {"gastat", "ministry_of_industry", "modon", "saso_catalogue", "saber_registry"}
    baseline = {f"sources without artifact or attempt record: {sorted(missing)}"} if missing else set()
    assert set(stored_evidence_problems(raw, config)) == baseline
    attempt = next((raw / "wits_trade").rglob("attempt.json"))
    payload = _load_json(attempt)
    assert payload["credential_env_var"] is None
    assert payload["credential_present"] is False
    payload["reason"] = "CREDENTIAL_ABSENT"
    attempt.write_text(json.dumps(payload), encoding="utf-8")
    assert set(stored_evidence_problems(raw, config)) == baseline | {
        f"{attempt}: CREDENTIAL_ABSENT on source without credential_env_var"
    }


def test_detector_meta_credential_absent_observed_response_non_null(tmp_path: Path) -> None:
    raw = _copy_raw_tree(tmp_path)
    attempt = next(
        p for p in raw.rglob("attempt.json") if _load_json(p).get("reason") == "CREDENTIAL_ABSENT"
    )
    payload = _load_json(attempt)
    payload["observed_response"] = {"http_status": 401, "headers_subset": []}
    attempt.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    problems = stored_evidence_problems(raw, _config())
    assert any("non-null observed_response" in problem for problem in problems)


def test_detector_meta_credential_absent_coverage_requests_made(tmp_path: Path) -> None:
    raw = _copy_raw_tree(tmp_path)
    attempt = next(
        p for p in raw.rglob("attempt.json") if _load_json(p).get("reason") == "CREDENTIAL_ABSENT"
    )
    payload = _load_json(attempt)
    payload["coverage"]["requests_made"] = 1
    attempt.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (attempt.parent / "coverage.json").write_text(
        json.dumps(payload["coverage"], indent=2), encoding="utf-8"
    )
    problems = stored_evidence_problems(raw, _config())
    assert any("requests_made != 0" in problem for problem in problems)


def test_detector_meta_credential_absent_sibling_coverage_mismatch(tmp_path: Path) -> None:
    raw = _copy_raw_tree(tmp_path)
    attempt = next(
        p for p in raw.rglob("attempt.json") if _load_json(p).get("reason") == "CREDENTIAL_ABSENT"
    )
    sibling = attempt.parent / "coverage.json"
    sibling_payload = _load_json(sibling)
    sibling_payload["pages_fetched"] = 99
    sibling.write_text(json.dumps(sibling_payload, indent=2), encoding="utf-8")
    problems = stored_evidence_problems(raw, _config())
    assert any("embedded coverage differs from sibling" in problem for problem in problems)


def test_detector_meta_credential_absent_page_artifact_present(tmp_path: Path) -> None:
    raw = _copy_raw_tree(tmp_path)
    attempt = next(
        p for p in raw.rglob("attempt.json") if _load_json(p).get("reason") == "CREDENTIAL_ABSENT"
    )
    fake_page = attempt.parent / "page-0001.contract.json"
    fake_page.write_text(json.dumps({"source_id": "un_comtrade"}), encoding="utf-8")
    problems = stored_evidence_problems(raw, _config())
    assert any("contains page artifacts" in problem for problem in problems)


def test_detector_meta_test_fixture_directory(tmp_path: Path) -> None:
    raw = _copy_raw_tree(tmp_path)
    (raw / "TEST-FIXTURE").mkdir()
    problems = stored_evidence_problems(raw, _config())
    assert any("TEST-FIXTURE directory" in problem for problem in problems)


def test_detector_meta_missing_source_directory(tmp_path: Path) -> None:
    raw = _copy_raw_tree(tmp_path)
    shutil.rmtree(raw / "baci_cepii")
    problems = stored_evidence_problems(raw, _config())
    assert any("baci_cepii" in problem for problem in problems)


def test_detector_meta_test_double_access_classification(tmp_path: Path) -> None:
    raw = _copy_raw_tree(tmp_path)
    contract = next(raw.rglob("page-*.contract.json"))
    payload = _load_json(contract)
    payload["access_classification"] = "test_double"
    contract.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    problems = stored_evidence_problems(raw, _config())
    assert any("test_double access_classification" in problem for problem in problems)


def test_detector_meta_wrong_source_partition(tmp_path: Path) -> None:
    raw = _copy_raw_tree(tmp_path)
    contract = next(raw.rglob("page-*.contract.json"))
    payload = _load_json(contract)
    payload["source_id"] = "un_comtrade"
    contract.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    problems = stored_evidence_problems(raw, _config())
    assert any("outside partition" in problem for problem in problems)


def test_detector_meta_coverage_json_wrong_depth(tmp_path: Path) -> None:
    raw = _copy_raw_tree(tmp_path)
    coverage = next(raw.rglob("coverage.json"))
    nested = coverage.parent / "nested" / "coverage.json"
    nested.parent.mkdir()
    nested.write_text(coverage.read_text(encoding="utf-8"), encoding="utf-8")
    problems = stored_evidence_problems(raw, _config())
    assert any("coverage.json not at" in problem for problem in problems)


def _source_ids() -> tuple[str, ...]:
    cfg = yaml.safe_load(
        (PROJECT_ROOT / "config" / "acquisition_sources.v1.yaml").read_text(
            encoding="utf-8"
        )
    )
    return tuple(sorted(cfg["sources"]))


@pytest.mark.parametrize(
    "contract_path",
    sorted((PROJECT_ROOT / "data" / "raw").rglob("page-*.contract.json"))
    if (PROJECT_ROOT / "data" / "raw").exists()
    else [],
)
def test_stored_contract_has_matching_payload(contract_path: Path) -> None:
    cfg = yaml.safe_load(
        (PROJECT_ROOT / "config" / "acquisition_sources.v1.yaml").read_text(
            encoding="utf-8"
        )
    )
    rs = cfg["raw_store"]
    store = RawStore(
        PROJECT_ROOT / "data" / "raw",
        max_artifact_bytes=rs["max_artifact_bytes_compressed"],
        max_store_bytes=rs["max_store_bytes_compressed"],
    )
    record = SourceContractRecord.from_json(
        json.loads(contract_path.read_text(encoding="utf-8"))
    )
    assert record.access_classification != "test_double"
    assert record.compressed_sha256
    assert record.raw_file_path
    payload_path = PROJECT_ROOT / record.raw_file_path
    assert payload_path.exists()
    compressed_hash = hashlib.sha256(payload_path.read_bytes()).hexdigest()
    assert record.compressed_sha256 == compressed_hash
    payload = store.read_payload(record)
    assert payload


@pytest.mark.parametrize("source_id", _source_ids())
def test_every_source_has_raw_record(source_id: str) -> None:
    raw = PROJECT_ROOT / "data" / "raw" / source_id
    assert raw.is_dir(), f"missing source directory: {source_id}"
    has_contract = any(raw.rglob("page-*.contract.json"))
    has_attempt = any(raw.rglob("attempt.json"))
    assert has_contract or has_attempt, source_id


def test_snapshot_contracts_not_pending() -> None:
    snap = next(
        (PROJECT_ROOT / "data" / "snapshots" / "partners").glob("*.json"),
        None,
    )
    if snap is None:
        pytest.skip("no partner snapshot")
    record = json.loads(snap.read_text(encoding="utf-8"))
    for ref in record["raw_artifact_refs"]:
        if not ref["artifact"].startswith("page-"):
            continue
        contract_path = PROJECT_ROOT / ref["path"].replace(
            ".payload.", ".contract."
        ).replace(".html.gz", ".json").replace(".json.gz", ".json")
        if not contract_path.name.endswith(".contract.json"):
            contract_path = Path(str(ref["path"]).rsplit("/", 1)[0]) / (
                ref["artifact"] + ".contract.json"
            )
            contract_path = PROJECT_ROOT / "data" / "raw" / "/".join(
                ref["path"].split("/")[2:-1]
            ) / f"{ref['artifact']}.contract.json"
        contract_path = (
            PROJECT_ROOT
            / "data"
            / "raw"
            / ref["source_id"]
            / ref["query_hash"]
            / ref["run_id"]
            / f"{ref['artifact']}.contract.json"
        )
        contract = SourceContractRecord.from_json(
            json.loads(contract_path.read_text(encoding="utf-8"))
        )
        assert contract.normalization_status not in {"PENDING", "UNPARSED"}


def _attempt_paths_with_page_payloads() -> list[Path]:
    raw_root = PROJECT_ROOT / "data" / "raw"
    if not raw_root.exists():
        return []
    attempts: list[Path] = []
    for attempt_path in raw_root.rglob("attempt.json"):
        run_dir = attempt_path.parent
        if any(run_dir.glob("page-*.payload.*.gz")):
            attempts.append(attempt_path)
    return sorted(attempts)


@pytest.mark.parametrize("attempt_path", _attempt_paths_with_page_payloads())
def test_attempt_with_page_payloads_records_observed_response(
    attempt_path: Path,
) -> None:
    payload = json.loads(attempt_path.read_text(encoding="utf-8"))
    observed = payload.get("observed_response")
    assert observed is not None
    run_dir = attempt_path.parent
    page_contracts = sorted(run_dir.glob("page-*.contract.json"))
    assert page_contracts
    last_page = json.loads(page_contracts[-1].read_text(encoding="utf-8"))
    assert observed.get("http_status") == last_page.get("http_status") or observed.get(
        "body_sha256"
    ) == last_page.get("sha256")
