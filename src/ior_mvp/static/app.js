import { bindGlobalEvents, handleError } from "./modules/events.js";
import { loadExtractionDemo } from "./modules/extraction.js";
import {
  loadLocale,
  resolveInitialLocale,
} from "./modules/i18n.js";
import { initializeAnalystLocation } from "./modules/analyst-navigation.js";
import { loadPortfolio } from "./modules/portfolio.js";
import { loadScreening } from "./modules/screening/index.js";

export async function initAnalyst() {
  initializeAnalystLocation();
  bindGlobalEvents();
  await Promise.all([
    loadPortfolio(),
    loadExtractionDemo(),
    loadScreening(),
    document.fonts.ready,
  ]);
  document.body.classList.remove("app-loading");
  document.body.setAttribute("aria-busy", "false");
}

export async function init() {
  await loadLocale(resolveInitialLocale());
  if (window.location.pathname === "/executive") {
    const { initExecutive } = await import("./modules/executive/index.js");
    await initExecutive();
  } else {
    await initAnalyst();
  }
}

init().catch(handleError);
