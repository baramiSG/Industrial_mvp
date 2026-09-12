"""GASTAT aggregate connector; source payload shape remains unobserved."""

from .base import InstitutionalConnector


class GastatConnector(InstitutionalConnector):
    source_id = "gastat"
    snapshot_kinds = frozenset({"production"})
    row_kind = "production"
