import { renderPublicStep, markStoredSourceNames } from "./steps.js";
import { renderSimulationStep } from "./simulation.js";
import { renderRoutes } from "./routes.js";

export const STEP_REGISTRY = Object.freeze({
  SIGNAL: Object.freeze({ component: "public", render: renderPublicStep }),
  FALSE_POSITIVE_CONTROLS: Object.freeze({ component: "public", render: renderPublicStep }),
  PUBLIC_CONCLUSION: Object.freeze({ component: "public", render: renderPublicStep }),
  MISSING_MINISTRY_FACTS: Object.freeze({ component: "public", render: renderPublicStep }),
  SIMULATED_EVIDENCE: Object.freeze({ component: "simulation", render: renderSimulationStep }),
  ROUTE_COMPARISON: Object.freeze({ component: "routes", render: renderRoutes }),
  INTERVENTION: Object.freeze({ component: "simulation", render: renderSimulationStep }),
  CONDITIONS_AND_KILL: Object.freeze({ component: "simulation", render: renderSimulationStep }),
});

export function renderRegisteredStep(stepId, context) {
  const descriptor = STEP_REGISTRY[stepId];
  if (!descriptor || !["public", "simulation", "routes"].includes(descriptor.component)) throw new Error("EXECUTIVE_COMPONENT_INVALID");
  const step = context.executiveCase.steps.find((row) => row.step_id === stepId);
  if (!step) throw new Error("EXECUTIVE_STEP_MISSING");
  const content = descriptor.render(step, context);
  return descriptor.component === "public" ? markStoredSourceNames(content, context) : content;
}
