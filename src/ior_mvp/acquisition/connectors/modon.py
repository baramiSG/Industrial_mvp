"""MODON directory connector; no inferred source parser."""

from .base import InstitutionalConnector


class ModonConnector(InstitutionalConnector):
    source_id = "modon"
    snapshot_kinds = frozenset({"directory"})
    row_kind = "directory"
