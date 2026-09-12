# Acquisition runbook (S11, S12a and S12b)

Operator-only acquisition commands require explicit `--max-requests` (Makefile `MAX_REQUESTS=`); only period-scoped acquire commands require `--years` (`YEARS=`). Tariff, directory and registry acquisition are period-free. Record chosen values and rationale in the active slice's implementation log before running; S11 history is in `.workflow/slices/S11-acquisition-trade-tariff/implementation_log.md`, and S12a records are in `.workflow/slices/S12a-acquisition-framework-institutional-sources/implementation_log.md`. Never infer parameters from frozen snapshots or worked cases.

## Environment

- Set `IOR_ACQUISITION_LIVE=1` only for the acquire command window.
- Optional: `IOR_COMTRADE_SUBSCRIPTION_KEY` (name only; absence is recorded as `CREDENTIAL_ABSENT`).
- CI and tests never contact live sources; positive guard tests may set explicit live intent only with injected FakeTransport/test-only dependencies and socket guards.
- Redaction is proven in-memory by tests; a stored record carries a redaction marker only where a credentialed request actually occurred. CREDENTIAL_ABSENT records are the honest absence path and are never edited.

## Recorded S11 operator parameters

| Command | YEARS | MAX_REQUESTS | Rationale |
|---|---|---|---|
| acquire-universe wits_trade | 2024 | operator partners run used separate invocation | Partners slice used explicit HS6 list for golden-adjacent codes |
| acquire-universe un_comtrade | 2024 | 5 | Minimum plan units for one flow plus credential probe |
| acquire-tariff zatca_tariff | 2024 (candidate-3 CLI; see note) | 5 | Single tariff unit with INDEX_ENUMERATION headroom |
| acquire-baci | 2024 | 3 | One BULK year plus terms capture attempt |
| acquire-partners wits_trade | 2024 | operator-set | Two HS6 codes × one flow × one year |

## Commands

```bash
make acquire-universe SOURCE=wits_trade YEARS=2024 MAX_REQUESTS=<explicit>
make acquire-universe SOURCE=un_comtrade YEARS=2024 MAX_REQUESTS=<explicit>
make acquire-tariff SOURCE=zatca_tariff MAX_REQUESTS=<explicit>
make acquire-baci YEARS=2024 MAX_REQUESTS=<explicit>
make acquire-partners SOURCE=wits_trade CANDIDATES=tests/fixtures/acquisition/candidates_operator_list.json YEARS=2024 MAX_REQUESTS=<explicit>
make build-snapshots KIND=all
make reconstruct
```

`acquire-tariff` takes no `YEARS`: the ZATCA tree is one period-free contract (DD-5/DD-19) whose as-of date comes from retrieval. The recorded tariff run `20260903T212901Z` was issued by the candidate-3 CLI, which still required `--years`, so its stored contract carries `period: "2024"`; it remains valid raw evidence and, because the tariff unit key `("ALL_TARIFF_LINES",)` is period-independent, a later run supersedes it under DD-21.

## Visual baselines

S11 changes nothing under `browser_tests/baselines/`. `src/ior_mvp/config.py` and `src/ior_mvp/data_repository.py` stay byte-identical to base; the acquisition config loader lives in `ior_mvp.acquisition.source_config` and the acquired-snapshot loaders in `ior_mvp.acquisition.repository`, so the visual provenance manifest remains valid. Do not run `make e2e-update-baselines` for this slice.

## Manifest regeneration

Run `python3 scripts/build_manifests.py` exactly once after all governed Core/ADR/config edits. Candidate 1 ran prematurely before T10 authority artifacts existed; the final justified run follows T10 completion.

## S12a institutional commands and evidence boundary

The recorded parameters and manifest history above describe S11; the period-free tariff exception remains as recorded. S12a adds `acquire-aggregates` (required SOURCE, YEARS, MAX_REQUESTS) and period-free `acquire-directory` / `acquire-registry` (required SOURCE, MAX_REQUESTS; no YEARS or flows). These are operator-only, explicit-live, not-CI commands. The recorded T7 live window is CLOSED: the examples below document syntax, not authorization to run again or suggested parameter defaults.

