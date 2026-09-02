import { getJSON } from "./api.js";
import {
  escapeHtml,
  sourceCaption,
  sourceIsland,
} from "./dom.js";
import { number } from "./formatters.js";
import { t } from "./i18n.js";
import { state } from "./state.js";

export function statusIcon(passed) {
  const label = t(
    passed ? "extraction.pass_aria" : "extraction.fail_aria",
  );
  const glyph = passed
    ? '<path d="m5 12 4 4L19 6" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>'
    : '<path d="M7 7l10 10M17 7 7 17" fill="none" stroke="currentColor" stroke-linecap="round"/>';
  return `
    <svg class="${passed ? "pass-mark" : "fail-mark"} status-icon" viewBox="0 0 24 24" role="img" aria-label="${escapeHtml(label)}">
      ${glyph}
    </svg>
  `;
}

export function renderExtraction() {
  if (!state.extraction) return;
  const result = state.extraction;
  document.getElementById("extraction-score").textContent = t(
    "extraction.score",
    {
      passed: number(result.passed, 0),
      total: number(result.total, 0),
    },
  );
  document.getElementById("extraction-grid").innerHTML = result.records.map(
    (row) => `
      <article class="extraction-card">
        ${sourceCaption()}
        <h3>${sourceIsland(row.field)} ${statusIcon(row.passed)}</h3>
        <div class="language-block" lang="ar" dir="rtl"><b>${escapeHtml(t("extraction.ar"))}</b><br>${escapeHtml(row.source_spans.ar)}</div>
        <div class="language-block source-language-island" lang="en" dir="ltr"><b>${escapeHtml(t("extraction.en"))}</b><br>${escapeHtml(row.source_spans.en)}</div>
        <div class="normalized-block"><b>${escapeHtml(t("extraction.normalized"))}</b><br>${sourceIsland(JSON.stringify(row.actual), "code")}</div>
      </article>
    `,
  ).join("");
}

export async function loadExtractionDemo() {
  state.extraction = await getJSON("/api/extraction-demo");
  renderExtraction();
}
