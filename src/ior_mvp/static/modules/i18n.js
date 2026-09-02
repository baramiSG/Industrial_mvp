import { getJSON } from "./api.js";
import { nextRequestEpoch, state } from "./state.js";

export const SUPPORTED_LOCALES = Object.freeze(["en", "ar"]);
export const DEFAULT_LOCALE = "en";
export const LOCALE_STORAGE_KEY = "ior.locale";

export function isSupportedLocale(locale) {
  return SUPPORTED_LOCALES.includes(locale);
}

export function interpolate(template, values = {}) {
  return template.replace(
    /\{([a-z][a-z0-9_]*)\}/g,
    (match, key) => (
      Object.hasOwn(values, key) ? String(values[key]) : match
    ),
  );
}

export function t(key, values = {}) {
  const template = state.ui?.strings?.[key];
  if (typeof template !== "string") {
    throw new Error(`UI_CATALOGUE_KEY_MISSING:${key}`);
  }
  return interpolate(template, values);
}

export function localeFromUrl() {
  const candidate = new URL(window.location.href).searchParams.get("locale");
  return isSupportedLocale(candidate) ? candidate : null;
}

export function storedLocale() {
  try {
    const candidate = window.localStorage.getItem(LOCALE_STORAGE_KEY);
    return isSupportedLocale(candidate) ? candidate : null;
  } catch {
    return null;
  }
}

export function resolveInitialLocale() {
  return localeFromUrl() || storedLocale() || DEFAULT_LOCALE;
}

export function canonicalizeLocaleUrl(locale) {
  const url = new URL(window.location.href);
  url.searchParams.set("locale", locale);
  window.history.replaceState(window.history.state, "", url);
}

export function applyStaticStrings() {
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-attr]").forEach((node) => {
    const [attribute, key] = node.dataset.i18nAttr.split(":");
    node.setAttribute(attribute, t(key));
  });
  document.title = t("app.document_title");
}

export function applyPolicyLabels(bundle = state.ui) {
  const order = state.locale === "ar" ? ["ar", "en"] : ["en", "ar"];
  document.querySelectorAll("[data-policy-labels]").forEach((node) => {
    node.replaceChildren(
      ...order.map((locale) => {
        const label = document.createElement("span");
        label.textContent = bundle.synthetic_labels[locale];
        label.lang = locale;
        label.dir = locale === "ar" ? "rtl" : "ltr";
        return label;
      }),
    );
  });
}

export function persistLocale(locale) {
  try {
    window.localStorage.setItem(LOCALE_STORAGE_KEY, locale);
  } catch {
    // URL and document state remain authoritative for this session.
  }
}

export function validateBundle(bundle, locale) {
  if (
    bundle?.locale !== locale
    || !isSupportedLocale(bundle.locale)
    || !["ltr", "rtl"].includes(bundle.direction)
    || typeof bundle.strings !== "object"
    || typeof bundle.synthetic_labels !== "object"
  ) {
    throw new Error("UI_CATALOGUE_BUNDLE_INVALID");
  }
  return bundle;
}

export async function fetchLocaleBundle(locale) {
  if (!isSupportedLocale(locale)) {
    throw new Error(`UI_LOCALE_NOT_FOUND:${locale}`);
  }
  return validateBundle(
    await getJSON(`/api/ui-strings/${encodeURIComponent(locale)}`),
    locale,
  );
}

export function applyLocaleBundle(bundle, { persist = true } = {}) {
  nextRequestEpoch();
  state.locale = bundle.locale;
  state.ui = bundle;
  document.documentElement.lang = bundle.locale;
  document.documentElement.dir = bundle.direction;
  canonicalizeLocaleUrl(bundle.locale);
  if (persist) persistLocale(bundle.locale);
  applyStaticStrings();
  applyPolicyLabels(bundle);
}

export async function loadLocale(locale, options = {}) {
  const bundle = await fetchLocaleBundle(
    isSupportedLocale(locale) ? locale : DEFAULT_LOCALE,
  );
  applyLocaleBundle(bundle, options);
  return bundle;
}

export function targetLocale() {
  return state.locale === "en" ? "ar" : "en";
}
