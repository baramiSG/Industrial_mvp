# S17 finding lineage

## Independently closed plan findings

`S17-PLAN1-F01`, `F02`, `F03`: VALID, corrected and closed in plan round 1. The approved plan and owner acceptance remain in force.

## Implementation findings pending final independent review

- `S17-IMPLEMENT-DEP-01`: public evidence graphs included synthetic support edges while top-level disclosure inspected nodes only. The bounded serializer correction has focused regression proof; independent scope approval is not implementation approval.
- `S17-OWNER-FIXTURE-01`: a fixture invented a public Product/evidence ID. It now copies the actual serialized public Product; only test-only Class-D elements are invented.
- Browser interaction/readiness: finite SVG edge pointer targets and request-complete waits were required. Test-only import/SVG text-accessor mistakes were corrected without changing expected behavior.
- Accessibility/disclosure: actual checks found lost keyboard focus, nested interactive SVG descendants, missing graph-level policy warnings and inaccessible tablet scrolling. Corrections and the four EN/AR desktop/tablet keyboard/axe checks passed; final full-candidate review remains pending.
- Race/security proof: the existing approved tests now include settled out-of-order responses, selection identity, unsafe URLs/markup and explicit rejection of synthetic elements in public payloads.

No implementation APPROVE or delivery is claimed by this record. Required functional, canonical visual and integrated evidence must be current before the retained reviewer issues that verdict.

## Final implementation review

Round 0 on tree `7788a822d1e351365085a365f2eb62a4cb3262cc`: **REJECT**.

- `S17-F1-F01` BLOCKER — stale simulated graph during mode transition.
- `S17-F1-F02` MEDIUM — stale generation/status claims.

Owner adjudication: VALID / VALID. The same retained implementation successor corrected both findings and refreshed visual source provenance without replaying graph/product generation or changing any WebP.

Re-review on tree `adc34119a6dcdcf18a52b0e94ae7089affff9d25`: **APPROVE**, zero unresolved findings. Direct Write, off-list Shell and near-miss Shell probes were denied; the exact read-only oracle passed 4/4. Separate owner acceptance followed.
