# Completion — S07 Bilingual Interface Foundation

**State:** MERGED (2026-09-02). Merge commit `9f045a4ecf929b82a0c4ad9013d255e148bc837d`; PR #9; PR CI run 33622991390 (5/5); default-branch CI run 33623528164 (5/5).

## Delivered

- Whole-interface Arabic/English switch (URL → `localStorage["ior.locale"]` → `en`), `<html lang dir>`, mirrored logical layout, Western digits in both locales, technical tokens as single LTR isolates, engine-emitted analytical text kept English and rendered as captioned source-language islands until S08–S10.
- Governed catalogue `config/ui_strings.v1.yaml` 1.0.0 (hashed; en/ar parity) served by `GET /api/ui-strings/{locale}`; `evidence_policy` 1.2.0 with `display_label_ar` "محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة" (Supervisor-approved default under ruling PR-03, owner-amendable); both labels on every synthetic surface in both locales, none on public surfaces.
- Token-only CSS (`static/css/tokens.css` sole literal zone), 19 named-export ES modules ≤ 132 lines, vendored Noto Sans / Noto Sans Arabic (OFL-1.1) with `unicode-range` provenance, inline-SVG symbols, `scripts/check_ui_contracts.py` and `scripts/check_es_modules.py` in `make ci` and CI.
- Dossier HTML `?locale=en|ar` with localized chrome and dual disclosure; demo `/docs` link removed (KL-31), route kept.
- Browser suite: 18 tests / 122 Chromium nodes (118 functional per locale, 4 visual); 40 lossless WebP governed baselines (2 locales × 2 viewports × 10 screens) with hashed manifest, Pillow comparator (channel > 8, ratio ≤ 0.10 %, mean ≤ 0.20, no masks), update only through the digest-pinned canonical container, never in CI.
- Authority: Core 01 NFR-007, Core 02 map entries, Core 09 §2.7 opened as `core_version: 2.0.0`; ADR-011; `build_manifests.py` extended and run twice (justified; diff limited to policy, catalogue, Core 01/02/09 rows).
- Closes KL-21 and KL-31; V3-A8, V3-A10, V3-G7 `COMPLETE`; V3-A3/V3-A6 evidence extended.

## Review trail

- Plan: 2 rounds — PR-01 (40 lossless WebP baselines at 2 locales × 2 viewports), PR-02 (inline-SVG symbols outside vendored unicode-ranges + coverage contract), PR-03 (Arabic label approved as owner-amendable default), PR-04 (digit policy), PR-05 (Docker-free compare; chromium-1234 assertion; exit 2 without Docker), RI-01 (attribution wording) → PLAN_APPROVED.
- Supervisor implementation review: SR-01 HIGH — six visual/bidi/layout defects found by converting and viewing the first captured baselines (grouped years, duplicated state chips, unseparated route label, RTL-reordered HS tokens, tablet hero overlap, mis-aligned Arabic disclosure); SR-02 summary overwrite — all fixed with browser assertions; baselines regenerated through the canonical container.
- Independent review (Grok 4.6): **APPROVE — zero unresolved findings**; ADR-011 generator wording corrected by the Supervisor and re-confirmed.

## Evidence

- Local (Supervisor-run on the staged candidate): `make ci` exit 0 — 344 tracked files scanned, UI contracts PASS, ES modules PASS (19), integrity PASS, Gate B PASS, `377 passed` (3.12; also 3.14), smoke PASS, functional `118 passed`, visual `4 passed`.
- Hosted: PR run 33622991390 and main run 33623528164, five jobs each, all green.

## Carried forward

- KL-32 (OPEN → S13): canonical container writes baselines as root on the host.
- Reviewer residuals for S18/S19: copy scanner does not HTML-parse JS template literals; token scanner does not read the `styles.css` façade; JS motion/SVG numeric literals; `decision_object_status` not islanded; governance card carries both policy labels via a data attribute in public mode; CHANGELOG Unreleased readability; host `fc-match` DejaVu vs vendored IOR Noto.
- S06 residual for S18: hard-coded "0" synthetic-leakage KPI (live integrity value).
- `docs/OPERATOR_RUNBOOK.md` pre-existing absolute paths → S21.
- Owner to confirm or amend the Arabic label wording and the Western-digit policy (both owner-amendable via a later §7.3 change).
