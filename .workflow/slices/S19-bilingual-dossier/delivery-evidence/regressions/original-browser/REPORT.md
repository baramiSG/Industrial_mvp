# S19 original browser defects — frozen delivered tree, RED only

**Result:** Both AR-V01 and TRADE-SCALE-01 reproduce against the unchanged delivered S18b source. The final diagnostic exits **1** because its 24 explicit original-defect assertions fail. This is expected RED evidence, **not** a PASS or S19 GREEN. The product writer owns correction and repeat proof.

## Bound source, tool, and scope

- Actual S19 base: main `ce407db9832b61c5a8a85dfda2e3b7623da2fbc9`, tree `789577cbd16cec9cd6c260b5e98a5eac0ae83c20` (owner actual-base acceptance). The clean frozen reference `/home/barami/projects/ior-worktrees/s18b` is head `1afd1715ed1e104c57469ada7dc4a4d23deaf18d` with the **same tree**. `git status --porcelain=v1` remained empty after proof. Source was mounted `/workspace:ro`; only this external directory was writable. No S19 source, generated artifact, Git index, service, or retained container was changed.
- Pinned local browser image: `sha256:938b534c8bac0f80012299fc0bba33c00d29f2ade02416bbc1df9d9c028f8112`; Docker `--network=none --read-only --tmpfs /tmp`, user `1000:1000`. The stock `browser_tests.harness.start_app_server`, `pages.goto_portfolio/select_case/open_dossier_popup`, and `executive_pages.goto_executive` drive the actual app. The small task-local [diagnostic](diagnostic.py) adds only explicit defect assertions. [COMMAND.txt](COMMAND.txt) retains the exact final command/redirections; [stdout.txt](stdout.txt), [stderr.txt](stderr.txt), [exit-status.txt](exit-status.txt) retain actual output/status. `stderr.txt` is empty and recorded status is `1`.
- Frozen source SHA-256: `dossier.py` `805bc8abfd94488505717c95ae15ac5ecf52bf73644ea85e6f2a755faf41ae7f`; `dossier.css` `022a5890c25b1605689401db308e73a411af10984ed32b4ee998231c772d6da3`; `renderers/trade.js` `5cd83c05c39014d2aeeff285d51f880e24d0ae8f550b8fa3c19d6b9fea7b0bc2`; `ui_strings.v1.yaml` `589c6eff0d681a6fafbc154c79fdaedfecc83a6af6faadfcce660053a0cf9e35`. They match the pre-run hashes. Diagnostic SHA-256 `e6618aa9755c6e2f7924d1b71cfc1630741e9250e8e349a223ce9ae1e02ceb00`; final [measurements.json](measurements.json) SHA-256 `b90728962a8e34aeaace0a908af68eab0ee02d1c99548b357f7b2a91a3e6a25e`.

## AR-V01 — actual Arabic simulated popup, 1024 × 768

The stock Analyst action opened each dossier at the exact URLs recorded in `measurements.json`:

- steel: `/api/opportunities/SAU-H0-721049/dossier.html?mode=simulated&locale=ar`;
- polypropylene: `/api/opportunities/SAU-H0-390210/dossier.html?mode=simulated&locale=ar`.

`document.fonts.ready` completed (`fontsReady: loaded`). Both pages had `document.documentElement.scrollWidth=1150` against `innerWidth=1024`, an unintended 126 px horizontal overflow. The **initial** RTL scroll position was `scrollX=0`: the text and element boxes measured within the viewport (title right `982`). Those initial observations are retained separately in [attempt3-measurements.json](attempt3-measurements.json); they are **not** mislabeled as initial-viewport clipping. The Playwright viewport screenshot displayed the leftmost horizontal crop. To match that captured/user-reachable legal scroll position, the final diagnostic explicitly moved the popup to `scrollX=-(1150-1024)=-126` before measuring and capturing. At that position, both the element box **and actual rendered text Range rects** cross the 1024 px viewport edge:

| Actual target, both cases | Element right | Text Range right, steel | Viewport right |
|---|---:|---:|---:|
| State badge `.state` | 1108 | 1097 | 1024 |
| Full Arabic title `.decision-narrative h1` | 1108 | 1108 | 1024 |
| Opportunity identity `.meta` | 1108 | 1108 | 1024 |
| Arabic policy warning `.warning strong[lang="ar"]` | 1093 | 1093 | 1024 |
| English policy warning `.warning strong[lang="en"]` | 1093 | 1093 | 1024 |
| Right-hand product content `.dossier-grid > .box:first-child` | 1108 | 1089 | 1024 |

Every corresponding leftmost-position assertion failed for **both** steel and PP: 12 AR failures. The DOM still contains the complete case ID and **both exact** policy warnings: `محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة` and `SIMULATED — NOT MINISTRY EVIDENCE`. That is content-preservation evidence, not visibility proof. Screenshots: [steel](ar-1024-steel-simulated-dossier.png), [polypropylene](ar-1024-polypropylene-simulated-dossier.png). Actual text, all element/text rects, `scrollX`, exact URLs, and viewport are in `measurements.json`. This proves inability to keep the required content inside the width at a reachable horizontal position; it does not assert the initial `scrollX=0` position itself was clipped.

