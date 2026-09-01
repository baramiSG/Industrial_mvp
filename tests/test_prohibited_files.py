from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

import pytest

import scripts.check_prohibited_files as scanner
from scripts.check_prohibited_files import Finding, ScannerError


@pytest.mark.parametrize(
    ("path", "rule"),
    [
        ("download:Zone.Identifier", "path:Zone.Identifier"),
        (".env", "path:.env"),
        ("nested/.env/value", "path:.env"),
        (".venv/bin/python", "path:.venv/"),
        ("pkg/__pycache__/module.py", "path:__pycache__"),
        ("pkg/module.PYC", "path:*.pyc"),
        ("assets/.DS_Store", "path:.DS_Store"),
        ("certs/server.PEM", "path:*.pem"),
        ("certs/server.KEY", "path:*.key"),
        ("certs/server.P12", "path:*.p12"),
        (".workflow/logs/run.log", "path:.workflow/logs/"),
    ],
)
def test_scan_tracked_files_flags_every_prohibited_path(path: str, rule: str) -> None:
    assert scanner.scan_tracked_files({path: b"safe"}) == (
        Finding(path=path, rule=rule),
    )


def test_scan_tracked_files_allows_env_example() -> None:
    assert scanner.scan_tracked_files({".env.example": b"IOR_HOST=127.0.0.1\n"}) == ()


@pytest.mark.parametrize(
    "path",
    [".env.template", "foo.env", "src/ior_mvp/app.py"],
)
def test_scan_tracked_files_allows_non_prohibited_paths(path: str) -> None:
    assert scanner.scan_tracked_files({path: b"safe"}) == ()


def test_normalize_path_handles_dot_prefix_and_backslashes() -> None:
    assert scanner.normalize_path("./.env") == ".env"
    assert scanner.normalize_path("a\\b\\c.txt") == "a/b/c.txt"


@pytest.mark.parametrize(
    ("content", "rule"),
    [
        (("ghp_" + "A" * 36).encode(), "secret:github-pat"),
        (("AKIA" + "A" * 16).encode(), "secret:aws-access-key"),
        (
            ("-" * 5 + "BEGIN OPENSSH PRIVATE KEY" + "-" * 5).encode(),
            "secret:private-key-header",
        ),
        (("sk-" + "A" * 20).encode(), "secret:sk-token"),
    ],
)
def test_scan_tracked_files_flags_each_secret_pattern(content: bytes, rule: str) -> None:
    findings = scanner.scan_tracked_files({"fixture.txt": content})
    assert findings == (Finding(path="fixture.txt", rule=rule),)


def test_scan_tracked_files_skips_secret_matching_for_binary_content() -> None:
    content = b"\x00" + ("ghp_" + "A" * 36).encode()
    assert scanner.scan_tracked_files({"image.bin": content}) == ()


def test_scan_tracked_files_applies_path_rules_to_invalid_utf8() -> None:
    content = b"\xff" + ("ghp_" + "A" * 36).encode()
    assert scanner.scan_tracked_files({"certs/server.key": content}) == (
        Finding(path="certs/server.key", rule="path:*.key"),
    )


def test_scan_tracked_files_is_deterministic() -> None:
    first = {".env": b"x", "private.key": b"y"}
    second = {"private.key": b"y", ".env": b"x"}
    assert scanner.scan_tracked_files(first) == scanner.scan_tracked_files(second)
    assert scanner.scan_tracked_files(first) == tuple(sorted(scanner.scan_tracked_files(first)))


def test_parse_git_ls_files_uses_nul_delimiters() -> None:
    assert scanner.parse_git_ls_files(b"b file.txt\0a.txt\0") == ("a.txt", "b file.txt")


def test_git_tracked_paths_invokes_nul_delimited_git(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def fake_run(
        command: list[str],
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[bytes]:
        assert command == ["git", "ls-files", "-z"]
        assert kwargs["cwd"] == tmp_path
        return subprocess.CompletedProcess(
            command,
            returncode=0,
            stdout=b"b.txt\0a.txt\0",
            stderr=b"",
        )

    monkeypatch.setattr(scanner.subprocess, "run", fake_run)
    assert scanner.git_tracked_paths(tmp_path) == ("a.txt", "b.txt")


def test_load_tracked_files_fails_closed_for_a_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ScannerError, match="unable to read tracked file: missing.txt"):
        scanner.load_tracked_files(tmp_path, ("missing.txt",))


def test_main_returns_one_for_a_planted_zone_identifier(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    finding = Finding(
        path="scanner-probe:Zone.Identifier",
        rule="path:Zone.Identifier",
    )
    monkeypatch.setattr(scanner, "scan_repository", lambda _root: ((finding,), 1))

    assert scanner.main(Path("/repository")) == 1
    captured = capsys.readouterr()
    assert "PROHIBITED FILE SCAN FAIL" in captured.err
    assert "scanner-probe:Zone.Identifier: path:Zone.Identifier" in captured.err


def test_main_never_prints_a_matched_secret(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    secret = "ghp_" + "A" * 36
    findings = scanner.scan_tracked_files({"fixture.txt": secret.encode()})
    monkeypatch.setattr(scanner, "scan_repository", lambda _root: (findings, 1))

    assert scanner.main(Path("/repository")) == 1
    captured = capsys.readouterr()
    assert secret not in captured.out
    assert secret not in captured.err
    assert "fixture.txt: secret:github-pat" in captured.err


def test_main_returns_two_when_git_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail_scan(_root: Path) -> tuple[tuple[Finding, ...], int]:
        raise ScannerError("git executable not found")

    monkeypatch.setattr(scanner, "scan_repository", fail_scan)
    assert scanner.main(Path("/repository")) == 2
    assert "PROHIBITED FILE SCAN ERROR: git executable not found" in capsys.readouterr().err


def test_main_scans_a_real_git_repository_without_following_symlinks(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)

    (tmp_path / "safe.txt").write_bytes(b"IOR_HOST=127.0.0.1\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "safe.txt"], check=True)
    assert scanner.main(tmp_path) == 0
    captured = capsys.readouterr()
    assert "PROHIBITED FILE SCAN PASS (1 tracked files)" in captured.out

    (tmp_path / ".env").write_bytes(b"placeholder\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "-f", ".env"], check=True)
    assert scanner.main(tmp_path) == 1
    captured = capsys.readouterr()
    assert "- .env: path:.env" in captured.err
    assert "placeholder" not in captured.err

    secret = "ghp_" + "A" * 36
    (tmp_path / "target.txt").write_text(secret, encoding="utf-8")
    os.symlink("target.txt", tmp_path / "link.txt")
    subprocess.run(["git", "-C", str(tmp_path), "add", "link.txt"], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "rm", "--cached", "-q", ".env"],
        check=True,
    )
    (tmp_path / ".env").unlink()

    assert scanner.main(tmp_path) == 0
    captured = capsys.readouterr()
    assert secret not in captured.out
    assert secret not in captured.err
