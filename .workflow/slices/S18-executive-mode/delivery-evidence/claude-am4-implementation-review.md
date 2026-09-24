# S18a exact-tree implementation review of `1364789a964f96f6ebabf8eae1d239a5bad0b15e`: **APPROVE**

## Preparation
- **Read:**
  - AGENTS.md and the approved AM-4 packet (plan `60f516f7…`, handoff `39d97eb0…`, `SHA256SUMS` `63ca77a2…`);
  - the owner record, including its `am4`, `am4_implementer_substitution` and `am4_test_fixture_resumption` entries;
  - the AM-4 stop report and fixture patch;
  - the full source, test and document diff from the rejected tree `2ab8d401`;
  - the implementation receipt directory, whose 856 checksums all verify.
- **Personas:**
  - an API-contract engineer, for B1 and INTERVENTION;
  - an evidence-provenance engineer, for B2 and B3;
  - a release-verification auditor, for tree identity, gates and the probe.
- **Skills invoked:** `strict-reviewer`, `sanad-provenance`, `muhasabah-gate`.

**Who implemented AM-4:** your message says Cascade, but the owner record and evidence show the owner reassigned AM-4 to a **Codex** session and recorded that Cascade was stopped. Everything below reviews that implementation.

## Candidate identity and scope (verified)
- **Tree identity:** the worktree equals `1364789a`, with nothing extra.
- **Scope:** the delta from `2ab8d401` is exactly AM-4's allowed set: the three executive source files, the three executive tests, the four control documents, the new `plan-amendment-4.md` (`60f516f7…`, byte-identical to the approved plan) and the recorded `plan_review.md` entry. That entry is 36 lines, unchanged since Codex recorded it.
- **Nothing else moved:**
  - frozen roots, config, graph, manifests, `docs/core` and the static sources are identical to the rejected tree;
  - visual manifest `216aa8e0…`, baseline tree `dfb2612b…`;
  - HEAD `564b1b7`, 0 staged, and all four indexes unchanged (`460778ca`, `93a57693`, `961805cb`, `8f6b047b`).

## Findings resolved (my own checks against the live candidate)
| Finding | Fix | My verification |
|---|---|---|
| B1 | A present `None` becomes a typed null whatever the route statuses. A mapping code must be `type(...) is int`, 0-8 and declared | All 11 cases return 200 over the API. The eight former failures show `preferred_route_code` as `NOT_CALCULABLE`/null. The test covers `True`, `False`, `"5"`, `5.0`, -1, 9, null, undeclared 7 (route removed), wrong types and a missing key, all expecting 422. Mixed `fails`/`NOT_CALCULABLE` with `None` returns 200 while polypropylene keeps real route 0 |
| B2 | One `_linked_claim_status` helper used by both branches | Steel `decision.simulated` and `step.CONDITIONS_AND_KILL.simulated` are CONTRADICTED; the other simulated claims stay SUPPORTED |
| B3 | Suffix exemption removed. IDs are checked by location, against the graph feed, dependent scenario declarations and stored evidence. Allowance only at route 8's two exact paths | Rejected: `ANY-UNRELATED::shared_enabler`, `…::other_suffix`, a real foreign ID in route 0, and forged dependents. Both aluminium cases build, with zero foreign IDs in their claims. The test covers 9 mutation types |
| INTERVENTION | Five `simulated_` keys; only `step.INTERVENTION.simulated` attached | Confirmed for all 11 cases |
| Invented need | The default is removed and the case fails closed | Confirmed in `claims.py`; negative and real-need tests present |
| D1 | Stable wording: "R1 EXACT TREE REJECTED; AM-4 EXACT-TREE VERIFICATION GATED" | Accurate. It records that the rejected R1 tree passed and was then rejected, states the AM-4 gate requirement, and points to an external receipt. The tree's own ID appears nowhere in its contents |

**Test changes:** the only removed assertions are the old INTERVENTION key names and claim expectations, replaced in line with AM-4. Nothing was weakened.

## Gates on `1364789a` (from the retained evidence)
- **Task 8:** all 16 commands exit 0 against tree `1364789a`, including 3,027 pytest and the all-11 outcome check (`ALL11_OUTCOMES_AND_REAL_DECISION_EQUALITY_PASS`).
- **`make e2e` compare-only:** exit 0, clean before and after, at `1364789a`.
- **R1 probe (re-derived by me):**
  - byte-identical R1 scripts (`f4644f0e…`, `afa84a5e…`), run in pinned image `938b534c…` with the network disabled;
  - both producer identities in all 12 files;
  - old tree `37390c9a`, new tree `1364789a`;
  - 12/5 rows, section boxes equal, old-repeat equals old;
  - zero violations in the unmodified DOM and in the rewrite control, in both locales, with exactly 5 of 61 text nodes rewritten.
- **`make ci` in two clean roots:** each exits 0 with separate compose projects and fresh graph containers:
  - 3,027 pytest, 513 functional, 4 visual;
  - graph load 925/1,045, reload 0/0, verify passing;
  - integrity, scenarios (11), every reconstruction stage and smoke passing;
  - `tree_after` = `1364789a`.

## Nonblocking observations
1. **Procedural deviation, reviewed now.** The mid-run fixture correction was authorized directly by the owner, not through AM-4 §4.3's planning-and-review path. It changed a newly written test to use `.get("unsupported_npv_m")`, because polypropylene's economics legitimately lack that field. The null comparison still means something. It fixes a test bug and weakens nothing. I accept it after the fact.
2. **Independence.** For AM-4, Codex both planned and implemented, on the owner's record. My independent review and the owner's acceptance are what keep this independent; I found no self-approval.
3. **One untyped path.** `scenario.get("synthetic_inputs", {}).get(...)` would raise an untyped error if `synthetic_inputs` weren't a mapping. Upstream scenario validation prevents that today.
4. **Receipt not in the repository.** The committed documents point to a local, untracked receipt path. The post-merge delivery record should publish the receipt's hash so others can verify it.
5. **Deferred items still open.** AM-4 §5's deferred items remain: case-level EVSI availability, untyped malformed-input paths, model partition checks and test gaps. Track them for S18b or a follow-up.

## Status
- **Approved:** exact tree `1364789a964f96f6ebabf8eae1d239a5bad0b15e`, with zero blocking findings.
- **Next steps:**
  1. The owner's separate implementation acceptance of this exact tree.
  2. Only then ordinary staging and commit of exactly this tree on `slice/s18-executive-mode`, then PR, hosted CI and merge.
  3. Post-merge delivery records, including the receipt hash.
- **Not authorized by this verdict:** anything that would change the tree. Any change needs a rebuild and the full gate set again.

## Self-audit (muhasabah gate: pass)
- **Checked myself:**
  - identity, scope and preservation: `git hash-object` and `rev-parse` of the tree, plus index hashes;
  - behaviour: my own TestClient runs and injection tests on the live worktree;
  - the probe: re-derived from the raw JSON;
  - gate results: the result JSON and log files, each bound to `1364789a`.
- **Agent- or receipt-reported only:** I didn't re-run pytest or `make ci`; those counts come from the retained logs, whose tree identity I confirmed. The True/False coverage comes from reading the test source. My direct `build_steps` call failed on its signature, so the test suite's pass is the evidence there.
- **Changes made:** read-only.