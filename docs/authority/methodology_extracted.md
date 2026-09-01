<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>STRATEGIC GEARS · INDUSTRIAL DECISION
SCIENCE</strong></p>
<p><strong>Industrial Opportunity<br />
Resolution Methodology</strong></p>
<p>A production-grade analytical system for converting HS-based
candidates into specification-level industrial decisions</p>
<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>Resolve the product before ranking the
opportunity.</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><strong>Test incumbent capability before recommending new
entry.</strong></td>
</tr>
<tr class="even">
<td><strong>Apply the smallest intervention that changes the
outcome.</strong></td>
</tr>
</tbody>
</table>
<p>Prepared for the Industrial Incentives Team<br />
Kingdom of Saudi Arabia<br />
August 2026</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**0. Document Map and Evidence Boundary**

This document specifies the analytical solution itself: the data
contract, screening rules, specification-resolution protocol,
plant-capability test, demand model, intervention logic, uncertainty
controls, AI boundaries, decision record and outcome-learning mechanism.
It is deliberately independent of any particular software platform or
delivery model.

| **Section**    | **Purpose**                                                                     |
|----------------|---------------------------------------------------------------------------------|
| **1**          | Decision object and governing principles                                        |
| **2**          | Canonical opportunity record                                                    |
| **3**          | Data contract and harmonisation                                                 |
| **4**          | Candidate-generation rulebook, including full/degraded/disabled execution paths |
| **5**          | Test 1 — genuine gap and bilingual specification resolution                     |
| **6**          | Test 2 — incumbent capability, sector profiles and brownfield route             |
| **7**          | Test 3 — unsupported economics and minimum effective intervention               |
| **8**          | Strategic value, resilience and portfolio sequencing                            |
| **9**          | Expected value of information                                                   |
| **10**         | AI, deterministic services and accountable authority                            |
| **11**         | Evidence governance, snapshots, validation and calibration                      |
| **12**         | End-to-end decision algorithm                                                   |
| **13**         | Worked case A — HS 721049 zinc-coated flat steel                                |
| **14**         | Worked case B — HS 390210 polypropylene; generic capacity support rejected      |
| **15**         | Decision Dossier and supporting evidence pack                                   |
| **16**         | Outcome learning and recalibration                                              |
| **Appendices** | Formulas, thresholds, data dictionary and source register                       |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>EVIDENCE BOUNDARY</strong></p>
<p>The Ministry’s brief requires specific investable opportunities, not
broad sectors; specification-level definition, genuine-gap testing,
incumbent-versus-new-entry analysis, proportionate intervention and a
repeatable method. Product-specific conclusions require product-line
evidence. Missing values remain unresolved rather than being replaced by
persuasive estimates. The public worked cases in Sections 13 and 14
demonstrate both outcomes the method must support: disciplined
investigation where the route is not yet proven, and rejection of
generic capacity support where evidence does not justify it.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**1. Decision Object and Governing Principles**

*The method ranks actions after resolving the industrial object.*

The unit of analysis is not an HS code. An HS code is a customs
coordinate that may contain multiple commercial products, grades,
dimensions, purity levels, coatings, applications and qualification
regimes. The decision object is a
Product–Specification–Application–Capability record tied to evidence.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>INVESTABLE OBJECT = PRODUCT × SPECIFICATION × APPLICATION
× CAPABILITY × DEMAND × ROUTE</strong></p>
<p>A candidate cannot advance while any decision-critical term remains
unresolved. A high import value can create a research priority; it
cannot, by itself, create an investable opportunity.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**1.1 The five governing principles**

- **Resolve identity before economics.** No financial, strategic or
  policy conclusion is valid until the commercial product, relevant
  specification and end use are defined.

- **Use administrative evidence as domestic ground truth.** Production,
  plant, customs, application and approved-deal records are primary for
  domestic facts; external data challenges and enriches them.

- **Brownfield is tested before greenfield.** A new factory is
  considered only after existing capacity, upgrade, certification,
  debottlenecking, technology licensing and joint-venture routes have
  been tested.

- **Intervention is a residual, not a starting assumption.** The first
  policy option is no action. Support is justified only when a verified
  market failure or strategic externality remains and the proposed
  action is additional.

- **Uncertainty changes the decision state.** Weak evidence does not
  lower a score invisibly; it changes the output to INVESTIGATE and
  identifies the next fact that can alter the route.

**1.2 Decision states and intervention routes**

| **Decision state** | **Meaning**                                                                                                    |
|--------------------|----------------------------------------------------------------------------------------------------------------|
| **REJECT**         | No genuine gap, uneconomic at efficient scale, unacceptable distortion, or hard technical/regulatory failure.  |
| **MONITOR**        | No immediate action; watch a defined trigger such as demand, regulation, technology or supplier concentration. |
| **INVESTIGATE**    | A material decision cannot yet be defended; acquire the minimum evidence with positive expected value.         |
| **ADVANCE**        | Evidence supports a route and the relevant hard gates are satisfied.                                           |

| **Route** | **Intervention**                                                  |
|-----------|-------------------------------------------------------------------|
| **0**     | No intervention                                                   |
| **1**     | Remove an administrative, classification or regulatory barrier    |
| **2**     | Information, market linkage or investor/technology matching       |
| **3**     | Certification, testing, metrology or quality-system support       |
| **4**     | Demand aggregation, procurement commitment or conditional offtake |
| **5**     | Debottlenecking, yield improvement or incremental line expansion  |
| **6**     | Technology licensing, specialist line or joint venture            |
| **7**     | Targeted greenfield entry                                         |
| **8**     | Shared enabling infrastructure serving several opportunities      |

**2. Canonical Opportunity Record**

*One record must be sufficient for data, engineering, competition,
finance and policy review.*

Every candidate is represented in a versioned record. The record is not
a narrative report; it is the structured source from which the screening
ledger, technical evidence pack and one-page Decision Dossier are
generated.

| **Block**         | **Minimum content**                                                                                                                                  |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Identity**      | HS revision and HS6; Saudi national tariff line; Arabic and English commercial names; chemical/material identity; model/part number where relevant.  |
| **Specification** | Grade, purity, composition, coating, dimensions, tolerances, performance, standard, regulatory class, packaging and approved-supplier requirements.  |
| **Application**   | End use, customer segment, operating environment, qualification pathway and substitutability.                                                        |
| **Demand**        | Historical value and physical quantity; retained imports; verified domestic sales; customer concentration; committed and announced pipeline; timing. |
| **Supply**        | Operating plants, production line, effective capacity, utilisation, yield, specification range, certifications, planned expansions and exports.      |
| **Capability**    | Feedstocks, process route, equipment envelope, laboratory/metrology, EHS, utilities, skills, technology/IP and customer access.                      |
| **Economics**     | Minimum efficient scale, capex, opex, delivered cost, price range, margin, hurdle rate, unsupported NPV/IRR and downside scenarios.                  |
| **Policy**        | Tariffs, exemptions, procurement rules, local-content mechanisms, existing support, competition effects and strategic criticality.                   |
| **Evidence**      | Source, date, period, field lineage, transformation, status, confidence, contradiction and reviewer.                                                 |
| **Decision**      | State, route, alternatives rejected, minimum intervention, conditions, sunset, kill condition and next evidence action.                              |

**2.1 Evidence status**

| **Class** | **Definition**                                                                                           |
|-----------|----------------------------------------------------------------------------------------------------------|
| **A**     | Official, current, product-specific and validated against the responsible authority or owner.            |
| **B**     | Authoritative but aggregated, lagged, transformed or awaiting minor validation.                          |
| **C**     | Credible technical/public evidence or company disclosure not yet confirmed by the responsible authority. |
| **D**     | Proxy, inference, model assumption or incomplete mapping.                                                |
| **E**     | Missing, contradictory, unusable or outside the classification boundary.                                 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>ADVANCE GATE</strong></p>
<p>An opportunity cannot reach ADVANCE if product identity, demand at
the required specification, domestic supply/capability, or a hard
regulatory/process gate is Class D or E. Such a case is INVESTIGATE,
regardless of its strategic appeal.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**3. Data Contract and Harmonisation**

*Most analytical failure occurs before modelling: in classification,
quantity, origin, entity and time.*

**3.1 Required source hierarchy**

| **Fact type**                        | **Preferred authority**                                                                                                    |
|--------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| **Domestic production and capacity** | Ministry administrative records, plant confirmations and official statistics.                                              |
| **Customs and trade**                | Saudi administrative customs for domestic decisions; UN Comtrade/WITS for international comparison and mirror diagnostics. |
| **Specifications and demand**        | Official standards, tenders, awards, approved-vendor documents, certificates and customer technical requirements.          |
| **Plant capability**                 | Licences, line-level records, producer technical sheets, equipment/certification evidence and technical review.            |
| **Project economics**                | Validated cash-flow templates, audited or approved assumptions and deterministic calculations.                             |
| **External strategic evidence**      | Official NIS/NIDLP, complexity datasets, regulation, project status and technology evidence with frozen release dates.     |

**3.2 Harmonisation rules**

- **HS revision discipline.** Every record stores the reported
  classification and year. Cross-revision links use official
  concordances. One-to-many mappings remain one-to-many; they are not
  forced into a single successor code.

- **National tariff-line preservation.** The Saudi tariff suffix is
  retained because specification and policy distinctions often disappear
  at HS6.

- **Quantity integrity.** Value, net weight, supplementary quantity and
  quantity unit are stored separately. Unit-value analysis is disabled
  when units are missing, estimated, non-comparable or physically
  implausible.

- **Valuation and currency.** Imports remain CIF and exports FOB unless
  adjusted explicitly. Original currency and nominal value are
  preserved; any deflation or currency conversion is versioned.

- **Re-export and origin treatment.** Gross imports, re-imports,
  domestic-origin exports and re-exports are separated wherever fields
  permit. Mirror statistics are anomaly evidence, not a replacement for
  the reporter’s official record.

- **Entity resolution.** Plants, companies, applicants, importers and
  parent groups receive persistent IDs. Names are normalised in Arabic
  and English; mergers and ownership changes are time-versioned.

- **Document normalisation.** Arabic/English numerals, units, symbols,
  transliterations, standard references and abbreviations are converted
  to a controlled vocabulary while the original text span remains
  attached.

- **As-of dating.** Every feature is reproducible as of a decision date.
  Later plant openings, tender awards or price data cannot leak into
  historical validation.

