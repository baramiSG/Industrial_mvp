from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = [
    ROOT / "data" / "manifests" / "snapshot_manifest.json",
    ROOT / "docs" / "authority" / "authority_hashes.json",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_manifest(path: Path) -> list[str]:
    if not path.exists():
        return [f"Missing manifest: {path.relative_to(ROOT)}"]
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    for item in payload.get("files", []):
        target = ROOT / item["path"]
        if not target.exists():
            errors.append(f"Missing file: {item['path']}")
            continue
        actual = sha256(target)
        if actual != item["sha256"]:
            errors.append(f"Hash mismatch: {item['path']} expected={item['sha256']} actual={actual}")
    return errors


def main() -> None:
    errors: list[str] = []
    for manifest in MANIFESTS:
        errors.extend(verify_manifest(manifest))
    if errors:
        print("INTEGRITY FAIL")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("INTEGRITY PASS")
    for manifest in MANIFESTS:
        print(f"- {manifest.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
