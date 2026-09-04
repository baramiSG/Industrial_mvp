# Acquisition runbook (S11)

Operator-only commands. Every invocation requires explicit `--years` and `--max-requests` (or Makefile `YEARS=` / `MAX_REQUESTS=`). Record the chosen values and rationale in `.workflow/slices/S11-acquisition-trade-tariff/implementation_log.md` before running. Never infer parameters from frozen snapshots or worked cases.

## Environment

- Set `IOR_ACQUISITION_LIVE=1` only for the acquire command window.
- Optional: `IOR_COMTRADE_SUBSCRIPTION_KEY` (name only; absence is recorded as `CREDENTIAL_ABSENT`).
- CI and tests never set live acquisition.
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
