from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tomllib
from itertools import product
from pathlib import Path

import pytest

from ior_mvp.config import PROJECT_ROOT


BASELINE_ROOT = (
    PROJECT_ROOT / "browser_tests" / "baselines" / "v0.3.0"
)
MANIFEST = BASELINE_ROOT / "manifest.json"
MANIFEST_HASH = BASELINE_ROOT / "manifest.sha256"
MAKEFILE = PROJECT_ROOT / "Makefile"
RUNNER = PROJECT_ROOT / "scripts" / "run_visual_baseline_container.py"
IMAGE_DIGEST = (
    "mcr.microsoft.com/playwright/python:v1.62.0-noble@"
    "sha256:aa81288e738725378becba5b3e06cb0f3a7f012a610e87e8d767a090ea3f740d"
)
LOCALES = ("en", "ar")
VIEWPORTS = {
    "desktop-1440x900": (1440, 900),
    "tablet-1024x768": (1024, 768),
}
SCREENS = (
    "journey-a-portfolio-public",
    "journey-a-portfolio-simulated",
    "journey-b-steel-public-workspace",
    "journey-c-steel-simulated-workspace",
    "journey-d-polypropylene-public-workspace",
    "journey-d-polypropylene-simulated-workspace",
    "journey-e-steel-public-dossier",
    "journey-e-steel-simulated-dossier",
    "journey-e-polypropylene-public-dossier",
    "journey-e-polypropylene-simulated-dossier",
    "journey-f-screening-summary",
    "journey-f-screening-queue-robust",
    "journey-f-screening-queue-empty",
    "journey-f-screening-record",
)


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_pillow_is_an_exact_e2e_only_dependency() -> None:
    project = tomllib.loads(
        (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )

    assert project["project"]["optional-dependencies"]["dev"] == [
        "pytest>=8,<9",
        "httpx>=0.27,<1",
        "pypdf==6.16.1",
    ]
    assert project["project"]["optional-dependencies"]["e2e"] == [
        "Pillow==12.3.0",
        "playwright==1.62.0",
        "pytest-playwright==0.9.0",
    ]


def test_visual_manifest_has_exact_56_entry_locale_viewport_screen_matrix() -> None:
    entries = _manifest()["entries"]
    actual = {
        (entry["locale"], entry["viewport"], entry["screen"])
        for entry in entries
    }
    expected = set(product(LOCALES, VIEWPORTS, SCREENS))

    assert len(entries) == 56
    assert actual == expected
    assert len(actual) == len(entries)


def test_visual_manifest_and_every_webp_hash_size_dimensions_and_rgb_decode_match() -> None:
    manifest_bytes = MANIFEST.read_bytes()
    payload = _manifest()
    expected_manifest_hash = MANIFEST_HASH.read_text(
        encoding="ascii"
    ).strip()
    assert hashlib.sha256(manifest_bytes).hexdigest() == (
        expected_manifest_hash
    )
    assert (
        "config/decision_narratives.v1.yaml"
        in payload["source_tree"]
    )
    for path, digest in payload["source_tree"].items():
        assert hashlib.sha256(
            (PROJECT_ROOT / path).read_bytes()
        ).hexdigest() == digest
    for path, digest in payload["font_hashes"].items():
        assert hashlib.sha256(
            (PROJECT_ROOT / path).read_bytes()
        ).hexdigest() == digest
    for entry in payload["entries"]:
        path = BASELINE_ROOT / entry["path"]
        encoded = path.read_bytes()
        assert path.stat().st_size == entry["bytes"]
        assert hashlib.sha256(encoded).hexdigest() == entry["sha256"]
        assert encoded[:4] == b"RIFF"
        assert encoded[8:12] == b"WEBP"
        assert encoded[12:16] == b"VP8L"
        assert encoded[20] == 0x2F
        bits = int.from_bytes(encoded[21:25], "little")
        dimensions = (
            (bits & 0x3FFF) + 1,
            ((bits >> 14) & 0x3FFF) + 1,
        )
        alpha_used = (bits >> 28) & 1
        assert alpha_used == 0
        assert dimensions == tuple(entry["dimensions"])
        assert dimensions == VIEWPORTS[entry["viewport"]]


def test_visual_baseline_files_are_lossless_webp_with_600_kib_and_12_mib_budgets() -> None:
    files = sorted(BASELINE_ROOT.glob("*/*/*.webp"))

    assert len(files) == 56
    assert all(path.read_bytes()[12:16] == b"VP8L" for path in files)
    assert all(path.stat().st_size <= 600 * 1024 for path in files)
    assert sum(path.stat().st_size for path in files) <= 12 * 1024 * 1024


def test_visual_tolerance_is_global_fixed_and_strict() -> None:
    from scripts.visual_metrics import TOLERANCE

    payload = _manifest()

    assert TOLERANCE == {
        "channel_delta": 8,
        "significant_pixel_ratio": 0.001,
        "mean_absolute_channel_error": 0.20,
    }
    assert payload["tolerance"] == TOLERANCE
    assert not any("tolerance" in entry for entry in payload["entries"])


def test_visual_comparator_enforces_pixel_mean_and_dimension_rules(
) -> None:
    from scripts.visual_metrics import compare_pixel_buffers

    baseline = [(20, 20, 20)] * 10_000
    under = list(baseline)
    under[0] = (28, 20, 20)
    over = list(baseline)
    for index in range(11):
        over[index] = (29, 20, 20)

    assert compare_pixel_buffers(
        baseline,
        under,
        dimensions=(100, 100),
    )["passes"] is True
    over_metrics = compare_pixel_buffers(
        baseline,
        over,
        dimensions=(100, 100),
    )
    assert over_metrics["significant_pixel_ratio"] > 0.001
    assert over_metrics["passes"] is False
    with pytest.raises(ValueError, match="dimensions"):
        compare_pixel_buffers(
            baseline,
            under[:-1],
            dimensions=(100, 100),
        )


def test_visual_code_never_reads_s06_documentary_references() -> None:
    sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            PROJECT_ROOT / "browser_tests" / "visual_baselines.py",
            PROJECT_ROOT / "browser_tests" / "test_visual_baselines.py",
            PROJECT_ROOT / "scripts" / "visual_metrics.py",
            RUNNER,
        ]
    )

    assert "reference-screenshots/v0.2.0" not in sources
    assert "S06-browser-acceptance-harness" not in sources


