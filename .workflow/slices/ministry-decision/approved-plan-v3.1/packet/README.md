# PLAN v3 review packet

**Proposed for Claude's independent review.** Company discovery and preliminary capability-gap assessment are included in the current Ministry demonstration. Neither review nor owner acceptance of this packet has been issued.

Read in this order:

1. [Assessment and source matrix](ASSESSMENT-v3.md)
2. [PLAN v3](PLAN-v3.md)
3. [Domain/method amendment](DOMAIN-CONTRACT.md), [discovery/graph contract](DISCOVERY-GRAPH-CONTRACT.md), [finite register/mapping supplement](REGISTER-FIXTURE-AND-MAPPINGS.md)
4. [Interaction design](INTERACTION-DESIGN.md) and [bilingual wireframes](WIREFRAMES.html)
5. [Delivery handoff](DELIVERY.md), [authority/pin inventory](AUTHORITY-AND-PINS.md)
6. [Claude finding responses](FINDING-RESOLUTION.md), [settled instructions/pending rulings](OWNER-DECISIONS.md)
7. [Sources and self-audit](SOURCES-AND-AUDIT.md), BASELINE.json, SOURCE-IDENTITIES.json, PACKET-CHECKS.json and SHA256SUMS.

This is one review subject. Normative implementation requirements are in the packet; retained notes/v2/review sources are evidence/history. Any change after approval requires a new hash binding and targeted review. SHA256SUMS includes every packet artifact except itself, plus the retained supporting notes and sources; verify from this directory with `sha256sum -c SHA256SUMS`. Its own hash is reported in chat with the plan hash, avoiding a self-referential checksum file.

The fixed baseline is ce407db. Actual upstream main was checked and is still ce407db; S19 remains undelivered. The local-origin observation correction is recorded transparently. Claude can review the design now; before Cascade writes code, reconcile the packet against S19's actual delivered commit and obtain targeted review of material changes. The other agent finishes S19 and stops; S20 is not authorised.
