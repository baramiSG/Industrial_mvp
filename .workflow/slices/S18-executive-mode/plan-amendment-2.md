# S18a PLAN v1 — Amendment 2: cycle-free generated identity binding

Status: owner correction for `AM1-F1`, submitted to the same independent plan reviewer. Precedence: AM-2 > AM-1 > PLAN v1.

Parent plan SHA-256: `1b300b0f05fcb7b658f6df95d1c8022ad179554106a1a77d70fbd72704cf017f`. AM-1 SHA-256: `b362205aa72d7b6a90892d97e185a1d2c66f57a30de90f6bda31bd1459b137ab`.

## Finding adjudication

`AM1-F1` is VALID. Core 09 is included by `graph.projection.discover_inputs()`. AM-1 incorrectly pinned the in-memory identity observed before its required Core 09 provenance-closure edit. Changing Core 09 necessarily changes the projection identity.

The advertised `GRAPH-SAU-2026-09-12-a87b670a1dad` is diagnostic evidence only. It is not an authorized output ID and must not appear as an expected generated identity in implementation tests, authority text or final records.

## Corrected order

1. Implement the public/simulated claim corrections and their RED/GREEN tests from AM-1.
2. Finish every graph-hashed source before identity calculation: Core 01/02/04/07/09, every `config/*.v1.yaml` in scope (none expected), and all graph-discovered engine implementation files. Core 09 must truthfully state that S18a changes graph and visual provenance without changing graph semantics/counts or WebP pixels.
3. Run focused/full pre-generation checks. Only the known stale graph/authority/visual provenance guards may remain red.
4. Run the existing in-memory builder in read-only mode and record its emitted projection ID and 925/1,045 counts. Do not compare to or force any pre-Core-09 diagnostic identity.
5. Return the emitted ID to the owner. The owner binds that exact diagnostic result in the local checkpoint and authorizes the single graph generation if all preconditions pass. No Core/config/graph-discovered engine file may change after this binding.
6. Run the existing graph generator once. Require its emitted identity equals the bound in-memory identity, counts equal 925/1,045, the old `b63159c7bdc1` projection remains byte-identical and no previous projection/current-history file is deleted or overwritten.
7. Record the actual identity only in non-graph-input control records (`docs/ARCHITECTURE_DECISIONS.md`, Build Roadmap/Progress/Traceability and owner workflow records). Do not add the actual ID to any `docs/core/*.md`, `config/*.v1.yaml` or graph-discovered engine file after generation.
8. Run `scripts/build_manifests.py` exactly once after the new graph files and control records exist. Audit the expected 722→724 snapshot inventory and 20 authority rows; they remain expectations, not forced values.
9. Run immediate integrity, graph reconstruction and `python -m ior_mvp.graph build --check`. All must resolve to the bound generated identity.
10. Run exactly one provenance-only canonical visual refresh, compare all 112 WebPs byte-for-byte, then update the exact visual-root pin. Any image change stops.
11. No graph-hashed file may change after steps 6–10. If a required correction touches one, stop before accepting the candidate; do not silently allocate a second graph generation.

## Core 09 correction requirement

Before step 4, replace the stale statement that S18a changes no graph or visual byte with the truthful invariant:

- S18a changes graph identity/projection bytes only because governed Core and engine input hashes change;
- node/edge semantics and counts remain expected at 925/1,045 and must be audited;
- visual manifest/provenance bytes change because `app.py` and the graph pointer/projection are visual sources;
- all 112 WebPs are expected byte-identical and no new visual path is added.

The proving test asserts this semantic contract without embedding a future projection ID.

## AM-1 claim correction remains

AM-1 public rule-ID mapping, no R10 over-linking, simulated Class-D claim metadata/current-scenario evidence, negative tests, model file-size boundary and no-S18b/no-Aura constraints remain unchanged and required.

## Updated generation oracle

Remove the stale identity literal from plan-review and implementation oracles. Proving evidence is:

1. after all hashed Core/source edits, read-only `build_repository_projection().projection_id` emits one ID;
2. single generation emits that same ID;
3. `data/graph/current.json`, new projection manifest/file hashes, reconstruction and `build --check` all agree;
4. a post-generation input rediscovery has the same path/hash set recorded in the projection.

## Non-goals and counts

No second generation, forced ID, graph semantic change, new graph vocabulary, Aura operation, scenario/data/golden change, S18b UI/visual path, or threshold/config change. Counts 925/1,045 and inventory 722→724 remain review expectations subject to actual audit.

Paused for independent plan re-review. No implementation continuation or generation is authorized until APPROVE.
