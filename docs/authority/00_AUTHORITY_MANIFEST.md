# 00 — Authority Manifest

## 1. Purpose

This manifest defines the authority chain for the Industrial Opportunity Resolution Engine MVP. Its purpose is to prevent an autonomous agent, developer or reviewer from silently changing the industrial decision method while implementing software around it.

The repository separates four things that are often conflated:

1. **Domain authority** — what the industrial decision method means.
2. **Implementation authority** — how that method is represented in software.
3. **Operating configuration** — versioned thresholds and sector profiles used in a decision cycle.
4. **Evidence snapshots** — the exact public and synthetic inputs used for the demonstration.

A lower layer may implement or instantiate a higher layer. It may not contradict it.

## 2. Authority precedence

| Rank | Authority | Path | Effect |
|---:|---|---|---|
| 1 | Final methodology | `Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx` | Governs the decision object, evidence boundary, R0–R12 semantics, capability logic, economics, intervention sequence, AI boundary, dossier and outcome learning. |
| 2 | Frozen implementation core | `../core/01_...` through `../core/09_...` | Converts the methodology into software contracts without changing its meaning. |
| 3 | Versioned operating configuration | `../../config/thresholds.v1.yaml`, `sector_profiles.v1.yaml`, `evidence_policy.v1.yaml` | Instantiates initial thresholds, weights, hard gates and evidence controls for this demo cycle. |
| 4 | Hashed evidence artifacts | `../../data/manifests/snapshot_manifest.json` | Defines the exact public snapshots, synthetic scenarios and extraction fixtures used by CI and the demo. |
| 5 | Source code and API behavior | `../../src/ior_mvp/` | Implements the contracts above. |
| 6 | Tests and proof artifacts | `../../tests/`, `../../scripts/` | Demonstrate conformance; they do not redefine authority. |
| 7 | Later-binding implementation notes | `../implementation/` | Explain UI, API, deployment and build slices. They are subordinate and may evolve without changing the frozen method. |

Where two same-rank documents conflict, stop and resolve the conflict through the methodology owner. Do not choose the version that is easier to code.

## 3. The frozen ten-document core

The core is intentionally small enough for autonomous agents to read before implementation:

1. `01_PRODUCT_AND_REQUIREMENTS.md`
2. `02_METHODOLOGY_IMPLEMENTATION_MAP.md`
3. `03_SYSTEM_ARCHITECTURE.md`
4. `04_CANONICAL_DATA_MODEL.md`
5. `05_DATA_SOURCES_AND_INGESTION.md`
6. `06_SYNTHETIC_MINISTRY_DATA_SPEC.md`
7. `07_DETERMINISTIC_ENGINE_SPEC.md`
8. `08_AI_EXTRACTION_AND_EVIDENCE_SPEC.md`
9. `09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md`
10. this authority manifest

The core merges closely related concerns to avoid the excessive authority surface that can prevent autonomous implementation from beginning.

## 4. Reusable build machinery is external

Flight Control and the Universal New-Project Guide are reusable firm assets. They are not copied into this repository.

Expected references:

```text
${FLIGHT_CONTROL_HOME}
${UNIVERSAL_NEW_PROJECT_GUIDE}
```

This repository provides only a thin domain overlay in:

- `../../AGENTS.md`
- `../../.cursor/rules/`
- `../implementation/BUILD_OVERLAY.md`

Those files define the mandatory reading list and domain-specific prohibitions. They do not redefine generic supervisor, implementer, reviewer, task-state, retry, CI or merge machinery.

## 5. Mandatory reading by change type

| Change type | Mandatory documents |
|---|---|
| R-rule, state or route behavior | Methodology Sections 1, 4 and 12; Core 02, 07 and 09; thresholds config; affected golden snapshot. |
| Capability or D\* | Methodology Section 6 and Appendix B; Core 02, 04, 07 and 09; sector profile. |
| Economics, S\*, national value or EVSI | Methodology Sections 7 and 9; Core 02, 07 and 09. |
| Data ingestion or harmonisation | Methodology Sections 2, 3 and 11; Core 04, 05 and 09. |
| Synthetic evidence | Methodology evidence boundary and Sections 2.1, 10 and 11; Core 06, 07 and 09; evidence policy. |
| Bilingual extraction | Methodology Sections 5 and 10; Core 08 and 09; AR/EN golden fixture. |
| GenUI or dossier | Methodology Sections 15 and 10.3; Core 01, 03 and 04; implementation UX specification. |
| Snapshot or threshold update | This manifest; Core 05, 07 and 09; manifest regeneration and full golden regression. |

## 6. Non-negotiable invariants

1. The real decision branch uses public evidence only in this MVP.
2. Synthetic evidence may only affect `simulation_decision`; it can never modify `real_decision`.
3. Synthetic records are always Class D, `source=DEMO_GENERATOR`, explicitly flagged and visibly disclosed.
4. Missing decision-critical evidence remains unresolved. It is not replaced with a persuasive estimate in the real branch.
5. `ADVANCE` is blocked when product identity, required-specification demand, domestic supply/capability or a hard gate remains Class D/E.
6. Unknown capability states are penalised and cannot improve adjacency.
7. Thresholds are read from versioned configuration, not embedded as hidden constants.
8. Unit value opens a specification investigation; it never proves a grade by itself.
9. No action, incumbent use, brownfield and non-financial routes precede supported greenfield.
10. Golden tests run only against hashed local snapshots, never live sources.
11. The steel public case remains `INVESTIGATE`; the polypropylene generic-capacity case remains `REJECT` unless the governing evidence snapshot and methodology are formally changed.
12. Computation may be autonomous; authorization of public support is not anonymous.

