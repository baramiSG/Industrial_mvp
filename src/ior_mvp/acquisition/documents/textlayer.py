"""Deterministic versioned text-layer derivation for document acquisition."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Mapping

from ..contracts import AcquisitionError

DOCUMENT_ENVELOPE_TYPES: frozenset[str] = frozenset({
    "application/pdf",
    "text/html",
    "application/xhtml+xml",
    "text/plain",
})

TEXT_LAYER_METHODS: Mapping[str, tuple[str, str]] = {
    "application/pdf": ("PDF_TEXT_LAYER_PYPDF_LAYOUT", "1.0.0"),
    "text/html": ("HTML_TEXT_LAYER_STDLIB", "1.0.0"),
    "application/xhtml+xml": ("HTML_TEXT_LAYER_STDLIB", "1.0.0"),
    "text/plain": ("PLAIN_TEXT_LAYER_STDLIB", "1.0.0"),
}

SEGMENTATION_METHOD: tuple[str, str] = ("LINE_SEGMENTATION_V1", "1.0.0")

BLOCK_TAGS = frozenset({
    "address", "article", "aside", "blockquote", "br", "details",
    "div", "dl", "dt", "dd", "fieldset", "figcaption", "figure", "footer", "form",
    "h1", "h2", "h3", "h4", "h5", "h6", "header", "hr", "li", "main", "nav",
    "ol", "p", "pre", "section", "table", "tbody", "td", "tfoot", "th", "thead",
    "tr", "ul",
})


class TextLayerDependencyError(AcquisitionError):
    """Required text-layer dependency is unavailable."""


@dataclass(frozen=True)
class TextLayerResult:
    status: str
    reason: str | None
    detail: str | None
    detail_error_type: str | None
    method_id: str | None
    method_version: str | None
    extraction_mode: str | None
    dependency: str | None
    pages: tuple[tuple[str, ...], ...]


def segment_lines(text: str) -> list[str]:
    """Split text into lines without normalisation; CRLF and lone CR become LF boundaries."""
    if not text:
        return []
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    if normalized.endswith("\n"):
        lines.pop()
    return lines


def page_text_sha256(lines: tuple[str, ...]) -> str:
    """Return SHA-256 of the newline-joined UTF-8 page lines."""
    payload = "\n".join(lines)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._suppressed: list[str] = []
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "template", "noscript"}:
            self._suppressed.append(tag)
            return
        if self._suppressed:
            return
        if tag in BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if self._suppressed:
            if tag == self._suppressed[-1]:
                self._suppressed.pop()
            return
        if tag in BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._suppressed and data:
            self._parts.append(data)

    def lines(self) -> list[str]:
        self.close()
        return segment_lines("".join(self._parts))


def _derive_pdf(payload: bytes) -> TextLayerResult:
    method_id, method_version = TEXT_LAYER_METHODS["application/pdf"]
    try:
        from pypdf import PdfReader
        from pypdf.errors import PyPdfError
    except ImportError as exc:
        raise TextLayerDependencyError("pypdf is required for PDF text extraction") from exc
    parser_errors = (
        PyPdfError,
        ValueError,
        TypeError,
        KeyError,
        IndexError,
        AttributeError,
        RecursionError,
        OverflowError,
        ZeroDivisionError,
        UnicodeError,
    )
    try:
        reader = PdfReader(__import__("io").BytesIO(payload))
    except parser_errors as exc:
        return TextLayerResult(
            status="UNAVAILABLE",
            reason="FORMAT_NOT_PARSEABLE",
            detail="PARSER_ERROR",
            detail_error_type=type(exc).__name__,
            method_id=method_id,
            method_version=method_version,
            extraction_mode="layout",
            dependency="pypdf==6.16.1",
            pages=(),
        )
    pages: list[tuple[str, ...]] = []
    for page in reader.pages:
        if "/Contents" not in page:
            text = ""
        else:
            try:
                text = page.extract_text(extraction_mode="layout") or ""
            except parser_errors as exc:
                return TextLayerResult(
                    status="UNAVAILABLE",
                    reason="FORMAT_NOT_PARSEABLE",
                    detail="PARSER_ERROR",
                    detail_error_type=type(exc).__name__,
                    method_id=method_id,
                    method_version=method_version,
                    extraction_mode="layout",
                    dependency="pypdf==6.16.1",
                    pages=(),
                )
        lines = segment_lines(text)
        pages.append(tuple(lines))
    has_text = any(line.strip() for lines in pages for line in lines)
    if not has_text:
        return TextLayerResult(
            status="UNAVAILABLE",
            reason="FORMAT_NOT_PARSEABLE",
            detail="NO_TEXT_LAYER",
            detail_error_type=None,
            method_id=method_id,
            method_version=method_version,
            extraction_mode="layout",
            dependency="pypdf==6.16.1",
            pages=tuple(pages),
        )
    return TextLayerResult(
        status="AVAILABLE",
        reason=None,
        detail=None,
        detail_error_type=None,
        method_id=method_id,
        method_version=method_version,
        extraction_mode="layout",
        dependency="pypdf==6.16.1",
        pages=tuple(pages),
    )


def _derive_html(payload: bytes, content_type: str) -> TextLayerResult:
    method_id, method_version = TEXT_LAYER_METHODS[content_type]
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeError:
        return TextLayerResult(
            status="UNAVAILABLE",
            reason="FORMAT_NOT_PARSEABLE",
            detail="NOT_UTF8",
            detail_error_type=None,
            method_id=method_id,
            method_version=method_version,
            extraction_mode=None,
            dependency=None,
            pages=(),
        )
    parser = _HTMLTextExtractor()
    parser.feed(text)
    lines = parser.lines()
    has_text = any(line.strip() for line in lines)
    return TextLayerResult(
        status="AVAILABLE" if has_text else "UNAVAILABLE",
        reason=None if has_text else "FORMAT_NOT_PARSEABLE",
        detail=None if has_text else "NO_TEXT_LAYER",
        detail_error_type=None,
        method_id=method_id,
        method_version=method_version,
        extraction_mode=None,
        dependency=None,
        pages=(tuple(lines),),
    )


def _derive_plain(payload: bytes) -> TextLayerResult:
    method_id, method_version = TEXT_LAYER_METHODS["text/plain"]
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeError:
        return TextLayerResult(
            status="UNAVAILABLE",
            reason="FORMAT_NOT_PARSEABLE",
            detail="NOT_UTF8",
            detail_error_type=None,
            method_id=method_id,
            method_version=method_version,
            extraction_mode=None,
            dependency=None,
            pages=(),
        )
    lines = segment_lines(text)
    has_text = any(line.strip() for line in lines)
    return TextLayerResult(
        status="AVAILABLE" if has_text else "UNAVAILABLE",
        reason=None if has_text else "FORMAT_NOT_PARSEABLE",
        detail=None if has_text else "NO_TEXT_LAYER",
        detail_error_type=None,
        method_id=method_id,
        method_version=method_version,
        extraction_mode=None,
        dependency=None,
        pages=(tuple(lines),),
    )


def derive_text_layer(payload: bytes, content_type: str) -> TextLayerResult:
    """Derive a deterministic text layer from raw document bytes."""
    mime = content_type.split(";", 1)[0].strip().casefold()
    if mime not in TEXT_LAYER_METHODS:
        raise ValueError(f"Unsupported content type for text layer: {content_type!r}")
    if mime == "application/pdf":
        return _derive_pdf(payload)
    if mime in {"text/html", "application/xhtml+xml"}:
        return _derive_html(payload, mime)
    return _derive_plain(payload)