Reusable test-body logic for the writer, using the existing popup helper after selecting mode/case, follows. The full `MEASURE` helper and six selectors are in `diagnostic.py`; check each target, not only `scrollWidth` or DOM presence:

```python
popup.evaluate("async () => { await document.fonts.ready; }")
popup.evaluate("window.scrollTo({left: -(document.documentElement.scrollWidth - innerWidth), top: 0, behavior: 'instant'})")
report = popup.evaluate(MEASURE, {"selectors": selectors, "expected": expected})
popup.screenshot(path=str(screenshot_path), full_page=False, animations="disabled")
assert report["fontsReady"] == "loaded"
assert report["scrollWidth"] <= report["viewport"]["width"], "AR-V01 horizontal dossier overflow"
for name, item in report["items"].items():
    assert not item.get("missing"), f"AR-V01 {name}: missing"
    assert item["text"], f"AR-V01 {name}: empty content"
    assert not item["beyondViewport"], f"AR-V01 {name}: clipped rendered text/box {item['box']}"
```

Before applying the final `scrollWidth` assertion as a regression, retain the per-target bounds: a box can be clipped even when root overflow is hidden. The exact warning and identity text assertions in `diagnostic.py` must also remain. The writer should repeat with an initial-position measurement and at the leftmost reachable position to prove the page fits without horizontal scrolling.

## TRADE-SCALE-01 — both actual chart consumers, EN and AR

At the same 1024 × 768 viewport, the actual steel Analyst public and simulated workspaces and Executive `SIGNAL` were opened in both locales. Exact URLs, modes, screenshots, chart text and SVG path counts are in `measurements.json`. Each chart retains two SVG path elements; those existing curves and any existing numeric values are **preservation scope**, not an original-defect failure. No native table or independent-scale interpretation was visible.

For **all six** consumer/locale/mode combinations, two separate assertions fail: the chart card has no exact approved note and no `<details><summary>` equal to the approved native observed-data label. That is 12 TRADE-SCALE-01 failures. `summaryTexts` is `[]` in each record. Approved copy comes from the separately reviewed [trade amendment](../../planning/s19-trade-chart-r2/AMENDMENT.md) Task 1, not a missing catalogue-key lookup:

```python
card = page.locator(".chart-wrap").locator("xpath=ancestor::article[1]")
expected_note = {
    "en": "Each line uses its own scale. Compare trends within a line; heights of the value and quantity lines are not comparable.",
    "ar": "لكل خط مقياس مستقل. قارن الاتجاه داخل كل خط؛ لا يمكن مقارنة ارتفاع خط القيمة بارتفاع خط الكمية.",
}[locale.code]
expected_summary = {"en": "View observed values", "ar": "عرض القيم المرصودة"}[locale.code]
page.evaluate("async () => { await document.fonts.ready; }")
page.screenshot(path=str(screenshot_path), full_page=False, animations="disabled")
assert expected_note in card.inner_text(), "TRADE-SCALE-01: visible independent-scale explanation absent"
assert expected_summary in card.locator("details > summary").all_inner_texts(), "TRADE-SCALE-01: native observed-data control absent"
```

The diagnostic executes both assertions independently to retain both failures; a conventional test may use two named parametrized tests. Screenshots are `en/ar-1024-steel-{public,simulated}-analyst.png` and `en/ar-1024-steel-public-executive-signal.png`. Complete row-value, unit, keyboard, zero/missing, and unchanged-curve GREEN/preservation tests remain the writer's required work under the reviewed amendment; this RED proof makes no claim about those checks.

## Attempts, provenance, and completion audit

`attempt0-*` retains a **setup** failure from a missing Playwright context base URL; it is not counted as defect RED. `attempt1-*` and `attempt2-*` retained genuine chart RED but AR bounds at initial `scrollX=0`, so AR was not claimed. `attempt3-*` used the actual popup and preserved its initial-position bounds. The final command alone supplies the 24 original-defect failures and matched leftmost-position screenshots. The local server stopped in teardown; `docker ps --filter ancestor=<pinned image>` returned no retained container.

Sanad: domain expectation comes from the original methodology DOCX §15, Core03/04/09 and approved S19 plan/design; AR-V01 case/scope from the continuation and prior finding; chart literals and consumer scope from the accepted trade R2 amendment and separate review. Measurements, URLs, screenshots, stdout, source hashes and exit status are direct observations from this run. **Inference:** 126 px horizontal overflow causes the clipping at the user-reachable leftmost RTL position. Assumption: frozen S18b tree identity is equivalent to actual S19 base because both Git tree IDs equal `789577…`; the proof did not execute the mutable S19 worktree.

Requirements: actual two AR simulated cases, fonts-ready text/element bounds and per-case screenshots; actual two chart consumers in both locales, public/simulated Analyst, exact absent note/native control; source hash, exact command/status and no product writes are satisfied. Risks/unverified: the default `scrollX=0` popup bounds do **not** establish default-position clipping; chart numeric equality and native keyboard behavior are not tested here; no corrected S19 GREEN, PDF, full CI, independent approval or product acceptance is claimed. Muhasabah gate: **PASS for bounded original RED evidence**, with these limits explicit. Al-Muhasibi audit resisted treating DOM presence, historical screenshots or initial-position `scrollWidth` as sufficient; final claims follow the actual text bounds and separate assertion failures.
