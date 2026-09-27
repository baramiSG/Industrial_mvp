# Targeted re-review of Codex's PLAN v3.1 — bounded corrections to PLAN v3 (B1, B2, P-a…P-e)

Reviewer: Claude Code (independent reviewer seat). Date: 2026-09-25. Read-only: no repository, worktree, index, candidate, generator, Aura or Git change; probes were reads of the isolated `ce407db` checkout, the two packet directories and three public nomenclature pages. Scope, as requested by the owner and as I bound it in the v3 review: **only the four changed files and the reissued checksum list**, judged against B1, B2 and P-a…P-e. Accepted v3 design and the twelve implementation-time CARRY items are not reopened.

**Review subject (bound by hash):** packet `/home/barami/.cache/industrial-opportunity-resolution-mvp/ministry-decision-plan-v3-1-20260925/packet/` —
- `PLAN-v3.md` `f88287e2f71e54f6ac91ec4635edb1138fb17a160ff59c38e26a396e472868d8`
- `REGISTER-FIXTURE-AND-MAPPINGS.md` `ce9f000e4e4471744f1865d10bb616d975e0e48ff106a38ee9ec8645d35fa886`
- `DOMAIN-CONTRACT.md` `c9e1aac2ce11b379ac023d9fc7219ec39dfbfa4bc5329d6919479df0c31afe8d`
- `INTERACTION-DESIGN.md` `ef155233864c1667fa41f30bf3f11b48f22a609f44107b3e14e2b2c6347506a5`
- `SHA256SUMS` `ca55d71e1d7afdab8a56e2c91eea7319ce39e884c7932e15a66ceb985b263f12` (`sha256sum -c`: 36 OK, 0 failed)
- every other packet file, `notes/**` and `sources/**`: byte-identical to hash-bound v3 (`diff -rq` of the two packet, notes and sources directories lists exactly the four files above plus SHA256SUMS; the SHA256SUMS diff changes exactly those four lines). The original v3 packet still verifies 36/36 with `PLAN-v3.md` `b312a9ad…f925c` and `SHA256SUMS` `7fcf7840…6549`.

**Controlling authority:** the owner stop recorded 2026-09-25 09:14:50 UTC (`S19-OWNER-STOP-HANDOFF-20260925.md`), which v3.1's header now cites correctly. This review authorises no implementation and no S19 resumption.

---

## Verdict: APPROVE PLAN v3.1 as the reviewed plan. B1 and B2 are resolved; P-a…P-e are resolved. Plan approval remains distinct from implementation approval, which waits on the gates in §4.

Plainly:

1. **B1 is closed the right way.** Customs matching now keys on revision-qualified six-digit identity in finite admitted sets (`(H6,790111)`, `(H6,790112)` for steel zinc input; `(H6,290122)` for propylene), with flow, re-export, window, subject and attribution predicates; the free-text `description` is stored but explicitly excluded from selector admission, and any legacy `description_tag` or authored `equipment_class` input fails unknown-key validation. Equipment acquisition (optional) is derived only from an admitted code **and** an independently source-linked technical declaration, encoded as a `reason_code` with `REVIEWED_INFERENCE`/P04 origin — no new finding key, no crosswalk, no installation inference. The contradiction I flagged ("display text never drives matching" vs a tag selector) is gone, and AC2 now says what a customs mutation must do.
2. **B2 is closed.** Every finding, its reason drawer and the selected-request rail must render four labelled slots — missing field, likely source dataset or confirmation action, affected decision (typed `route_effect`), subject scope — from the validated typed request, with a native `<details>` for concision, a typed `NO_ADDITIONAL_REQUEST` state, and a four-slot DOM omission-negative oracle in both locales. The design is honest that the existing effect text is English-only and must be rendered through the catalogue successor.
3. **P-a…P-e are closed** exactly as required (registry assertion field and Class-D copy; origin badge + P-rule on every finding with "calculation" replaced by REVIEWED_INFERENCE · P09; AC10 rewritten to the six existing tests plus one more real one, 200 % zoom withdrawn; Arabic terms aligned to the catalogue; K via `capability.known` and the legend).
4. **Nothing else moved.** The §6.0/§10.2 amendment text, the register identities, the pins, the F1/F2 content, the estimate, the Aura procedure and the twelve CARRY items are untouched; v3.1 §7 restates the CARRY obligations and the pending P1–P3 prerequisites.

---

## 1. Preparation

