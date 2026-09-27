# G1.3 actual visual baseline pin handoff

**PAUSE.** The sole authorized source edit is complete: `tests/test_frozen_public_evidence_pins.py` now pins `browser_tests/baselines` to the actual OID `9dea0ee08c8c6f198bdf1f0fc904033874685a7a` from [ACTUAL-BASELINE-PIN-replacement-2.json](/home/barami/projects/industrial-opportunity-resolution-mvp/.autonomous-workflow/mission-20260925/ministry-decision/ACTUAL-BASELINE-PIN-replacement-2.json). The previous literal was `b1a5bde7c3da6f13ab05df18bfc26a5511e028fe`. [TASK-ONLY.diff](TASK-ONLY.diff) is the one-line patch against the original source bytes.

Root's [canonical capture result](/home/barami/projects/industrial-opportunity-resolution-mvp/.autonomous-workflow/mission-20260925/ministry-decision/canonical-capture-replacement-4/RESULT.json) and [inspection](/home/barami/projects/industrial-opportunity-resolution-mvp/.autonomous-workflow/mission-20260925/ministry-decision/canonical-capture-replacement-4/INSPECTION.json) record 140 byte-equal images, zero changed images, 250 source inputs and accepted test-only provenance. The pin is taken from the fresh freeze index receipt, not inferred from an image or placeholder.

`tests/test_s17_status_docs.py` is unchanged from the [SOURCE-BEFORE.json](SOURCE-BEFORE.json) capture and already asserts 140 entries and `MINISTRY-M-V3-1-20260926`. The targeted pure provenance and status-doc tests passed: **2 passed in 0.04s**, exit 0, using the project venv with a stripped environment, source `PYTHONPATH`, no bytecode and no cache provider. Exact command is in [CHECKS.json](CHECKS.json). I did not run HEAD frozen-pin checks in W because its HEAD is intentionally F.

[SOURCE-AUDIT.json](SOURCE-AUDIT.json) records SHA-256 comparison of all 3,544 paths in the admitted pre-edit source inventory. Exactly the pin test changed; no paths were missing. Ordinary index `770d3e296985bb61b52211fd365a2b0cad96e8faf512949dfb57f236eb54eaf5`, PID 34210 start 79799 and lock inode 2358670 are preserved. No secret contents were printed.

Root owns the final freeze, full gates, independent Claude review, GitHub and Aura. This is an implementer handoff, not an approval.

**PAUSE.**
