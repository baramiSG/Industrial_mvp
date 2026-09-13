import {
  dossierEndpoint,
  dossierHtmlEndpoint,
  getJSON,
} from "./api.js";
import { toast } from "./dom.js";
import { renderExtraction } from "./extraction.js";
import {
  DEFAULT_LOCALE,
  loadLocale,
  localeFromUrl,
  t,
  targetLocale,
} from "./i18n.js";
import {
  loadPortfolio,
  populateSelect,
  renderKPIs,
  renderOpportunityCards,
  renderPortfolioChip,
} from "./portfolio.js";
import { state } from "./state.js";
import {
  loadOpportunity,
  rerenderWorkspace,
} from "./workspace.js";
import {
  openQueue,
  openRecord,
  rerenderScreening,
  screeningBack,
} from "./screening/index.js";

export function scrollToSection(id) {
  document.getElementById(id)?.scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
}

export async function setMode(mode) {
  state.mode = mode;
  document.querySelectorAll(".mode-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === mode);
  });
  await loadPortfolio();
}

export function handleError(error) {
  console.error(error);
  if (state.ui) toast(t("common.error"));
}

export function rerenderLocaleState() {
  renderKPIs();
  renderOpportunityCards();
  populateSelect();
  rerenderWorkspace();
  renderPortfolioChip();
  renderExtraction();
  rerenderScreening();
}

export async function switchLocale() {
  const button = document.getElementById("locale-switch");
  button.disabled = true;
  try {
    await loadLocale(targetLocale());
    rerenderLocaleState();
  } finally {
    button.disabled = false;
  }
}

async function handleClick(event) {
  const target = event.target.closest(
    "[data-mode],[data-target],[data-open-id],[data-dossier-html],"
    + "[data-copy-json],[data-locale-switch],[data-queue-id],[data-hs6],"
    + "[data-screening-back],[data-screening-page],[data-passport-ref],"
    + "#open-first-case,#view-methodology",
  );
  if (!target) return;
  if (target.dataset.localeSwitch !== undefined) {
    await switchLocale();
  } else if (target.dataset.mode) {
    await setMode(target.dataset.mode);
  } else if (target.dataset.target) {
    document.querySelectorAll(".nav-item").forEach(
      (node) => node.classList.remove("active"),
    );
    target.classList.add("active");
    scrollToSection(target.dataset.target);
  } else if (target.dataset.openId) {
    state.selectedId = target.dataset.openId;
    document.getElementById("opportunity-select").value = state.selectedId;
    await loadOpportunity(state.selectedId);
    scrollToSection("workspace");
  } else if (target.dataset.queueId) {
    await openQueue(target.dataset.queueId);
  } else if (target.dataset.hs6) {
    await openRecord(target.dataset.hs6);
  } else if (target.dataset.screeningBack) {
    screeningBack(target.dataset.screeningBack);
  } else if (target.dataset.screeningPage) {
    const page = state.screening.page;
    const direction = target.dataset.screeningPage;
    const offset = direction === "next"
      ? page.offset + page.limit
      : Math.max(0, page.offset - page.limit);
    await openQueue(state.screening.queueId, offset);
  } else if (target.dataset.passportRef !== undefined) {
    event.preventDefault();
    const reference = target.getAttribute("href") || "";
    const card = document.getElementById(reference.replace(/^#/, ""));
    if (!card) return;
    card.focus({ preventScroll: true });
    card.scrollIntoView({ behavior: "smooth", block: "center" });
  } else if (target.dataset.dossierHtml) {
    window.open(
      dossierHtmlEndpoint(
        target.dataset.dossierHtml,
        state.mode,
        state.locale,
      ),
      "_blank",
      "noopener",
    );
  } else if (target.dataset.copyJson) {
    const dossier = await getJSON(
      dossierEndpoint(target.dataset.copyJson, state.mode),
    );
    await navigator.clipboard.writeText(JSON.stringify(dossier, null, 2));
    toast(t("actions.copied"));
  } else if (target.id === "open-first-case") {
    const steel = state.opportunities.find((item) => item.hs6 === "721049")
      || state.opportunities[0];
    if (!steel) return;
    state.selectedId = steel.id;
    document.getElementById("opportunity-select").value = steel.id;
    await loadOpportunity(steel.id);
    scrollToSection("workspace");
  } else if (target.id === "view-methodology") {
    scrollToSection("methodology");
  }
}

export function bindGlobalEvents() {
  document.addEventListener("click", (event) => {
    handleClick(event).catch(handleError);
  });
  document.getElementById("opportunity-select").addEventListener(
    "change",
    (event) => loadOpportunity(event.target.value).catch(handleError),
  );
  window.addEventListener("popstate", () => {
    loadLocale(localeFromUrl() || DEFAULT_LOCALE)
      .then(rerenderLocaleState)
      .catch(handleError);
  });
}
