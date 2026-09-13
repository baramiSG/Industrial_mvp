# PR Record — S15a Pharma/API and Fertiliser Evidence

- PR: [#29](https://github.com/baramiSG/Industrial_mvp/pull/29)
- M15 integration parent: `6dc966a9f210b47a94b96aaeffadcbcc6642415f`
- W1' preparation commit: `7d4853e8d979d86a5fa932fbd4468bceacfb63b4`; candidate commit: `6413d04b4c43c256e6dbab12217e77f1027563fa`.
- Reviewed candidate identity: `9e2853cfc7a6ae4208c24ab12daf90dfd24a8ccabbb0e5f3ebf87c9df3dbca31` (20 uncommitted candidate paths; full M15 branch delta reviewed).
- Independent reviewer: APPROVE with zero findings. It checked the W1' integration resolution, the recorded-input selection replay, the scoped same-day partner snapshot, all four briefs and public engine proofs, authority/manifest deltas, exact reconstruction and evidence precision.
- Owner local CI on exact candidate: integrity; Gate B for seven existing scenarios; selection/case/document/entity/screening reconstruction; 2,600 pytest tests; frozen smoke outcomes; 339 functional + 4 visual Chromium tests.
- PR CI: run `34748809072`, all five jobs green on exact head `6413d04`: uv Python 3.12, uv Python 3.14, pip Python 3.12, Docker image build and Chromium (15m38s).
- Merge: owner approval OD-18; GitHub GraphQL merge operation had a provider error, so the exact-head squash merge was completed using GitHub’s documented REST merge endpoint; merge commit `8053f2b70c4440efb6a00bbc7922e6d14e30377d`. Remote branch deleted after merge.
- Merged tree equals the PR head tree. Clean-worktree post-merge verification: `INTEGRITY PASS`; 2,600 pytest tests; smoke preserving steel public `INVESTIGATE` and polypropylene public `REJECT`; `CASE RECONSTRUCTION PASS (5 snapshots, 9 briefs)`, `RECONSTRUCTION PASS (5 snapshots, 42 artifacts)`, `DOCUMENT RECONSTRUCTION PASS (26 records, 26 artifacts)`, `ENTITY RECONSTRUCTION PASS (3 artifacts, 46 links)`, `SCREENING RECONSTRUCTION PASS (1 snapshots)`, `CASE SELECTION RECONSTRUCTION PASS (2 records)`.
- Default-branch CI: run `34749303450` on merge `8053f2b`, all five jobs succeeded.
- Manifest §7: exactly one S15a generation at 2026-09-13T07:43:54Z; snapshot manifest 638 → 698 (60 additions, zero prior change/removal); authority set stays 19 with six changed rows (acquisition sources, product families, Core 02/04/05/09).
