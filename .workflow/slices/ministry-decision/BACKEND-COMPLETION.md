# Ministry M backend completion

Status: backend batch implemented and focused tests passing. Overall M source remains pending. This is not generation, Claude approval, or delivery.

Worktree: `/home/barami/projects/ior-worktrees/ministry-decision`
Branch: `slice/ministry-decision`
Source is uncommitted.

## What changed

- `src/ior_mvp/candidate_register.py` — H0 and H6 identities both validate; only an exact revision matches a selector. Effort must be the nine configured dimensions. Dates are real half-open windows. Attribution checks ownership, period, duplicate links, and cumulative quantity. Coverage subjects resolve. Public refs must hit the allowlisted steel or polypropylene snapshot, its hash, evidence id, and field. Synthetic purposes cannot claim Class A/B/C.
- `src/ior_mvp/line_contract.py` — legacy plant/capability/equivalence pointers are admitted only on reference line `LINE-7315366f6a9166d8`. Requirement items cannot carry P03/P04 parameter keys. Fact refs must match kind and line subject.
- `src/ior_mvp/candidate_discovery.py` and `src/ior_mvp/line_comparison.py` — P01–P08 findings, including linked P04 equipment classification. Galvanising acquisition can add one equipment signal. A wire-coil winder does not. P09 qualified supply stays on the line capacity result: formula and admitted supply are separate, known zero stays zero, and a positive allocation beside a current technical failure is not silently capped.
- Polypropylene application and customer qualification use `application_qualification`. Declared effort is copied before masking. Unknown and conflict mask the mapped dimension. A known width or customer failure does not.
- `data/synthetic/SYN-MINISTRY-STEEL-001.json` and `SYN-MINISTRY-PP-001.json` — one shared register, scenario-specific lines. Archived v2.0 bytes are unchanged: steel `535d66e9c511899e787bfb11558933d0507bf54402068e32c98935d00bd21567`, polypropylene `0c7a8b94e17be26c6de9764bf1836c490ae2cb031fa14077e2f95de688711580`.

## Tests

RED, before the repair, six focused tests failed. The log is `.workflow/slices/ministry-decision/evidence/backend-red.txt`. H0 was rejected. Cumulative allocation, incomplete effort, a malformed identity, an alternative legacy pointer, and linked hot-dip acquisition did not fail closed or did not produce `P04_GALVANISING_ACQUISITION`.

GREEN: `31 passed` in the four backend modules plus the two in-memory Hadeed attribution tests. The golden-case loop kept every recorded real and simulated state. Older scenarios return `NO_REGISTER` and `NO_LINE_RECORDS`.

The frozen-artifact adjacency test remains failed closed until authorized generation. It was not rewritten.

## Still outside this batch

Executive workspace, screening bridge, policy 1.5, UI catalogue, scene stems, the governing DOCX binary, graph generation, and manifests. A searched-empty customs fixture and an explicit half-open window equality test are not separate cases yet; the validator and comparator implement those rules and the width, MFR, allocation, re-export, company-scope, and wire-coil cases cover the adjacent boundaries.

## Sanad / Muhasabah

PASS for this backend batch report. FAIL if it is read as complete M source or an accepted candidate.
