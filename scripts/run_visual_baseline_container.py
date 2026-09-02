from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence


ROOT = Path(__file__).resolve().parents[1]
CHROMIUM_REVISION = "chromium-1234"


@dataclass(frozen=True)
class MountSpec:
    relative: str
    read_only: bool


def mount_specs(root: Path = ROOT) -> tuple[MountSpec, ...]:
    """Return the exact no-secret container mount allow-list."""
    del root
    return (
        MountSpec("src", True),
        MountSpec("config", True),
        MountSpec("data", True),
        MountSpec("docs/authority", True),
        MountSpec("browser_tests", True),
        MountSpec("scripts", True),
        MountSpec("pyproject.toml", True),
        MountSpec("uv.lock", True),
        MountSpec("browser_tests/baselines/v0.3.0", False),
        MountSpec(".artifacts/e2e", False),
    )


def docker_available(docker: str) -> bool:
    try:
        result = subprocess.run(
            [docker, "version", "--format", "{{.Server.Version}}"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return False
    return result.returncode == 0 and bool(result.stdout.strip())


def build_command(
    *,
    docker: str,
    image: str,
    mode: str,
    change_ref: str,
    uid: int,
    gid: int,
    root: Path = ROOT,
) -> list[str]:
    """Build one shell-free Docker command from allow-listed values."""
    command = [
        docker,
        "run",
        "--rm",
        "--network=none",
        "--ipc=host",
        "--user",
        f"{uid}:{gid}",
        "--env",
        "HOME=/tmp",
        "--env",
        "XDG_CACHE_HOME=/tmp/.cache",
        "--env",
        "PLAYWRIGHT_BROWSERS_PATH=/ms-playwright",
        "--env",
        f"IOR_HOST_UID={uid}",
        "--env",
        f"IOR_HOST_GID={gid}",
        "--env",
        "IOR_E2E_EXPLICIT=1",
        "--env",
        "IOR_E2E_ARTIFACT_DIR=/workspace/.artifacts/e2e",
        "--env",
        f"IOR_VISUAL_MODE={mode}",
        "--env",
        f"IOR_BASELINE_CHANGE_REF={change_ref}",
        "--env",
        "IOR_CANONICAL_VISUAL=1",
        "--env",
        f"IOR_CHROMIUM_REVISION={CHROMIUM_REVISION}",
        "--env",
        "PYTHONPATH=/workspace/src",
    ]
    for mount in mount_specs(root):
        source = (root / mount.relative).resolve()
        destination = f"/workspace/{mount.relative}"
        option = f"type=bind,src={source},dst={destination}"
        if mount.read_only:
            option += ",readonly"
        command.extend(["--mount", option])
    command.extend(
        [
            image,
            "python",
            "browser_tests/visual_container.py",
            "--mode",
            mode,
        ]
    )
    if change_ref:
        command.extend(["--change-ref", change_ref])
    return command


def first_non_owned_path(
    roots: Sequence[Path],
    *,
    expected_uid: int,
    stat_func: Callable[..., os.stat_result] = os.stat,
) -> Path | None:
    """Return the first written path not owned by the expected host UID."""
    for root in roots:
        paths = [root, *sorted(root.rglob("*"))] if root.exists() else []
        for path in paths:
            if (
                stat_func(path, follow_symlinks=False).st_uid
                != expected_uid
            ):
                return path
    return None


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docker", default="docker")
    parser.add_argument("--image", required=True)
    parser.add_argument(
        "--mode",
        required=True,
        choices=("compare", "update"),
    )
    parser.add_argument("--change-ref", default="")
    args = parser.parse_args(argv)
    if not docker_available(args.docker):
        print(
            "VISUAL BASELINE CONTAINER ERROR: Docker is unavailable",
            file=sys.stderr,
        )
        return 2
    if args.mode == "update":
        if os.environ.get("IOR_UPDATE_VISUAL_BASELINES") != "1":
            print(
                "VISUAL BASELINE CONTAINER ERROR: "
                "IOR_UPDATE_VISUAL_BASELINES=1 is required",
                file=sys.stderr,
            )
            return 2
        if not args.change_ref or os.environ.get("CI"):
            print(
                "VISUAL BASELINE CONTAINER ERROR: "
                "a change reference is required and CI updates are forbidden",
                file=sys.stderr,
            )
            return 2
    for mount in mount_specs(ROOT):
        path = ROOT / mount.relative
        if mount.read_only and not path.exists():
            print(
                f"VISUAL BASELINE CONTAINER ERROR: missing {mount.relative}",
                file=sys.stderr,
            )
            return 2
        if not mount.read_only:
            path.mkdir(parents=True, exist_ok=True)
    uid = os.getuid()
    gid = os.getgid()
    result = subprocess.run(
        build_command(
            docker=args.docker,
            image=args.image,
            mode=args.mode,
            change_ref=args.change_ref,
            uid=uid,
            gid=gid,
        ),
        check=False,
    )
    if result.returncode != 0:
        return result.returncode
    if args.mode == "update":
        writable_roots = tuple(
            ROOT / mount.relative
            for mount in mount_specs(ROOT)
            if not mount.read_only
        )
        wrong_owner = first_non_owned_path(
            writable_roots,
            expected_uid=uid,
        )
        if wrong_owner is not None:
            try:
                display = wrong_owner.relative_to(ROOT)
            except ValueError:
                display = wrong_owner
            actual_uid = os.stat(
                wrong_owner,
                follow_symlinks=False,
            ).st_uid
            print(
                "VISUAL BASELINE CONTAINER ERROR: "
                f"{display} owner uid={actual_uid}, expected uid={uid}",
                file=sys.stderr,
            )
            return 2
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