**3.3 Core trade measures**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Retained imports = Gross imports − Verified
re-exports</strong></p>
<p>If re-export data is unavailable, the value remains gross and the
confidence class is reduced.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Net import exposure = Retained imports − Domestic-origin
exports</strong></p>
<p>This is a screening measure. It is not domestic demand and must not
be interpreted as a plant opportunity without production and
specification evidence.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Apparent consumption = Domestic production + Retained
imports − Domestic-origin exports</strong></p>
<p>Use physical quantities wherever possible; value-based apparent
consumption is highly exposed to price movements.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **Import penetration = Retained imports ÷ Apparent consumption** |
|------------------------------------------------------------------|

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Supplier HHI = Σ (supplier share)²</strong></p>
<p>Shares are calculated on retained import value and quantity
separately. Concentration creates a resilience flag, not an automatic
localisation recommendation.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**4. Candidate-Generation Rulebook**

*Cheap, auditable rules determine where deep analysis is justified.*

A candidate is generated through one or more independent rules. No
candidate advances because a composite score is high. Every trigger is
recorded, and each trigger has an explicit false-positive test.
Thresholds are operational defaults, not economic laws: each is
versioned, sector-scoped, sensitivity-tested and calibrated against
known Ministry cases before policy use.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>THRESHOLD DISCIPLINE</strong></p>
<p>The rulebook is intentionally falsifiable. A reviewer may challenge
any default, but must preserve the disclosed feature, formula, execution
state and decision path. Thresholds are never changed case by case to
improve a preferred result.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **Execution state** | **Data condition**                                                                              | **Permitted analytical effect**                                                                                    |
|---------------------|-------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| **FULL**            | Required grain, continuity, quantities and classifications are available.                       | The formal rule may fire and support later route analysis, subject to all quality gates.                           |
| **DEGRADED**        | A documented lower-grain proxy is available, but one or more full-rule requirements are absent. | May generate INVESTIGATE, MONITOR or REJECT. It cannot by itself support ADVANCE or establish a specification gap. |
| **DISABLED**        | The available data cannot support even a defensible proxy.                                      | No inference. The record states the missing input and uses EVSI to decide whether to obtain it.                    |

| **Rule** | **Name**                               | **Initial operating test**                                                                                                                                                         | **Result**                                                                                |
|----------|----------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| **R0**   | Identity gate                          | Current HS/tariff-line mapping is valid; one-to-many mappings and ambiguous descriptions remain visible.                                                                           | If unresolved, classify as an evidence case; do not score.                                |
| **R1-F** | Persistent retained exposure — full    | Positive retained net import exposure in ≥30 of 36 months or three consecutive complete years, above the higher of the policy floor or the 75th percentile within its NIS cluster. | Generate demand-gap candidate.                                                            |
| **R1-D** | Persistence signal — degraded          | At least three positive observed years within a four-year window; no interpolation; no known classification break; materiality test still passed.                                  | Generate INVESTIGATE only; confidence capped at C.                                        |
| **R2**   | Quantity-led expansion                 | Physical quantity is rising and contributes ≥60% of absolute log-change decomposition; initial quantity CAGR trigger ≥5%.                                                          | Separate structural demand from price inflation.                                          |
| **R3**   | Supplier concentration                 | HHI ≥0.25 or top supplier ≥50% of retained imports.                                                                                                                                | Generate resilience/diversification candidate; not automatically localisation.            |
| **R4-F** | Product-tier heterogeneity — full      | Comparable quantity coverage ≥70% of import value; ≥5 partner-month/tariff-line cells; two-cluster model improves BIC by \>10; medians differ ≥1.5×; each cluster ≥10%.            | Open specification investigation; clusters remain hypotheses until technically confirmed. |
| **R4-D** | Unit-value dispersion — degraded       | Only annual/partner data exist, but valid quantities cover material trade and robust dispersion or partner-mix discontinuity is visible.                                           | Open descriptive product-mix investigation; no statistical cluster or grade claim.        |
| **R5**   | Domestic supply plus continued imports | Verified domestic production exists while retained imports exceed 20% of apparent consumption or the cluster materiality threshold.                                                | Test specification, qualification, capacity, price and application mismatch.              |
| **R6**   | Capacity pressure                      | Effective utilisation ≥85% and specification-matched demand exceeds effective qualified capacity by ≥10% for a sustained period.                                                   | Test debottlenecking or incumbent expansion.                                              |
| **R7**   | Latent domestic capacity               | Effective utilisation ≤70% and local certified product is equivalent to the imported specification and available in the demand window.                                             | Test no-support, market linkage, procurement or barrier removal.                          |
| **R8**   | Committed future demand                | Probability-adjusted awarded/financed demand adds ≥20% to base demand or fills ≥25% of minimum efficient scale.                                                                    | Advance timing and offtake analysis.                                                      |

**4. Candidate-Generation Rulebook — continued**

| **Rule** | **Name**                          | **Initial operating test**                                                                                                                                                                                                                   | **Result**                                                                                    |
|----------|-----------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| **R9-S** | Coarse incumbent adjacency screen | A verified Saudi plant operates in the same product/process family plus at least one additional signal: matching feedstock, core process, equipment, adjacent output, relevant certification or imported inputs; no known hard-gate failure. | Open the full Test-2 capability assessment. Do not assign D\* or select a route at screening. |
| **R10**  | Strategic criticality             | Critical product, material resilience externality or enabling linkages verified by the responsible authority.                                                                                                                                | Run strategic-value case even if market size is modest.                                       |
| **R11**  | Economic exclusion                | Downside delivered cost is structurally \>25% above import parity with no verified strategic externality or export path.                                                                                                                     | Reject or monitor; do not use incentives to hide structural uncompetitiveness.                |
| **R12**  | Evidence-value trigger            | Probability that one missing fact changes state/route × value of decision change exceeds evidence cost and delay.                                                                                                                            | Commission targeted evidence only.                                                            |

**4.1 Price–quantity decomposition**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Δ ln(Trade value) = Δ ln(Physical quantity) + Δ ln(Unit
value)</strong></p>
<p>When quantity rises and unit value falls, growth is quantity-led.
When value rises only because unit value rises, the product does not
pass the volume-growth rule.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Quantity contribution share = |Δ ln Q| ÷ (|Δ ln Q| + |Δ
ln UV|)</strong></p>
<p>The initial R2 trigger uses a contribution share of 60% and positive
quantity growth. Sector calibration can alter the threshold but not the
disclosed formula.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**4.2 Hard exclusions before deep analysis**

- The commercial product cannot be separated from a highly heterogeneous
  residual code and no product-level evidence is available.

- The sustainable market is smaller than minimum efficient scale under
  downside demand and there is no credible export contract.

- A legal, safety, environmental, IP or customer-qualification hard gate
  cannot be satisfied.

- Domestic production already meets the required specification with
  material idle capacity and no binding market failure is found.

- The apparent gap is dominated by re-export, one-off project demand,
  temporary price arbitrage or classification discontinuity.

- The intervention would create unacceptable redundant capacity or crowd
  out a more efficient incumbent.

**5. Test 1 — Genuine Gap Resolution**

*The method resolves what is missing: quantity, specification,
application, timing, resilience—or evidence.*

**5.1 Specification extraction schema**

| **Field group**             | **Required extraction**                                                                                                  |
|-----------------------------|--------------------------------------------------------------------------------------------------------------------------|
| **Commercial identity**     | Arabic and English name, material/chemical identity, model/part number, synonyms and excluded meanings.                  |
| **Composition and grade**   | Purity, alloy, polymer/additive package, coating, active content, impurity limits and grade designation.                 |
| **Geometry**                | Thickness, width, length, diameter, particle size, tolerance, surface and packaging.                                     |
| **Performance**             | Strength, barrier, conductivity, corrosion, temperature, pressure, sterility, shelf-life or agronomic performance.       |
| **Standard and regulation** | SASO/GSO/SFDA/ASTM/ISO/EN/USP/EP or customer standard; edition and mandatory clauses.                                    |
| **Application**             | End-use industry, operating environment, criticality and substitutable alternatives.                                     |
| **Qualification**           | Approved supplier, customer test, regulatory registration, GMP, fire rating, food contact, automotive or other approval. |
| **Evidence span**           | Exact document, page/line, original Arabic/English text, extraction confidence and reviewer status.                      |

**5.1.1 Demonstrated Arabic–English specification extraction**

The extraction engine must preserve the original language span,
normalise the technical field, reconcile units and state what the source
does and does not prove. The example below uses corresponding UNICOIL
Arabic and English product pages; it demonstrates the extraction
contract, not customer qualification or current spare capacity.

| **Field**                     | **Arabic source span**                                           | **English source span**                                                                    | **Normalised value**                                                 | **Decision boundary**                                                                          |
|-------------------------------|------------------------------------------------------------------|--------------------------------------------------------------------------------------------|----------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| **Standard**                  | اعتمدت الهيئة السعودية للمواصفات والمقاييس ASTM A653 / A653M     | SASO … has adopted ASTM A653/A653M                                                         | SASO–ASTM A653/A653M                                                 | Producer-stated conformance; edition and tender clause still require confirmation.             |
| **Mandatory minimum coating** | الحد الأدنى الإلزامي … هو 60 جم / م2                             | The mandatory minimum zinc coating … is 60 gsm                                             | 60 g/m², total both sides                                            | Resolves the stated local minimum, not the specification of each imported shipment.            |
| **Exposure condition**        | التطبيقات القريبة من البحر … تتطلب طلاءًا أثقل                    | Applications closer to the sea, offshore, or in urban areas require a heavier zinc coating | Heavier coating may be required by environment                       | Application and installation location remain decision-critical.                                |
| **Product envelope**          | السماكة 0.18–3.00 مم؛ العرض 600–1300 مم؛ طبقة الزنك 45–350 جم/م2 | Thickness and width ranges; web product range 40–400 g/m²                                  | Dimensions and coating envelope recorded with source-specific values | Conflicting ranges are retained in the contradiction register and confirmed with the producer. |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>EXTRACTION CONTROL</strong></p>
<p>The source span is evidence of a published specification. It does not
prove effective capacity, local allocation, customer approval, current
availability or equivalence to the imported product. Those facts remain
separate fields and gates.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**5.2 Unit-value diagnostic — full and degraded paths**

**5.2.1 Full-data path (R4-F)**

