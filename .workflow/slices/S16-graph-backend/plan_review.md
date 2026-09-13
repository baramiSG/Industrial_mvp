# Plan review — S16 plan-1 (attempt 1)

**Subject:** `.autonomous-workflow/plans/s16-graph-backend/cycle-1/plan-1-s16.json` (SHA-256 `7e888e7a9b04d45579bfe799113a39066d4ea39e274aa2ceb5f573e0770d1b8d`), authored by `planner-fable` against `main` `ab6211f`/`ec859f7`; mirror `plan.md` in this folder. Implementation starts only after both S14 children merge (`M16`).
**Supervisor (owner lead agent) material review — 2026-09-13:** no B1–B7 finding. Independent review by `reviewer-grok` follows; `PLAN_APPROVED` only on its APPROVE.

## Supervisor checks

- B1: single project-owned graph with public and labelled Class-D subgraphs; five provenance properties on 100% of nodes/edges; `scenario_id='PUBLIC'` sentinel and `synthetic_flag=false` filters on real-decision paths (TL-09 10–12); route-8 inputs only from a governed Class-D enabler block (Core 06 §3.5 amendment, Gate B) or passported public evidence — none today, so the public branch keeps `GRAPH_REQUIRED`; route 8 activated (evaluated, precedence-blockable) without weakening any lower route; both goldens and the exact public payload fixture byte-stable; the engine consumes the hashed projection artifact (offline, NFR-004/005) with the live mirror proven equal; Aura writes gated by instance-id confirmation and `--confirm-clear`; tests/CI never see Aura; thresholds 1.3.0 key in governed YAML; one manifest run per child; `config/graph_views.v1.yaml` as a new hashed §7.3 file.
- B2: the planner cited code paths (route-8 hard refusal, selector filter, socket guard, visual pins, payload fixture), official Neo4j pages (constraint editions, compose secrets, `execute_query`, Aura URI, `CALL IN TRANSACTIONS`, APOC subset) and the sanitized Aura evidence; assumptions (5.28.x lock on 3.14; local image + `cypher-shell`; ports; pair ΔNV) are T0 checks.
- B3: exact oracles — `GRAPH RECONSTRUCTION PASS`, two builds identical, Cypher == artifact equality tests per view, provenance null-counts, second load 0/0, `GRAPH_UNAVAILABLE` for five failure classes incl. `docker stop`, route-8 boundary tests and the fixture pair, §9 pinned text, Aura verification counts.
- B4: Manifest §7 — `data/graph/**` (§7.5), `config/graph_views.v1.yaml` and thresholds 1.3.0 (§7.3), Core 03/04/06/07/09 (§7.4); dependency extra `graph` with lock resolution proof; Dockerfile unchanged with a neo4j-free image proof; CI `graph-gates` job with a digest-pinned service container.
- B5: RED-first per task; s16a before s16b; the seam at the visual `source_tree` pins keeps the single regeneration in s16b.
- B6: credentials by name only; ephemeral CI credential; no Aura in tests; loader refuses destructive operations without the instance-scoped flag.
- B7: scope preserved — every PR-S16-12 requirement delivered with supported approaches; §8.3 portfolio outputs beyond scope recorded as KL, not added; no GDS/APOC dependence.

## Owner rulings (`.autonomous-workflow/owner-decisions/20260913-s16-plan-1-rulings.md`)

OD-1…OD-17 ACCEPTED as proposed; the route-8 SELECTION unreachability is accepted as an honest finding and returned to the owner under R-5.

## IAC (transferred to the implementer)

- IAC-1 Isolated worktree; bytecode isolation; no Aura connection outside the recorded operator step; env names only.
- IAC-2 T0 proves the lock resolves offline on 3.12/3.14 (else 6.x with justification and a re-review); the local image and `cypher-shell` presence; ports 7475/7688 free.
- IAC-3 Every graph query the S17 views need is delivered by Cypher 5 or artifact computation with an equality test; nothing silently dropped or added (PR-S16-12).
- IAC-4 Class-D enabler values carry the four synthetic markers and the warning; no enabler value ever reaches a public path (TL-09 extension tests).
- IAC-5 `make ci` incl. the graph gate, portability copy, CI-equivalent scratch clone, canonical identity before hand-off; the Aura verification step is recorded before execution and reported sanitized.

### Independent plan review — `reviewer-grok`, 2026-09-13: APPROVE, no findings — PLAN_APPROVED

Public branch stays `GRAPH_REQUIRED` with the no-candidate payload fixture byte-stable; route 8 activated only from governed Class-D enabler edges (the ALU pair is evaluated then precedence-blocked: foil ΔNV 172 route 6, profiles ΔNV 31 route 4); goldens not rewritten; Aura writes need instance-id confirmation and tests/CI never receive Aura; PR-S16-12 table complete with §8.3 portfolio analytics as a KL; Manifest §7, RED-first s16a → s16b and the visual `source_tree` seam specified. Risk flagged: cached `neo4j` 5.28.4 declares classifiers through 3.13 (`Requires-Python >=3.7`) — T0 must prove the offline lock on 3.12 and 3.14, else 6.x with justification (SC-9). Advisories ADV-1…ADV-11 (loopback-only `graph_tests` env, primitive Neo4j property maps, per-label indexes, §9 pin test, T0 lock proof) are binding implementer IACs. Record: `.autonomous-workflow/evidence/s16-graph-backend/plan-1-review.json`.