```bash
make acquire-aggregates SOURCE=gastat YEARS=<explicit> MAX_REQUESTS=<explicit>
make acquire-directory SOURCE=<ministry_of_industry-or-modon> MAX_REQUESTS=<explicit>
make acquire-registry SOURCE=<saso_catalogue-or-saber_registry> MAX_REQUESTS=<explicit>
make build-snapshots KIND=<production-or-directory-or-registry-or-all>
make reconstruct
```

## Recorded S12a operator parameters

Copied from the commands and rationale recorded before execution in `.workflow/slices/S12a-acquisition-framework-institutional-sources/implementation_log.md` on 2026-09-11 UTC. Each acquire invocation used `IOR_ACQUISITION_LIVE=1`, no CI, existing virtualenv PATH, `PYTHONPATH=src`, external bytecode cache and `UV_OFFLINE=1` for the locked local toolchain; no .env read. Every `parameters.units` value was UNAVAILABLE, yielding one explicit unverified-unit contract, never a guessed dataset/directory ID.

| Command / SOURCE | YEARS | MAX_REQUESTS | run_id | Recorded rationale |
|---|---|---|---|---|
| acquire-aggregates / gastat | 2025 | 2 | 20260911T215546Z | 2025 is the observed methodology reference year; one unit plus documented terms allowance, not physical production input inferred from the IPI. |
| acquire-directory / ministry_of_industry | not applicable (period-free) | 1 | 20260911T215956Z | Minimum one unverified unit; no observed terms-capture URL. |
| acquire-directory / modon | not applicable (period-free) | 1 | 20260911T215956Z | Minimum one unverified unit; no observed terms-capture URL. |
| acquire-registry / saso_catalogue | not applicable (period-free) | 2 | 20260911T220134Z | One unverified unit plus one documented terms allowance. |
| acquire-registry / saber_registry | not applicable (period-free) | 2 | 20260911T220134Z | One unverified unit plus one documented terms allowance. |

All five returned application exit 3 (Make exit 2), ENDPOINT_UNVERIFIED, zero requests/pages and INCOMPLETE coverage; observed response/stop were null. Exact query hashes and attempt paths are KL-47–51. Endpoint/unit preflight stopped before terms or budget use. Documentation consultations are separate observations, not acquisition HTTP responses. No data body, institutional snapshot or source-specific parser exists from these runs. Offline `make build-snapshots KIND=all` exited 0 naming only the existing WITS partner snapshot; all five institutional kind/source pairs returned COVERAGE_INCOMPLETE. Offline reconstruction with the pre-generation `--no-check-manifest` option passed 1 snapshot / 4 artifacts; normal `make reconstruct` retains default manifest checking. No optional second acquisition was justified without an observed source contract.

Before any separately authorized future acquisition, record its source, periods where applicable, units, request bound and rationale from actual documentation. Never infer credentials, pagination, MIME, dataset units or access from a portal name. An unobserved credential stays the literal UNAVAILABLE in config, causes no environment lookup/Authorization header, and is serialized as null with false credential flags in attempts. An observed credential name follows the existing absence guard. Unknown endpoint/unit precedes unknown access/terms refusal; no .env is read.

DIRECTORY/REGISTRY data responses use Core 05 §10's exact declared-MIME, strict UTF-8/BOM/control and bounded label screening before storage; no sniffing/fallback or guessed decoding. PersonalDataFields or UninspectableTextPayload means OUT_OF_SCOPE_CONTENT, hash-only safe metadata, no refused body/labels/values retained, INCOMPLETE coverage overriding apparent pagination completeness, and preserved prior pages. Unknown inspectable text can be stored UNPARSED, but old write-once metadata is never relabelled. PDF/XLSX/non-UTF-8 bodies are outside the approved DD-15(b) offline-parser path; later parsers cannot recover unstored bodies. Cite an actual policy refusal as OUT_OF_SCOPE_CONTENT:UninspectableTextPayload, not FORMAT_NOT_PARSEABLE; none occurred in the five zero-request T7 runs. Parser/encoding expansion requires a separately governed change.


Future-use template copied verbatim from the approved privacy policy (not an actual T7 refusal; fill only from a future observed refusal record):