**1.** Retain trade value, net weight, supplementary quantity, quantity
unit, partner, month, tariff line and reporter status.

**2.** Exclude zero/missing weights, incompatible units, obviously
mis-scaled records and records below a documented de minimis level for
clustering.

**3.** Calculate unit value at the finest stable grain: month × partner
× tariff line, not only annual HS6 totals.

**4.** Transform to log unit value; inspect data completeness, partner
mix, structural breaks and changes in customs classification.

**5.** Compare one-cluster and multi-cluster models using BIC and
stability under resampling. Do not keep a cluster supported only by tiny
shipments.

**6.** Compare cluster membership with origin, description, dimensions,
standard, importer/offtaker and end use.

**7.** Confirm any grade or specification conclusion using tenders,
standards, invoices, certificates, catalogues or plant evidence.

**5.2.2 Degraded-data path (R4-D)**

When month × partner × tariff-line data are unavailable, the system may
calculate annual partner unit values only if value and comparable
quantities are valid. It reports coverage, robust dispersion, partner
mix and outliers, but does not fit or claim specification clusters.

| **Degraded step**   | **Required action**                                                                                                                |
|---------------------|------------------------------------------------------------------------------------------------------------------------------------|
| **Coverage**        | Report the share of import value and quantity with valid comparable units; disable the diagnostic when coverage is inadequate.     |
| **Dispersion**      | Use weighted medians, interquartile ranges and material partner observations; retain all raw cells and flag small-volume extremes. |
| **Interpretation**  | Classify the result only as a product-mix/specification research signal. Do not label a premium observation as a higher grade.     |
| **Decision effect** | R4-D can create INVESTIGATE. It cannot establish a genuine specification gap, justify support or select brownfield/greenfield.     |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>NON-NEGOTIABLE INTERPRETATION RULE</strong></p>
<p>A unit-value premium is not proof of higher quality. It may reflect
freight, packaging, order size, timing, origin, small samples, errors or
a mixed HS basket. Unit values generate hypotheses; technical evidence
resolves them.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**5.3 Gap taxonomy and decision test**

| **Gap class**               | **Diagnostic definition**                                                                       | **Typical route**                                                                |
|-----------------------------|-------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| **False / measurement**     | Re-export, classification change, one-off import, price effect, product mix or data error.      | Reject, monitor or correct data.                                                 |
| **Quantity**                | Demand at the required specification exceeds effective qualified capacity.                      | Debottleneck, expand or add capacity.                                            |
| **Specification / quality** | Domestic product exists but fails grade, purity, coating, performance or quality system.        | Quality, process, lab, certification or technology upgrade.                      |
| **Application**             | Domestic production serves a different end use or customer qualification.                       | Application-specific line/qualification or targeted investor.                    |
| **Timing**                  | Demand window precedes available supply or expansion.                                           | Temporary sourcing, phased offtake or timed investment.                          |
| **Resilience**              | Supply may be adequate, but concentration/criticality creates unacceptable disruption exposure. | Diversification, strategic stock, regional source or localisation if economical. |
| **Evidence**                | Product identity, demand, supply or process cannot be defended.                                 | INVESTIGATE; specify the minimum next fact.                                      |

| **Specification-adjusted gap = Demand meeting required specification − Verified effective capacity meeting that specification** |
|---------------------------------------------------------------------------------------------------------------------------------|

**6. Test 2 — Incumbent Capability and Brownfield Route**

*Plant-level capability replaces country-level adjacency as the route
decision.*

Product Space and trade complexity can identify national capability
priors. They cannot establish whether a particular Saudi plant can
produce a target specification. The brownfield test therefore compares
the target process and qualification requirements with line-level
evidence.

**6.1 Effective capacity**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Effective qualified capacity = Nameplate × Availability ×
Yield × Qualification share × Market-allocated share</strong></p>
<p>Nameplate capacity alone is not supply. Qualification share is the
portion capable of the target specification; market-allocated share
removes capacity committed to other products or export
contracts.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**6.2 Common capability ontology**

| **\#** | **Dimension**                            | **Weight** | **Evidence question**                                                                    |
|--------|------------------------------------------|------------|------------------------------------------------------------------------------------------|
| **1**  | Feedstock / chemistry                    | 10%        | Correct substrate, feedstock, precursor and impurity control.                            |
| **2**  | Core process route                       | 20%        | Required chemistry, forming, coating, synthesis, fabrication or transformation sequence. |
| **3**  | Equipment and operating envelope         | 15%        | Scale, temperature, pressure, atmosphere, tolerances, dimensions and automation.         |
| **4**  | Finishing / specification control        | 10%        | Coating, purification, heat treatment, surface, formulation or packaging.                |
| **5**  | QA, laboratory and metrology             | 10%        | Test methods, analytical capability, calibration, release and traceability.              |
| **6**  | Certification and customer qualification | 10%        | Regulatory approval, approved-supplier status and application qualification.             |
| **7**  | Capacity and time window                 | 10%        | Effective spare capacity, debottlenecking potential and schedule fit.                    |
| **8**  | Utilities, EHS and permitting            | 10%        | Power, gas, water, waste, emissions, occupational safety and permits.                    |
| **9**  | Skills and market integration            | 5%         | Workforce, suppliers, customers, service network and operating know-how.                 |

**6.3 Sector-specific weight profiles and hard gates**

The nine dimensions are common, but their weights and hard gates are
sector-specific. A profile is approved and frozen for a sector cycle; it
is never altered case by case to improve a preferred route. Percentages
below are initial calibration profiles and sum to 100 in the order:
feedstock / process / equipment / finishing / QA / certification /
capacity / utilities-EHS / skills-market.

| **Sector profile**       | **Initial weights (%)**                  | **Illustrative hard gates**                                                                                                |
|--------------------------|------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| **Coated steel**         | 5 / 20 / 20 / 15 / 10 / 10 / 10 / 5 / 5  | Substrate range; width/thickness; coating route and mass; surface treatment; mandatory/customer standard.                  |
| **Technical plastics**   | 15 / 20 / 15 / 10 / 10 / 15 / 5 / 5 / 5  | Polymer/additive compatibility; conversion route; tooling; barrier/performance; food, medical or automotive qualification. |
| **Pharma/API**           | 10 / 20 / 10 / 10 / 15 / 15 / 5 / 10 / 5 | Named molecule and synthesis route; GMP; containment; impurity control; analytical validation; effluent; IP/FTO.           |
| **Fertilizers**          | 15 / 20 / 15 / 10 / 5 / 5 / 10 / 15 / 5  | Feedstock route; formulation/granulation; nutrient basis; agronomic performance; emissions and safe handling.              |
| **Fabricated aluminium** | 10 / 15 / 15 / 15 / 10 / 15 / 10 / 5 / 5 | Alloy; forming/fabrication; heat treatment; joining/finishing; engineering certification; customer liability.              |

**6.4 Dimension states, evidence coverage and uncertainty**

| **State** | **Meaning**                                                                                                |
|-----------|------------------------------------------------------------------------------------------------------------|
| **0**     | Verified present at target requirement.                                                                    |
| **1**     | Minor, known upgrade: debottleneck, tooling, certification or limited capex.                               |
| **2**     | Major new line, specialist technology or JV required, but existing site/assets materially reduce the leap. |
| **3**     | Fundamentally absent; existing plant provides little route advantage.                                      |
| **U**     | Unknown; evidence acquisition required.                                                                    |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>K = Σ(wj for known dimensions)</strong></p>
<p>K is the known-evidence weight coverage.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>U = 1 − K = Σ(wj for unknown dimensions)</strong></p>
<p>If K = 0, D* is not computed and the case is INVESTIGATE.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>D_known = Σ(wj × dj / 3) ÷ K | D* = min(1, D_known +
λU)</strong></p>
<p>Initial λ = 0.50. A route band is issued only when K ≥ Kmin (initial
Kmin = 0.70), every sector hard gate is resolved, and no hard gate is
scored 3. Unknown evidence cannot improve adjacency.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**6.5 Route bands**

| **Initial calibration band** | **Route class**           | **Interpretation**                                                              |
|------------------------------|---------------------------|---------------------------------------------------------------------------------|
| **D\* ≤ 0.20**               | Immediate adjacency       | Use idle capacity, market linkage, yield improvement or simple debottlenecking. |
| **0.20 \< D\* ≤ 0.40**       | Incremental upgrade       | Brownfield capex, quality system, certification or additional finishing stage.  |
| **0.40 \< D\* ≤ 0.65**       | Major line / JV adjacency | Use existing site and assets with technology partner or new specialist line.    |
| **D\* \> 0.65**              | Greenfield likely         | Test new investor only if efficient scale and demand are robust.                |

Source note: These bands, λ and Kmin are initial operating defaults.
They must be back-tested by sector against known plant upgrades, failed
projects, greenfield cases and no-action decisions before becoming
policy thresholds.

**6.6 Brownfield-versus-greenfield counterfactual**

**1.** Can the incumbent meet the target specification with existing
assets and non-capital intervention?

**2.** If not, what exact equipment, process, technology, certification
or utility is missing?

**3.** What are the brownfield capex, schedule, yield and qualification
risks versus greenfield?

**4.** Does sustainable demand support both the incumbent and a new
efficient-scale entrant under downside conditions?

**5.** Would new entry displace efficient domestic production, reduce
utilisation or create persistent overcapacity?

**6.** Is a technology-bearing JV superior to either pure incumbent
expansion or independent greenfield entry?

**7. Test 3 — Minimum Effective Intervention**

*Support is selected by the binding constraint and measured against the
no-action counterfactual.*

**7.1 Unsupported project economics**

Every route is modelled on a common, auditable cash-flow schema.
Brownfield is evaluated before greenfield, and non-financial
interventions are evaluated before financial support.

| **Required cash-flow block** | **Minimum fields**                                                                                                           |
|------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| **Investment**               | Engineering, equipment, construction, certification, customer qualification, working capital, contingency and commissioning. |
| **Operations**               | Feedstock, utilities, labour, yield/ramp-up, maintenance, consumables, EHS, waste, logistics and inventory.                  |
| **Revenue**                  | Volume and price by target specification; domestic/export split; qualification timing; downside/base/upside demand.          |
| **Finance and tax**          | Funding structure, financing cost, depreciation, tax, duties/exemptions, incentive timing, residual value and delay.         |
| **Risk**                     | Execution, technology, price, demand, feedstock, qualification and schedule sensitivities.                                   |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>NPV₀ = Σ [Free cash flowt / (1 + h)^t] − Initial
investment</strong></p>
<p>h is the validated investor hurdle rate. Cash flows, tax,
depreciation, working capital, terminal value and financing assumptions
are deterministic and auditable.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **If NPV₀ ≥ 0 and no material market failure remains → Financial intervention = 0** |
|-------------------------------------------------------------------------------------|

