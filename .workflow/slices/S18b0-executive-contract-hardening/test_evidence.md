# S18b0 focused evidence before exact-candidate verification

The commands below ran in the B0-owned locked Python3.14 environment with
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src`. No Aura variables or graph services
were used. Exact final candidate proof is a later gate, not inferred here.

| Command/evidence | Observed result |
|---|---|
| `uv run --locked --extra dev pytest -q tests/test_executive_validation.py` on unchanged production source | Exit1;113 failed,47 passed, one warning; expected original-defect RED |
| Full seven-file focused RED in a new isolated original-source proof copy | Exit1;113 failed,177 passed, one warning,21.34seconds; the same113 new regression failures, zero original-suite failures |
| First full focused run, retained as `focused-green.log` | Exit2; five collection errors from introduced circular import; not GREEN |
| Full focused run after independently approved correction | Exit0;290 passed, one existing Starlette/httpx deprecation warning,21.37seconds |
| `compare_valid_contracts.py` | Exit0;12 exact API byte responses,12 canonical responses and22 complete analyses unchanged; all11 real-decision equality |
| `verify_preservation.py` | Exit0; zero allowed-path intersection or hash drift across228 graph inputs,83 visual sources,724 snapshot rows and20 authority rows; actual discovery equality |

Full focused command:

```text
uv run --locked --extra dev pytest -q tests/test_executive_validation.py tests/test_executive_models.py tests/test_executive_service.py tests/test_executive_api.py tests/test_executive_claims.py tests/test_executive_isolation.py tests/test_executive_performance.py
```

The full RED proof copied base tree
`1364789a964f96f6ebabf8eae1d239a5bad0b15e` into a new isolated Git repository
and added only the byte-identical new regression file, SHA256
`47dfbeafd128f60e5d89d7aa6e64a3b01b27fb37194463f38bd61ef2c5f1e5ec`.
Its proof-only tree is `01c1499ecd3fc02709845b3efa9cad1c7ca170a4`; it contains
none of the production fixes and remains clean after verification. The source
worktree, retained proof roots and their indexes were not modified by this run.
`FULL-RED-RESULT.json` and `full-original-red.log` retain the full command,
identity, failure groups and result separately from the initial targeted RED.

The new160 cases distinguish repaired defects from already-valid guards.
Original failures comprise14 direct trade cases,7 trade API cases,2 direct R11
cases,40 supplied EVSI numeric API cases,5 missing numeric API cases,1 blank
next-fact case,30 model numeric cases,2 synthetic-marker cases and12 dependent
scenario cases. Passing controls include legitimate zero/absent EVSI, public
Class-D proxy, malformed structures already rejected, duplicate/missing model
identifiers, branch-reference validation and single missing referenced rows.
The R11 missing case's original direct exception prevented its API assertion
from running in RED; GREEN executes both. Missing R11's typed API guard is
therefore GREEN behavioral coverage, not independently claimed original API RED.

Every existing executive test file is byte-identical. The complete new test
file and full assertion diff are retained for separate review; no assertion was
removed or weakened. No old S18a gate log substitutes for B0 verification.

Unverified until exact-candidate proof: full default pytest, clean-root makeci,
different-path reconstruction/pytest/e2e, final frozen-root checks and required
hosted checks. No approval, merge or complete malformed-input coverage is claimed.

Sanad: counts derive from retained command output and the RED failure inventory;
valid equality and preservation are direct executable comparisons. Muhasabah:
PASS for focused evidence with failed attempt and unverified gates explicit.

## R1 numeric-overflow correction evidence

The earlier evidence remains historical and unchanged. Independent review found
two numeric representation gaps after the initial focused GREEN and rejected
that candidate. Full gates for that rejected tree were stopped and retained.
The independently approved three-file correction was applied only after root's
delegated acceptance and verification of all before/after hashes.

| New command/evidence | Actual result |
|---|---|
| Full seven-file focused RED in new `/tmp/s18b0-overflow-red-r1`, rejected product source plus only proposed tests | Exit1;28 failed,315 passed, one warning,27.22seconds; no retained-test failure |
| Same full focused command after exact accepted patch, `focused-green-overflow.log` | Exit0;343 passed, one existing Starlette/httpx warning,27.50seconds |
| `compare_valid_contracts_overflow.py` | Exit0; all46 original artifacts equal;12 HTTP200 responses; all11 real decisions equal |
| `verify_preservation_overflow.py` | Exit0; zero boundary/hash drift; actual graph/visual input discovery equal; old executive tests, packets and indexes preserved; source staged paths0 |

The28 failing regression instances distinguish ten direct oversized-integer
errors, ten oversized-integer API500-versus-422 errors, four direct aggregate
errors and four aggregate API500-versus-422 errors. Positive/negative `10**400`
is covered across all five supplied EVSI fields. Aggregate tests cover positive
and negative total overflow plus positive-only and non-positive-only bucket
overflow with a representable interspersed total. Original direct tracebacks
reach all three fsum operations. GREEN checks their fixed aggregate labels and
the existing governed422 API code; no broad exception handler was added.

Twenty-five new controls pass on both rejected and corrected source: ten model
oversized-integer rejections, seven representable helper values, and eight
direct/API zero, large-finite and successful-cancellation cases. The latter
retain7available/4unavailable rows and nulls for unavailable EVSI. Existing
optional-absence/zero, AM4 True/False422 and B3 assertions remain intact.
The tests now contain213 cases in367 lines, up from the historical160 in260.
No pre-existing assertion was removed or weakened.

Exact accepted patch SHA256:
`89e9e4823316b67d92db58eeaa060023709289cd591250e35878094018a5119d`.
RED log SHA256:
`09c1d5305fe56bc3a99e47840df8daaa2366dafa00e700b3e07851f8a9b0173c`.
Own resumed GREEN log SHA256:
`9ea4efde40afac4080b9d490c2c8a3fdba942637371c9845f7fface560b2b0df`.
The new comparison result is independently regenerated and hashes to
`73462107ce637df2c805f182fd2afd6eb2f3e1d488ee7729cff4cbfb50ef4296`,
identical to the retained earlier result because all compared bytes and recorded
base facts remain equal. Separate execution log and result path distinguish runs.

Sanad/Muhasabah: PASS for these actual focused runs and comparisons, with
independent correction approval attributed to same-model Codex. Assumption:
injections verify advertised error boundaries, not current frozen-data defects.
Unverified: new complete candidate, full clean-root gates, independent exact-tree
implementation approval, hosted checks and delivery. Those gates must run anew;
neither previous focused GREEN nor stopped v1 proofs substitute for them.
