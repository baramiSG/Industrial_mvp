"""S01 evidence promotion: exact-string replacements in traceability after CI green on PR #1.

Supervisor-authored, deterministic; run once. Each replacement must match exactly once or the script fails.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACE = ROOT / "docs" / "REQUIREMENTS_TRACEABILITY.md"
CI = "CI run 33569855956 (PR #1, head b0b2ab4): uv 3.12, uv 3.14, pip 3.12, Docker all pass"

REPLACEMENTS = [
    (
        "| NFR-004 | Offline demo, no API key | Core 01 §7 | no network calls | frontend CDN test | IMPLEMENTED | S01 |",
        f"| NFR-004 | Offline demo, no API key | Core 01 §7 | no network calls | frontend CDN test; {CI} | TESTED | S01 |",
    ),
    (
        "| NFR-008 | Runs in WSL, Linux, Docker | Core 01 §7 | scripts, Dockerfile | CI (S01) | IMPLEMENTED | S01 |",
        f"| NFR-008 | Runs in WSL, Linux, Docker | Core 01 §7 | scripts, Dockerfile | WSL `make ci` (S01 evidence); {CI} | TESTED | S01 |",
    ),
    (
        "| INV-10 | Golden tests on hashed snapshots only, never live | Manifest §6.10; AGENTS #8 | repository loaders | integrity | IMPLEMENTED | S01 |",
        f"| INV-10 | Golden tests on hashed snapshots only, never live | Manifest §6.10; AGENTS #8 | repository loaders | integrity; {CI} | TESTED | S01 |",
    ),
    (
        "| TL-01 | Integrity layer (hashes, no synthetic in public, mandatory metadata) | Core 09 §2.1 | `verify_integrity.py`, `test_integrity_contract`, `test_synthetic_isolation` | IMPLEMENTED | S01 |",
        f"| TL-01 | Integrity layer (hashes, no synthetic in public, mandatory metadata) | Core 09 §2.1 | `verify_integrity.py`, `test_integrity_contract`, `test_synthetic_isolation`; {CI} | TESTED | S01 |",
    ),
    (
        "| TL-02 | Formula unit tests | Core 09 §2.2 | `test_capability_economics`, `test_rules` | IMPLEMENTED | S01 |",
        f"| TL-02 | Formula unit tests | Core 09 §2.2 | `test_capability_economics`, `test_rules`; {CI} | TESTED | S01 |",
    ),
    (
        "| TL-03 | Rule tests (R1-D boundary, R2, R3, R4-F disabled, R4-D, R11) | Core 09 §2.3 | partial — no R1-D boundary, no R3 explicit, no R4-F explicit | IMPLEMENTED (partial) | S02 |",
        f"| TL-03 | Rule tests (R1-D boundary, R2, R3, R4-F disabled, R4-D, R11) | Core 09 §2.3 | existing cases executed in CI ({CI}); R1-D boundary, R3 explicit and R4-F explicit tests remain S02 | TESTED (partial; existing cases executed in CI; R1-D boundary, R3 explicit and R4-F explicit tests remain S02) | S02 |",
    ),
    (
        "| TL-04 | Golden A, A-S, B, B-S | Core 09 §2.4 | `test_golden_cases` | IMPLEMENTED | S01 |",
        f"| TL-04 | Golden A, A-S, B, B-S | Core 09 §2.4 | `test_golden_cases`; {CI} | TESTED | S01 |",
    ),
    (
        "| TL-05 | Extraction golden (4 fields exact, spans retained) | Core 09 §2.5 | `test_extraction` | IMPLEMENTED | S01 |",
        f"| TL-05 | Extraction golden (4 fields exact, spans retained) | Core 09 §2.5 | `test_extraction`; {CI} | TESTED | S01 |",
    ),
    (
        "| TL-06 | API tests | Core 09 §2.6 | `test_api` | IMPLEMENTED | S01 |",
        f"| TL-06 | API tests | Core 09 §2.6 | `test_api`; {CI} | TESTED | S01 |",
    ),
    (
        "| GATE-H | Release: build_manifests (approved only), verify, pytest, smoke all pass | Core 09 §6 | `.github/workflows/ci.yml`, `Makefile` `ci`; `build_manifests.py` not run because S01 has no governed change | IMPLEMENTED | S01 |",
        f"| GATE-H | Release: build_manifests (approved only), verify, pytest, smoke all pass | Core 09 §6 | `.github/workflows/ci.yml`, `Makefile` `ci`; `build_manifests.py` not run because S01 has no governed change; {CI} | TESTED | S01 |",
    ),
    (
        "| BC-04 | CI on PR/push executing integrity, tests, smoke, scans | `.github/workflows/ci.yml`, `tests/test_ci_contract.py` | IMPLEMENTED | S01 |",
        f"| BC-04 | CI on PR/push executing integrity, tests, smoke, scans | `.github/workflows/ci.yml`, `tests/test_ci_contract.py`; {CI} | TESTED | S01 |",
    ),
]


def main() -> None:
    text = TRACE.read_text(encoding="utf-8")
    for old, new in REPLACEMENTS:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"expected exactly one match, found {count}: {old[:60]}...")
        text = text.replace(old, new)
    TRACE.write_text(text, encoding="utf-8")
    print(f"PROMOTED {len(REPLACEMENTS)} rows")


if __name__ == "__main__":
    main()
