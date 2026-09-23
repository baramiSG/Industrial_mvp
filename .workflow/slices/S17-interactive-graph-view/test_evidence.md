# S17 verification evidence

Accepted product tree: `adc34119a6dcdcf18a52b0e94ae7089affff9d25`
Detached verification commit: `d1b398f4c0d0c2fb57683eb5a182611442bb77d5`

Two fresh isolated materializations under `s17-native01/final-3/` each ran complete `make ci` against separate disposable Neo4j containers, volumes, networks and credentials. Both exited 0 and remained clean at the exact tree.

Each run observed:

- 2,887 Python tests passed; one known Starlette deprecation warning;
- 513 functional Chromium tests passed, four visual tests deselected;
- four visual Chromium tests passed, 513 functional tests deselected;
- graph first/second load 925/1,045 then 0/0, live graph equality/UI and stopped-service proof;
- integrity, 11-scenario reconciliation/back-tests, full reconstruction and smoke PASS;
- steel public `INVESTIGATE` and polypropylene public generic-capacity `REJECT` unchanged.

Generated evidence:

- graph `GRAPH-SAU-2026-09-12-b63159c7bdc1`, 925 nodes / 1,045 edges;
- snapshot manifest 722 rows; authority manifest 20 rows;
- visual manifest SHA-256 `725a5fc1bb3d0d4136cb0b56fc26646b6d8ca7ce93d393ff2c1dc2f1c9fb4aee`;
- visual root OID `ba10ae7c54ac96614c015484e7445752b5680285`;
- 112/112 WebPs byte-identical through final review correction.

The reviewer independently ran the hash-bound stdlib oracle: 4 tests, OK. Hosted CI remains pending until the reviewed owner-record delta is committed and pushed.

## Hosted and merged-main delivery

- PR run `35831654002`: six of six checks passed on head `a0b7141eb681184ab47b0d3d92f37f97a028a675`.
- Main run `35834129601`: six of six checks passed on merge `e10225005fe13295d1c10e443276e0139be806c6`.
- Clean merged-main: integrity PASS; 2,887 pytest PASS; smoke PASS; all reconstruction stages PASS; graph build-check PASS at 925/1,045.
