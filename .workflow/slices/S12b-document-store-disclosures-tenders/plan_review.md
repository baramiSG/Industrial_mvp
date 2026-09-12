# Plan review — S12b (plan attempt 1)

**Subject:** `.autonomous-workflow/plans/s12b-document-store-disclosures-tenders/cycle-1/plan-1.json`, SHA-256
`c70e90652b448e2e9b9447bf3cb6fb161fe9224d20f2021e00a1368e7a2fbdb5`.
**Supervisor (owner lead agent, claude-fable-5.1) material review — 2026-09-12:** no B1–B7 finding.
**Independent plan review — `reviewer-grok` (cursor-grok-4.6-xhigh), 2026-09-12: APPROVE, zero findings, six advisories.** Record:
`.autonomous-workflow/evidence/s12b-document-store-disclosures-tenders/plan-1-review.json`. The reviewer independently re-verified
BF-1–BF-17, BF-20–BF-23, BF-25 against the cited code (including re-running the planner's `/tmp` pypdf probes) and all 36
`authority_hashes`. A first dispatch had correctly refused an intermediate, still-being-written copy of the plan on identity mismatch
(`plan-1-review-identity-mismatch-8b0ff175.json`). **State: `PLAN_APPROVED`** (decision D-0001 in the slice decisions ledger).

## Supervisor checks

- B1 authority conflict: none found. The new Core 05 §3.3 row and the Core 04 `DocumentRecord 1.0.0` section are additive §7.4 changes;
  Core 05 §3.1 and the S12a acquisition block are pinned byte-identical ([22], [24]). FORMAT_NOT_PARSEABLE keeps its Core 05 §10 meaning.
- B2 fabricated facts: BF-16/BF-17 (pypdf 6.16.1 wheel in the local uv cache; BSD-3-Clause; pure Python; `typing_extensions` only for
  Python < 3.11) re-verified by the supervisor against `~/.cache/uv/archive-v0/MxF7zC3Qr3ZMkmzV/pypdf-6.16.1.dist-info/{METADATA,WHEEL}`.
  No URL reachability, terms or content is asserted; the 2026-09-02 probe is marked risk-only (BF-25).
- B3 frozen-oracle risks carry proof commands: [5]–[10], [14], [17], [19], [25].
- B4 ADR-017 precedes the single `build_manifests.py` run (T8/T9 → T11) with [14] immediately after; §11 mirror step named.
- B5 tests are falsifiable (pinned hashes, exact literals, tamper and negative probes, cross-process determinism).
- B6 no credential path: sentinel `UNAVAILABLE` never looked up or sent; credential names only when observed; `.env` never read.
- B7 no scope creep: no S20 labels/metrics, s12c IDs, S13/UI, engine consumption, new support code, KindRegistry kind or budget change.

## Owner rulings (delegated authority; recorded locally in `.autonomous-workflow/owner-decisions/20260912-s12b-plan-1-rulings.md`)

| Decision | Ruling | Basis |
|---|---|---|
| OD-1 pypdf in the `dev` extra | ACCEPTED | ci.yml byte-identical; every environment that runs reconstruction already installs `dev`; runtime image free of pypdf (DD-21). |
| OD-2 classes: etimad_tenders B, saso_documents B; producers/Tadawul C | ACCEPTED | Methodology §2.1 (official documents awaiting validation = B; company disclosures = C); Core 05 §3.2 rows already C. |
| OD-3 per-producer source ids | ACCEPTED | Passport `source_identity` (authority/terms/access) is read per source mapping and differs per publisher. |
| OD-4 new Core 05 §3.3 row "SASO public technical regulations" | ACCEPTED | Distinct from the S12a registry-metadata row; additive §7.4 with ADR-017. |
| OD-5 `DocumentConnector.snapshot_kinds = {'document'}` | ACCEPTED | Document sources are neither built by `build_snapshots` nor mis-reported as `raw_only`. |
| OD-6 PDF `extraction_mode='layout'` | ACCEPTED | BF-17: plain mode reverses RTL runs and drops mixed-direction segments; layout mode is verbatim and deterministic on the probes. |
| OD-7 four envelope types only | ACCEPTED | Owner disposition 4; no sniffing; octet-stream/x-pdf refusals become KL rows; widening is a later governed change. |

Additional owner disposition 6 (not in context.md, whose hash the plan cites): **tooling network use for `uv lock` / `uv sync --locked`
dependency resolution at T1 is authorized** as an environment operation (as the S12a browser-runtime download was); it is not a data
acquisition and must be recorded in the implementation log (command, exit code, whether the index was contacted). Data-source network
remains confined to T7.

## Findings transferred to the Implementation Acceptance Checklist (IAC; not rejections)

- IAC-1 `tests/test_acquisition_institutional_connectors.py` and `tests/test_acquisition_institutional_snapshots.py` must be
  byte-identical to HEAD and green after the `_pre_storage_refusal` hook refactor (the plan says "green unchanged"; make byte identity explicit).
- IAC-2 `scripts/reconstruct_snapshot.py --all` must print `DOCUMENT RECONSTRUCTION PASS (0 records, 0 artifacts)` and exit 0 with zero
  records pre-T7 so that [5] holds from T6; "no acquired snapshots" exit 1 only when neither snapshots nor records exist (DD-17).
- IAC-3 T7 consultation observations (URL, date, status, media type, byte count, SHA-256) are recorded without bodies; every
  `application/octet-stream` / `application/x-pdf` refusal is a KL row citing the query_hash.
- IAC-4 Stored PDFs are bounded by the unchanged budgets; the PR body reports the total `data/documents` + new `data/raw` bytes.
- IAC-5 `uv lock` must not upgrade unrelated packages: the lock diff is limited to the `pypdf` entry and the project's dev-extra list
  (recorded in the log; reviewer checks `git diff --stat uv.lock`).
- IAC-6 The candidate identity procedure of S12a (sorted path/sha256/bytes list, slice records excluded) is reused verbatim at T12.

### Transferred from the independent plan review (reviewer-grok advisories A-01–A-06)

- IAC-7 (A-01) The T3 GATE is not runnable as written: [5]'s `DOCUMENT RECONSTRUCTION PASS` grep exists only from T6 and [11] only after
  T7. At T3 prove O-1 with the existing `^RECONSTRUCTION PASS (1 snapshots, 4 artifacts)$` line plus [6]–[10]; [5] in full from T6; [11]/[26]
  from the end of T7 (as `verification_notes` already times them).
- IAC-8 (A-02) `tests/test_acquisition_reconstruction.py:568-570` asserts `'RECONSTRUCTION PASS' not in stdout` on a snapshot tamper.
  `scripts/reconstruct_snapshot.py` must therefore evaluate snapshots and documents first and print **any** PASS line only when everything
  passed; on any failure print only FAIL lines and exit non-zero. Keep the snapshot token anchored (`^RECONSTRUCTION PASS`), print the
  document line exactly as the plan's [5]/[17] grep it, and never weaken the tamper assertions.
- IAC-9 (A-03) Verification [25] as written is vacuous (`rg` rejects the git pathspec `:(glob)src/ior_mvp/*.py`, exits 2, and `!` inverts
  it). Run [25] verbatim for the record **and** the corrected form
  `! rg -q 'pypdf' src/ior_mvp/*.py Dockerfile && ! rg -q -e 'import urllib' -e 'from urllib' -e 'import socket' -e 'import ssl' -e 'import http' src/ior_mvp/acquisition/documents src/ior_mvp/acquisition/connectors/documents.py && echo RUNTIME_AND_DOCUMENT_MODULES_OFFLINE_OK`;
  both outputs go in `test_evidence.md`. O-6 remains additionally covered by [1], [8], `test_offline_guard` and the T4 no-network-import test.
- IAC-10 (A-04) Pin the existing DIRECTORY/REGISTRY literals (`PersonalDataFields`, `UninspectableTextPayload`,
  `Response refused by institutional text-only privacy policy; body not stored`) in the new hook tests; the two institutional test files stay
  byte-identical (IAC-1).
- IAC-11 (A-05) BF-9's "fourteen keys" is a count slip — `passports.py` `required_top` has fifteen; call `assert_passport_complete`, never
  re-implement the check; `passports.py` byte-identical.
- IAC-12 (A-06) Author the T2 CID/Arabic PDF fixture from the planner's probed recipe (the `/tmp/fixture_ar*.pdf` bytes if still present,
  otherwise an equivalent Type0/Identity-H + ToUnicode bfchar construction); never relax the verbatim Arabic line pin. `uv lock` without
  `--upgrade`; the lock diff is limited to the pypdf entry and the project's dev-extra list; record whether the index was contacted.

### Owner deviation approvals during implementation

- IAC-13 / OD-8 (2026-09-12): `tests/test_browser_harness_contract.py` and `tests/test_visual_baseline_contract.py` pin the exact `dev`
  extra list; adding `"pypdf==6.16.1"` to those two assertions is accepted as a recorded deviation from `files.modify` (direct consequence of
  DD-4). ADR-017 names both files. No other unplanned file may change; the reviewer verifies the changed-file set against the plan plus this line.
