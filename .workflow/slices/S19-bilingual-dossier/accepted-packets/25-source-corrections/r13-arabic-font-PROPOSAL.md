# Finite Arabic source-island typography correction

Proposed only src/ior_mvp/static/css/dossier.css. At its existing font rule replace `.source-language-island,` with `.source-language-island[lang="en"],`. Keep code selector, declarations, Arabic/interface font tokens, font size, all layout/footer/geometry rules and all tests/harnesses unchanged.

Actual inherited full-functional test_dossier_rtl_element_renders_real_arabic_glyphs[chromium-public-steel-en] fails. Its trace returns a real visible Arabic commercial-name node with dir=rtl and proper loaded glyphs but a computed font-family beginning IOR Noto Sans rather than the required IOR Noto Sans Arabic. Later generic source-island selector overrides earlier [lang=ar] at equal specificity. Restricting the interface override to actual English-language source islands lets the existing Arabic rule apply to the Arabic island. No source text or test accommodation is proposed.

Keep frozen r13/fullrun unchanged until completion. Retain original failure/trace; after independent concurrence/root acceptance, run the exact inherited font test and its preserved locale/mode matrix on the corrected CSS. Source/PDF identity must rebind; compare actual affected render output and repeat required full functional44PDF/strict/render proof. No generated write/canonical operation, font installation, new helper/framework or weakened assertion.

Sanad: TRACE-OBSERVATION.json binds the real call@886 result, source ledger and trace hash; current dossier.css and existing harness.py:505-627 establish selector precedence and exact failure condition. Muhasabah PASS for a finite proposed correction: typography cause is observed, corrected full-suite behavior and PDF consequences remain unverified. No missing-Arabic-data claim is made.
