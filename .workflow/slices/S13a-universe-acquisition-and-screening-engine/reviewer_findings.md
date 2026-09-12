# Reviewer Findings — S13a Universe Acquisition and Screening Engine

Reviewer seat: `reviewer-grok` (cursor-grok-4.6-xhigh), sole approving independent reviewer. The round-1 instance could not be resumed by the harness after its verdict; rounds 2–4 ran on a fresh instance of the same seat carrying the round-1 verdict file as context (owner ruling OR-5). Verdict files: `.autonomous-workflow/evidence/s13-public-universe-screening/implementation-review-s13a-slot-{1,2,3,4}.json` (local-only records).

## Plan reviews

- `plan-1-s13a.json` (`9d1f8134…`): APPROVE; advisories transferred as IAC-1…IAC-14 in `plan_review.md`.
- Amendment AM-1 (`d562ddca…`, validator enforces HS revisions from rows): APPROVE.
- Amendment AM-2 (`88abbab2…`, sharded write-once directory with per-file/total budgets): APPROVE.

## Round 1 — candidate `612626ed400446e7b13986f5d7213af89b6de178d80b23426cc637a502e26343` (378 files, base `81eac4f2`) — REJECT

Oracles passed (2190 tests, `INTEGRITY PASS`, frozen smoke outcomes, four reconstruction passes) and every real-data figure was recomputed independently (8/8 COMPLETE units, 5,443 HS6, dispositions 4,996/447/0, queues 119/0/0/4,727/15 in key order, 135 unqueued, manifest 216 → 535 rows with zero changed prior rows, authority set 17 → 19). Findings:

- S13A-IR1-F01 — `docs/core/05_DATA_SOURCES_AND_INGESTION.md` §3.1 UN Comtrade / WITS row still described the S11 connector after the official v1 universe was proven. Owner adjudication: VALID (OD-13).
- S13A-IR1-F02 — `docs/KNOWN_LIMITATIONS.md` lacked rows for methodology §8.2(c) `NOT_CALCULABLE` at screening grain (OD-3) and for persistence-only unqueued candidates (OD-4). Owner adjudication: VALID (OD-13).
- Advisories A-01 (ADR-019 header cited AM-1 only), A-02 (partner detail KL-40 residual), A-03 (Core 01 §8 "1,300-product universe" wording), A-04 (latest-snapshot selection by `as_of_date` then id), A-05 (CLI exit-code test), A-06 (reviewer did not run `make ci`).

## Round 2 — candidate `e73aeba9d5d997eaf8973eac324b0f0f679a25ebfc8700e263709facfea70fc6` (378 files, base `81eac4f2`) — APPROVE, zero findings

Delta versus round 1 was exactly ten files; all 320 `data/**` hashes unchanged. F01/F02 CLOSED (Core 05 §3.1 row and KL-81/KL-82 pinned by tests); A-01, A-03 (Core 01 §8 rewording plus new §11 FR-080…FR-083), A-04 (repository) and A-05 CLOSED. Fourth manifest run verified: only Core 01 and Core 05 changed among prior authority rows; 216 prior snapshot rows identical; §11 mirror 19/19. Residual advisories: A-02 (partner detail), A-04-residual (CLI `_latest_snapshot` uses `sorted(glob)[-1]`; single directory today — carried to s13b/backlog), A-06 (reviewer did not run `make ci`; the owner lead agent did, exit 0).

## Round 3 — candidate `402ff348dd0a11d148a825aa3e2bcdd27b197f2df773dfa41d5f35771a193558` (253 paths: 130 present, 123 deleted; base `e72eb57`) — APPROVE, zero findings

Hosted CI-F-01 correction (OD-15). Recomputed: 96/96 record shards and `queues.json` byte-identical to the superseded `311f105c4ccf` snapshot; `summary.json` differs in exactly four leaves (three input paths now repository-relative, `snapshot_id` = `9b6b22032fd8`); dispositions and queues unchanged; universe, entity artifact, plant-family links and configs byte-identical to HEAD; no `/home/` string under `data/screening`; 411 non-screening manifest rows identical and authority hashes unchanged; validator and reconstruction both reject an injected absolute path with `screening input path must be repository-relative manifest key`; portability copy at a different absolute path produced `INTEGRITY PASS` and all four reconstruction passes; 2197 tests.

## Round 4 — candidate `f7af7f75902e0fee75189906575103dcf83ce7ea8ba81bff77c01e4bed630cfc` (1 file, base `c69e17f`) — APPROVE, zero findings

Hosted CI-F-02 correction (OD-17), `tests/test_acquisition_stored_artifacts.py` only: 0 assertions removed, 3 added; every `next(raw.rglob(...))` selection is now `sorted(...)[0]`; the wrong-source test derives the wrong id from the chosen file's own partition; new `test_detector_un_comtrade_partition_explicit`. Order-independence recomputed for all five raw partitions and reversed `rglob` order. Python 3.14.6 resolved offline; a full 3.14 pytest environment was UNAVAILABLE locally, so the two fixed functions were invoked directly under 3.14.6 (PASS) and the hosted `uv / Python 3.14` job was treated as authoritative. 2198 tests.

## Limits of the reviews

The reviewer did not run `make ci` or the browser suites in any round; the owner lead agent ran `make ci` on the identical trees for rounds 2 and 3 (exit 0; logs in local evidence) and hosted CI ran the full five-job matrix on every pushed head.
