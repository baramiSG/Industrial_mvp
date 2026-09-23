# S18a delivery record — PR37

S18a was merged on 2026-09-23 at21:09:41UTC through [PR37](https://github.com/baramiSG/Industrial_mvp/pull/37). This additive record belongs to the S18b0 follow-up; it does not change the approved S18a source or its historical records.

- Independent Claude implementation APPROVE and separate owner acceptance cover tree `1364789a964f96f6ebabf8eae1d239a5bad0b15e`.
- Delivered commit: `f9a8be7e780916f60e194174a75d94dd065f496d`, parent `564b1b7a3924ba14d219af8ed027c54311911910`.
- Squash merge: `b4a00adb685c61c4d50c24e94647fbd24e599096`; its tree is exactly the accepted tree.
- [Authenticated Claude verdict](delivery-evidence/claude-am4-implementation-review.md) SHA-256 `8c5ae016ada1adf520352afbe2679bbe82c455d121ff32a355695a315d8a5562`; original model attribution `claude-opus-5-5`,2026-09-23T20:13:58.237Z. This verdict is distinct from the same-model Codex delivery review.
- Full [implementation receipt](delivery-evidence/am4/AM4-IMPLEMENTATION-RECEIPT.md) SHA-256 `8fc1368371a067bc3e2fe99359600be5d01c663024644e9e3d8147478e4122fb`.
- Historical856-entry [checksum list](delivery-evidence/am4/AM4-FINAL-SHA256SUMS) SHA-256 `af9c76a7594ed497ae2f0b6f9098031b90f1416cc1034666c3522ac7ad238214`; full original local bundle preserved. The [published subset](delivery-evidence/README.md) explicitly contains54 evidence records plus the manifest and wrapper, not all856 files.
- Codex independent exact PR-head delivery APPROVE report SHA-256 `5ffdf79314b91dd61c3a14f8a5a033b2c91e90052dbaa34370a11a41cc9c088b`. Root separately recorded delegated merge-go; the author did not approve its own implementation.

## Actual hosted verification

[PR run35917239905](https://github.com/baramiSG/Industrial_mvp/actions/runs/35917239905) passed all six jobs. Its checkout was GitHub synthetic merge `d9945f3be76dd3677567a0d5196e354613ce5ea6`, whose parents include the exact delivered head and whose tree equals the approved tree. It was not a direct branch checkout.

[Main run35920687954](https://github.com/baramiSG/Industrial_mvp/actions/runs/35920687954) passed all six jobs on the actual merge commit. Each Python matrix environment ran3027 tests successfully; graph load925/1045 and reload0/0, equality, live graph/UI and unavailable tests passed; Docker build and optional-driver exclusion passed. Browser functional513 passed and visual4 passed. The graph suite's opt-in Aura skip is not live Aura evidence.

Root retained and inspected each complete main job log; the SHA-256 bindings below allow later downloaded-log comparison. The local main-verification receipt is SHA-256 `b7e0efb006cfb2102f250ba993232aabe5112333285d1459b4ff2262117e1f11`.

| Main job | GitHub log reference | SHA-256 |
|---|---|---|
| browser / Chromium / Python 3.12 | [job107383564230](https://github.com/baramiSG/Industrial_mvp/actions/runs/35920687954/job/107383564230) | `9e5c29c317e94065262ea24de7fb61f3607652ae496ef737163f18863df8bb90` |
| pip / Python 3.12 | [job107383564451](https://github.com/baramiSG/Industrial_mvp/actions/runs/35920687954/job/107383564451) | `60c80f276a21c057cb9960a99f34e4064746a18fdace681c724024f4349706a5` |
| uv / Python 3.12 | [job107383564568](https://github.com/baramiSG/Industrial_mvp/actions/runs/35920687954/job/107383564568) | `1a07df67fc8f8bb6d1b849a13c93a16efe074af5f24af66202830329f42b286a` |
| uv / Python 3.14 | [job107383564605](https://github.com/baramiSG/Industrial_mvp/actions/runs/35920687954/job/107383564605) | `02db70b377e1335a60e006df1e78c4f2e0e491ad65acc0ec7ad5e1c7d985eeb9` |
| Docker image build | [job107383564674](https://github.com/baramiSG/Industrial_mvp/actions/runs/35920687954/job/107383564674) | `18d4833ee0e536af9338ec982e2403a34855654a51e814ede828e1f00d9284b7` |
| graph / Neo4j service / Python 3.12 | [job107383564845](https://github.com/baramiSG/Industrial_mvp/actions/runs/35920687954/job/107383564845) | `be055b2d4fdfa3d247748f92399d5492106b96060ce7bb208d2fb4714ef80a2e` |

## Preserved state and remaining work

The owner-authorized Codex implementer substitution preserved Cascade's historical assignment and the approved AM4 packet bytes. Cascade had been confirmed stopped for S18. Approved source was staged only after identity verification; staged and committed trees matched. Ordinary pre-stage index backup and all historical alternate indexes were retained. Primary dirty checkout, frozen artifacts and historical approvals were preserved.

AM4 deferred issues remain explicitly tracked: case-level EVSI availability schema, malformed-input paths, model partition validation and test gaps. S18b0 addresses only its independently reviewed subset; broad case-wide R12 need mapping and explicit case-level EVSI schema remain open. S18 frontend, later milestone work, actual Aura replacement/verification and final cross-model audit are separate work. No release tag or final milestone acceptance is claimed.

Sanad: source/staged/committed/merged tree identity and six actual PR/main job logs were checked by the coordinator; the separate delivery reviewer approved the exact PR head after CI. Historical implementation counts are bound to the immutable receipt. Muhasabah: PASS for S18a delivery; later work is neither pre-approved nor represented as complete. Tonight's delegated Codex reviews are same-model independent reviews, not Claude approval.