Read the four unified diffs in full; the unchanged v3 files were not reread. Re-verified against `ce407db`: `src/ior_mvp/evidence_needs.py:23-44` (`_ROUTE_EFFECTS`, English-only) and `:197-210` (returns `need_code`, `blocked_field`, `route_effect`, `numeric_evsi=NOT_CALCULABLE`, localized text); `config/ui_strings.v1.yaml` keys `need.*` (`:538-542`, AR `:1279ff`), `executive.dataset.*` (`:104-110`, AR `:845-851`), `capability.known` (`:284`, AR `:1025` «التغطية المعروفة K»), `actions.open_dossier` (`:309`, AR `:1050`), `executive.status.satisfied/not_satisfied` (`:130-131`, AR `:871-872`); `static/modules/executive/labels.js:13-16` (`DATASET_IDS`); `browser_tests/test_executive_states.py:158` (`test_unresolved_claim_names_actual_case_wide_needs` exists), plus the six existing tests confirmed in the v3 review. Nomenclature grounded by fetching the three Japan Customs HS 2022 chapter pages the packet cites (chapters 79, 29, 84): 79.01 "Unwrought zinc" → 7901.11 "Containing by weight 99.99 % or more of zinc", 7901.12 "less than 99.99 %", 7901.20 "Zinc alloys"; 29.01 → 2901.22 "Propene (propylene)"; 84.79 → 8479.81 "For treating metal, including electric wire coil-winders"; 84.77 → 8477.20 "Extruders". Personas: evidence-provenance/data-architecture reviewer (B1), bilingual decision-UX reviewer (B2, P-b…P-e), change-control reviewer (file boundary, hashes). Skills in force this session and re-invoked for today's reviews: strict-reviewer, sanad-provenance, al-muhasibi, muhasabah-gate (task-standards, project-orientation loaded at session start). No subagents.

---

## 2. Finding-by-finding disposition

| Finding | v3.1 change (where) | Verified against | Disposition |
|---|---|---|---|
| **B1** tag-keyed customs selectors | REGISTER §1: `FACTORY_CUSTOMS` = `hs_revision,hs6,description,flow,quantity_kt,reexport,transaction_id,equipment_model_id`; `description` "stored display field … explicitly excluded from selector admission"; new optional `EQUIPMENT_TECHNICAL` kind. REGISTER §2: `input_procurement/steel` = `(hs_revision,hs6) ∈ {(H6,790111),(H6,790112)}` ∧ IMPORT ∧ reexport=false ∧ valid subject/window, plant signal only with explicit attribution; PP = `{(H6,290122)}`; `equipment_acquisition` = H6/847981 + same-transaction/model `HOT_DIP_ZINC_COATING`/`STEEL_STRIP` → `P04_GALVANISING_ACQUISITION`; H6/847720 + `EXTRUSION`/`PLASTICS` → `P04_PLASTICS_WORKING_CONTEXT` only (never resin-production R9-S credit). "HS identity and parameter storage": `discovery_items` entries for P03/P04 carry exactly `{item_id,rule_id,record_selectors,hs_revision,admitted_hs6,basis}` with ENGINEERING_DECLARATION origin; four-digit headings can never be `hs6`; no padding/prefix/expansion; other-revision code → NOT_ESTABLISHED with concordance request; missing/invalid six-digit → strict validator failure; valid non-admitted → non-match. Fixture rows: Steel A plant-attributed H6/790111 import; PP A company-only H6/290122; Importer 50 kt H6/721049 target-trade context (correctly *not* an input match). REGISTER §5 "B1/P-a regression matrix". DOMAIN P03/P04 rows and §7.2 rewritten to this contract. PLAN AC2 rewritten. | Code/subheading texts (fetched); `matching_feedstock` still unused; `imported_inputs` counted once; attribution rule unchanged from DISCOVERY; no product-family change; no config; `description_tag`/`equipment_class` now appear only as rejected inputs | **RESOLVED.** The rule now keys on the record's real identity field, transfers to real customs extracts in principle, and AC2's HS mutation is decisive while description mutation is inert. The equipment narrowing (8479.81 also covers coil-winders → negative control; 8477.20 is plastics-working, not polymerisation) is sound and more careful than my illustrative list. |
| **B2** next-evidence triple unbound in UI | INTERACTION §2 "Required next-evidence element, every finding" (four slots; sources: `need.*` + exact `missing_field`/`blocked_field`, `executive.dataset.*` + named dataset/record/field or confirmation action, typed `route_effect`, exact company/plant/line + requirement item; no free-text derivation; "likely" source wording; company-only requests name the missing factory link); native `<details>` per finding, drawer next-action step and rail carry the same request; `action_code=NO_ADDITIONAL_REQUEST` typed state; bilingual example; honest note that `_ROUTE_EFFECTS` is English-only and the catalogue successor must render it. §3 extends the contract to comparison findings and the Q5 rail. §7 "Four-slot DOM oracle" with remove-each-slot omission negatives, restore-between, collapsed-empty fails, scope coverage. PLAN AC10 makes the oracle mandatory. | `evidence_needs.py:197-210` supplies exactly those typed fields; catalogue keys exist in EN/AR; `test_executive_states.py:158` exists | **RESOLVED.** Owner requirement R8 is now a normative UI obligation with a falsifiable oracle. |
| **P-a** "verified" on synthetic registry rows | `operating_status_asserted_by_registry` (Boolean); copy "Registry asserts operating · Class D" / «يفيد السجل بأن المصنع يعمل · الفئة د»; fixture rows "registry-asserted"; §5 extends `test_every_synthetic_row_is_labeled` with EN/AR negatives (no verified/observed/official incl. «مُتحقق منه/مرصود/رسمي»); PLAN M1 "source-linked factory parent" | AGENTS non-negotiable 2; `tests/test_synthetic_isolation.py:91` | **RESOLVED.** |
| **P-b** origin vocabulary on findings | INTERACTION §2 mock "57.5092 kt / P09 inference"; new paragraph: origin badge + P01–P09 rule ID on every finding row and drawer conclusion; input-origin separation (DIRECT_RECORD input keeps its origin); width = REVIEWED_INFERENCE · P06 | DOMAIN §3 closed vocabulary (unchanged) | **RESOLVED.** |
| **P-c** AC10 / test naming / zoom | INTERACTION §7 table of seven existing tests to extend (the six I named + `test_executive_states.py::test_unresolved_claim_names_actual_case_wide_needs`), proposed bodies kept separate, `test_executive_candidate_zoom_keyboard` → `test_executive_candidate_keyboard_focus` with existing `aria-live="polite"`; "Withdraw the unbound 200 % browser-zoom promise"; PLAN AC10 rewritten accordingly | all seven names exist at `ce407db`; `render.js:29` aria-live | **RESOLVED.** |
| **P-d** Arabic terms | «افتح ملف القرار» via `actions.open_dossier`; «متحقق/غير متحقق» per catalogue, wireframe variant explicitly subordinated | `ui_strings.v1.yaml:1050,:871-872` | **RESOLVED.** |
| **P-e** K label | Comparison table splits "Effort basis" from "Known coverage K"; "Render K through existing `capability.known` … and its existing capability legend, never bare K1/K0 or an accuracy percentage" | `ui_strings.v1.yaml:284/:1025` | **RESOLVED.** |

