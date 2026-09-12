import { t } from "../i18n.js";

export const RULE_NAME_KEYS = Object.freeze({
  R0: "screening.rule.r0",
  "R1-F": "screening.rule.r1_f",
  "R1-D": "screening.rule.r1_d",
  R2: "screening.rule.r2",
  R3: "screening.rule.r3",
  "R4-D": "screening.rule.r4_d",
  R5: "screening.rule.r5",
  "R9-S": "screening.rule.r9_s",
  R10: "screening.rule.r10",
  R11: "screening.rule.r11",
});

export const RESULT_KEYS = Object.freeze({
  R0_DISABLED_NA: "screening.result.r0_disabled_na",
  R0_FULL_FIRED: "screening.result.r0_full_fired",
  R0_DEGRADED_FIRED: "screening.result.r0_degraded_fired",
  R1_F_DISABLED_NA: "screening.result.r1_f_disabled_na",
  R1_F_FULL_NOT_FIRED: "screening.result.r1_f_full_not_fired",
  R1_D_DEGRADED_FIRED: "screening.result.r1_d_degraded_fired",
  R1_D_DEGRADED_NOT_FIRED: "screening.result.r1_d_degraded_not_fired",
  R2_DISABLED_NA: "screening.result.r2_disabled_na",
  R2_FULL_FIRED: "screening.result.r2_full_fired",
  R2_FULL_NOT_FIRED: "screening.result.r2_full_not_fired",
  R3_DISABLED_NA: "screening.result.r3_disabled_na",
  R3_FULL_FIRED: "screening.result.r3_full_fired",
  R3_FULL_NOT_FIRED: "screening.result.r3_full_not_fired",
  R4_D_DISABLED_NA: "screening.result.r4_d_disabled_na",
  R4_D_DEGRADED_FIRED: "screening.result.r4_d_degraded_fired",
  R5_DISABLED_NA: "screening.result.r5_disabled_na",
  R5_FULL_FIRED: "screening.result.r5_full_fired",
  R5_FULL_NOT_FIRED: "screening.result.r5_full_not_fired",
  R5_DEGRADED_FIRED: "screening.result.r5_degraded_fired",
  R5_DEGRADED_NOT_FIRED: "screening.result.r5_degraded_not_fired",
  R9_S_DISABLED_NA: "screening.result.r9_s_disabled_na",
  R9_S_FULL_FIRED: "screening.result.r9_s_full_fired",
  R9_S_FULL_NOT_FIRED: "screening.result.r9_s_full_not_fired",
  R10_DISABLED_NA: "screening.result.r10_disabled_na",
  R10_FULL_FIRED: "screening.result.r10_full_fired",
  R10_DEGRADED_FIRED: "screening.result.r10_degraded_fired",
  R11_FULL_FIRED: "screening.result.r11_full_fired",
  R11_FULL_NOT_FIRED: "screening.result.r11_full_not_fired",
  R11_DEGRADED_NOT_FIRED: "screening.result.r11_degraded_not_fired",
});

export const EFFECT_KEYS = Object.freeze({
  R0_EFFECT: "screening.effect.r0_effect",
  R1_F_EFFECT: "screening.effect.r1_f_effect",
  R1_D_EFFECT: "screening.effect.r1_d_effect",
  R2_EFFECT: "screening.effect.r2_effect",
  R3_EFFECT: "screening.effect.r3_effect",
  R4_D_EFFECT: "screening.effect.r4_d_effect",
  R5_EFFECT: "screening.effect.r5_effect",
  R9_S_EFFECT: "screening.effect.r9_s_effect",
  R10_EFFECT: "screening.effect.r10_effect",
  R11_EFFECT: "screening.effect.r11_effect",
});

function label(keys, code, vocabulary) {
  const key = keys[code];
  if (!key) {
    throw new Error(`UI_CATALOGUE_KEY_MISSING:${vocabulary}:${code}`);
  }
  return t(key);
}

export function ruleName(code) {
  return label(RULE_NAME_KEYS, code, "screeningRule");
}

export function resultLabel(code) {
  return label(RESULT_KEYS, code, "screeningResult");
}

export function effectLabel(code) {
  return label(EFFECT_KEYS, code, "screeningEffect");
}
