# S11 context

Milestone v0.3.0 slice S11 delivers operator-only acquisition for WITS, UN Comtrade, ZATCA tariff and BACI with honest UNAVAILABLE/INCOMPLETE records, one WITS partners analytical snapshot, passports, reconstruction CI, and ADR-015. Frozen public goldens unchanged.

T8-GATE: n=1 normalized partners snapshot (`PARTNERS-SAU-WITS-TRADE-2026-09-03.json`).

Candidate 4 (implementer-fable): `browser_tests/baselines/**`, `config.py` and `data_repository.py` byte-identical to base; acquisition config loader in `acquisition/source_config.py`, acquired-snapshot loaders in `acquisition/repository.py` (DELIVERY-F-01; ADR-015 module placement).

Candidate 5 (implementer-composer, plan-4): DD-23 stored-evidence semantics and DD-24 credential-echo guard; `data/raw/**`, manifests, config, docs/core and browser baselines byte-identical to candidate 4; no acquire-* command run.