```text
<source/query_hash/run_id>: OUT_OF_SCOPE_CONTENT:UninspectableTextPayload. Response refused before storage by S12a text-only policy. No payload retained; DD-15(b) offline parsing unavailable. Evidence: <attempt path/status/body SHA-256/byte count>. Format/encoding support requires a separate governed change. Do not call this FORMAT_NOT_PARSEABLE; that code describes stored UNPARSED build refusal.
```

## S12a manifest gate (T9 authoring: not yet executed)

At T9 authoring, S12a manifest run count is **0**. ADR-016 records the approved §7.3/§7.4/§7.5 rationale before the single authorized T11 generation. After T9 review and T10 regression, the coordinator may run `scripts/build_manifests.py` exactly once, mirror the authority §11 table and check the exact generated diff; this runbook does not execute or pre-approve the result. Existing S11/raw/partner/public/synthetic/golden/browser bytes remain fixed. Acquisition-config and four Core hash drift at T9 is expected until T11, not an integrity PASS. Owner direct approval replaces plugin ceremony and ordinary logs replace plugin evidence capture; PR/CI/merge approval remains a separate delivery gate. Record the actual T11 completion separately, not by treating this authorization as a receipt. No repeated generation to conceal a mismatch, no visual baseline update and no source network outside a newly authorized operator window.

Recorded T11 outcome: the single generator invocation exited 0 on 2026-09-11 at 22:31:25 UTC; five authority-table rows were mirrored, and immediate canonical [12] passed. Current manifest run count is **1** and that permission is exhausted. ADR-016 and the slice test evidence contain the generated hashes and exact unchanged-S11 proof. No rerun is authorized by this runbook; T12 and session review remain separate gates.

## S12b manifest gate (T9 authoring: not yet executed)

At T9 authoring, **S12b manifest run count is 0** (S12a already consumed its single authorized run). ADR-017 records the approved §7.3/§7.4/§7.5 rationale before the single authorized T11 generation for this slice. After T9 review and T10 regression, the coordinator may run `scripts/build_manifests.py` exactly once, mirror the authority §11 table and check the exact generated diff; this runbook does not execute or pre-approve the result. Existing S11/S12a raw/partner/public/synthetic/golden/browser bytes remain fixed. Acquisition-config and four Core hash drift at T9 is expected until T11, not an integrity PASS. Document `-v1`/`-v2` lists and honest attempt records under `data/raw/{document-source}/` and `data/documents/**` are the expected §7.5 additions. No COMPLETE DocumentRecord is required for slice completion when KL cites every source without a record.

**Recorded T11/owner-authorized outcomes:** (1) slot 2 — generator exited 0 on 2026-09-12 at 05:26:47 UTC; five authority-table rows mirrored; immediate [14] passed; snapshot manifest +88 rows (lists and zero-request attempts). (2) slot 3 OD-9 — generator exited 0 at 05:43:02 UTC after the T7-v3 SR-06 re-runs produced twelve COMPLETE records; §11 mirrored and immediate [14] passed. (3) slot 4 OD-10 — generator exited 0 at 06:37:37 UTC after reviewer-driven F01/F02 corrections; §11 mirrored and immediate [14] passed. (4) slot 5 OD-13 — generator exited 0 at 07:30:41 UTC after the page-hash, physical-page, superseded-run and governed-text corrections, all twelve offline record rebuilds and corrected T10 regression; §11 was mirrored and immediate [14] passed. S12b's final manifest run count is **4**; all four authorizations are exhausted and no fifth run is authorized.

**T7-v3 operator window (slot 3, SR-06):** closed 2026-09-12 05:40:21 UTC. Terms: SASO acceptable-use policy recorded for `saso_documents`; UNICOIL privacy policy consulted — no document reuse terms (`license_capture_required: false`). `-v3` lists and runs `20260912T053622Z` (saso, 6 COMPLETE units) and `20260912T053955Z` (unicoil, 6 COMPLETE units). Current records: the six `saso_documents` DocumentRecords are built from the declaration-corrected list `saso_documents-v4` against run `20260912T053622Z` (slot-4 correction round, OD-11 — the v3-built records were replaced before any commit; same `document_id`s); the six `producer_unicoil` records are built from `producer_unicoil-v3` against run `20260912T053955Z`. v1/v2/v3 lists and every prior run are retained as history; no list is edited after a run.
