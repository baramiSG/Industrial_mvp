export async function getJSON(url) {
  const response = await fetch(url);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const detail = payload.detail;
    const message = typeof detail === "string"
      ? detail
      : detail?.message || `Request failed: ${response.status}`;
    throw new Error(message);
  }
  return response.json();
}

export function caseSelectionEndpoint() {
  return "/api/case-selection";
}

export function opportunityListEndpoint(mode) {
  return `/api/opportunities?mode=${encodeURIComponent(mode)}`;
}

export function opportunityEndpoint(id, mode) {
  return `/api/opportunities/${encodeURIComponent(id)}?mode=${encodeURIComponent(mode)}`;
}

export function manifestEndpoint(id, mode) {
  return `/api/opportunities/${encodeURIComponent(id)}/ui-manifest?mode=${encodeURIComponent(mode)}`;
}

export function dossierEndpoint(id, mode) {
  return `/api/opportunities/${encodeURIComponent(id)}/dossier?mode=${encodeURIComponent(mode)}`;
}

export function dossierHtmlEndpoint(id, mode, locale) {
  const query = new URLSearchParams({ mode, locale });
  return `/api/opportunities/${encodeURIComponent(id)}/dossier.html?${query}`;
}

export function screeningSummaryEndpoint() {
  return "/api/screening";
}

export function screeningEvidenceEndpoint() {
  return "/api/screening/evidence";
}

export function screeningQueueEndpoint(queueId, offset = 0, limit = 50) {
  const query = new URLSearchParams({ offset, limit });
  return `/api/screening/queues/${encodeURIComponent(queueId)}?${query}`;
}

export function screeningRecordEndpoint(hs6) {
  return `/api/screening/records/${encodeURIComponent(hs6)}`;
}
