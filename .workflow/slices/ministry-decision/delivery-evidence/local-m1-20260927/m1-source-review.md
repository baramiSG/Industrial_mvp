**Source review complete: no material findings. The final affected gates are still pending.** This is not an APPROVE and not READY_FOR_CI, because the successor artifact and its gates don't exist yet. Everything was read-only: no writes, Git, services, credentials or lease access.

**Subject:** the current W source. The M1 correction diff is `TASK-ONLY.diff` `b88d3d4f…`, compared against the immutable `final-candidate-replacement-2/proof` (241e4df / fe98722). `SOURCE-AFTER.json` lists exactly five changed paths out of 3,544, matching the expected set. I confirmed independently that `config/`, `data/` and the DOCX are byte-identical to proof 2, and that under `src/` only `graph/projection.py` differs, so `rules.py`, `screening/*`, the evidence snapshots and the golden and synthetic data are unchanged.

## Checked against approved M1, both conditions and the third-alias addendum

- **Exactly three aliases, no fallback.**
  - `_PUBLIC_SOURCE_FAMILY_IDS` holds only `coated_steel`, `polypropylene` and `fabricated_aluminium`, looked up case-sensitively with `.get()`.
  - Non-string or unmapped labels resolve to `None`, then `UNAVAILABLE`.
  - There's no identity or sector fallback. The `technical_plastics_conversion` negative proves a label that equals a configured family ID is still treated as unmapped.
- **Config comes from the real build root.**
  - `build_repository_projection` loads `root/config/product_families.v1.yaml` with the existing `_load`, validates it with `validate_product_families`, and passes it into the only repository `_public_analysis` call.
  - The standalone default uses the governed cached config.
  - The target comes from `family_for_hs6(hs6, config)`.
- **Unknown stays unknown.** Unchanged `evaluate_r9s` (`rules.py:1269–1271`) turns `UNAVAILABLE` into DISABLED with `fired: None`. The adapter exposes `same_process_family: null`, not the internal `NOT_CALCULABLE`, and `qualifying_signal_count` stays an integer. A known but different family gives `false`, as with 392010's conversion family.
- **Input closure.** `screening/__init__.py` and `screening/config.py` are required `ENGINE_IMPLEMENTATION` inputs and fail closed if missing. The tests pin 240 inputs (238 + 2), exact membership and hashes, and show that changing either helper changes the projection ID.
- **Per-producer attribution.** `_sole_record_signals` is unchanged.
  - The PP regression pins: SABIC `(True, fired True, 1, ADJACENT_PLANT_WITH_SIGNALS, [P-SABIC])`; Advanced and Tasnee `(True, False, 0, NO_DEFENSIBLE_SIGNAL, [])`.
  - The separate reference summary stays fired with count 2.
  - The aluminium preservation test runs on a projection rebuilt in memory from source (the module fixture is `build_repository_projection(PROJECT_ROOT)`). It pins the exact producer IDs, relationship keys, evidence (`P-ALUPCO-760429` / `P-TALCO-760429`), scope, and the unchanged true / FULL / not-fired / 0 results.
- **Completeness uses the build's loader.** The inventory is enumerated through `_load_repository_cases`, as my addendum condition required. `LOADER-INVENTORY.json` reports 11 cases, 7 records, labels `{coated_steel: 2, fabricated_aluminium: 2, polypropylene: 3}` and nothing unmapped.
- **Authority records.** The Core02 row and ADR-033 state the exact semantics accurately, including the Manifest §7 observable correction, no identity or sector fallback, and the strict-R1 STOP condition, and they don't overclaim.
- **Receipts.** RED shows 2 failed / 3 passed, with `technical_plastics_conversion` failing under the rejected fallback. GREEN shows focus tests 8 passed and the affected suite 131 passed in 11.70 s.

## Nonblocking

- `projection.py` imports the private `_load` from `screening/config.py`. That reuses the existing loader without editing the file.
- The alternate-root test monkeypatches the case loader back to `PROJECT_ROOT`, so only the config varies. That scope is disclosed and acceptable.
- Earlier tracked items stand: the candidate-fact notice wording, the arrowhead convergence, and the generic `role` substring match.

## Pending for the final verdict (one bound packet on this thread)

- Actual stock generation, then semantic inspection proving that exactly three PP edges and five leaves change, with every steel, aluminium and other element equal after identity normalization.
- Snapshot membership 746→748, with authority still at 20.
- Pins, the canonical capture with any token-only differences inspected, and a fresh freeze.
- Full pytest, integrity, static checks and smoke; the full functional and visual browser gate; strict R1 (STOP on failure, no M-A4 waiver); the single bounded graph gate under the post-reboot lease guard; and the F→M feed replay rebound to the successor.

**Evidence basis:** directly inspected — the diff and current source, protected-byte equality, the test bodies, the R9-S code and the receipts. Relied on Sol's and root's executions. Hosted CI and M-A3 live Aura remain later obligations.

**Muhasabah: PASS.** Findings rest on the actual code and receipts. Nothing about the successor or the gates is presumed.
