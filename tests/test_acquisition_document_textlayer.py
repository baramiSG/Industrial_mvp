"""Document text-layer derivation tests — pypdf pin and deterministic extraction."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "acquisition" / "documents"


def test_pypdf_pin_exact_and_dev_extra_only() -> None:
    import re
    import tomllib

    import pypdf

    assert pypdf.__version__ == "6.16.1"
    proj = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert "pypdf==6.16.1" in proj["optional-dependencies"]["dev"]
    assert not any(d.startswith("pypdf") for d in proj["dependencies"])
    lock = Path("uv.lock").read_text(encoding="utf-8")
    assert re.search(r'name = "pypdf"\nversion = "6.16.1"', lock)
    assert "name = \"arabic-reshaper\"" not in lock
    assert "name = \"python-bidi\"" not in lock


def test_layout_mode_available() -> None:
    from pypdf import PdfReader

    reader = PdfReader(FIXTURES / "test_double_latin_two_pages.pdf")
    text = reader.pages[0].extract_text(extraction_mode="layout")
    assert isinstance(text, str)


def test_latin_pdf_two_pages_lines_and_pinned_hash() -> None:
    from ior_mvp.acquisition.documents.textlayer import derive_text_layer, page_text_sha256

    payload = (FIXTURES / "test_double_latin_two_pages.pdf").read_bytes()
    result = derive_text_layer(payload, "application/pdf")
    assert result.status == "AVAILABLE"
    assert result.method_id == "PDF_TEXT_LAYER_PYPDF_LAYOUT"
    assert len(result.pages) == 2
    assert "TEST DOUBLE - NOT REAL EVIDENCE" in result.pages[0][0]
    digest = hashlib.sha256(
        json.dumps(
            {"pages": result.pages, "method": result.method_id, "version": result.method_version},
            sort_keys=True,
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()
    assert digest == "52dd2a46192c39cf23f2551763a6c753fcf9573d5050a1119852b194e5fa6099"


def test_page_text_sha256_hashes_newline_joined_lines() -> None:
    from ior_mvp.acquisition.documents.textlayer import page_text_sha256

    lines = ("first", "", "الثالث")
    expected = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
    assert page_text_sha256(lines) == expected


def test_pdf_keeps_empty_pages_at_physical_page_indexes() -> None:
    from io import BytesIO

    from pypdf import PdfReader, PdfWriter

    from ior_mvp.acquisition.documents.textlayer import derive_text_layer

    source = PdfReader(FIXTURES / "test_double_latin_two_pages.pdf")
    writer = PdfWriter()
    writer.add_page(source.pages[0])
    writer.add_blank_page(
        width=float(source.pages[0].mediabox.width),
        height=float(source.pages[0].mediabox.height),
    )
    writer.add_page(source.pages[1])
    payload = BytesIO()
    writer.write(payload)
    pdf_bytes = payload.getvalue()
    assert pdf_bytes.rstrip().endswith(b"%%EOF")

    result = derive_text_layer(pdf_bytes, "application/pdf")
    assert result.status == "AVAILABLE"
    assert len(result.pages) == 3
    assert result.pages[0]
    assert result.pages[1] == ()
    assert result.pages[2]


def test_arabic_cid_pdf_preserves_logical_order_verbatim() -> None:
    from ior_mvp.acquisition.documents.textlayer import derive_text_layer

    payload = (FIXTURES / "test_double_arabic_cid.pdf").read_bytes()
    result = derive_text_layer(payload, "application/pdf")
    assert result.status == "AVAILABLE"
    assert result.pages[0][:2] == (
        "الحد الأدنى الإلزامي 60 جم/م2",
        "Minimum coating 60 gsm",
    )
    assert len(result.pages[0]) >= 2


def test_derivation_deterministic_across_two_process_invocations() -> None:
    script = """
