from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from ior_mvp.app import app


client = TestClient(app)
DISCLOSURE = "SIMULATED — NOT MINISTRY EVIDENCE"


@pytest.mark.parametrize(
    "opportunity_id",
    ["SAU-H0-721049", "SAU-H0-390210"],
)
def test_real_dossier_has_no_disclosure_and_zero_synthetic_rows(
    opportunity_id: str,
) -> None:
    json_response = client.get(
        f"/api/opportunities/{opportunity_id}/dossier"
        "?mode=public"
    )
    html_response = client.get(
        f"/api/opportunities/{opportunity_id}/dossier.html"
        "?mode=public"
    )

    assert json_response.status_code == 200
    dossier = json_response.json()
    assert dossier["synthetic_disclosure"] is None
    assert dossier["evidence_summary"]["synthetic_records"] == 0
    assert dossier["gap_diagnosis"]["simulated_rules"] == []

    assert html_response.status_code == 200
    assert DISCLOSURE not in html_response.text
    expected_evidence_paragraph = (
        "<p>"
        f"{dossier['evidence_summary']['public_records']} "
        "public records; 0 synthetic records."
        "</p>"
    )
    assert expected_evidence_paragraph in html_response.text
    assert "Simulated R6–R8 ledger" not in html_response.text


def test_simulated_dossier_retains_disclosure_and_synthetic_rows() -> None:
    json_response = client.get(
        "/api/opportunities/SAU-H0-721049/dossier"
        "?mode=simulated"
    )
    html_response = client.get(
        "/api/opportunities/SAU-H0-721049/dossier.html"
        "?mode=simulated"
    )

    assert json_response.status_code == 200
    dossier = json_response.json()
    assert (
        dossier["synthetic_disclosure"]["display_label"]
        == DISCLOSURE
    )
    assert dossier["evidence_summary"]["synthetic_records"] > 0
    rows = dossier["gap_diagnosis"]["simulated_rules"]
    assert [row["rule_id"] for row in rows] == [
        "R6",
        "R7",
        "R8",
    ]
    assert all(row["synthetic_flag"] is True for row in rows)
    assert all(row["evidence_class"] == "D" for row in rows)
    assert all(row["display_label"] == DISCLOSURE for row in rows)

    assert html_response.status_code == 200
    assert DISCLOSURE in html_response.text
    assert "Simulated R6–R8 ledger" in html_response.text
    for rule_id in ("R6", "R7", "R8"):
        assert rule_id in html_response.text
