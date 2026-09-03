# Legacy Cursor configuration — compatibility audit

Historical audit of legacy workspace configuration against the certified
`cursor-autonomous-workflow` plugin cutover. This document records context only;
it does not reopen architecture decisions.

## Current cutover truth

- **Role pins and modes are owner-defined and frozen.** The seven governed
  Salim agents — `flight-supervisor`, `planner-fable`, `reviewer-grok`,
  `implementer-composer`, `implementer-fable`, `implementer-sol`, `advisor-sol` —
  their exact model slugs, foreground dispatch, and readonly frontmatter are not
  open for redesign in this cutover.
- **Strategic Gears Team Rules and installed skills remain in force, with this
  workflow's contract governing role gates.** Project rules such as SG-TR-001
  through SG-TR-009 and installed skills (`project-orientation`,
  `task-standards`, `strict-reviewer`, `sanad`, `muhasib`, `github-flow`, and
  related aliases) stay active and are not edited or duplicated; where their
  role-gate text says to pause for the coordinator, ask a human, or limit plan
  rejection to fixed blocker categories, the `autonomous-operation` rule maps
  that onto the governed gates (`flight-supervisor` is the coordinator; Grok is
  the gate) and never onto a human. Team read, shell, governance-path and MCP
  guards remain in force.
- **Source and installed plugin are intentionally mirrored and certified.** The
  plugin source tree and its installed copy are kept aligned; this report
  describes compatibility, not installation status.
- **`flight-supervisor` owns semantics.** After `/start-autonomous-project`, Sol
  supervises orchestration, attempt tracking, delivery after Grok approval,
  post-merge review, and the next slice — never Fable planning, Grok review,
  Composer-first coding, or Sol self-approval.
- **Only two plugin safety hooks remain.** While `.autonomous-workflow/checkpoint.json`
  exists, hooks deny sibling-project reads, sibling traversal and destructive Git
  commands. They do not parse checkpoint content, certify models, or enforce
  ladders. They are registered through the plugin manifest and, because manifest
  loading was not observed to fire in the certified IDE session, also in
  `~/.cursor/hooks.json`.
- **Pins are applied by the explicit Task `model` argument at dispatch.** Live
  certification of the installed agents showed that IDE Task subagents do not
  apply agent frontmatter `model`: a seat dispatched without the argument ran on
  the caller's model. The start command and the supervisor therefore pass each
  seat's exact slug explicitly on every dispatch. `readonly: true` is configured
  for `planner-fable`, `reviewer-grok` and `advisor-sol` but is not enforced for
  Task subagents in the certified runtime, so reviewer and advisor independence
  rests on the prompt prohibitions in their agent files and on the supervisor's
  candidate-identity verification before and after every review.
- **Global Salim semantic hook bridge is removed.** Unrelated global hooks are
  preserved. `tools/global_hook_filter.py` supports filtering the legacy semantic
  bridge without touching other hook families.

## Coexistence with `sg-delivery-core`

The Strategic Gears team plugin is active in every workspace and is left in
force. Three interactions are resolved narrowly:

| Interaction | Resolution |
| --- | --- |
| `guard-governance.py` denies `Write`/`Delete` on any path containing `/.cursor/` | The checkpoint and plan artifacts live at `.autonomous-workflow/`, never under `.cursor/`. |
| `guard-governance.py` denies writes under `/.github/workflows/` | Owner-authorized narrow exemption: the guard permits writes under `<project>/.github/workflows/` only when that project root contains `.autonomous-workflow/checkpoint.json`. All other governance paths stay protected. |
| `guard-shell.py` denies `git push` text containing `main`, `master` or `prod*` | Slice branches never contain those words; bootstrap uses `gh repo create --push` or `git push -u origin HEAD`. |

The team plugin's `planner` (claude-fable-5) and `implementer` (cursor-grok-4.6)
agents coexist in the Agent picker but are never dispatched by this workflow.

## Categories

| Category | Meaning |
| --- | --- |
| `KEEP` | Still correct and actively relied on by the plugin. |
| `REPLACE` | Superseded by a plugin component. Same intent, new implementation. |
| `CONFLICT` | Directly contradicts the plugin. Cannot remain authoritative alongside it. |
| `HISTORICAL` | Recorded for cutover context; not an open decision. |

---

## 1. Legacy workspace subagents — `.cursor/agents/`

The eight legacy agents describe the earlier V2 flow where Grok
planned/implemented and Sol reviewed. The plugin inverts that: Grok is the sole
approving reviewer; Sol is the final implementation seat and the supervisor.