import json, sys
from pathlib import Path
from ior_mvp.acquisition.documents.textlayer import derive_text_layer
p = Path(sys.argv[1]).read_bytes()
r = derive_text_layer(p, sys.argv[2])
print(json.dumps({"status": r.status, "pages": r.pages, "method_id": r.method_id}, ensure_ascii=False))
"""
    payload = (FIXTURES / "test_double_latin_two_pages.pdf").read_bytes()
    env = {"PYTHONPATH": "src"}
    cmd = [sys.executable, "-c", script, str(FIXTURES / "test_double_latin_two_pages.pdf"), "application/pdf"]
    out1 = subprocess.check_output(cmd, env={**subprocess.os.environ, **env}, text=True)
    out2 = subprocess.check_output(cmd, env={**subprocess.os.environ, **env}, text=True)
    assert out1 == out2


def test_no_text_layer_pdf_is_unavailable_format_not_parseable() -> None:
    from ior_mvp.acquisition.documents.textlayer import derive_text_layer

    payload = (FIXTURES / "test_double_no_text_layer.pdf").read_bytes()
    result = derive_text_layer(payload, "application/pdf")
    assert result.status == "UNAVAILABLE"
    assert result.reason == "FORMAT_NOT_PARSEABLE"
    assert result.detail == "NO_TEXT_LAYER"
    assert result.pages == ((),)


@pytest.mark.parametrize(
    "payload,content_type",
    [
        (b"", "text/plain"),
        (b"<html><body>   </body></html>", "text/html"),
    ],
)
def test_text_layer_requires_a_non_whitespace_line(
    payload: bytes, content_type: str
) -> None:
    from ior_mvp.acquisition.documents.textlayer import derive_text_layer

    result = derive_text_layer(payload, content_type)
    assert result.status == "UNAVAILABLE"
    assert not any(line.strip() for page in result.pages for line in page)


def test_garbage_pdf_is_parser_error() -> None:
    from ior_mvp.acquisition.documents.textlayer import derive_text_layer

    payload = (FIXTURES / "test_double_garbage.pdf").read_bytes()
    result = derive_text_layer(payload, "application/pdf")
    assert result.status == "UNAVAILABLE"
    assert result.reason == "FORMAT_NOT_PARSEABLE"
    assert result.detail_error_type == "PdfStreamError"


def test_html_derivation_block_tags_script_style_bom_and_arabic() -> None:
    from ior_mvp.acquisition.documents.textlayer import derive_text_layer

    payload = (FIXTURES / "test_double_arabic_english.html").read_bytes()
    result = derive_text_layer(payload, "text/html")
    assert result.status == "AVAILABLE"
    assert result.method_id == "HTML_TEXT_LAYER_STDLIB"
    assert result.pages[0] == (
        "",
        "",
        "TEST DOUBLE - NOT REAL EVIDENCE",
        "",
        "",
        "",
        "",
        "",
        "العربية paragraph with U+200F\u200f marker",
        "",
        "",
        "English paragraph for bilingual fixture",
        "",
        "",
        "",
        "",
        "Header AR",
        "",
        "Header EN",
        "",
        "",
        "",
        "",
        "خلية",
        "",
        "Cell",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    )
    flat = "\n".join(line for page in result.pages for line in page)
    assert "\u200f" in result.pages[0][8]
    assert "script-body-hidden" not in flat
    assert "style-body-hidden" not in flat
    assert "\ufeff" not in flat or result.pages[0][0][0] != "\ufeff"


@pytest.mark.parametrize(
    ("payload", "expected"),
    (
        (
            b"<table><tr><td>a</td><td>b</td></tr></table>",
            ("", "", "", "a", "", "b", "", ""),
        ),
        (b"<div><p>a</p></div>", ("", "", "a", "")),
        (
            b"<ul><li>one</li><li>two</li></ul>",
            ("", "", "one", "", "two", ""),
        ),
    ),
)
def test_html_derivation_literal_dd5_block_boundaries(
    payload: bytes, expected: tuple[str, ...]
) -> None:
    from ior_mvp.acquisition.documents.textlayer import derive_text_layer

    result = derive_text_layer(payload, "text/html")
    assert result.pages == (expected,)


def test_html_derivation_deterministic_across_processes() -> None:
    script = """
