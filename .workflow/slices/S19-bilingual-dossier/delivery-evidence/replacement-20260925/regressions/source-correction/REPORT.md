# D-S19-1 source-correction report

Writer paused. This unit is not approved.

Personas used after preparation: bilingual dossier-projection engineer; evidence-boundary regression author.

## Renderer change

`render_dossier_html` still selects the first two public passports and the public contradiction-register ids, in that order. Those lists are no longer concatenated under `evidence.title`.

- Supporting ids render in one `p.summary-evidence` labelled with existing `evidence.title`.
- Public contradiction ids render in a second `p.summary-evidence` labelled with existing `dossier.public_contradictions`.
- An empty public register omits the second paragraph. No page-1 "none" sentence was added.
- A reference in both lists stays in both. Steel `S-UNICOIL-SPEC` stays only in the contradiction group because it is not one of the first two public passports.
- Appendix contradiction prose, empty-register appendix copy, and public/synthetic partition are unchanged.
- No catalogue, CSS, calculation, or decision change.

## Files

- `src/ior_mvp/dossier.py` — already modified versus HEAD before this unit; this unit added the two-group summary markup at the evidence-group lines.
- `tests/test_dossier_projection.py` — untracked before this unit (not in the index at HEAD `ce407db9832b61c5a8a85dfda2e3b7623da2fbc9`); this unit appended the summary regressions. 496 lines.

SHA256:
- `src/ior_mvp/dossier.py` `34f20faa89ea15f441285e56b238702df9de960097b4da69ed01336f4c3fb0f0`
- `tests/test_dossier_projection.py` `af95c0e13822ccb32d9da7e1fc5d7112443bf1a9828786ad87801ffcd2f30915`

No staging, commit, push, CSS, catalogue, manifest, or screenshot edit.

## Tests actually run

RED, unchanged renderer, `red-pytest.log`: exit 1. Five failures were the concatenated summary ids (`S-WITS-721049 S-UNICOIL-EPD` plus `S-UNICOIL-SPEC` in one group). Four empty-register cases passed because that omission already matched the ruling.

GREEN, `green-dossier-unit.log`: exit 0. `674 passed, 1 warning` in `tests/test_dossier_projection.py`, `tests/test_dossier_contract.py`, `tests/test_dossier_isolation.py`, `tests/test_dossier_availability.py`. Warning is the pre-existing Starlette/`httpx` deprecation, not this change.

Print sample, `print-sample-pytest.log`: exit 1 at setup. Playwright 1.62.0 Chromium is missing. Package install is outside this unit, so Chromium was not installed. No PDF was produced.

## Limitation

One physical first page was not measured. Font minima and CSS were not changed. The second group uses the existing `.summary-evidence` rule. Whether steel EN/AR public/simulated still keeps the whole summary on one A4 page is unverified. No break rule is proposed, because there is no measured overflow.

## Remaining gates, not run here

Claude source-readiness review. Replacement projection, manifest build, all-44 PDF proof, canonical capture, R1, pin rebinding, full `pytest -q`, `verify_integrity.py`, and delivery. This writer does not continue.

## Sanad

Facts above come from the brief, Claude review §3.3, the edited source, and the three logs in this directory. HEAD was read with `GIT_OPTIONAL_LOCKS=0 git rev-parse HEAD`.

## Muhasabah

PASS for this bounded source unit. Unrun physical-page measurement and all later completion gates stay open. No approval is claimed.