---

## 3. Boundary and regression check of the reissue

- **File boundary honoured:** exactly the four files I named, plus SHA256SUMS; filenames retained for diffability; v3 preserved; notes/sources untouched. PLAN §7 states the boundary, the v3 hashes, my review hash (`e3d8301b…d234`) and that unchanged v3 records (incl. `PACKET-CHECKS.json`, `OWNER-DECISIONS.md`) do not certify the reissue.
- **No design regression:** DOMAIN §2 amendment text, §3 origins, §4 rules other than P03/P04, §5 outputs, §6 comparator, fixture identities and ceilings, R9-S adapter rules, engine-feed ledger, Aura procedure, pins, estimate — unchanged. DISCOVERY-GRAPH-CONTRACT (unchanged) already delegates fact payloads/selectors to REGISTER and lists "optional engineering/certificate records", so `EQUIPMENT_TECHNICAL` fits without contradiction.
- **Authority accuracy:** the header now names the 09:14:50 stop as controlling and withdraws the "finish S19 and stop" scheduling language; consistent with my S19 addendum review of today.
- **One cross-reference the implementer must carry:** my S19 addendum review (`s19-completion-addendum-review-20260925.md`, `9b83fef2…32b3`) requires a bounded `dossier.py` correction and a replacement generation before S19 delivery. The delivered S19 base will therefore differ from the retained worktree in `dossier.py`, graph/manifest identities, canonical images and pins; R0 reconciliation of this plan must bind those actual values — the plan already says so in principle (§3 R0, AUTHORITY-AND-PINS §4).

---

## 4. Implementation-start gates (unchanged; restated so approval is not misread)

