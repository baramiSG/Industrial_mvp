# S12b implementation context

Base: `cdfd4ba4b016619b7ab33a373d334f22c337166d` (main after PR #16; S12a merged at `cc85cbc`).
Branch: `slice/s12b-document-store-disclosures-tenders`.

Authority for this slice: the owner's 2026-09-12 delegation to the owner lead agent (local-only record
`.autonomous-workflow/owner-decisions/20260912-owner-lead-agent-takeover-and-s12a-delivery.md`); the approved S12 split
(`docs/BUILD_ROADMAP.md` §S12 split; `.autonomous-workflow/plans/s12-acquisition-institutional-documents/cycle-1/decomposition-1.json`,
SHA-256 `ad234d819270e40b63ef2e12fff435379e9e412630feda3e0c5629dcd887dbd7`, child `s12b` goal and acceptance boundary);
AGENTS.md; Manifest; Core 03/04/05/08/09; methodology §§2, 3, 5, 11, 15 (DOCX governs; mirror is a search aid).

Read-first for every seat: AGENTS.md, `docs/authority/00_AUTHORITY_MANIFEST.md`, Core 04/05/08/09, `docs/implementation/ACQUISITION_RUNBOOK.md`,
ADR-015/ADR-016, KL-40–KL-53, S11 and S12a slice records, `src/ior_mvp/acquisition/**`, `scripts/reconstruct_snapshot.py`,
`scripts/build_manifests.py`, `config/acquisition_sources.v1.yaml`, `tests/test_acquisition_*`, `tests/acquisition_doubles.py`.

Owner dispositions recorded for planning (delegated authority; each must still be justified in the slice ADR):

1. Text layer: a pinned, pure-Python, permissively licensed PDF/HTML text-extraction dependency MAY be added under SG-TR-007
   (pyproject + uv.lock; exercised by uv, pip and Docker CI jobs) if the planner shows deterministic, versioned derivation and a
   reconstruction test; OCR and inferred text are prohibited. Documents without an extractable text layer are stored raw with spans
   `UNAVAILABLE` / `FORMAT_NOT_PARSEABLE`.
2. Document acquisition is explicit-operator-list driven (as S11 partners, KL-40): every document URL, declared source, publisher and
   expected type is recorded before the guarded operator window; nothing is crawled or guessed. Access outcomes are recorded honestly
   per document (COMPLETE / UNAVAILABLE with observed response).
3. Size budgets stay in versioned YAML; any change is a Manifest §7.3 change with rationale.
4. The S12a DIRECTORY/REGISTRY text-only privacy guard is unchanged; the document store defines its own envelope policy for
   `application/pdf`, `text/html`, `text/plain` with no personal-data field storage and hash-only refusal metadata.
5. Exactly one `scripts/build_manifests.py` run after the ADR and full regression; S11/S12a raw, snapshots, partner snapshot, frozen
   public/synthetic/golden data and browser baselines remain byte-identical.

Environment: existing `.venv` (uv-locked); bytecode redirected via `PYTHONPYCACHEPREFIX` outside the repository; `.env` never read;
runtime, tests and CI offline; live network only inside the guarded operator window with explicit parameters recorded in the
implementation log. No commit before independent implementation APPROVE; PR + hosted CI green on the exact head + recorded owner
merge decision before merge.