## 7. Change classes

### 7.1 Editorial

Spelling, formatting or non-semantic explanation. Requires review but does not require threshold or snapshot regeneration.

### 7.2 Implementation-preserving

Refactoring that leaves observable behavior, formulas, route logic and golden outcomes unchanged. Requires unit tests, golden regression and integrity verification.

### 7.3 Operating configuration

A change to a threshold, sector weight, hard gate, evidence policy or scenario parameter. Requires:

- a new versioned artifact;
- rationale and sector scope;
- sensitivity result;
- methodology-owner approval;
- full golden and boundary regression;
- updated hashes.

### 7.4 Methodology change

A change to the decision object, evidence boundary, formula, route order, state meaning or authority rule. Requires an updated governing methodology and a new core version. Do not implement it through code alone.

### 7.5 Evidence refresh

A replacement or revision of a public source snapshot. Requires a new snapshot ID, as-of date, query contract, hash and comparison with the prior decision. Existing historical snapshots are retained rather than overwritten.

## 8. Integrity artifacts

- `authority_hashes.json` contains SHA-256 hashes for the methodology, frozen core and operating configuration.
- `../../data/manifests/snapshot_manifest.json` contains SHA-256 hashes for every public, synthetic and golden data artifact.
- `../../scripts/verify_integrity.py` fails closed on a missing file or hash mismatch.
- `../../scripts/build_manifests.py` may regenerate manifests only as part of an approved change.

A hash mismatch is not repaired by automatically accepting the new file. First determine whether the change is authorized.

## 9. Searchable mirror

`methodology_extracted.md` is generated from the governing DOCX so agents can search headings and text. It has no independent authority. If the Markdown conversion differs from the DOCX, the DOCX governs and the mirror must be regenerated.

## 10. Stop conditions

Stop the change and raise an owner decision when:

- a required methodology term has more than one defensible interpretation;
- a requested feature would cause synthetic evidence to appear official;
- a threshold change is requested without rationale and versioning;
- a live source revision changes a golden outcome;
- a route would `ADVANCE` despite unresolved hard gates;
- a project-local instruction conflicts with external Flight Control or the Universal New-Project Guide;
- a reviewer is asked to weaken a test simply to make a preferred outcome pass.

## 11. Current authority hashes

The machine-readable source of truth is `authority_hashes.json`. The table below is regenerated when the approved authority set changes.

<!-- HASH_TABLE_START -->
| Governed file | SHA-256 | Bytes |
|---|---|---:|
| `docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx` | `5717cbd42acc9947ce5e450013719275acb7ed1470847b21fb2cc547c8ac4ce9` | 224,257 |
| `config/thresholds.v1.yaml` | `4e891b9706408f6a661565e09609d0d663e1a00a17bda4e283a4b2ee63d3c47a` | 3,887 |
| `config/sector_profiles.v1.yaml` | `9765e84dc32297d624f72644a436f5aac15fe600df5536d717f3600b05708e3e` | 2,879 |
| `config/evidence_policy.v1.yaml` | `2587aea624237295d9523c8e3ac49068286e0feb36b9f3fe3f50e44e7cf657aa` | 1,681 |
| `config/ui_strings.v1.yaml` | `cb1881fdfbbbd757c83a01f5ad489ab6587a39a28c387522d982e08338d4a08b` | 24,254 |
| `config/decision_narratives.v1.yaml` | `a6011d64a3035f27b68666274dcd9a0fbe84b643622b6a6a440eba47ff7c253f` | 25,905 |
| `docs/core/01_PRODUCT_AND_REQUIREMENTS.md` | `ed74fcd10fa3b6767402b740981720081aec52f4c808f1e057e3b26e729d46cd` | 13,545 |
| `docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md` | `ca14eb7895ed02c867c0479e8f9d9ba413d656ef782ff0fd0dc25ba6aa04130c` | 17,196 |
| `docs/core/03_SYSTEM_ARCHITECTURE.md` | `33cfb90b3e394413855144c70abfdf79c6c41584caa0ad1b73dfb044281cac66` | 9,337 |
| `docs/core/04_CANONICAL_DATA_MODEL.md` | `db387c4f048f2a51aa2d38f7b0331c9f63d78f3e6dbf028a2e58b1828c825aa5` | 11,227 |
| `docs/core/05_DATA_SOURCES_AND_INGESTION.md` | `d47823ae761996faf3f67a14850a75ddb4a37a3e8dd3a160ad54afacca8548ad` | 9,259 |
| `docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md` | `5c930ea5756aea802325a26ab94066353f59fd73dc9a04b1496f88dd6ba0863e` | 6,562 |
| `docs/core/07_DETERMINISTIC_ENGINE_SPEC.md` | `145f98ba782a666f2f8784e29b0cfaeb22e533eb9a150c543eec040457e06176` | 26,249 |
| `docs/core/08_AI_EXTRACTION_AND_EVIDENCE_SPEC.md` | `875f30b1a597f94548cf1cdb8315c753dc0fe9d780674b36a7bd8653e9e56f58` | 5,564 |
| `docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md` | `eaced2a680b5fe42b6d93a5d402dc6ad877b09d98571b097197859806c4a24ae` | 10,527 |
<!-- HASH_TABLE_END -->
