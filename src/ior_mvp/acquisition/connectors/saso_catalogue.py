"""SASO registry connector; catalogue metadata never establishes compliance."""

from .base import InstitutionalConnector


class SasoCatalogueConnector(InstitutionalConnector):
    source_id = "saso_catalogue"
    snapshot_kinds = frozenset({"registry"})
    row_kind = "registry"
