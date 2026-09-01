# 08 — AI, Bilingual Extraction and Evidence Control

## 1. Governing principle

> AI resolves language and ambiguity; deterministic code calculates; accountable experts authorize.

The MVP contains an offline schema-constrained extraction demonstration so the complete package runs without an API key. A production LLM adapter can replace the extractor only if it satisfies the same source-span, schema, validation and golden-test contract.

## 2. Permitted AI tasks

- Arabic–English specification extraction;
- synonym and transliteration normalization;
- unit and standard normalization proposals;
- entity-link proposals;
- anomaly explanation;
- contradiction detection;
- evidence synthesis into a draft dossier;
- prioritization of a missing fact, subject to deterministic EVSI.

## 3. Prohibited AI tasks

AI may not:

- calculate NPV, IRR, S\*, D\*, HHI or quantity contribution;
- alter thresholds or sector weights;
- invent missing capacity, utilization, demand or customer qualification;
- convert synthetic evidence into observed evidence;
- approve an intervention;
- suppress a contradiction;
- produce a grade conclusion from unit value alone;
- insert free-form factual statements into the canonical record without a typed field and evidence pointer.

## 4. Extraction contract

Input:

```json
{
  "document_id": "...",
  "language": ["ar", "en"],
  "source_spans": [],
  "target_schema": "specification.v1"
}
```

Output:

```json
{
  "fields": {
    "standard": "SASO-ASTM A653/A653M",
    "coating_mass_g_m2": [45, 350],
    "thickness_mm": [0.18, 3.0],
    "width_mm": [600, 1300]
  },
  "source_spans": {"ar": "...", "en": "..."},
  "status": "calculated",
  "confidence": {},
  "warnings": [],
  "contradictions": []
}
```

No field enters the record without the exact supporting span.

## 5. Bilingual normalization rules

- preserve Arabic and English original text;
- normalize Arabic/Western numerals;
- normalize `جم/م2`, `gsm` and `g/m²` to `g/m2` internally;
- preserve whether coating is total-both-sides or per side;
- normalize standard punctuation and spaces;
- keep standard edition unresolved when the source does not state it;
- retain source-specific range differences as contradictions;
- distinguish “published conformance” from “customer acceptance.”

## 6. Demo golden set

The packaged fixture contains four labeled fields from the methodology’s bilingual UNICOIL example:

1. standard;
2. mandatory minimum coating;
3. coastal exposure condition;
4. product dimension/coating envelope.

The offline extractor must reach 4/4 exact field matches. This demonstrates the contract, not production-level language-model performance.

## 7. Production LLM dual pass

### Pass 1 — Extract

- populate only allowed schema fields;
- quote exact source spans;
- return unresolved when no span supports the field;
- identify exclusions and negation.

### Pass 2 — Verify

Independently check:

- source fidelity;
- units and scale;
- standard identity;
- negation and exceptions;
- conflicting ranges;
- whether the source proves specification only or also qualification/capacity.

Deterministic validators then check dates, units, ranges, HS codes and arithmetic.

## 8. Evaluation metrics

A production extraction gate should measure:

- exact field accuracy;
- source-span precision and recall;
- unit-normalization accuracy;
- contradiction recall;
- false assertion rate;
- unresolved precision;
- Arabic/English consistency;
- reviewer disagreement.

Decision-critical fields require stricter thresholds than descriptive fields.

Suggested initial gate for anchor sectors:

```text
critical-field exact accuracy ≥ 95%
source-span precision ≥ 98%
unit-normalization accuracy = 100%
unsupported assertion rate ≤ 1%
contradiction recall ≥ 90%
```

These are implementation targets, not methodology thresholds, and require calibration on a real labeled corpus.

## 9. Etimad expansion set

The next data-enrichment task should add real public Etimad tender excerpts for selected sectors. Each item should include:

- tender/document ID;
- page/line;
- Arabic source span;
- English translation where present;
- normalized specification fields;
- application and qualification fields;
- reviewer label.

The current package does not fabricate Etimad excerpts. It provides the evaluation harness into which they can be added.

## 10. Entity-link controls

AI may propose that Arabic and English names refer to the same company, plant or standard. Final links require:

- deterministic identifiers where available;
- exact registration or document evidence;
- reviewer approval for ambiguous links;
- time-versioning of ownership/name changes.

## 11. Evidence synthesis

A model may draft narrative from approved structured evidence. The generated dossier must not introduce facts absent from the record. The structured fields and source pointers remain the authority.

## 12. Security and privacy

Production processing of Ministry documents requires:

- data-residency approval;
- access control by source classification;
- no provider training on confidential material;
- prompt/output logging policy;
- redaction where needed;
- model and prompt versioning;
- reviewer identity and override record.

## 13. GenUI boundary

The GenUI layer may select and configure approved components from structured analysis. It may not generate arbitrary executable code or invent controls at runtime. In a regulated setting, the component registry, action permissions and data bindings are reviewed artifacts.
