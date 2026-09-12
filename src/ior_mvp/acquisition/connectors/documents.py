"""Document acquisition connectors."""

from __future__ import annotations

from typing import Any

from ..contracts import (
    PageMeta,
    QualityCheck,
    QualityReport,
    QueryContract,
    RawArtifact,
    Stage,
    UNAVAILABLE,
)
from ..documents.textlayer import DOCUMENT_ENVELOPE_TYPES, derive_text_layer
from .base import BaseConnector


class DocumentConnector(BaseConnector):
    snapshot_kinds = frozenset({"document"})
    parse_rows = None

    def _pre_storage_refusal(
        self, result: Any, stage: Stage
    ) -> tuple[str, str] | None:
        if stage is Stage.TERMS:
            return None
        if stage is Stage.DOCUMENT:
            mime = self._content_type(result).casefold()
            if mime not in DOCUMENT_ENVELOPE_TYPES:
                return (
                    "UnsupportedDocumentEnvelope",
                    "Response refused by document envelope policy; body not stored",
                )
            return None
        # DIRECTORY/REGISTRY keep the S12a text-only privacy guard exactly as BaseConnector
        # implements it (DD-7); every other stage returns None there.
        return super()._pre_storage_refusal(result, stage)

    def page_meta(self, payload: bytes, content_type: str) -> PageMeta:
        return PageMeta(
            page_index=1,
            pages_expected=1,
            next_page_token_present=False,
            rows_in_page=UNAVAILABLE,
            enumerated_children=None,
        )

    def classify_page(
        self, payload: bytes, content_type: str, stage: Stage
    ) -> tuple[str, str | None]:
        if stage is Stage.TERMS:
            return super().classify_page(payload, content_type, stage)
        derived = derive_text_layer(payload, content_type)
        if derived.status == "AVAILABLE":
            return "NORMALIZED", None
        return "UNPARSED", "no_text_layer"

    def validate(self, raw: RawArtifact) -> QualityReport:
        contract = raw.contract
        payload = self.store.read_payload(contract)
        identity_ok = (
            contract.source_id == self.source_id
            and contract.query_contract.stage is Stage.DOCUMENT
            and contract.reporter == self.source_config.get("reporter_code")
        )
        envelope_ok = contract.content_type.casefold() in DOCUMENT_ENVELOPE_TYPES
        hash_ok = contract.sha256 == __import__(
            "hashlib"
        ).sha256(payload).hexdigest()
        checks = (
            QualityCheck(
                "source_stage_reporter",
                "PASS" if identity_ok else "FAIL",
                "source identity",
            ),
            QualityCheck(
                "document_envelope",
                "PASS" if envelope_ok else "FAIL",
                "content type",
            ),
            QualityCheck(
                "payload_hash",
                "PASS" if hash_ok else "FAIL",
                "payload hash",
            ),
        )
        status = "PASS" if identity_ok and envelope_ok and hash_ok else "FAIL"
        return QualityReport(
            contract.source_id,
            contract.query_hash,
            contract.run_id,
            status,
            checks,
        )

    def normalize(self, raw: RawArtifact) -> list[Any]:
        return []

    def snapshot(self, observations: list[Any], as_of_date: Any) -> dict[str, Any]:
        raise NotImplementedError


class TadawulDisclosuresConnector(DocumentConnector):
    source_id = "tadawul_disclosures"


class EtimadTendersConnector(DocumentConnector):
    source_id = "etimad_tenders"


class SasoDocumentsConnector(DocumentConnector):
    source_id = "saso_documents"


class ProducerUnicoilConnector(DocumentConnector):
    source_id = "producer_unicoil"


class ProducerSabicConnector(DocumentConnector):
    source_id = "producer_sabic"


class ProducerAdvancedPetrochemicalConnector(DocumentConnector):
    source_id = "producer_advanced_petrochemical"


class ProducerTasneeConnector(DocumentConnector):
    source_id = "producer_tasnee"
