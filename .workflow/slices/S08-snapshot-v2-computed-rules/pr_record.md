# PR Record — S08 Public Snapshot Schema v2 and Computed Rule Ledger

- PR: https://github.com/baramiSG/Industrial_mvp/pull/10
- Head commit reviewed and merged: `38f033a` (equal to the local approved candidate; identity list `/tmp/s08_candidate_hashes_v2.txt`, unchanged after the reviewer's verdict).
- Base: `9f045a4ecf929b82a0c4ad9013d255e148bc837d` (S07 merge).
- PR CI: `uv / Python 3.12` pass (22s), `uv / Python 3.14` pass (22s), `pip / Python 3.12` pass (27s), `Docker image build` pass (24s), `browser / Chromium / Python 3.12` pass (5m41s; 118 functional + 4 visual against the regenerated canonical baselines).
- Merge: squash by the Supervisor after ADR-007 gate — merge commit `8b6d55cc8f1f10b828f3af7a6a1e045364cb5537`; branch deleted. Local `main` fast-forwarded cleanly (KL-32 fix: regenerated baselines were host-owned).
- Default-branch CI on the merge commit: run 33637594756 — all five jobs `success`. Post-merge integrity on `main`: `INTEGRITY PASS`.
- Models: planner `gpt-5.6-sol-max` (agent 334c755b), implementer `gpt-5.6-sol-max` (agent f1587e62), independent reviewer `cursor-grok-4.6-xhigh` (agent e6fd5b79), Supervisor `claude-fable-5-1-thinking-max`.