import json, sys
from pathlib import Path
from ior_mvp.acquisition.documents.textlayer import derive_text_layer
r = derive_text_layer(Path(sys.argv[1]).read_bytes(), "text/html")
print(json.dumps(r.pages, ensure_ascii=False))
"""
    path = FIXTURES / "test_double_arabic_english.html"
    env = {"PYTHONPATH": "src"}
    cmd = [sys.executable, "-c", script, str(path)]
    out1 = subprocess.check_output(cmd, env={**subprocess.os.environ, **env}, text=True)
    out2 = subprocess.check_output(cmd, env={**subprocess.os.environ, **env}, text=True)
    assert out1 == out2


def test_html_suppresses_template_and_noscript_with_exact_block_tags() -> None:
    from ior_mvp.acquisition.documents.textlayer import BLOCK_TAGS, derive_text_layer

    assert BLOCK_TAGS == frozenset(
        {
            "address", "article", "aside", "blockquote", "br", "dd", "details",
            "div", "dl", "dt", "fieldset", "figcaption", "figure", "footer",
            "form", "h1", "h2", "h3", "h4", "h5", "h6", "header", "hr", "li",
            "main", "nav", "ol", "p", "pre", "section", "table", "tbody", "td",
            "tfoot", "th", "thead", "tr", "ul",
        }
    )
    result = derive_text_layer(
        b"<div>visible</div><template>hidden-template</template>"
        b"<noscript>hidden-noscript</noscript>",
        "text/html",
    )
    flat = "\n".join(line for page in result.pages for line in page)
    assert "visible" in flat
    assert "hidden-template" not in flat
    assert "hidden-noscript" not in flat


def test_html_not_utf8_is_unavailable() -> None:
    from ior_mvp.acquisition.documents.textlayer import derive_text_layer

    payload = (FIXTURES / "test_double_windows1256.html").read_bytes()
    result = derive_text_layer(payload, "text/html")
    assert result.status == "UNAVAILABLE"
    assert result.detail == "NOT_UTF8"


def test_plain_text_crlf_segmentation() -> None:
    from ior_mvp.acquisition.documents.textlayer import derive_text_layer

    payload = (FIXTURES / "test_double_plain_crlf.txt").read_bytes()
    result = derive_text_layer(payload, "text/plain")
    assert result.status == "AVAILABLE"
    assert result.method_id == "PLAIN_TEXT_LAYER_STDLIB"
    assert len(result.pages) == 1
    assert any("Arabic" in line or "العربية" in line for line in result.pages[0])


@pytest.mark.parametrize(
    "text,expected",
    [
        ("", []),
        ("a", ["a"]),
        ("a\n", ["a"]),
        ("a\n\n", ["a", ""]),
        ("a\r\nb", ["a", "b"]),
        ("a\rb", ["a", "b"]),
        ("a\u2028b", ["a\u2028b"]),
        (" a ", [" a "]),
        ("\n", [""]),
    ],
)
def test_segment_lines_rules(text: str, expected: list[str]) -> None:
    from ior_mvp.acquisition.documents.textlayer import segment_lines

    assert segment_lines(text) == expected


def test_methods_are_versioned_and_content_type_routed() -> None:
    from ior_mvp.acquisition.documents.textlayer import TEXT_LAYER_METHODS, derive_text_layer

    assert "application/pdf" in TEXT_LAYER_METHODS
    assert "text/html" in TEXT_LAYER_METHODS
    assert "text/plain" in TEXT_LAYER_METHODS
    with pytest.raises(ValueError, match="Unsupported"):
        derive_text_layer(b"x", "application/zip")


def test_no_normalisation_applied() -> None:
    from ior_mvp.acquisition.documents.textlayer import derive_text_layer

    # decomposed e + combining acute vs precomposed é; Arabic-Indic digit ٦
    text = "e\u0301 ٦"
    payload = text.encode("utf-8")
    result = derive_text_layer(payload, "text/plain")
    assert result.pages[0][0] == text


def test_missing_pypdf_raises_dependency_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import builtins

    from ior_mvp.acquisition.documents import textlayer

    real_import = builtins.__import__

    def fail_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "pypdf":
            raise ImportError("blocked")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fail_import)
    payload = (FIXTURES / "test_double_latin_two_pages.pdf").read_bytes()
    with pytest.raises(textlayer.TextLayerDependencyError):
        textlayer.derive_text_layer(payload, "application/pdf")