**7.1.1 Mandatory route sequence**

| **Order** | **Case tested**                                                                           |
|-----------|-------------------------------------------------------------------------------------------|
| **1**     | No action and unsupported use of existing qualified capacity.                             |
| **2**     | Unsupported incumbent debottlenecking or upgrade.                                         |
| **3**     | Incumbent route with non-financial barrier, qualification or demand intervention.         |
| **4**     | Incumbent route with minimum financial support, only if unsupported economics fail.       |
| **5**     | Technology licence or joint venture using existing assets.                                |
| **6**     | Unsupported greenfield.                                                                   |
| **7**     | Supported greenfield, only after every lower-cost route fails and competition gates pass. |

**7.2 Minimum effective support and hurdle-rate control**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>S* = min { S : NPV(project | S) ≥ 0 and IRR(project | S)
≥ h }</strong></p>
<p>Support can be financial or non-financial. The selected instrument
must address the binding constraint; a capex grant cannot solve missing
customer qualification or fragmented demand.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>HURDLE-RATE CONTROL</strong></p>
<p>The hurdle rate h is Ministry-approved, sector- and risk-consistent,
calibrated against comparable deal profiles where appropriate, and
sensitivity-tested. It is never reverse-engineered to make a preferred
project pass.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**7.3 Incremental national value**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>ΔNV = ΔDomestic value added + ΔExports + Resilience value
+ Knowledge/skill spillovers + Fiscal receipts − Government cost −
Displacement − Resource/environment cost − Risk allowance</strong></p>
<p>Every term is measured relative to the no-intervention
counterfactual. Gross project output is not national value.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Proceed only if ΔNV(S*) &gt; Fiscal cost(S*) +
Displacement + Distortion + Risk</strong></p>
<p>A financially viable project can still be a poor public intervention.
Gross output, jobs or capex do not replace incremental national
value.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**7.4 Intervention decision tree**

| **Finding**                                                  | **Route**                                                                                         |
|--------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| **No verified gap**                                          | REJECT or INVESTIGATE; no intervention.                                                           |
| **Verified gap; unsupported economics already viable**       | No financial support. Remove only a proven administrative or information barrier.                 |
| **Specification or qualification is binding**                | Certification, testing, metrology, quality system, process improvement or customer qualification. |
| **Demand fragmentation/uncertainty is binding**              | Demand aggregation, procurement commitment or conditional offtake.                                |
| **Incumbent capacity/process is binding and D\* ≤ 0.40**     | Debottlenecking or incremental expansion, conditional on delivery and additionality.              |
| **Technology is binding and 0.40 \< D\* ≤ 0.65**             | Technology licence, JV or specialist line using existing assets.                                  |
| **No qualified incumbent; D\* \> 0.65; demand supports MES** | Targeted greenfield investor, with competition and downside tests.                                |
| **Several opportunities share the same missing enabler**     | Shared laboratory, treatment, tooling, utility, logistics or training capability.                 |

**7.5 Competition and distortion gates**

| **Gate**                      | **Required analysis**                                                                                                                                                                 |
|-------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Post-entry capacity ratio** | (Existing effective capacity + proposed capacity) ÷ sustainable downside demand. A ratio \>1.25 is a default warning requiring an export contract or exceptional strategic rationale. |
| **Incumbent displacement**    | Estimate production, utilisation, employment and investment displaced from efficient existing producers.                                                                              |
| **Market concentration**      | Assess HHI before and after intervention, but do not equate lower concentration with benefit if efficient scale is destroyed.                                                         |
| **Non-additional support**    | Reject support that rewards investment already approved, financed or commercially necessary.                                                                                          |
| **Instrument neutrality**     | Compare support to incumbent, entrant, buyer, shared enabler and no action using the same national-value basis.                                                                       |
| **Conditions and sunset**     | Tie support to specification, capacity, timing, local value, export, employment or resilience outcomes; include milestone suspension and clawback where appropriate.                  |

**8. Strategic Value, Resilience and Portfolio Logic**

*Commercial viability and national strategic value remain separate
dimensions.*

A product may be commercially attractive but strategically ordinary,
strategically critical but commercially weak, or both. The method
preserves these distinctions rather than hiding them in one weighted
score.

| **Decision vector**        | **Contents**                                                                                                                 |
|----------------------------|------------------------------------------------------------------------------------------------------------------------------|
| **Market / gap**           | Retained demand, quantity growth, import penetration, specification-adjusted gap, customer concentration and price dynamics. |
| **Strategic / resilience** | Criticality, NIS alignment, supplier concentration, enabling linkages, knowledge spillovers and option value.                |
| **Execution feasibility**  | Capability distance, efficient scale, cost position, technology access, standards, infrastructure and time.                  |
| **Evidence confidence**    | Completeness, authority, recency, product specificity, contradictions and sensitivity.                                       |

**8.1 Complexity and Product Space as priors**

Economic complexity metrics are useful for national diversification
hypotheses. They are not plant-capability measures and must not override
line-level process, specification, cost or customer evidence. The Atlas
release, product classification, trade year and country coverage are
frozen for each decision cycle; missing PCI, RCA or distance values are
not imputed.

**8.2 Portfolio sequencing**

| **Portfolio concept**      | **Decision use**                                                                                          |
|----------------------------|-----------------------------------------------------------------------------------------------------------|
| **Unlock nodes**           | A shared laboratory, treatment, tooling, utility or input that enables several otherwise viable products. |
| **Dependencies**           | Product A or capability X must exist before products B–D become competitive.                              |
| **Common risk**            | Several shortlisted products rely on the same imported feedstock, customer, utility or technology owner.  |
| **Mutual cannibalisation** | Separate product opportunities compete for the same demand and should not all be supported.               |
| **Option value**           | A modest initial opportunity creates capabilities that reduce distance to more valuable future products.  |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>RANKING RULE</strong></p>
<p>Use Pareto frontiers and route-specific queues. Produce separate
rankings for (a) robust opportunities ready to advance, (b) incumbent
upgrades, (c) greenfield candidates, (d) resilience cases, and (e)
high-value evidence investigations. A single ordinal list of 1,300
products is not the decision.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**8.3 Industrial dependency graph and unlock value**

Portfolio analysis represents opportunities, inputs, processes,
technologies, shared laboratories, utilities, logistics, skills, buyers,
plants and policy instruments as linked nodes. A dependency edge is
created only when the relationship is evidence-backed and
decision-relevant.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>UnlockValue(e) = Σi [P(i,e) × ΔNVi ×
DependencyShare(i,e)] − Cost(e)</strong></p>
<p>P(i,e) is the probability that enabler e removes the binding
constraint for opportunity i. The formula is used to compare a shared
enabler with separate product interventions, not to manufacture
precision where probabilities are weak.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

| **Portfolio output**      | **Operational test**                                                                                                         |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------|
| **Shared unlock node**    | One enabler removes a verified hard or binding constraint for several positive-value opportunities.                          |
| **Sequencing dependency** | Product/capability A must precede B because B’s cost, qualification or supply chain is not viable without A.                 |
| **Common exposure**       | Several opportunities depend on the same imported input, buyer, utility, technology owner or logistics path.                 |
| **Cannibalisation**       | Separate candidates compete for the same downside demand or incumbent capacity; aggregate support would create overcapacity. |
| **Option value**          | A modest first move creates verified capability that lowers future distance to higher-value products.                        |

**9. Expected Value of Information**

*Research is commissioned only when it can change a material decision.*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>EVSI = Σe P(e) × maxa E[V(a) | e] − maxa E[V(a)] −
Cost(e) − Delay cost(e)</strong></p>
<p>e is a possible evidence result; a is an available action; V is
incremental national value. Positive EVSI means the evidence is worth
obtaining before deciding.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**9.1 Practical approximation**

| **Approximate EVSI = P(route changes) × \|Value of best alternative − Value of current route\| − Evidence cost − Delay cost** |
|-------------------------------------------------------------------------------------------------------------------------------|

The probability of a route change is estimated from historical cases,
technical reviewer calibration or structured low/base/high elicitation.
The calculation is stored with the request. “Interesting information”
without a plausible decision effect receives zero priority.

| **Evidence option**                 | **Potential route effect**                                                                                            |
|-------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| **Customs invoice descriptions**    | Can separate commodity and certified grade; may move the case from greenfield to quality upgrade.                     |
| **Plant utilisation and yield**     | Can move the case between no action, debottlenecking and new capacity.                                                |
| **Customer qualification evidence** | Can confirm whether imports persist because the local product is technically unacceptable.                            |
| **Paid shipment/company data**      | Can identify named buyers or competitor expansions when open sources cannot resolve investor or demand concentration. |
| **Site visit or expert review**     | Can verify process/equipment hard gates for a high-value surviving case.                                              |
| **Laboratory test**                 | Can establish equivalence or specification failure where document evidence is insufficient.                           |

**10. AI, Deterministic Services and Human Authority**

*AI resolves language and ambiguity; code calculates; accountable
experts decide.*

| **AI task**                            | **Controlled use**                                                                                                                                     |
|----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Bilingual specification extraction** | Read Arabic and English tenders, regulations, standards, catalogues, certificates and applications; populate the fixed schema with exact source spans. |
| **Description normalisation**          | Resolve synonyms, transliterations, units, standards and commercial names while preserving original text.                                              |
| **Entity linkage**                     | Propose links among plant, company, importer, applicant, product and parent group; deterministic rules and reviewer approval govern final links.       |
| **Anomaly explanation**                | Summarise why unit values, partner mix, quantities or records appear inconsistent; never delete records silently.                                      |
| **Evidence synthesis**                 | Draft the Decision Dossier from approved structured evidence and identify contradictions and missing hard gates.                                       |
| **Research prioritisation**            | Estimate which missing fact is most likely to change the route, subject to an explicit EVSI calculation.                                               |

**10.1 Deterministic services**

- HS/tariff-line concordance, unit conversion and duplicate control.

- Trade, quantity, concentration, volatility, index decomposition and
  cluster diagnostics.