def test_screening_visual_anchor_quantizes_scroll_before_capture() -> None:
    source = (
        PROJECT_ROOT / "browser_tests" / "test_visual_baselines.py"
    ).read_text(encoding="utf-8")

    assert "def _anchor_screening" in source
    assert "Math.round" in source
    assert "requestAnimationFrame" in source
    assert "page.screenshot(" in source


def test_screening_visual_anchor_waits_for_fonts_before_measuring_layout() -> None:
    source = (
        PROJECT_ROOT / "browser_tests" / "test_visual_baselines.py"
    ).read_text(encoding="utf-8")
    helper = source.split("def _anchor_screening", 1)[1].split(
        "@pytest.mark.parametrize", 1
    )[0]

    assert "await document.fonts.ready" in helper
    assert helper.index("await document.fonts.ready") < helper.index(
        "getBoundingClientRect"
    )


def test_screening_visual_anchor_cancels_smooth_scroll_before_capture() -> None:
    source = (
        PROJECT_ROOT / "browser_tests" / "test_visual_baselines.py"
    ).read_text(encoding="utf-8")
    helper = source.split("def _anchor_screening", 1)[1].split(
        "@pytest.mark.parametrize", 1
    )[0]

    assert 'root.style.scrollBehavior = "auto"' in helper
    assert 'behavior: "auto"' in helper
    assert "SCREENING_ANCHOR_NOT_SETTLED" in helper


def test_screening_visual_anchor_waits_for_navigation_scroll_to_settle() -> None:
    source = (
        PROJECT_ROOT / "browser_tests" / "test_visual_baselines.py"
    ).read_text(encoding="utf-8")
    helper = source.split("def _anchor_screening", 1)[1].split(
        "@pytest.mark.parametrize", 1
    )[0]

    assert "stableFrames < 3" in helper
    assert "NAVIGATION_SCROLL_NOT_SETTLED" in helper


def test_update_requires_explicit_flag_reason_non_ci_and_canonical_image() -> None:
    makefile = MAKEFILE.read_text(encoding="utf-8")

    assert 'test "$(IOR_UPDATE_VISUAL_BASELINES)" = "1"' in makefile
    assert 'test -n "$(IOR_BASELINE_CHANGE_REF)"' in makefile
    assert 'test -z "$(CI)"' in makefile
    assert "e2e-update-baselines:" in makefile
    assert "run_visual_baseline_container.py" in makefile
    assert IMAGE_DIGEST in (
        PROJECT_ROOT / "browser_tests" / "visual" / "Dockerfile"
    ).read_text(encoding="utf-8")


