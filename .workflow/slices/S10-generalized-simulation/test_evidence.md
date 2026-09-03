# S10 test evidence

## T0 baseline

```
T0-OK
INTEGRITY PASS
SCENARIO VALIDATION PASS (2 scenarios)
SMOKE PASS
811 passed, 1 warning
```

## T15 candidate 2 verification (2026-09-03)

```
PYTHONPATH=src .venv/bin/python -m pytest -q
867 passed, 1 warning in 3.35s

PYTHONPATH=src .venv/bin/python scripts/verify_integrity.py
INTEGRITY PASS

PYTHONPATH=src .venv/bin/python scripts/validate_scenarios.py
SCENARIO VALIDATION PASS (2 scenarios)

PYTHONPATH=src .venv/bin/python scripts/demo_smoke.py
SMOKE PASS

.venv/bin/python scripts/check_threshold_literals.py
THRESHOLD LITERAL SCAN PASS (22 Python files; 23 configured numeric values)

FROZEN OUTCOMES EXACT
VISUAL MANIFEST OK (change_ref=S10-generalized-simulation, 40 entries)

IOR_UPDATE_VISUAL_BASELINES=1 IOR_BASELINE_CHANGE_REF=S10-generalized-simulation make e2e-update-baselines
4 passed, 118 deselected (visual update container run)

make e2e-functional
118 passed (functional browser nodes)

Second visual baseline update after dom.js narrativeEntry fix (permitted post-T14 governed frontend edit):
IOR_UPDATE_VISUAL_BASELINES=1 IOR_BASELINE_CHANGE_REF=S10-generalized-simulation make e2e-update-baselines
4 passed, 118 deselected

make e2e
122 passed (118 functional + 4 visual)
```

Reviewer-authorized path delta: `tests/test_authority_disclosure.py` (decision_narratives pin 1.1.0) included in working tree beyond plan T15 exact-set snippet.

## T15 candidate 3 correction (2026-09-03)

### F-01 proving commands

```
rg -n 'until the S10 simulation branch is implemented|supplies no governed schema|do not define a current JSON schema|Until governed bilingual engine narratives exist' docs/KNOWN_LIMITATIONS.md docs/core/01_PRODUCT_AND_REQUIREMENTS.md
(no matches)

rg -n 'S10-LOCAL|V3-C3|FR-055' docs/REQUIREMENTS_TRACEABILITY.md
(hits)

rg -n 'bilingual' docs/core/01_PRODUCT_AND_REQUIREMENTS.md  (Journey C section)
(hits)
```

### F-02 visual oracle inventory

- Manifest: `change_ref=S10-generalized-simulation`, 40 entries, digest `7352210ffbc090890c6de2672c9e50e46a69377b8c6f7c2decffe81abb4c8d23`.
- Public workspace WebPs restored byte-identical to base `66d4835` (`git diff --name-only 66d4835 -- browser_tests/baselines/v0.3.0 | grep public` → empty).
- **13 simulated WebPs changed vs base** (27 unchanged public/simulated oracles):

| Path | SHA-256 | Bytes |
|---|---|---:|
| `ar/desktop-1440x900/journey-c-steel-simulated-workspace.webp` | `0297111637bc97e08f103656e916601052c2db71df88f741968c2df375e03a64` | 228,152 |
| `ar/desktop-1440x900/journey-d-polypropylene-simulated-workspace.webp` | `ac0466e58ddab3c043af0968824fcbe6f53a420b3a638792cefcf2c84ae31bfc` | 216,566 |
| `ar/desktop-1440x900/journey-e-polypropylene-simulated-dossier.webp` | `6d8b0693a9ec1d5bd2ab311f11c59890599c541db96b29cfcb0c1d86a2bf4341` | 44,716 |
| `ar/desktop-1440x900/journey-e-steel-simulated-dossier.webp` | `777a7f876567a49261ee06da35ceaa54f1e146364df4aae7a1121a5844d04fe4` | 53,192 |
| `ar/tablet-1024x768/journey-c-steel-simulated-workspace.webp` | `4b92e432f4db4455edfa504b4c324af58714f0acb905b8f84297a41b1a804377` | 174,204 |
| `ar/tablet-1024x768/journey-d-polypropylene-simulated-workspace.webp` | `ad222592ebe722ca43995dc56273e8f39a177305367aeff852f9952257b39c08` | 165,694 |
| `ar/tablet-1024x768/journey-e-polypropylene-simulated-dossier.webp` | `af11dafe7e0e1cdb450f53c66fb94bded5478a023400b1d6234f71fb1ffcca12` | 35,070 |
| `ar/tablet-1024x768/journey-e-steel-simulated-dossier.webp` | `fc02d07ab88e05f9a5cd4256ec3c784016d9f48573611257baab2b70229e4151` | 42,668 |
| `en/desktop-1440x900/journey-c-steel-simulated-workspace.webp` | `a89e7a4b06271ed9ea979308685652426cf005a8d52085cafae77b7d1e45dd3c` | 229,630 |
| `en/desktop-1440x900/journey-d-polypropylene-simulated-workspace.webp` | `2753978ae5ab51e9df3a742f4a8ea0fb7fca94d99ca05be28f35ca11ee817bb7` | 226,618 |
| `en/desktop-1440x900/journey-e-polypropylene-simulated-dossier.webp` | `dda684fa7b5f864f38ec344154052bea29d706469c0baae49ca03c8ed0d6dc55` | 51,884 |
| `en/tablet-1024x768/journey-c-steel-simulated-workspace.webp` | `45cbb16f36b5f8abd71a196e9db2efc6aacb4ac8e8a837e3699b175a17f199a0` | 180,498 |
| `en/tablet-1024x768/journey-d-polypropylene-simulated-workspace.webp` | `5da6fbd8c45552f108e1a31ad01faff46ce714ebbceb13ff5fc03b23dd4aacb1` | 174,500 |

- Accidental public drift (53-pixel cluster on eight public workspace WebPs) reverted in candidate 3; not accepted as oracle change.

### Candidate 3 full verification (recorded after correction)

See envelope `verification` block for pytest 867, integrity, Gate B, smoke, scanners, plan snippets, and `make e2e` output.