- Capacity, yield, mass balance, logistics, landed cost and minimum
  efficient scale.

- IRR, NPV, tax, depreciation, incentive, carbon and national-value
  calculations.

- Scenario simulation, thresholds, sensitivity, ranking and rule
  execution.

- Evidence completeness, versioning, confidence and audit checks.

**10.2 AI controls**

| **Control**                   | **Rule**                                                                                                          |
|-------------------------------|-------------------------------------------------------------------------------------------------------------------|
| **Schema-constrained output** | No free-form factual output enters the record; every field has a type, unit, allowed status and evidence pointer. |
| **Dual-pass extraction**      | One pass extracts; a second pass checks source fidelity, units, negation, exclusions and contradictions.          |
| **Deterministic validation**  | Standards, units, dates, HS codes, ranges and arithmetic are validated outside the language model.                |
| **Fail-closed hard gates**    | Unresolved product identity, process, regulatory or capacity gates route the case to INVESTIGATE.                 |
| **Human sign-off**            | Industrial, competition, fiscal and policy reviewers approve the relevant conclusion and any override.            |

**10.3 Autonomous analysis; accountable authorization**

The system may execute extraction, harmonisation, rule evaluation,
scenario analysis, route comparison and adversarial checks without
manual intervention. Public intervention and formal overrides remain
accountable acts. Human authority is concentrated at genuine decision
boundaries rather than inserted into every calculation.

| **Gate**                          | **Automated work**                                                   | **Accountable authority**                                        |
|-----------------------------------|----------------------------------------------------------------------|------------------------------------------------------------------|
| **Identity and measurement**      | Concordance, unit checks, anomaly flags, execution-state assignment. | Data steward or authorised analyst validates exceptions.         |
| **Process and capability**        | Capability matrix, K/D\* calculation, hard-gate identification.      | Sector/process expert confirms hard gates and plant reality.     |
| **Competition and additionality** | Counterfactual, overcapacity, displacement and S\* calculations.     | Competition and fiscal authority approves assumptions and tests. |
| **Final ADVANCE / intervention**  | Ranked routes, conditions, sunset and kill condition generated.      | Authorised policy decision-maker approves the public action.     |
| **Override**                      | Base result and evidence remain immutable.                           | Named authority records rationale, scope and expiry of override. |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>AUTHORITY PRINCIPLE</strong></p>
<p>Computation can be autonomous. The allocation of public support
cannot be anonymous.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**11. Evidence Governance and Quality Assurance**

*Every conclusion must be reproducible, challengeable and reversible.*

| **Evidence-passport field** | **Required content**                                                                                   |
|-----------------------------|--------------------------------------------------------------------------------------------------------|
| **Source identity**         | Authority, document/table/API endpoint, owner and access classification.                               |
| **Observation context**     | Reporting period, retrieval date, as-of date, geography, reporter, partner and product classification. |
| **Measurement**             | Original value, currency, unit, valuation basis, quantity type and estimation flags.                   |
| **Transformation**          | Formula, code version, parameters, exclusions and derived value.                                       |
| **Status**                  | Observed, calculated, model-estimated, inferred, assumption or unresolved.                             |
| **Confidence**              | A–E class and reasons.                                                                                 |
| **Contradiction**           | Competing source, conflict type, resolution status and chosen authority.                               |
| **Approval**                | Analyst, technical reviewer, policy authority, date and override rationale.                            |

**11.1 Quality gates**

| **Gate**                    | **Pass condition**                                                                                 |
|-----------------------------|----------------------------------------------------------------------------------------------------|
| **G0 — Identity**           | Correct revision, tariff line, commercial product and application boundary.                        |
| **G1 — Measurement**        | Quantity/unit completeness, origin/re-export treatment, time-series continuity and anomaly review. |
| **G2 — Gap**                | Specification-adjusted demand and effective qualified supply are separately evidenced.             |
| **G3 — Capability**         | Incumbent distance and hard gates reviewed by sector/process expertise.                            |
| **G4 — Economics**          | All calculations deterministic; unsupported and intervention scenarios reproducible.               |
| **G5 — Competition/policy** | Additionality, displacement, overcapacity and proportionality tested.                              |
| **G6 — Decision**           | Alternatives, confidence, conditions, kill condition and next evidence action visible.             |

**11.2 Validation and back-testing**

- Use only information available as of the historical decision date.

- Split validation by time; do not randomly mix near-identical products
  or revisions across train and test sets.

- Retain a transparent rule-based baseline before introducing machine
  learning.

- Back-test known successful investments, failed opportunities,
  non-additional support and incumbent upgrades.

- Measure route accuracy, false-positive rate, evidence cost, decision
  stability and reviewer disagreement—not only ranking correlation.

- Treat approval and rejection as process outcomes, not success labels;
  validate realised production, investment, value added, exports,
  resilience and fiscal/competition effects.

**11.3 Evidence snapshot and reproducibility bundle**

| **Frozen item**        | **Required control**                                                                                                            |
|------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| **Raw source**         | Store the raw extract, document or API response; do not rely only on a live web link.                                           |
| **Query contract**     | Record endpoint, reporter, partner, flow, product code, nomenclature, period and filters.                                       |
| **Retrieval identity** | Record retrieval timestamp, source refresh date where available and access classification.                                      |
| **Integrity**          | Calculate a cryptographic hash for every raw file and analytical output.                                                        |
| **Transformation**     | Store cleaning rules, code version, parameters, exclusions and intermediate tables.                                             |
| **Decision snapshot**  | Freeze features and evidence states at the decision date; later revisions create a new version rather than overwriting history. |
| **Link verification**  | Recheck public links and source availability immediately before circulation.                                                    |

**11.4 Calibration use of applications and approved-deal profiles**

| **Corpus**                             | **Permitted calibration use**                                                                                                                                                 | **Prohibited inference**                                                                |
|----------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| **Applications and rejection reasons** | Reconstruct evidence available at the original date; map reasons to rules/hard gates; test early detection; measure false positives/negatives and recurring missing evidence. | Rejection is not proof that the opportunity was economically bad.                       |
| **Approved-deal profiles**             | Validate cash-flow schema, hurdle-rate ranges, instrument timing, sensitivity conventions and unsupported-vs-supported route comparisons.                                     | Approval is not success and cannot be used as an automatic positive label.              |
| **Realised outcomes, when available**  | Calibrate route accuracy, additionality and intervention effects using time-based or matched/phased comparisons.                                                              | Do not infer causality from post-approval outcomes without a defensible counterfactual. |

**12. End-to-End Decision Algorithm**

*The full workflow is deterministic where possible and evidence-gated
where judgment is unavoidable.*

**1.** Freeze the decision date, data versions, HS revision and policy
taxonomy.

**2.** Create the product master and preserve every national tariff line
and Arabic/English description.

**3.** Run identity and data-quality gates; route unresolved mappings to
evidence work.

**4.** Compute retained imports, net exposure, quantity growth,
price–quantity decomposition, concentration, volatility and initial
demand signals.

5\. Apply candidate-generation rules using FULL, DEGRADED or DISABLED
execution states; record the exact trigger, confidence cap and
false-positive risks.

**6.** Extract and normalise specification, application and
qualification evidence from official/technical documents.

**7.** Classify the gap and calculate specification-adjusted demand and
effective qualified supply.

8\. Run R9-S to identify coarse incumbent adjacency; then map line-level
capabilities, resolve sector hard gates, calculate K and D\* only when K
≥ Kmin, and produce brownfield, JV and greenfield route hypotheses.

**9.** Build base, committed and announced demand scenarios without
mixing them.

**10.** Calculate unsupported economics, minimum effective intervention,
national value, additionality and distortion under base/downside/upside
scenarios.

**11.** Use EVSI to decide whether any missing evidence is worth
obtaining before the route is selected.

**12.** Assign decision state and intervention route; record
alternatives rejected, conditions, sunset and kill condition.

13\. Generate the Decision Dossier and frozen evidence bundle; obtain
the accountable domain, competition, fiscal and policy authorisations
required for the selected route.

**14.** Monitor realised outcomes and recalibrate rules only after
sufficient comparable evidence exists.

**12.1 Pseudocode**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>for candidate in product_universe:<br />
identity = resolve_identity(candidate, as_of_date)<br />
if identity.hard_mapping_unresolved:<br />
emit(INVESTIGATE, next_fact=identity.missing_fact)<br />
continue<br />
<br />
features, data_state = compute_screening_features(identity)<br />
triggers = apply_rules(features, execution_state=data_state)<br />
if not triggers:<br />
emit(MONITOR_or_REJECT)<br />
continue<br />
<br />
specification = resolve_bilingual_specification(identity,
documents)<br />
gap = classify_gap(features, specification, domestic_supply)<br />
if gap.false_or_measurement:<br />
emit(REJECT_or_MONITOR)<br />
continue<br />
<br />
coarse_adj = run_R9S(identity, plants)<br />
capability = evaluate_sector_profile(gap, plants, coarse_adj)<br />
if capability.K == 0 or capability.K &lt; Kmin or
capability.hard_gate_unknown:<br />
emit(INVESTIGATE, next_fact=max_EVSI(capability.missing_facts))<br />
continue<br />
<br />
capability.D_star = adjusted_distance(capability, lambda_unknown)<br />
demand = build_separate_base_committed_announced_scenarios(gap)<br />
alternatives = evaluate_in_order(<br />
no_action, existing_capacity, unsupported_brownfield,<br />
nonfinancial_brownfield, supported_brownfield,<br />
technology_JV, unsupported_greenfield, supported_greenfield,<br />
shared_enabler<br />
)<br />
<br />
evidence_action = maximise_EVSI(alternatives, missing_facts)<br />
if evidence_action.positive:<br />
emit(INVESTIGATE, next_fact=evidence_action)<br />
else:<br />
decision = select_max_incremental_national_value(alternatives)<br />
request_accountable_authorisation(decision)<br />
emit(decision, conditions, sunset, kill_condition,
frozen_evidence_passport)</strong></p>
<p>The implementation may use SQL, Python and controlled AI services.
The decision contract is invariant to the technology stack.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**13. Worked Case A — HS 721049**

*Non-corrugated zinc-coated flat-rolled iron or non-alloy steel, width
600 mm or more; screening nomenclature H0.*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>PURPOSE OF THE CASE</strong></p>
<p>This case demonstrates what the method can conclude from public
evidence—and where it must stop. It does not use the Ministry’s
line-level customs, production, utilisation, invoice or application
records. The correct output is therefore a defensible route restriction
and evidence request, not a fabricated final investment
recommendation.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**13.1 Public trade screen**