def test_container_runner_exits_2_with_clear_message_when_docker_is_unavailable() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--docker",
            "/definitely/missing/docker",
            "--image",
            "ior-visual-baselines:playwright-1.62.0-noble",
            "--mode",
            "compare",
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "Docker is unavailable" in result.stderr


def test_container_runner_mounts_only_the_exact_allow_list() -> None:
    from scripts import run_visual_baseline_container as runner
    mounts = runner.mount_specs(PROJECT_ROOT)
    inputs = {
        "src",
        "config",
        "data",
        "docs/authority",
        "browser_tests",
        "scripts",
        "pyproject.toml",
        "uv.lock",
    }

    assert {mount.relative for mount in mounts if mount.read_only} == inputs
    assert {
        mount.relative for mount in mounts if not mount.read_only
    } == {
        "browser_tests/baselines/v0.3.0",
        ".artifacts/e2e",
    }
    assert all(".env" not in mount.relative for mount in mounts)


def test_container_command_maps_host_user_and_safe_runtime_directories() -> None:
    from scripts import run_visual_baseline_container as runner

    command = runner.build_command(
        docker="docker",
        image="image",
        mode="update",
        change_ref="S08-test",
        uid=123,
        gid=456,
        root=PROJECT_ROOT,
    )

    assert command[command.index("--user") + 1] == "123:456"
    for value in (
        "HOME=/tmp",
        "XDG_CACHE_HOME=/tmp/.cache",
        "PLAYWRIGHT_BROWSERS_PATH=/ms-playwright",
        "IOR_HOST_UID=123",
        "IOR_HOST_GID=456",
    ):
        assert value in command


def test_ownership_sweep_accepts_host_owned_tree_and_reports_first_violation(
    tmp_path: Path,
) -> None:
    from scripts import run_visual_baseline_container as runner

    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    (first / "owned.txt").write_text("owned", encoding="utf-8")
    wrong = second / "wrong.txt"
    wrong.write_text("wrong", encoding="utf-8")

    assert runner.first_non_owned_path(
        (first,),
        expected_uid=os.getuid(),
    ) is None

    real_stat = os.stat

    def fake_stat(path: Path, *, follow_symlinks: bool) -> object:
        result = real_stat(path, follow_symlinks=follow_symlinks)
        if Path(path) == wrong:
            values = list(result)
            values[4] = os.getuid() + 1
            return os.stat_result(values)
        return result

    assert runner.first_non_owned_path(
        (first, second),
        expected_uid=os.getuid(),
        stat_func=fake_stat,
    ) == wrong


def test_container_identity_mismatch_fails_before_visual_pytest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from browser_tests import visual_container

    monkeypatch.setenv("IOR_HOST_UID", "123")
    monkeypatch.setenv("IOR_HOST_GID", "456")
    monkeypatch.setattr(visual_container.os, "geteuid", lambda: 999)
    monkeypatch.setattr(visual_container.os, "getegid", lambda: 456)

    with pytest.raises(RuntimeError, match="UID/GID"):
        visual_container.assert_container_identity()


def test_visual_container_disables_read_only_workspace_pytest_cache() -> None:
    source = (
        PROJECT_ROOT / "browser_tests" / "visual_container.py"
    ).read_text(encoding="utf-8")

    assert '"-p",\n            "no:cacheprovider",' in source


def test_container_runner_requires_chromium_1234_and_records_browser_metadata() -> None:
    runner_source = RUNNER.read_text(encoding="utf-8")
    manifest = _manifest()

    assert "chromium-1234" in runner_source
    assert manifest["chromium_revision"] == "chromium-1234"
    assert manifest["browser_version"]
    assert manifest["launch_flags"] == [
        "--font-render-hinting=none",
        "--disable-lcd-text",
        "--force-color-profile=srgb",
    ]


def test_make_e2e_compare_does_not_require_docker_or_container_runner() -> None:
    makefile = MAKEFILE.read_text(encoding="utf-8")
    match = re.search(
        r"(?m)^e2e:[^\n]*(?:\n\t[^\n]*)*",
        makefile,
    )
    assert match is not None
    compare = match.group(0)

    assert "e2e-functional" in compare
    assert "e2e-visual" in compare
    assert "docker" not in compare.lower()
    assert "run_visual_baseline_container.py" not in compare


def test_ci_contains_no_baseline_update_mode_or_target() -> None:
    workflow = (
        PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
    ).read_text(encoding="utf-8")

    assert "IOR_UPDATE_VISUAL_BASELINES" not in workflow
    assert "e2e-update-baselines" not in workflow
    assert "--mode update" not in workflow
