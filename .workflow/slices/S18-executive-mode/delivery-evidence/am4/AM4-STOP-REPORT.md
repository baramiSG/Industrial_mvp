# AM-4 implementation stop — for Codex planning and Claude review

Status: STOPPED at first focused green verification. This is an incomplete implementation handoff, not an exact-tree approval request. No final candidate was built and no implementation acceptance is claimed.

## Assignment and preparation

The owner assigned this Codex GPT-6 Astra Ultra session as AM-4 implementer, replacing Cascade, and confirmed “Cascade is stopped for S18.” The existing owner-control file contains an additive `am4_implementer_substitution` entry; its earlier fields and assignments remain intact. Claude Code remains independent approving reviewer. Personas: senior Python/API contract engineer and evidence-provenance/reproducible-verification engineer. Applied task-standards, project-orientation, github-flow, executing-plans, systematic-debugging, test-driven-development, verification-before-completion, DOCX, sanad-provenance and muhasabah-gate skills. A read-only advisory agent inspected gates and source contracts; it neither edited nor approved.

Read the approved AM-4 packet and finding map, Claude review/rejection and boundary correction, verified owner acceptance, prior PLAN/AM-1/AM-2/AM-3/R1 records, domain manifest and extracted governing DOCX, relevant Core contracts/configuration, source, tests, control records and proof receipts. The historical salim-autonomous-workflow plugin path and both authority environment variables are absent. The installed salim-autonomous skill resources contain the existing workflow handoff and original guide. No plugin migration, workflow replacement or competing orchestration was introduced; this continuation follows the owner's exact AM-4 handoff and preserves independent approval and acceptance gates.

## Exact retained state

- Branch: `slice/s18-executive-mode`
- HEAD: `564b1b7a3924ba14d219af8ed027c54311911910`
- Rejected base tree: `2ab8d401c2312725540aa6270d449da16a96e01f`
- Final candidate tree: **not built**.
- Diagnostic inventory SHA-256 (canonical sorted JSON path-to-SHA256 map in `stopped-state.json`): `44ffb406c850d210aca818381de8e8f7cbeba95f951943a8f477c6419a6b19dc`
- Six source/test paths changed in this session. The approved `plan_review.md` append and exact new AM-4 plan file were already retained and are preserved.
- Ordinary index: zero staged paths; ordinary, checkpoint, prior AM-3 and R1 alternate-index hashes all unchanged.
- All 228 graph input, 83 visual source, 724 snapshot and 20 authority bindings match; all 112 WebPs unchanged since takeover. Approved packet bytes unchanged.

## Finding-to-fix/test status

| Finding | Retained fix | Focused evidence / remaining work |
|---|---|---|
| B1 | Present None maps to typed null independently of statuses; mapping code must be an exact integer 0–8 in validated routes. | All 11 service/API cases pass; malformed fixtures including True/False, missing code and undeclared code pass; mixed fails/NOT_CALCULABLE + None with real route 0 passes. |
| B2 | Public and simulated paths share the linked-contradiction predicate over validated evidence. | Steel decision/conditions retain S-UNICOIL-SPEC and are CONTRADICTED; linked synthetic contradiction and unlinked control pass. |
| B3 | Validated graph feed, scenario declarations and stored dependency evidence; exact source-path allowance; only verified foreign dependency IDs omitted from claims. | API negatives and both aluminium positives pass. Additional direct claims-level negative coverage required before final candidate. |
| INTERVENTION | Five simulated_ keys; available step uses only simulated claim; unavailable step contains no simulated claim/value. | Branch/absence checks pass. New PP numeric preservation fixture errors before comparing output (see below). |
| Missing need | No-support/no-need raises ExecutiveIntegrityError instead of fabricating identity/tariff-line. | Negative and real declared-need regression passes. |
| D1 | Not yet changed. | Four permitted control documents still need truthful S18a wording and ADR-028 dependency rule before tree freeze. |

## Stop evidence and prepared correction

Command (host execution, with source bytecode/cache writes disabled):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider -o faulthandler_timeout=30 tests/test_executive_service.py tests/test_executive_api.py tests/test_executive_claims.py
```

- Before fixes: **53 failed, 53 passed**, exit 1; `focused-red-host.log`.
- First green attempt: **1 failed, 105 passed**, exit 1; `focused-green.log`.
- Failure: `test_am4_intervention_is_exclusively_simulated[True-SAU-H0-390210]`, `tests/test_executive_service.py:375`, `KeyError: 'unsupported_npv_m'`.
- Cause: my new test directly indexes an optional field. The governed PP economics contain only `passes=False`, `minimum_effective_support_m=0.0` and a rejection reason. The projected unsupported NPV correctly remains `NOT_CALCULABLE`/null.
- Prepared but **not applied**: `proposed-fixture-correction.patch`, one-line direct-index → `.get("unsupported_npv_m")` change. This preserves the expected value comparison with None and requires no product/frozen-input change.
- AM-4 §4.3 states: “Any unexpected test or contract failure stops rather than prompting an unplanned edit.” Owner authorization for this concrete correction/resumption is pending in the conversation. No product edits after this stop.
- Initial sandboxed focused run stalled at TestClient, was interrupted (exit 130), and is retained as `focused-red.log`. Host rerun completed in 4.95s. Existing FastAPI/Starlette deprecation warning retained; no dependency changes.

## Gates not run

Task 8, compare-only make e2e, approved R1 geometry probe, and make ci in both clean roots: **NOT RUN**. Historical R1 passes do not apply to this retained work. D1, candidate materialization and final gate receipt are incomplete. Staging, source commit, PR, delivery and S18b are not authorized or performed.

## Self-audit

Evidence-reporting audit: PASS for this stopped-state report; completion gate: NOT SATISFIED. Claims above are limited to actual focused logs, source inspection and retained hash checks. No independent approval is impersonated. The complete diff and content inventory are retained. Deferred AM-4 §5 observations (including case EVSI availability and broader model/malformed-input gaps), KL-132 and separate owner implementation acceptance remain unchanged.