1. S19 delivered to `main` per the approved completion path (currently STOPPED; resumption needs the owner decisions in the addendum review).
2. R0 reconciliation against the actual delivered S19 tree; material deltas → targeted review.
3. P1 recorded against **v3.1 hashes**, with the ruling text referring to revision-qualified HS6 sets, not to "tags" (the historical `OWNER-DECISIONS.md` draft predates B1); P2 after reconciliation; P3 only if preflight requires.
4. External workflow authority located or explicitly superseded (AGENTS.md; also flagged in the S19 review).
5. Separate exact-tree implementation review and owner implementation acceptance before staging/PR/merge.

---

## 5. CARRY (unchanged twelve from the v3 review, plus three notes; none blocks)

The twelve items in v3 review §6 remain as restated in v3.1 §7. Additional notes:
- **N1** In the `basis` of each `admitted_hs6` entry, name the nomenclature edition as WCO HS 2022 (the Japan Customs pages are a national reproduction of the six-digit texts; verified today to match) — provenance wording only.
- **N2** The v3.1 directory's `README.md` is the byte-identical v3 README by design; PLAN §7 is the reissue's identity statement. Fine, but a future v3.2 (if ever) should not accumulate a stale README.
- **N3** Comparison table "Known coverage K — B: Existing typed value": render the engine's typed value (B declares all nine states, so K should be 1.0 by the unchanged formula); do not hard-code.

---

## 6. Sources (Sanad)

Packet v3.1 (hashes in header): full unified diffs of `PLAN-v3.md` (header, §3 M1, AC2, AC10, new §7), `REGISTER-FIXTURE-AND-MAPPINGS.md` (§1 table/paragraphs, §2 table + three new blocks + attribution + nomenclature paragraph, §3 fixture rows, §5 matrix), `DOMAIN-CONTRACT.md` (P03/P04 rows, §7.2), `INTERACTION-DESIGN.md` (§2 mock + three new paragraphs, §3 table/paragraph, §3 addendum, §5 open-dossier, §7 rewrite); `SHA256SUMS` diff (four lines). Packet v3: unchanged files as hash-bound on 2026-09-25 (`7fcf7840…6549`). Checkout `ce407db`: `src/ior_mvp/evidence_needs.py:23-44,:197-210`; `config/ui_strings.v1.yaml:104-110,:130-131,:284,:309,:538-542,:845-851,:871-872,:1025,:1050,:1279ff`; `src/ior_mvp/static/modules/executive/labels.js:13-16`, `render.js:29`; `browser_tests/test_executive_states.py:158`; earlier-verified `browser_tests/test_executive_accessibility.py:14,:33,:47`, `test_executive_races.py:50`, `test_graph.py:482`, `test_dossier.py:223`; `tests/test_synthetic_isolation.py:91`. External (WebFetch, read-only, 2026-09-25): `customs.go.jp/english/tariff/2022_1_1/data/e_79.htm`, `e_29.htm`, `e_84.htm` (texts quoted in §1). Prior reviews: v3 review `e3d8301b…d234`; S19 addendum review `9b83fef2…32b3`; owner-stop handoff `1ce621b5…f310c`.

## 7. Self-audit (al-Muhasibi; Muhasabah gate)

**Khawatir.** First instinct: "every item is ticked, approve on the diff summary." Second: "find something new to show rigour." Both rejected: the first skips verifying that the referenced code/catalogue facts exist; the second would breach the targeted-review boundary I set myself.

**Muraqaba.** Watched for: (i) approving a fix that merely renamed the tag (checked — the selector is the six-digit code set, the tag is rejected as input, and AC2's decisive mutation is on `hs6`); (ii) accepting nomenclature by assertion (fetched the three pages); (iii) accepting test names by assertion (grepped); (iv) reopening accepted design under the guise of "notes" (the three notes are wording-level and marked non-blocking).

**Mujahada.** Verified hashes, 36/36 both packets, the exact file boundary by directory diff, every diff hunk, the code lines and catalogue keys the design relies on, the existence of all seven existing tests, the four subheading texts, and the absence of residual tag/verified wording outside negative controls.

**Muhasaba (gate).** Provenance — every statement carries a diff hunk, file:line, hash or fetched text: PASS. Assumptions — the fetched national tariff pages reproduce the WCO six-digit texts (they matched the headings I verified from WCO texts in v2; stated as N1): PASS. Fabrication — none; no test executed, no product claim: PASS. Requirements — targeted scope honoured; each of B1/B2/P-a…P-e dispositioned with evidence; CARRY preserved; hashes bound; review saved: PASS. Risk — read-only; approval of a plan, explicitly not of implementation or S19 resumption: PASS.

**Final.** APPROVE PLAN v3.1. What would change it: evidence that a v3.1 file differs from the bound hashes, or an owner instruction altering the settled scope.
