"""Raw store size budget tests."""

from __future__ import annotations

from ior_mvp.acquisition.source_config import acquisition_sources_config
from ior_mvp.config import PROJECT_ROOT


def test_raw_store_within_config_budget() -> None:
    cfg = acquisition_sources_config()
    max_store = cfg["raw_store"]["max_store_bytes_compressed"]
    max_artifact = cfg["raw_store"]["max_artifact_bytes_compressed"]
    raw = PROJECT_ROOT / "data" / "raw"
    if not raw.exists():
        return
    total = sum(p.stat().st_size for p in raw.rglob("*.gz"))
    assert total <= max_store
    for path in raw.rglob("*.gz"):
        assert path.stat().st_size <= max_artifact
