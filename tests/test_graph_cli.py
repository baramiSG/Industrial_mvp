from __future__ import annotations

from ior_mvp.graph.cli import main


def test_credential_command_never_prints_value(tmp_path, capsys) -> None:
    path = tmp_path / ".secrets/neo4j_auth.txt"
    assert main(["credential", "--path", str(path)]) == 0
    output = capsys.readouterr().out.strip()
    assert output == "CREDENTIAL_CREATED"
    assert path.read_text(encoding="utf-8").strip() not in output
    assert main(["credential", "--path", str(path)]) == 0
    assert capsys.readouterr().out.strip() == "CREDENTIAL_PRESENT"


def test_aura_mismatch_exits_before_driver_creation(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setenv(
        "NEO4J_URI",
        "neo4j+s://wrong.databases.neo4j.io",
    )
    monkeypatch.setenv("NEO4J_USERNAME", "neo4j")
    monkeypatch.setenv("NEO4J_PASSWORD", "not-printed")
    monkeypatch.setenv("NEO4J_DATABASE", "neo4j")
    monkeypatch.setenv("AURA_INSTANCEID", "expected")
    assert (
        main(
            [
                "load",
                "--target",
                "aura",
                "--confirm-instance",
                "expected",
            ]
        )
        == 3
    )
    captured = capsys.readouterr()
    assert "INSTANCE_MISMATCH" in captured.err
    assert "not-printed" not in captured.err
