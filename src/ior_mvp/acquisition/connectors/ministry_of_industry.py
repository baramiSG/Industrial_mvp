"""Ministry of Industry directory connector; no inferred source parser."""

from .base import InstitutionalConnector


class MinistryOfIndustryConnector(InstitutionalConnector):
    source_id = "ministry_of_industry"
    snapshot_kinds = frozenset({"directory"})
    row_kind = "directory"
