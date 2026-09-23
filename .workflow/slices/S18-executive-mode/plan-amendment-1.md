# S18a PLAN v1 — Amendment 1: provenance closure and simulated claim evidence

Status: owner-proposed amendment for independent plan re-review; implementation continuation is not authorized until APPROVE.

Parent plan SHA-256: `1b300b0f05fcb7b658f6df95d1c8022ad179554106a1a77d70fbd72704cf017f`. Amendment precedence: AM-1 > PLAN v1 where they differ. All other plan obligations remain.

## Trigger and evidence

The retained implementation child completed pre-generation source/tests and exposed two previously omitted dependency contracts:

1. `graph.projection.discover_inputs()` hashes every `docs/core/*.md` and selected top-level engine files. Required S18a Core edits therefore produce new write-once identity `GRAPH-SAU-2026-09-12-a87b670a1dad` at unchanged 925 nodes / 1,045 edges. Graph reconstruction correctly rejects the old current pointer.
2. The visual manifest source tree hashes top-level `app.py`, graph current/projection files and manifests. The required executive API mount and new graph pointer therefore require a canonical provenance refresh even though S18a adds no UI/static/browser behavior.

The full suite has 2,932 passes and seven failures confined to these guards. Integrity separately reports the five expected pending Core hashes. Tests must not be weakened.

Owner source inspection also found two claim-provenance gaps before generation:

- `_rule_evidence()` names nonexistent generic `R4` and omits actual `R1-F`, `R4-F`, `R4-D`, causing stored trade evidence to be reported unresolved; it also over-links `R10` to unrelated product evidence.
- `build_claim_registry(public)` supplies only public claims. Simulated evidence is present in `evidence_index`, but simulated decision/step/intervention claims do not link the Class-D rows that support them.

## Amended generated scope

S18a now owns this exact order after source correction and focused GREEN:

1. One graph generation through the existing builder. Require literal in-memory identity `GRAPH-SAU-2026-09-12-a87b670a1dad`, 925/1,045, old `b63159c7bdc1` projection byte-identical and retained, and no graph semantic/count change beyond input/projection identity.
2. One `scripts/build_manifests.py` run. Expected snapshot inventory 722 → 724: two new projection files, existing current-pointer row changed, every prior projection row retained. Authority remains 20 rows with changed hashes confined to Core 01/02/04/07/09. Audit actual bytes; do not force counts.
3. Immediate integrity, reconstruction and graph build-check. Rebuilt graph identity must remain `a87b670a1dad` after manifest generation.
4. One canonical visual refresh with `IOR_BASELINE_CHANGE_REF=S18A-EXECUTIVE-API-PROVENANCE-1`. Expect all 112 WebPs byte-identical, zero path/count/dimension change and source-provenance updates only. Any WebP difference stops for owner adjudication.
5. Compute the exact new `browser_tests/baselines` tree OID through a separate alternate index; change only its frozen pin. Entry count stays 112.

Allowed new/changed generated paths:

- `data/graph/current.json`;
- `data/graph/projections/GRAPH-SAU-2026-09-12-a87b670a1dad/{projection.json,manifest.json}`;
- `data/manifests/snapshot_manifest.json`;
- `docs/authority/authority_hashes.json`;
- generated table in `docs/authority/00_AUTHORITY_MANIFEST.md`;
- `browser_tests/baselines/v0.3.0/{manifest.json,manifest.sha256}`;
- `tests/test_frozen_public_evidence_pins.py` exact visual-tree literal.

No WebP path is allowed to change if the expected byte-equality proof passes. No Aura load/clear/refresh is authorized. Local/CI graph gates load the new projection into fresh owned mirrors.

## Amended claim contract

### Public rule mapping

Use exact rule IDs:

- product identity: `R0`;
- trade: `R1-F`, `R1-D`, `R2`, `R3`, `R4-F`, `R4-D`, `R5`;
- supply/capability: `R9-S`;
- generic-capacity control: `R11`;
- structured needs: `R12`;
- no stored-support fallback: `R6`, `R7`, `R8`, `R10` remain `UNRESOLVED` unless their exact delivered evidence support exists.

Never substitute an unrelated product passport for criticality (`R10`) or a disabled simulated rule.

### Simulated claims

Extend `ClaimReference` with explicit branch metadata. Public claims prohibit synthetic metadata/evidence. Simulated claims that use Class-D rows require `branch=SIMULATED`, `synthetic_flag=true`, scenario ID, Class D, `DEMO_GENERATOR` and both policy labels; they may also retain public evidence IDs used by the counterfactual.

Add deterministic simulated claim IDs:

- `decision.simulated`;
- `step.SIMULATED_EVIDENCE.simulated`;
- `step.ROUTE_COMPARISON.simulated`;
- `step.INTERVENTION.simulated`;
- `step.CONDITIONS_AND_KILL.simulated`.

Map exact synthetic support suffixes:

- simulated evidence: all current-scenario synthetic rows;
- route comparison: `route_evidence`, `counterfactual`, `hard_exclusion_inputs`, `class_if_confirmed`;
- intervention: `economics`, `evsi`, `route_evidence`, `counterfactual`;
- conditions/kill and decision: current-scenario rows used by the simulated decision, plus relevant public claim evidence.

Executive simulated step values carry those exact evidence IDs. Cross-scenario IDs and synthetic rows in public claims fail closed.

`models.py` must remain at most 500 lines. If branch validation would exceed that boundary, create `src/ior_mvp/executive/provenance_models.py` and keep model responsibilities acyclic; do not compress unreadably to evade the limit.

## Additional TDD obligations

Before generation:

1. RED/GREEN exact evidence links for `R1-F`, `R4-F`, `R4-D`; R10 must be unresolved with no unrelated evidence.
2. RED/GREEN simulated claim metadata and exact synthetic evidence IDs for steel decision, simulated-evidence, route-comparison and intervention steps.
3. Negative tests: synthetic evidence in a public claim; wrong scenario; missing Class-D/source/labels; cross-scenario evidence; absent referenced ID.
4. All eleven public claims reference only public rows; all eleven simulated claim sets use only their current scenario's Class-D rows plus valid public rows.
5. Model and source file line limits remain compliant.

After generation, run original Task 8 plus graph validation/build-check and visual compare. Final verification/portability roots each run complete `make ci` against fresh isolated graph containers/credentials. The candidate remains unstaged/uncommitted for independent implementation review.

## Authority/control updates

Amend ADR-028, S18 roadmap/progress/traceability and Core 09 to state that S18a graph/visual changes are provenance closure only: graph semantics/counts and every WebP remain unchanged. Do not claim generated results before observing them.

## Non-goals unchanged

No S18b route/HTML/JS/CSS/catalogue/browser journey/new visual path; no scenario/data/golden change; no new graph node/edge semantics; no Aura operation; no approval workflow; no EVSI dataset inference.

Paused for independent plan re-review. No correction, generation, staging, commit, push or PR is authorized by this amendment.
