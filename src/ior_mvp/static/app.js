import { bindGlobalEvents, handleError } from "./modules/events.js";
import { loadExtractionDemo } from "./modules/extraction.js";
import {
  loadLocale,
  resolveInitialLocale,
} from "./modules/i18n.js";
import { loadPortfolio } from "./modules/portfolio.js";
import { loadScreening } from "./modules/screening/index.js";

export async function init() {
  await loadLocale(resolveInitialLocale());
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

init().catch(handleError);
