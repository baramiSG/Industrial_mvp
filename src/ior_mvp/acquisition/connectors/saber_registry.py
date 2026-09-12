"""SABER registry connector; registration never establishes buyer qualification."""

from .base import InstitutionalConnector


class SaberRegistryConnector(InstitutionalConnector):
    source_id = "saber_registry"
    snapshot_kinds = frozenset({"registry"})
    row_kind = "registry"
