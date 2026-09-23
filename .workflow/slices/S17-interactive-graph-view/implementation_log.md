# S17 implementation log

Base: `6e85eeec2686c59ae3c0d9e7dcb0baf2d7f2dcd8`
Branch: `slice/s17-interactive-graph-view`
Approved plan: `421515e85aedc027d6b2d06bff3215dafe473ffd1e5c7a573bda564c100f84a5`

The uncommitted implementation adds the approved collapsed bilingual `graph_view`, deterministic SVG and native controls, stored-evidence drill-down, public/simulation isolation, live loopback graph-UI gate, catalogue 1.5.0 and the 112-image visual matrix. `S17-DEP-AM1` supplies the reviewed evidence-edge isolation correction.

Controlled generation completed:

- graph projection `GRAPH-SAU-2026-09-12-b63159c7bdc1`, 925 nodes / 1,045 edges;
- snapshot inventory 722 and authority inventory 20;
- 112 canonical visual entries;
- final source-provenance refresh `S17-FINAL-REVIEW-R1`, with all 112 WebPs byte-identical and zero image changes.

Final integrated review corrections:

- `S17-F1-F01`: mode/opportunity graph gating and serialized context actions prevent a stale simulated graph from opening or committing under Public chrome.
- `S17-F1-F02`: ADR-027 and Build Progress now record completed generation without claiming delivery.

Final accepted product candidate:

- tree `adc34119a6dcdcf18a52b0e94ae7089affff9d25`;
- detached verification commit `d1b398f4c0d0c2fb57683eb5a182611442bb77d5`;
- independent re-review `APPROVE`;
- separate owner acceptance `ACCEPT`.

No commit, push, PR, hosted CI, merge, Aura refresh or delivery is claimed by this pre-delivery record.
