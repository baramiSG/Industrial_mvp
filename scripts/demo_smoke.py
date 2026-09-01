from __future__ import annotations

from ior_mvp.ai_extraction import run_extraction_golden_set
from ior_mvp.decision_engine import analyze


def main() -> None:
    steel_public = analyze("SAU-H0-721049", "public")
    steel_sim = analyze("SAU-H0-721049", "simulated")
    pp_public = analyze("SAU-H0-390210", "public")

    assert steel_public["active_decision"]["state"] == "INVESTIGATE"
    assert steel_sim["real_decision"]["state"] == "INVESTIGATE"
    assert steel_sim["active_decision"]["state"] == "ADVANCE"
    assert pp_public["active_decision"]["state"] == "REJECT"
    assert run_extraction_golden_set()["accuracy"] == 1.0

    print("SMOKE PASS")
    print("- Steel / public: INVESTIGATE")
    print("- Steel / simulated: ADVANCE, real state unchanged")
    print("- Polypropylene / public: REJECT generic capacity")
    print("- AR/EN extraction golden gate: 100%")


if __name__ == "__main__":
    main()
