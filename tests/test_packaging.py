from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from zipfile import ZipFile

from ior_mvp.config import PROJECT_ROOT


def test_package_contains_only_tracked_files(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "package-fixture"
    scripts_dir = repository / "scripts"
    scripts_dir.mkdir(parents=True)
    shutil.copy2(
        PROJECT_ROOT / "scripts" / "package_project.sh",
        scripts_dir / "package_project.sh",
    )
    (repository / "README.md").write_text(
        "tracked\n",
        encoding="utf-8",
    )
    (repository / ".env").write_text(
        "UNTRACKED=1\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["git", "init", "-q"],
        cwd=repository,
        check=True,
    )
    subprocess.run(
        ["git", "add", "README.md"],
        cwd=repository,
        check=True,
    )
    archive = tmp_path / "project.zip"

    subprocess.run(
        ["bash", "scripts/package_project.sh", str(archive)],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )

    with ZipFile(archive) as package:
        members = package.namelist()
    assert f"{repository.name}/README.md" in members
    assert not any(member.endswith("/.env") for member in members)
    assert not any("/.git/" in member for member in members)


def test_package_fails_outside_git_repository(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "not-a-repository"
    scripts_dir = repository / "scripts"
    scripts_dir.mkdir(parents=True)
    shutil.copy2(
        PROJECT_ROOT / "scripts" / "package_project.sh",
        scripts_dir / "package_project.sh",
    )

    result = subprocess.run(
        ["bash", "scripts/package_project.sh"],
        cwd=repository,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "Git working tree" in result.stderr
