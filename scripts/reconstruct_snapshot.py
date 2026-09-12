"""Reconstruct acquired snapshots from raw store — offline."""

from __future__ import annotations

import hashlib
import json
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _install_socket_block() -> None:
    original = socket.socket.connect

    def blocked(self: socket.socket, address: object) -> None:
        raise RuntimeError(f"Socket connect blocked: {address!r}")

    socket.socket.connect = blocked  # type: ignore[method-assign]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest_paths_for_snapshot(
    snap_path: Path,
    data_root: Path,
) -> set[str]:
    record = json.loads(snap_path.read_text(encoding="utf-8"))
    rel_snap = f"data/{snap_path.relative_to(data_root).as_posix()}"
    paths = {rel_snap}
    for ref in record.get("raw_artifact_refs", []):
        paths.add(ref["path"])
    return paths


def _reconstruct_documents(
    data_root: Path,
    *,
    check_manifest: bool,
    manifest_rows: dict[str, tuple[str, int]],
) -> tuple[int, int]:
    from ior_mvp.acquisition.documents.store import DocumentStore, reconstruct_document
    from ior_mvp.acquisition.raw_store import RawStore
    from ior_mvp.acquisition.source_config import acquisition_sources_config

    documents_root = data_root / "documents"
    doc_store = DocumentStore(documents_root)
    records = list(doc_store.iter_records())
    if not records:
        return 0, 0

    config = acquisition_sources_config()
    raw_cfg = config["raw_store"]
    store = RawStore(
        data_root / "raw",
        max_artifact_bytes=raw_cfg["max_artifact_bytes_compressed"],
        max_store_bytes=raw_cfg["max_store_bytes_compressed"],
    )
    verified = 0
    for path, _ in records:
        rel = path.relative_to(data_root.parent).as_posix()
        record = json.loads(path.read_text(encoding="utf-8"))
        if check_manifest:
            manifest_refs = [rel]
            list_ref = record.get("list_ref", {})
            list_id = list_ref.get("list_id")
            if list_id:
                manifest_refs.append(
                    f"data/documents/{record['source_id']}/lists/{list_id}.json"
                )
            raw_ref = record.get("raw_artifact_ref", {})
            raw_path = raw_ref.get("path")
            if raw_path:
                if str(raw_path).startswith("data/"):
                    manifest_refs.append(str(raw_path))
                else:
                    try:
                        manifest_refs.append(
                            Path(str(raw_path)).resolve().relative_to(
                                data_root.parent.resolve()
                            ).as_posix()
                        )
                    except ValueError:
                        manifest_refs.append(str(raw_path))
            for manifest_ref in manifest_refs:
                if manifest_ref not in manifest_rows:
                    print(f"RECONSTRUCTION FAIL: manifest row missing for {manifest_ref}")
                    sys.exit(2)
            expected_hash, expected_bytes = manifest_rows[rel]
            actual = path.read_bytes()
            if _sha256_file(path) != expected_hash or len(actual) != expected_bytes:
                print(f"RECONSTRUCTION FAIL: manifest hash mismatch for {rel}")
                sys.exit(1)
        result = reconstruct_document(path, store, config, doc_store)
        verified += result.artifacts_verified
        if not result.match:
            detail = result.detail.get("reason", "BYTE_MISMATCH")
            print(f"RECONSTRUCTION FAIL: {result.snapshot_id} ({detail})")
            sys.exit(1)
    return len(records), verified


def main() -> None:
    _install_socket_block()
    import argparse

    from ior_mvp.acquisition.connectors.base import default_registry
    from ior_mvp.acquisition.raw_store import RawStore
    from ior_mvp.acquisition.snapshots import reconstruct
    from ior_mvp.acquisition.kinds import default_kind_registry
    from ior_mvp.acquisition.source_config import acquisition_sources_config

    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--data-root", type=Path, default=ROOT / "data")
    parser.add_argument("--no-check-manifest", action="store_true")
    args = parser.parse_args()

    data_root = args.data_root
    snapshots: list[Path] = []
    for kind, rel in default_kind_registry().roots().items():
        kind_dir = data_root / rel.replace("data/", "")
        if kind_dir.exists():
            snapshots.extend(sorted(kind_dir.glob("*.json")))

    from ior_mvp.acquisition.documents.store import DocumentStore

    doc_store = DocumentStore(data_root / "documents")
    has_documents = bool(list(doc_store.iter_records()))

    if not snapshots and not has_documents:
        print("RECONSTRUCTION FAIL: no acquired snapshots")
        sys.exit(1)

    config = acquisition_sources_config()
    raw_cfg = config["raw_store"]
    store = RawStore(
        data_root / "raw",
        max_artifact_bytes=raw_cfg["max_artifact_bytes_compressed"],
        max_store_bytes=raw_cfg["max_store_bytes_compressed"],
    )
    registry = default_registry()

    manifest_path = data_root / "manifests" / "snapshot_manifest.json"
    manifest_rows: dict[str, tuple[str, int]] = {}
    if not args.no_check_manifest:
        if not manifest_path.exists():
            print("RECONSTRUCTION FAIL: manifest missing")
            sys.exit(2)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_rows = {
            row["path"]: (row["sha256"], row["bytes"])
            for row in manifest["files"]
        }

    verified = 0
    for snap_path in snapshots:
        paths_to_check = _manifest_paths_for_snapshot(snap_path, data_root)
        if not args.no_check_manifest:
            for rel in sorted(paths_to_check):
                if rel not in manifest_rows:
                    print(f"RECONSTRUCTION FAIL: manifest row missing for {rel}")
                    sys.exit(2)
                expected_hash, expected_bytes = manifest_rows[rel]
                abs_path = data_root.parent / rel
                if not abs_path.exists():
                    print(f"RECONSTRUCTION FAIL: referenced file missing {rel}")
                    sys.exit(2)
                actual = abs_path.read_bytes()
                if (
                    _sha256_file(abs_path) != expected_hash
                    or len(actual) != expected_bytes
                ):
                    print(f"RECONSTRUCTION FAIL: manifest hash mismatch for {rel}")
                    sys.exit(1)

        result = reconstruct(snap_path, store, config, registry)
        verified += result.artifacts_verified
        if not result.match:
            detail = result.detail.get("reason", "BYTE_MISMATCH")
            print(
                f"RECONSTRUCTION FAIL: {result.snapshot_id} ({detail})"
            )
            sys.exit(1)

    doc_records, doc_artifacts = _reconstruct_documents(
        data_root,
        check_manifest=not args.no_check_manifest,
        manifest_rows=manifest_rows,
    )

    if snapshots or doc_records:
        print(
            f"RECONSTRUCTION PASS ({len(snapshots)} snapshots, {verified} artifacts)"
        )
    print(
        f"DOCUMENT RECONSTRUCTION PASS ({doc_records} records, {doc_artifacts} artifacts)"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