| File | Category | Note |
| --- | --- | --- |
| `implementer.md` | `CONFLICT` | Grok as planner/implementer conflicts with plugin pins. |
| `plan-reviewer.md` | `CONFLICT` | Sol plan gate conflicts with `reviewer-grok`. |
| `implementation-reviewer.md` | `CONFLICT` | Sol implementation gate conflicts with Grok-only approval. |
| `arbiter.md` | `REPLACE` | Superseded by `advisor-sol` with hard one-ruling limits. |
| `baseline-architect.md` | `REPLACE` | Superseded by onboarding planner/reviewer reads. |
| `fable-rescue.md` | `REPLACE` | Superseded by the fixed eight-step implementation ladder. |
| `fable-final-reviewer.md` | `REPLACE` | Superseded by single `reviewer-grok` approval path. |
| `sol-rescue.md` | `REPLACE` | Superseded by `implementer-sol` at ladder positions 7 and 8. |

These legacy agents must not remain authoritative once the plugin workflow is
active. Name collisions with plugin agents are absent, but both sets would still
appear in the Agent picker if legacy copies stay enabled.

## 2. Legacy workspace rules — `.cursor/rules/`

| File | Category | Note |
| --- | --- | --- |
| `salim-controller.mdc` | `CONFLICT` | Legacy orchestrator routing conflicts with `flight-supervisor`. |
| `autonomous-execution.mdc` | `CONFLICT` | V2 sequence and alternate gate mechanics conflict with plugin law. |
| `severity-taxonomy.mdc` | `CONFLICT` | Severity labels may be kept; gate mechanics differ. |
| `task-expertise-discovery.mdc` | `REPLACE` | Substantively covered by `autonomous-operation.mdc` plus `autonomous-delivery`. |
| `critical-path-foreground.mdc` | `HISTORICAL` | Redundant once every plugin agent is foreground; not a conflict. |

Strategic Gears Team Rules at workspace or user scope are **not** candidates for
removal as part of this cutover.

## 3. Installed skills — `.cursor/skills/` and user scope

| Skill | Category | Note |
| --- | --- | --- |
| `project-orientation` | `KEEP` | Required by planner and reviewer seats. |
| `task-standards` | `KEEP` | Required by all implementation seats. |
| `strict-reviewer` | `KEEP` | Review rigor for `reviewer-grok`; the Grok gate itself is defined by the plugin. |
| `sanad` | `KEEP` | Required by every seat. |
| `muhasib` | `KEEP` | Required by every seat. |
| `github-flow` | `KEEP` | Delivery sequence; its "coordinator" is `flight-supervisor` in this workflow. |

The plugin bundles exactly one skill (`autonomous-delivery`) and recreates none of
the installed skills above. Tests assert that separation.

## 4. Readonly frontmatter — resolved owner policy

`planner-fable`, `reviewer-grok`, and `advisor-sol` use `readonly: true` in the
certified plugin. That choice is owner-defined, not an open compatibility
question. Reviewer independence is enforced structurally by role separation,
work-unit scoping, and candidate identity — not by re-litigating readonly flags
in this report.

## 5. Commands and hooks

| Surface | Category | Note |
| --- | --- | --- |
| `/start-autonomous-project` | `REPLACE` | Provided by the plugin command; launches one fresh foreground supervisor Task and relaunches a fresh one on abnormal return, bounded. |
| Project hooks | `HISTORICAL` | Plugin supplies the first project hook config for this workflow; only two safety events remain. |

## 6. Duplicate configuration at user scope

The same legacy rule and agent filenames may exist under `~/.cursor/`. Project
subagents out-rank user subagents of the same name, but always-applied rules
from both scopes load together. Cutover planning must account for user-scope
duplicates explicitly; this report records the risk without prescribing user-scope
edits here.

## 7. Skill availability

`sanad-provenance` and `muhasabah-gate` aliases are available under user skill
paths in the current runtime. Plugin safety hooks do not validate skill opens;
required installed skills remain discoverable through normal Cursor skill loading.

## 8. Certified cutover sequence

1. Certify the plugin against a disposable docs-only project using the source and
   installed mirrored copies.
2. Enable the plugin workflow via `/start-autonomous-project` and `flight-supervisor`.
3. Resolve legacy `CONFLICT` agents and rules in the target workspace so only the
   plugin workforce remains authoritative for autonomous delivery.
4. Remove the global Salim semantic hook bridge while preserving unrelated hooks;
   register only the two non-semantic safety hooks globally.
5. Continue with supervisor-owned slices; Strategic Gears rules and installed
   skills remain in force, with role-gate clauses mapped onto the governed gates
   by the `autonomous-operation` rule.
