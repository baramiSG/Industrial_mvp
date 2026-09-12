from __future__ import annotations

import re
import subprocess
import sys

from ior_mvp.acquisition.entities.ids import (
    ENTITY_ID_PATTERN,
    company_key,
    entity_id,
    licence_holder_key,
    line_key,
    plant_key,
)


def test_entity_id_v1_format_and_type_prefix() -> None:
    value = entity_id("COMPANY", company_key("universal metal coating company"))

    assert re.fullmatch(ENTITY_ID_PATTERN, value)
    assert value.startswith("COMPANY-")


def test_entity_id_deterministic_across_two_process_invocations() -> None:
    script = (
        "from ior_mvp.acquisition.entities.ids import company_key,entity_id;"
        "print(entity_id('COMPANY',company_key('universal metal coating company')))"
    )

    first = subprocess.check_output([sys.executable, "-c", script], text=True).strip()
    second = subprocess.check_output([sys.executable, "-c", script], text=True).strip()

    assert first == second


def test_company_key_uses_exact_normalised_primary_name_only() -> None:
    assert company_key("universal metal coating company") == (
        "ENTITY_ID_V1|COMPANY|universal metal coating company"
    )


def test_plant_key_includes_company_id_and_locality_token() -> None:
    company_id = entity_id("COMPANY", company_key("universal metal coating company"))

    assert plant_key(company_id, "SAU-JUBAIL") == (
        f"ENTITY_ID_V1|PLANT|{company_id}|SAU-JUBAIL"
    )


def test_line_key_includes_plant_id_and_designation() -> None:
    assert line_key("PLANT-0123456789abcdef", "line 4") == (
        "ENTITY_ID_V1|LINE|PLANT-0123456789abcdef|line 4"
    )


def test_licence_holder_key_is_a_separate_namespace() -> None:
    exact = "universal metal coating company"

    assert licence_holder_key(exact) != company_key(exact)
    assert entity_id("LICENCE_HOLDER", licence_holder_key(exact)).startswith(
        "LICENCE_HOLDER-"
    )


def test_entity_id_never_reissued_when_display_name_changes() -> None:
    canonical_key = company_key("universal metal coating company")
    before = entity_id("COMPANY", canonical_key)
    display_name_after_change = "Universal Metal Coating Company / UNICOIL"

    assert display_name_after_change
    assert entity_id("COMPANY", canonical_key) == before