<table>
<colgroup>
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>Year</strong></th>
<th><strong>Imports<br />
USD m</strong></th>
<th><strong>Imports<br />
kt</strong></th>
<th><strong>Import UV<br />
USD/t</strong></th>
<th><strong>Exports<br />
USD m</strong></th>
<th><strong>Exports<br />
kt</strong></th>
<th><strong>Gross net<br />
USD m</strong></th>
<th><strong>Gross net<br />
kt</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><strong>2021</strong></td>
<td>194.1</td>
<td>177.4</td>
<td>1,094</td>
<td>49.6</td>
<td>39.7</td>
<td>144.5</td>
<td>137.8</td>
</tr>
<tr class="even">
<td><strong>2023</strong></td>
<td>186.0</td>
<td>173.8</td>
<td>1,070</td>
<td>16.3</td>
<td>15.8</td>
<td>169.7</td>
<td>158.0</td>
</tr>
<tr class="odd">
<td><strong>2024</strong></td>
<td>236.9</td>
<td>287.9</td>
<td>823</td>
<td>27.1</td>
<td>27.6</td>
<td>209.8</td>
<td>260.3</td>
</tr>
</tbody>
</table>

**Source note:** *WITS/UN Comtrade reported data. WITS identifies the
nomenclature as HS 1988/92 (H0) and notes that imports and exports are
gross. “Gross net” is imports minus gross exports; it is a screening
indicator, not retained domestic demand.*

<img src="media/image1.png"
title="Bar chart of Saudi HS 721049 gross imports, gross exports, and screening net exposure for 2021, 2023, and 2024."
style="width:6.45669in;height:3.32854in"
alt="Bar chart of Saudi HS 721049 gross imports, gross exports, and screening net exposure for 2021, 2023, and 2024." />

**Source note:** *Public data for 2021, 2023 and 2024. The missing 2022
observation is not interpolated.*

**13.2 What the screen establishes**

- R1-D persistence signal, not R1-F. Gross imports were material in all
  three observed years—approximately USD 194.1 million in 2021, USD
  186.0 million in 2023 and USD 236.9 million in 2024—but 2022 is
  missing. The full persistence rule is therefore NOT EVALUABLE; the
  degraded signal fires with confidence capped at C.

- **Quantity-led 2024 expansion.** From 2023 to 2024, import value rose
  about 27.4%, physical quantity rose about 65.6%, and average unit
  value fell about 23.1%. The increase is therefore quantity-led, not a
  price-only effect.

- **Material gross net exposure.** In 2024, gross imports less gross
  exports were approximately USD 209.8 million and 260.3 thousand
  tonnes. This remains a screening measure because re-exports and
  domestic-origin exports are not separated.

- **Concentrated external supply.** China and Korea represented about
  76.3% of 2024 import value. The approximate partner-value HHI is 0.36,
  indicating high concentration for resilience review.

**13.3 Partner unit-value diagnostic — R4-D only**

<img src="media/image2.png"
title="Horizontal bar chart of Saudi HS 721049 import unit values by partner in 2024, annotated with each partner&#39;s share of import value."
style="width:6.45669in;height:3.76949in"
alt="Horizontal bar chart of Saudi HS 721049 import unit values by partner in 2024, annotated with each partner&#39;s share of import value." />

Source note: annual partner data permit only the degraded R4-D
dispersion path. The full partner-month/tariff-line clustering rule R4-F
is DISABLED. Implied unit values are calculated from partner trade value
and net weight; small high-value observations are not interpreted as
grades.

The large-volume Asian suppliers cluster around roughly USD 776–864 per
tonne. Austria appears near USD 4,179 per tonne on only about 1.0
thousand tonnes; Germany and several very small partners also sit above
the bulk range. This is sufficient to open a product-mix or
specification investigation. It is not sufficient to claim that the
imported market is predominantly a higher grade. The public data
actually shows the opposite warning: most imported tonnage is in a
relatively tight bulk unit-value band.

**13.4 Domestic capability evidence**

| **Evidence**                               | **What it establishes**                                                                                                                                                                             |
|--------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **UNICOIL installed capacity and process** | The 2024 EPD reports 250,000 t/y galvanized-coil installed capacity, continuous hot-dip galvanising, cold rolling/pickling and Saudi production data for 2023.                                      |
| **Published specifications**               | UNICOIL lists SASO–ASTM A653/A653M and other standards, multiple grades and coating designations. The live English page gives 40–400 g/m²; the 2024 EPD gives 45–350 g/m² and G15/Z45 to G115/Z350. |
| **Contradiction control**                  | The web/EPD range difference is retained, not harmonised away. Producer confirmation is required before using the envelope for a target-specification conclusion.                                   |
| **Quality and testing**                    | The EPD reports ISO management certifications and ISO/IEC 17025 laboratory accreditation for steel coils and sheets.                                                                                |
| **Additional incumbent evidence**          | Hadeed publicly lists cold-rolled galvanised and colour-coated coil; the public page does not establish line capacity, utilisation or target-grade output.                                          |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>CRITICAL INFERENCE</strong></p>
<p>Saudi Arabia demonstrably has domestic galvanising capability and
exports this HS6 product. Therefore, high imports cannot support a
greenfield recommendation by themselves. The route must first
distinguish capacity pressure, specification/application mismatch,
price/logistics, customer qualification, re-export and market-allocation
effects.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**13.5 Capability-distance status from public evidence**

| **Dimension**                          | **Public status** | **Interpretation**                                                                         |
|----------------------------------------|-------------------|--------------------------------------------------------------------------------------------|
| **Feedstock / substrate**              | 0 — Present       | Cold-rolled and pickled coil capability is publicly described.                             |
| **Core galvanising route**             | 0 — Present       | Continuous hot-dip galvanising line is publicly described.                                 |
| **Grade/coating breadth**              | 0/1 — Broad range | Multiple standards, grades and coating masses are offered; exact target mix unknown.       |
| **QA/laboratory**                      | 0 — Present       | Laboratory and quality accreditations publicly stated.                                     |
| **Effective capacity/utilisation**     | U — Unknown       | Installed capacity is not current effective spare capacity.                                |
| **Customer/application qualification** | U — Unknown       | Public product sheets do not prove acceptance by every importing buyer/end use.            |
| **Domestic product allocation**        | U — Unknown       | Production split among local sales, exports, grades and customer contracts is unavailable. |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>CAPABILITY-DISTANCE CONTROL</strong></p>
<p>Public evidence resolves core process and published product breadth
but leaves effective capacity, allocation and customer qualification
unknown. D* is not published unless the steel profile reaches Kmin and
all hard gates are resolved. The correct public-data state is
INVESTIGATE, not a numeric adjacency claim.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**13.6 Provisional decision and route restriction**

| **Item**              | **Conclusion**                                                                                                                                            |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Decision state**    | INVESTIGATE — material demand and domestic capability are both verified; the binding constraint is unresolved.                                            |
| **Greenfield**        | NOT JUSTIFIED from public evidence. A new entrant cannot be recommended before incumbent effective capacity and target-specification coverage are tested. |
| **Brownfield**        | PRIORITY ROUTE TO TEST. Existing process, product breadth and quality infrastructure create strong adjacency.                                             |
| **Specification gap** | POSSIBLE but unproven. Unit-value dispersion contains small high-value observations, while most tonnage remains in a bulk band.                           |
| **Resilience**        | MATERIAL. Supplier concentration is high enough to justify a resilience review, but diversification may be cheaper than localisation support.             |

**13.7 Minimum internal evidence that can change the route**

| **Next fact**                        | **Route effect**                                                                                                               |
|--------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| **Line-level production actuals**    | Output by Saudi tariff line, grade, coating mass, thickness, width, application and domestic/export destination.               |
| **Effective capacity**               | Availability, yield, target-spec qualification share, current utilisation, backlog and planned outages/expansions.             |
| **Importer/offtaker specifications** | Invoice/tender descriptions, coating/grade/standard, end use, customer qualification and reason local supply was not selected. |
| **Re-export and origin**             | Separate retained domestic imports, re-exports, domestic-origin exports and processing trade.                                  |
| **Economics**                        | Local delivered cost and lead time by target specification compared with import parity; unsupported brownfield NPV/IRR.        |

**13.8 Decision rules after internal evidence**

| **Evidence result**                                                                                      | **Correct route**                                                                                                     |
|----------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| **Idle qualified capacity exists and import spec matches**                                               | No financial support; investigate buyer linkage, pricing, procurement, lead time or administrative barrier.           |
| **Core line exists; certification/quality/customer qualification missing**                               | Quality/certification intervention with defined customer acceptance milestone.                                        |
| **Qualified utilisation ≥85% and sustained spec-matched demand exceeds effective capacity**              | Brownfield debottlenecking or line expansion; calculate minimum effective support only if unsupported economics fail. |
| **Target product requires a process/operating envelope absent from incumbents, and demand supports MES** | Technology JV or targeted new line; greenfield only after the incumbent/JV route fails.                               |
| **Demand is temporary, re-exported or below efficient scale**                                            | No capacity intervention; monitor, diversify supply or use temporary procurement measures.                            |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>WHAT THE CASE DEMONSTRATES</strong></p>
<p>The solution does not force a dramatic answer; it prevents an
unsupported one. Public data provides a degraded persistence signal, a
full quantity-led growth trigger, a concentration trigger, a degraded
product-mix signal and verified domestic galvanising capability. That is
sufficient to block “high imports = new factory” and to identify the
exact internal facts that can select no action, qualification support,
brownfield expansion, JV or new entry.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**14. Worked Case B — HS 390210**

Polypropylene, in primary forms; public WITS screening nomenclature H0.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>PURPOSE OF THE CASE</strong></p>
<p>This case tests whether the method can reach a disciplined
no-capacity-support conclusion. Saudi Arabia is a large exporter and
also records imports under the same HS6. The method therefore asks
whether imports represent a genuine missing grade or merely trade,
distribution and product-mix effects. It does not treat imports as
evidence that more generic polypropylene capacity is needed.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**14.1 Public trade screen**

