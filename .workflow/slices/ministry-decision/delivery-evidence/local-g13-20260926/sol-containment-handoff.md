# G1.3 scoped containment recovery handoff

**Status: PAUSE.** Sole implementer work is complete for the approved section A correction. Independent Claude implementation review and root release operations remain pending. This is not an implementation approval.

## Exact source change

The task-only patch is [TASK-ONLY.diff](TASK-ONLY.diff). Against the original [SOURCE-BEFORE.json](/home/barami/projects/industrial-opportunity-resolution-mvp/.autonomous-workflow/mission-20260925/ministry-decision/codex-cli-g1-scoped-containment/SOURCE-BEFORE.json) and immutable proof, exactly two files changed: `browser_tests/graph_pages.py` and `browser_tests/test_graph.py`. The helper recognizes only a direct `.graph-details > .card-body-scroll > table.graph-source-table`, checks count and native region semantics, RTL-aware reachable scroll extent, cell/text parent bounds, and retains the original panel/document checks for all other content. The existing steel 390 EN/AR browser body adds nine reversible mutations per locale, each rejected by the helper and followed by an exact restored-good check. No named browser test was added.

[SOURCE-AUDIT.json](SOURCE-AUDIT.json) records the original/current SHA-256 values, 1,338 audited repository files, with no secret-named source files read, equal untouched top-level Python AST, unchanged bound product/data/manifest hashes, ordinary index `770d3e296985bb61b52211fd365a2b0cad96e8faf512949dfb57f236eb54eaf5`, PID 34210 start 79799 and lock inode 2358670. No credential contents were read or hashed in this audit.

## Actual checks

The original focused Docker container `a6e79caa9922…` survived the CLI provider failure. Root's read-only [FOCUSED-RUN-RECOVERY.json](/home/barami/projects/industrial-opportunity-resolution-mvp/.autonomous-workflow/mission-20260925/ministry-decision/codex-cli-g1-scoped-containment/FOCUSED-RUN-RECOVERY.json) reports browser exit 0; [RECOVERED-BROWSER.stdout](/home/barami/projects/industrial-opportunity-resolution-mvp/.autonomous-workflow/mission-20260925/ministry-decision/codex-cli-g1-scoped-containment/RECOVERED-BROWSER.stdout) reports **18 passed in 462.04s** under the immutable [COMMAND.json](/home/barami/projects/industrial-opportunity-resolution-mvp/.autonomous-workflow/mission-20260925/ministry-decision/codex-cli-g1-scoped-containment/COMMAND.json) image `sha256:938b534c8bac0f80012299fc0bba33c00d29f2ade02416bbc1df9d9c028f8112`, no network. [run-summary-functional.json](/home/barami/projects/industrial-opportunity-resolution-mvp/.autonomous-workflow/mission-20260925/ministry-decision/codex-cli-g1-scoped-containment/browser-artifacts/run-summary-functional.json) confirms 18 collected, 18 passed, zero failed/skipped: 12 panel variants (steel/aluminium × 390/1024/1440 × EN/AR), 4 native endpoint variants (public/simulated × EN/AR), and 2 all-view narrow-panel variants (EN/AR). The native Tab/focus-visible, ArrowLeft/ArrowRight endpoint-and-return, same-focus and axe assertions remain in the four keyboard cases. The steel 390 cases execute the nine negative mutations in both locales.

Three targeted pure-Python contracts passed in 0.51s: exact 96-name browser inventory, bilingual named/focusable scoped table rendering, and fixed four-view fixture coverage. Exact command and receipts are in [CHECKS.json](CHECKS.json).

The earlier CLI EXIT1/provider error receipt was preserved. The prior full browser run belongs to root and is separate; this handoff makes no claim about its final classification or the later stock capture, graph retry, publication, CI or Aura. Root owns those steps, including actual baseline pin and independent Claude review.

**PAUSE.**
