import { t } from "./i18n.js";
import { state } from "./state.js";

export function localeTag() {
  const base = state.ui?.bcp47 || "en-US";
  return state.locale === "ar"
    ? `${base}-u-ca-gregory-nu-latn`
    : `${base}-u-nu-latn`;
}

export function number(value, digits = 1) {
  if (value == null) return t("common.unavailable");
  return new Intl.NumberFormat(localeTag(), {
    numberingSystem: "latn",
    minimumFractionDigits: 0,
    maximumFractionDigits: digits,
  }).format(value);
}

export function integer(value) {
  if (value == null) return t("common.unavailable");
  return new Intl.NumberFormat(localeTag(), {
    numberingSystem: "latn",
    maximumFractionDigits: 0,
    useGrouping: false,
  }).format(value);
}

export function percent(value, digits = 0) {
  if (value == null) return t("common.unavailable");
  return new Intl.NumberFormat(localeTag(), {
    numberingSystem: "latn",
    style: "percent",
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value);
}

export function money(value) {
  if (value == null) return t("common.unavailable");
  return `${t("currency.sar")} ${number(value)}${t("unit.million")}`;
}

export function usd(value) {
  if (value == null) return t("common.unavailable");
  return `${t("currency.usd")} ${number(value)}${t("unit.million")}`;
}

export function date(value) {
  if (!value) return t("common.unavailable");
  const [year, month, day] = String(value).split("-").map(Number);
  return new Intl.DateTimeFormat(localeTag(), {
    calendar: "gregory",
    numberingSystem: "latn",
    day: "2-digit",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(Date.UTC(year, month - 1, day)));
}