| **Year** | **Imports USD m** | **Imports kt** | **Exports USD m** | **Exports kt**                 | **Export/import value ratio** |
|----------|-------------------|----------------|-------------------|--------------------------------|-------------------------------|
| **2021** | 91.2              | 50.5           | 6,827.8           | Not reported on WITS world row | 74.9×                         |
| **2023** | 91.0              | 67.0           | 4,806.3           | 3,666.6                        | 52.8×                         |
| **2024** | 92.3              | 56.0           | 4,670.5           | 4,257.9                        | 50.6×                         |

Source note: WITS/UN Comtrade gross imports and gross exports under HS
1988/92 (H0). The series does not identify Saudi retained demand,
tariff-line grades, domestic sales or re-exports. The 2021 WITS world
export row does not report total quantity and is left unresolved.

**14.2 Rule execution and analytical result**

| **Rule** | **Execution**                       | **Result**                                                                                                                                                                                  |
|----------|-------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **R1-F** | NOT EVALUABLE                       | 2022/monthly continuity is absent in the public extract.                                                                                                                                    |
| **R1-D** | FIRES                               | Imports are positive and material in three observed years within a four-year window; confidence capped at C.                                                                                |
| **R2**   | DOES NOT FIRE for 2023→2024 imports | Import value rose ~1.4%, quantity fell ~16.4% and unit value rose ~21.3%; growth is not quantity-led.                                                                                       |
| **R5**   | FIRES as a product-mix test         | Large domestic/export capability coexists with imports; exact retained consumption and grade equivalence remain unresolved.                                                                 |
| **R7**   | NOT EVALUABLE                       | Public evidence does not establish idle qualified capacity or specification equivalence. One public producer reported exceeding nameplate in Q1 2026, so latent capacity cannot be assumed. |
| **R11**  | Generic capacity warning            | A country exporting more than 50× the import value cannot justify generic new PP capacity from HS6 imports alone.                                                                           |

In 2024, imports were only about 2.0% of export value. Average import
unit value was approximately USD 1,649/t versus an average export unit
value of approximately USD 1,097/t. The difference is a product-mix,
grade, origin or distribution signal—not proof of a domestic
specialty-grade gap.

**14.3 Domestic capability evidence**

| **Evidence**                    | **What it establishes**                                                                                                                                       | **What it does not establish**                                                                   |
|---------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| **SABIC official PP portfolio** | A broad Saudi-linked polypropylene family portfolio covering homo, random and impact products and compounds for flexible and rigid applications.              | Exact Saudi-origin grade, HS 390210 classification, local availability and importer equivalence. |
| **Advanced Petrochemical**      | Official company information gives 450,000 t/y polypropylene nameplate capacity; a May 2026 disclosure says the Jubail complex exceeded nameplate in Q1 2026. | National spare capacity or availability of each imported grade.                                  |
| **Tasnee**                      | Official product information reports a Saudi polypropylene plant expanded to 720,000 t/y.                                                                     | Current utilisation, domestic allocation and target-grade qualification.                         |
| **Trade position**              | Gross exports exceeded imports by more than 50× in value in both 2023 and 2024.                                                                               | Whether a small high-value imported niche is genuinely unavailable locally.                      |

**14.4 Provisional decision**

| **Item**                        | **Conclusion**                                                                                                                                                     |
|---------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Decision state**              | REJECT generic capacity support; INVESTIGATE only explicitly defined grade/application exceptions.                                                                 |
| **Generic greenfield PP plant** | NOT JUSTIFIED. National trade and producer evidence demonstrate large established capability and export surplus.                                                   |
| **Financial support**           | ZERO for generic capacity. A specific intervention can be considered only after a named imported grade, buyer requirement and incumbent capability gap are proven. |
| **Likely low-cost routes**      | Market linkage, local-grade visibility, customer qualification, procurement correction, logistics/distribution or targeted grade development.                      |
| **Residual uncertainty**        | Saudi tariff-line mix, importer/offtaker specifications, local grade availability, distribution/re-export effects and incumbent qualification.                     |

**14.5 Internal evidence that can change the route**

| **Next fact**                                       | **Route effect**                                                                                                                    |
|-----------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| **Saudi tariff-line and invoice description**       | Separates commodity homopolymer from specialty grade, compounded material, copolymer or possible classification mismatch.           |
| **Importer/offtaker application and qualification** | Establishes whether the import persists because of performance, certification, supplier approval, price, lead time or distribution. |
| **Producer grade/local-availability matrix**        | Confirms equivalence and whether the grade is offered domestically in required volume and timing.                                   |
| **Plant allocation and utilisation**                | Tests a targeted grade upgrade or additional line only after a real specification gap is established.                               |
| **Delivered economics**                             | Determines whether the market can resolve the niche without support.                                                                |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>WHAT THE CASE DEMONSTRATES</strong></p>
<p>The method is designed to recommend spending nothing when the
evidence does not justify capacity support. A large import number can
coexist with overwhelming domestic/export capability. The correct
response is to resolve the narrow grade or market-friction question—not
subsidise another generic plant.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**15. Decision Dossier and Supporting Evidence Pack**

*The one-page decision is backed by a reproducible analytical record.*

| **Dossier block**      | **Required content**                                                                                    |
|------------------------|---------------------------------------------------------------------------------------------------------|
| **Decision headline**  | State and route: e.g., ADVANCE — incumbent certification and debottlenecking; greenfield rejected.      |
| **Product identity**   | Commercial product, HS/tariff line, grade/purity/dimensions/standard/application and excluded meanings. |
| **Demand conclusion**  | Base, committed and announced scenarios; customers, concentration, timing and confidence.               |
| **Supply conclusion**  | Named producers, effective qualified capacity, utilisation, target specifications and planned changes.  |
| **Gap diagnosis**      | Quantity, specification, application, timing, resilience, false or evidence gap.                        |
| **Capability route**   | Incumbent D\*, hard gates, missing capability, schedule and greenfield/JV counterfactual.               |
| **Economics**          | Unsupported case, minimum effective intervention, downside result and national-value comparison.        |
| **Competition/policy** | Additionality, displacement, overcapacity, instrument choice, conditions and sunset.                    |
| **Evidence**           | Top supporting and contradictory evidence, confidence, missingness and reviewer status.                 |
| **Kill condition**     | Observable fact/threshold that stops or reroutes the opportunity.                                       |

**15.1 Supporting evidence pack**

- Source extracts and evidence passports.

- HS/tariff-line revision and concordance log.

- Trade cleaning, quantity coverage and re-export treatment.

- Price–quantity decomposition, concentration and unit-value
  diagnostics.

- Specification crosswalk with Arabic/English source spans.

- Plant-capability matrix, hard gates and effective-capacity
  calculation.

- Demand scenarios and project/BOM assumptions.

- Unsupported and intervention cash-flow models.

- Competition, national-value and sensitivity analysis.

- Contradiction register, expert overrides and decision history.

**15.2 Kill-condition examples**

| **Domain**        | **Illustrative kill condition**                                                                                      |
|-------------------|----------------------------------------------------------------------------------------------------------------------|
| **Demand**        | Awarded demand falls below minimum efficient scale or the project is cancelled/delayed beyond the investment window. |
| **Supply**        | An incumbent expansion already closes the specification-adjusted gap.                                                |
| **Specification** | Imported and domestic products are shown to be equivalent and qualified.                                             |
| **Economics**     | Downside delivered cost exceeds import parity beyond the accepted strategic premium.                                 |
| **Technology/IP** | Required route is unavailable, unlicensable or fails freedom-to-operate review.                                      |
| **Competition**   | Post-intervention capacity creates unacceptable overcapacity or displacement.                                        |
| **Additionality** | Investor proceeds without the proposed support or support does not change timing/scale/specification.                |

**16. Outcome Learning and Recalibration**

*The method learns from realised industrial outcomes, not from approvals
alone.*

| **Outcome family**        | **Measured fields**                                                                            |
|---------------------------|------------------------------------------------------------------------------------------------|
| **Investment**            | Committed vs actual capex; financing; milestone timing; cancellation or delay.                 |
| **Production**            | Commissioned capacity, effective output, yield, specification achieved and utilisation.        |
| **Market**                | Domestic sales, import displacement, exports, price, customer qualification and concentration. |
| **National value**        | Domestic value added, wages/skills, local sourcing, tax, technology transfer and resilience.   |
| **Government**            | Disbursement, contingent liabilities, administrative cost, conditionality and clawback.        |
| **Competition**           | Incumbent utilisation, entry/exit, price effects, concentration and redundant capacity.        |
| **Environment/resources** | Energy, water, emissions, waste and compliance against the approved case.                      |

**16.1 Learning rules**

- Keep predicted values, ranges and evidence state frozen at approval;
  do not overwrite them with actuals.

- Compare actuals with base, downside and upside scenarios and record
  the cause of deviation.

- Recalibrate thresholds only when there are enough comparable
  observations; do not tune the model to a handful of visible successes.

- Use time-based back-tests and matched/phased comparisons for
  intervention effectiveness where feasible.

- Treat applications, rejections and 26 approved deal profiles as a
  structured case corpus and formula-calibration source—not as automatic
  causal training labels.

- Publish rule performance: false positives, false negatives, route
  changes after evidence, decision stability, analyst time and fiscal
  exposure avoided.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>FINAL SOLUTION STANDARD</strong></p>
<p>A successful system does not maximise the number of opportunities
advanced. It maximises the expected national value of correct decisions,
minimises unsupported intervention, and makes every uncertainty,
assumption and route change visible.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**A. Formula Reference**

| **Measure**                      | **Formula**                                                                                |
|----------------------------------|--------------------------------------------------------------------------------------------|
| **Retained imports**             | M − RX                                                                                     |
| **Net import exposure**          | M − RX − Xdom                                                                              |
| **Apparent consumption**         | Qprod + Mret − Xdom                                                                        |
| **Import penetration**           | Mret / Apparent consumption                                                                |
| **Supplier HHI**                 | Σsi²                                                                                       |
| **Unit value**                   | Trade value / valid comparable net quantity                                                |
| **Value decomposition**          | ΔlnV = ΔlnQ + ΔlnUV                                                                        |
| **Effective qualified capacity** | Nameplate × Availability × Yield × Qualification share × Market allocation                 |
| **Specification-adjusted gap**   | Demand at target specification − effective qualified capacity at target specification      |
| **Known evidence coverage**      | K = Σ known dimension weights                                                              |
| **Unknown evidence weight**      | U = 1 − K                                                                                  |
| **Capability distance**          | D\* = min(1, Dknown + λU), only when K ≥ Kmin and hard gates are resolved                  |
| **Minimum effective support**    | S\* = min{S: NPV(S) ≥ 0 and IRR(S) ≥ h}                                                    |
| **Incremental national value**   | Benefits relative to no action − fiscal, displacement, distortion, resource and risk costs |
| **Shared-enabler unlock value**  | Σi\[P(i,e) × ΔNVi × DependencyShare(i,e)\] − Cost(e)                                       |
| **Approximate EVSI**             | P(route changes) × value difference − evidence cost − delay cost                           |

