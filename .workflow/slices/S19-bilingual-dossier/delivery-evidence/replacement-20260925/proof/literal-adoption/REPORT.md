# Literal-adoption report

Paused. These four expectation updates do not certify a final candidate.

Persona: test-literal and provenance auditor. D-S19-1 was not revised.

## Adopted literals

Emitted proof read before edit: `GRAPH-EMISSION-CHECK.json` engine `ENGINE-6b54371e99f3`, projection `GRAPH-SAU-2026-09-12-6f43b1a8c4aa`, 925/1045, 230 inputs; `MANIFEST-MEMBERSHIP-CHECK.json` snapshot 728+2=730, authority rows 20 unchanged, 45 indexes preserved. Live files confirmed: `current.json` points at that projection; projection `engine.engine_run_id` is `ENGINE-6b54371e99f3`; snapshot `files` length is 730.

1. `browser_tests/test_graph.py:845` `new_token` `ENGINE-5e01ef7c4b9d` → `ENGINE-6b54371e99f3`. `old_token` remains `ENGINE-7ae34188bdec`.
2. `tests/test_integrity_contract.py:1298` live `len(paths)` 728 → 730.
3. `tests/test_s17_generation.py:58` live snapshot length 728 → 730.
4. `tests/test_s17_status_docs.py:33` live snapshot length 728 → 730. Visual count 128 and `change_ref` `S19-BILINGUAL-DOSSIER-1` were already present and were not edited.

## Hashes

Before:

- `browser_tests/test_graph.py` `2b37163125581c45cf8067c04257dc9b7c3c0dd6d0bc984883ec853a44ce454c`
- `tests/test_integrity_contract.py` `ee966276b75722536a71b0c0e02d7ed7ba4be3e615ce4c87ca2df59292326d44`
- `tests/test_s17_generation.py` `2da86d1e5fa9c10cd35bd033b2855751a035213ab67365d86ed81388b6b1bfc5`
- `tests/test_s17_status_docs.py` `0cf24731063eb87022bede6a2ef290801791669e469c1821575e3fc1b35fb0cc`

After:

- `browser_tests/test_graph.py` `15bc85930e2e1575ba762624bc669814f43a5469e8c4ac8ef61d52e5ecb9e7bd`
- `tests/test_integrity_contract.py` `7173cc2c853947207f191c909aa69e2ec6055396aa4faca4cf6f026fef9ed04b`
- `tests/test_s17_generation.py` `f9eedca0df040983aebdd0ae5af373c55aef71c4d99e9e56a0c730d8c7c87bdd`
- `tests/test_s17_status_docs.py` `18553320fc58ea1be5cebcaf523e28e3f626f279fdfe87a062bbfc76c7fb7ff2`

`four-line.diff` is the working-tree delta. `git-diff-vs-index.diff` also shows earlier uncommitted literals (index still has 726, `ENGINE-a1dcbf0e7665`, and `S18B-BILINGUAL-EXECUTIVE-SURFACE-1`). This unit did not change those earlier hunks.

## Tests actually run

Command: `GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1 uv run --locked --offline --extra dev --extra graph python -m pytest -q -p no:cacheprovider` on the three named functions.

`three-tests.log`: exit 0, **3 passed** in 2.61s. The in-memory graph build is the existing generation test. No graph write, manifest build, capture, or browser test was run.

## Not done

Browser sensitivity control, full graph matrix, canonical capture, all-44 proof, R1, pins, CI, publication, and Aura remain later root-owned gates.

## Sanad

Claude source APPROVE `7e78bf3ba431f148f1bdadeb94582c01b4eca4bd87cd0c3c7e55ff417206e867` and operation GO `faa407e9ff9d6435ba9a0adf0e264559f895b15f65c34aa0f183cd479af201a7`. Release `b8047de6e0711493ac9028f18f531f0cf96a495648341d80cf200a3e104d54c4` allowed these edits only after emitted proof. Counts and engine id are from `GRAPH-EMISSION-CHECK.json`, `MANIFEST-MEMBERSHIP-CHECK.json`, and the live projection/snapshot reads above. `HANDOFF.md` still says generation was unwritten; `RESULT.json` `bc011a453647fb0a6ba4810aadd78a350b2d6407d5f2801473824994232b9d6d` records the completed unit. Test result is `three-tests.log`.

## Muhasabah

PASS for these four admitted literals and the three prescribed tests. Unrun browser and later gates stay open. No final-candidate certification.