**B. Initial Thresholds and Calibration Policy**

Thresholds are operational defaults, not universal economic laws. Each
threshold is retained with a version, rationale, sector scope,
sensitivity and back-test result. The Ministry may approve
sector-specific values, but the underlying feature and decision path
must remain visible.

| **Default**                         | **Initial value**                                                                                                      |
|-------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| **Full persistence (R1-F)**         | 30/36 months or three consecutive complete years.                                                                      |
| **Degraded persistence (R1-D)**     | Three positive observed years in a four-year window; no interpolation; confidence ≤C; no ADVANCE from this rule alone. |
| **Cluster materiality**             | Higher of policy floor or 75th percentile within NIS cluster.                                                          |
| **Quantity-led growth**             | Positive quantity growth; quantity contribution share ≥60%; initial CAGR flag ≥5%.                                     |
| **Supplier concentration**          | HHI ≥0.25 or largest supplier ≥50%.                                                                                    |
| **Full UV cluster evidence (R4-F)** | ≥70% value coverage; ≥5 partner-month/tariff-line cells; ΔBIC\>10; ≥1.5× median separation; each cluster ≥10%.         |
| **Degraded UV dispersion (R4-D)**   | Annual/partner diagnostics only; descriptive dispersion; no cluster or grade conclusion.                               |
| **Capacity pressure**               | Effective utilisation ≥85% and specification-matched shortage ≥10% sustained.                                          |
| **Latent capacity**                 | Effective utilisation ≤70% with specification equivalence and availability in the demand window.                       |
| **Unknown penalty λ**               | 0.50 initial; sector-calibrated and versioned.                                                                         |
| **Minimum known coverage Kmin**     | 0.70 initial; no route band below Kmin or with an unresolved hard gate.                                                |
| **All-unknown convention**          | If K=0, D\* is not computed; decision state = INVESTIGATE.                                                             |
| **Capability route bands**          | D\* ≤0.20 immediate; ≤0.40 incremental; ≤0.65 major/JV; \>0.65 greenfield likely, subject to Kmin and hard gates.      |
| **Overcapacity warning**            | Post-entry capacity/downside demand \>1.25 unless credible export demand exists.                                       |
| **Economic exclusion**              | Downside delivered cost \>25% above import parity absent a verified strategic externality.                             |

**B.1 Calibration sequence**

**1.** Select known true opportunities, false positives, incumbent
upgrades, greenfield successes/failures and no-action cases.

**2.** Reconstruct the evidence available at the original decision date.

**3.** Run the unchanged rules and compare trigger, route and outcome.

**4.** Optimise thresholds for asymmetric error costs: a false
greenfield can be more costly than a missed research candidate.

**B.1 Calibration sequence — continued**

**5.** Freeze thresholds for the decision cycle; document approved
exceptions rather than changing rules case by case.

**6.** Review annually or when a major classification, policy or market
regime changes.

**C. Minimum Data Dictionary**

| **Field group**                                            | **Definition**                                 | **Status**                              |
|------------------------------------------------------------|------------------------------------------------|-----------------------------------------|
| **product_id**                                             | Persistent internal ID                         | Required                                |
| **hs_revision / hs6 / national_tariff_line**               | Classification and time validity               | Required                                |
| **commercial_name_ar / commercial_name_en**                | Normalised and original names                  | Required                                |
| **specification_fields**                                   | Grade/purity/dimensions/standard/application   | Required before deep decision           |
| **period / reporter / partner / flow**                     | Trade observation keys                         | Required                                |
| **trade_value / currency / valuation**                     | Original and converted value                   | Required                                |
| **net_weight / supplementary_qty / unit**                  | Physical quantity fields and flags             | Required for UV                         |
| **reexport_flag / domestic_origin_flag**                   | Flow decomposition                             | Preferred; otherwise confidence penalty |
| **plant_id / company_id / parent_group_id**                | Entity resolution                              | Required                                |
| **line_id / process_route / equipment_window**             | Plant capability                               | Required for route decision             |
| **nameplate / availability / yield / qualification_share** | Effective capacity inputs                      | Required for capacity gap               |
| **certification / customer_qualification**                 | Specification acceptance                       | Required where applicable               |
| **base / committed / announced demand**                    | Demand scenario layers                         | Required                                |
| **capex / opex / price / hurdle / cash_flow**              | Economics                                      | Required for intervention               |
| **rule_execution_state**                                   | FULL / DEGRADED / DISABLED with confidence cap | Required for every rule                 |
| **known_weight_coverage / lambda / Kmin**                  | Capability uncertainty parameters and version  | Required when D\* is used               |
| **snapshot_hash / query_contract / code_version**          | Frozen evidence and transformation identity    | Required for reproducibility            |
| **source / date / transformation / confidence**            | Evidence passport                              | Required for every field                |
| **decision / route / condition / kill_condition**          | Decision record                                | Required                                |

**D. Source Basis and Public Worked Cases**

The method is grounded in the engagement record and supplied research
materials. The worked cases use WITS/UN Comtrade and official Saudi
producer sources rechecked on 31 August 2026. Production use must store
raw snapshots, query contracts, retrieval timestamps and cryptographic
hashes; a live link alone is not an evidence snapshot.

| **ID**           | **Reference**                                                                                                                                                                           |
|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **M1**           | Engagement meeting record: specific investable opportunities, specification-level gaps, incumbent versus new investor, proportionate intervention and repeatable decision support.      |
| **R1**           | Saudi Arabia Industrial Opportunity Prioritization Research Dossier: evidence boundaries, trade formulas, unit-value safeguards, candidate generation, uncertainty and counterfactuals. |
| **S-W1 to S-W6** | WITS/UN Comtrade: Saudi Arabia HS 721049 imports and exports by country for 2024, 2023 and 2021; H0 gross flows.                                                                        |
| **S-U1**         | UNICOIL Arabic and English galvanized-product specification pages; bilingual source spans and published coating/grade envelope.                                                         |
| **S-U2**         | UNICOIL 2024 Environmental Product Declaration: installed capacity, process, product specification and accreditations.                                                                  |
| **S-H1**         | Hadeed official flat-products catalogue: cold-rolled galvanized and colour-coated products.                                                                                             |
| **P-W1 to P-W6** | WITS/UN Comtrade: Saudi Arabia HS 390210 imports and exports by country for 2024, 2023 and 2021; H0 gross flows.                                                                        |
| **P-S1**         | SABIC official polypropylene portfolio page: broad PP family and application portfolio.                                                                                                 |
| **P-A1**         | Advanced Petrochemical official company information: 450,000 t/y PP nameplate capacity.                                                                                                 |
| **P-A2**         | Advanced Petrochemical May 2026 disclosure: Jubail complex exceeded nameplate in Q1 2026.                                                                                               |
| **P-T1**         | Tasnee official petrochemicals page: Saudi polypropylene capacity expanded to 720,000 t/y.                                                                                              |
| **C1**           | UN Comtrade API package/documentation: final, tariff-line, mirror and metadata extraction fields.                                                                                       |

**D.1 Public links and retrieval scope**

S-W1:
https://wits.worldbank.org/trade/comtrade/en/country/SAU/year/2024/tradeflow/Imports/partner/ALL/product/721049

S-W2:
https://wits.worldbank.org/trade/comtrade/en/country/SAU/year/2024/tradeflow/Exports/partner/ALL/product/721049

S-W3:
https://wits.worldbank.org/trade/comtrade/en/country/SAU/year/2023/tradeflow/Imports/partner/ALL/product/721049

S-W4:
https://wits.worldbank.org/trade/comtrade/en/country/SAU/year/2023/tradeflow/Exports/partner/ALL/product/721049

S-W5:
https://wits.worldbank.org/trade/comtrade/en/country/SAU/year/2021/tradeflow/Imports/partner/ALL/product/721049

S-W6:
https://wits.worldbank.org/trade/comtrade/en/country/SAU/year/2021/tradeflow/Exports/partner/ALL/product/721049

S-U1-AR:
https://www.unicoil.com.sa/ar/products%26services/gi-product-brands-specifications/

S-U1-EN:
https://www.unicoil.com.sa/products%26services/gi-product-brands-specifications-2/

S-U2:
https://www.unicoil.com.sa/wp-content/uploads/2026/05/EPD-Report_GS_Unicoil_Rev02-1_1.pdf

S-H1:
https://hadeed.com.sa/products?group-category=cold-rolled-galvanized&main-category=flat-products

P-W1:
https://wits.worldbank.org/trade/comtrade/en/country/SAU/year/2024/tradeflow/Imports/partner/ALL/product/390210

P-W2:
https://wits.worldbank.org/trade/comtrade/en/country/SAU/year/2024/tradeflow/Exports/partner/ALL/product/390210

P-W3:
https://wits.worldbank.org/trade/comtrade/en/country/SAU/year/2023/tradeflow/Imports/partner/ALL/product/390210

P-W4:
https://wits.worldbank.org/trade/comtrade/en/country/SAU/year/2023/tradeflow/Exports/partner/ALL/product/390210

P-W5:
https://wits.worldbank.org/trade/comtrade/en/country/SAU/year/2021/tradeflow/Imports/partner/ALL/product/390210

P-W6:
https://wits.worldbank.org/trade/comtrade/en/country/SAU/year/2021/tradeflow/Exports/partner/ALL/product/390210

P-S1: https://www.sabic.com/en/products/polymers/polypropylene-pp

P-A1: https://advancedpetrochem.com/about/

P-A2:
https://advancedpetrochem.com/news/advanced-petrochemical-company-21st-ordinary-general-assembly-meeting-jubail-industrial-city-kingdom-of-saudi-arabia-tuesday-may-5-2026-tadawul-2330/

P-T1: https://www.tasnee.com/en/products/petrochemicals

C1: https://github.com/uncomtrade/comtradeapicall
