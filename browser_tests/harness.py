from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal
from urllib.parse import parse_qsl, urlencode, urlsplit

from ior_mvp import __version__
from scripts.check_browser_prerequisites import (
    AXE_ROOT,
    check_axe_assets,
)


ROOT = Path(__file__).resolve().parents[1]
SERVER_START_TIMEOUT_SECONDS = 15.0
SERVER_STOP_TIMEOUT_SECONDS = 10.0
ASSERTION_TIMEOUT_MS = 10_000
AXE_TAGS = ("wcag2a", "wcag2aa", "wcag21a", "wcag21aa")

Mode = Literal["public", "simulated"]
FailureCategory = Literal[
    "console-error",
    "pageerror",
    "requestfailed",
    "app-http-error",
    "external-request",
]


@dataclass(frozen=True)
class Locale:
    code: str
    bcp47: str
    direction: str


EN = Locale("en", "en-US", "ltr")
AR = Locale("ar", "ar-SA", "rtl")
LOCALES = (EN, AR)
LOCALE_BY_CODE = {locale.code: locale for locale in LOCALES}


@dataclass(frozen=True)
class Case:
    id: str
    hs6: str
    slug: str
    real_state: str
    public_active_state: str
    simulated_active_state: str

    def active_state(self, mode: Mode) -> str:
        if mode == "simulated":
            return self.simulated_active_state
        return self.public_active_state


STEEL = Case(
    id="SAU-H0-721049",
    hs6="721049",
    slug="steel",
    real_state="INVESTIGATE",
    public_active_state="INVESTIGATE",
    simulated_active_state="ADVANCE",
)
POLYPROPYLENE = Case(
    id="SAU-H0-390210",
    hs6="390210",
    slug="polypropylene",
    real_state="REJECT",
    public_active_state="REJECT",
    simulated_active_state="REJECT",
)
GALVALUME = Case(
    id="SAU-H6-721061",
    hs6="721061",
    slug="galvalume",
    real_state="INVESTIGATE",
    public_active_state="INVESTIGATE",
    simulated_active_state="ADVANCE",
)
TINPLATE = Case(
    id="SAU-H6-721012",
    hs6="721012",
    slug="tinplate",
    real_state="INVESTIGATE",
    public_active_state="INVESTIGATE",
    simulated_active_state="ADVANCE",
)
ALU_FOIL = Case(
    id="SAU-H6-760711",
    hs6="760711",
    slug="alu-foil",
    real_state="INVESTIGATE",
    public_active_state="INVESTIGATE",
    simulated_active_state="ADVANCE",
)
ALU_PROFILES = Case(
    id="SAU-H6-760429",
    hs6="760429",
    slug="alu-profiles",
    real_state="INVESTIGATE",
    public_active_state="INVESTIGATE",
    simulated_active_state="ADVANCE",
)
PE_FILM = Case(
    id="SAU-H6-392010",
    hs6="392010",
    slug="pe-film",
    real_state="INVESTIGATE",
    public_active_state="INVESTIGATE",
    simulated_active_state="REJECT",
)
PENICILLIN_API = Case(
    id="SAU-H6-294110",
    hs6="294110",
    slug="penicillin-api",
    real_state="INVESTIGATE",
    public_active_state="INVESTIGATE",
    simulated_active_state="ADVANCE",
)
STREPTOMYCIN_API = Case(
    id="SAU-H6-294120",
    hs6="294120",
    slug="streptomycin-api",
    real_state="INVESTIGATE",
    public_active_state="INVESTIGATE",
    simulated_active_state="REJECT",
)
SOP = Case(
    id="SAU-H6-310430",
    hs6="310430",
    slug="sop",
    real_state="INVESTIGATE",
    public_active_state="INVESTIGATE",
    simulated_active_state="ADVANCE",
)
FERT_RETAIL_PACKS = Case(
    id="SAU-H6-310510",
    hs6="310510",
    slug="fert-retail-packs",
    real_state="INVESTIGATE",
    public_active_state="INVESTIGATE",
    simulated_active_state="REJECT",
)
CASES = (
    STEEL,
    POLYPROPYLENE,
    GALVALUME,
    TINPLATE,
    ALU_FOIL,
    ALU_PROFILES,
    PE_FILM,
    PENICILLIN_API,
    STREPTOMYCIN_API,
    SOP,
    FERT_RETAIL_PACKS,
)
MODES: tuple[Mode, ...] = ("public", "simulated")


@dataclass(frozen=True)
class Viewport:
    name: str
    width: int
    height: int

    def as_dict(self) -> dict[str, int]:
        return {"width": self.width, "height": self.height}


DESKTOP = Viewport("desktop-1440x900", 1440, 900)
TABLET = Viewport("tablet-1024x768", 1024, 768)
PRESENTATION_1080 = Viewport(
    "presentation-1920x1080",
    1920,
    1080,
)
PRESENTATION_1440 = Viewport(
    "presentation-2560x1440",
    2560,
    1440,
)
VIEWPORTS = (
    DESKTOP,
    TABLET,
    PRESENTATION_1080,
    PRESENTATION_1440,
)
@dataclass(frozen=True)
class AppServer:
    base_url: str
    process: subprocess.Popen[bytes]
    log_path: Path


@dataclass(frozen=True)
class BrowserSession:
    page: Any
    context: Any
    collector: BrowserFailureCollector
    app_server: AppServer
    artifact_dir: Path
    locale: Locale


@dataclass(frozen=True)
class BrowserFailure:
    category: FailureCategory
    detail: str
    method: str = ""
    url: str = ""
    status: int | None = None

    def render(self) -> str:
        fields = [self.category]
        if self.method:
            fields.append(self.method)
        if self.status is not None:
            fields.append(str(self.status))
        if self.url:
            fields.append(self.url)
        if self.detail:
            fields.append(self.detail)
        return " | ".join(fields)


@dataclass(frozen=True)
class FocusRecord:
    identity: str
    focus_visible: bool
    before_signature: str
    focused_signature: str


@dataclass(frozen=True)
class KeyboardFocusReport:
    dom_order: tuple[str, ...]
    focused_order: tuple[str, ...]
    wrap_identity: str
    records: tuple[FocusRecord, ...]


@dataclass(frozen=True)
class ArabicRenderReport:
    visible_rtl_nodes: int
    font_family: str
    document_direction: str
    intended_font_loaded: bool
    arabic_width: float
    replacement_width: float
    arabic_pixel_signature: str
    replacement_pixel_signature: str
    distinct_arabic_glyph_signatures: int


def url_origin(url: str) -> str | None:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}"


def sanitized_url(url: str, app_origin: str) -> str:
    parsed = urlsplit(url)
    origin = url_origin(url)
    if origin is None:
        return f"{parsed.scheme}:{parsed.path}" if parsed.scheme else parsed.path
    query = ""
    if origin == app_origin:
        safe_pairs = [
            (key, value)
            for key, value in parse_qsl(
                parsed.query,
                keep_blank_values=True,
            )
            if (
                (key == "mode" and value in MODES)
                or (
                    key == "locale"
                    and value in LOCALE_BY_CODE
                )
            )
        ]
        query = urlencode(safe_pairs)
    suffix = parsed.path or "/"
    if query:
        suffix = f"{suffix}?{query}"
    return f"{origin}{suffix}"


def load_axe_source() -> str:
    check_axe_assets(AXE_ROOT)
    return (AXE_ROOT / "axe.min.js").read_text(encoding="utf-8")


def run_axe(page: Any) -> dict[str, Any]:
    page.add_script_tag(content=load_axe_source())
    result = page.evaluate(
        """async (tags) => {
          return await axe.run(document, {
            runOnly: {
              type: "tag",
              values: tags,
            },
          });
        }""",
        list(AXE_TAGS),
    )
    if not isinstance(result, dict):
        raise AssertionError("axe returned a non-object result")
    return result


def format_axe_violations(
    violations: list[dict[str, Any]],
) -> str:
    lines: list[str] = []
    for violation in violations:
        lines.extend(
            [
                f"id: {violation.get('id')}",
                f"impact: {violation.get('impact')}",
                f"help: {violation.get('help')}",
                f"help_url: {violation.get('helpUrl')}",
            ]
        )
        for node in violation.get("nodes", []):
            lines.extend(
                [
                    "target: "
                    + json.dumps(
                        node.get("target", []),
                        ensure_ascii=False,
                    ),
                    "failure_summary: "
                    + str(node.get("failureSummary", "")),
                    "html: " + str(node.get("html", ""))[:500],
                ]
            )
        lines.append("")
    return "\n".join(lines)


_FOCUS_INVENTORY_SCRIPT = """() => {
  const selector = [
    "button:not([disabled])",
    "a[href]",
    "select:not([disabled])",
    "summary",
    "[tabindex]:not([tabindex='-1'])",
  ].join(",");
  const visible = (element) => {
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return (
      style.display !== "none" &&
      style.visibility !== "hidden" &&
      rect.width > 0 &&
      rect.height > 0
    );
  };
  const identity = (element) => {
    if (element.dataset.target) return `nav:${element.dataset.target}`;
    if (element.dataset.mode) return `mode:${element.dataset.mode}`;
    if (element.dataset.queueId) return `queue:${element.dataset.queueId}`;
    if (element.dataset.hs6) return `record:${element.dataset.hs6}`;
    if (element.dataset.screeningBack) {
      return `screening-back:${element.dataset.screeningBack}`;
    }
    if (element.dataset.screeningPage) {
      return `page:${element.dataset.screeningPage}`;
    }
    if (element.dataset.selectionDetail) {
      return `selection:${element.dataset.selectionDetail}`;
    }
    if (element.getAttribute("href")) {
      return `href:${element.getAttribute("href")}`;
    }
    if (element.id) return `id:${element.id}`;
    if (element.dataset.openId) return `open:${element.dataset.openId}`;
    if (element.dataset.dossierHtml) {
      return `dossier:${element.dataset.dossierHtml}`;
    }
    if (element.dataset.copyJson) return `copy:${element.dataset.copyJson}`;
    return `${element.tagName.toLowerCase()}:${element.textContent.trim()}`;
  };
  const signature = (element) => {
    const style = getComputedStyle(element);
    return JSON.stringify({
      outlineStyle: style.outlineStyle,
      outlineWidth: style.outlineWidth,
      outlineColor: style.outlineColor,
      outlineOffset: style.outlineOffset,
      boxShadow: style.boxShadow,
    });
  };
  const elements = Array.from(document.querySelectorAll(selector)).filter(visible);
  return elements.map((element) => ({
    identity: identity(element),
    signature: signature(element),
  }));
}"""

_FOCUSED_CONTROL_SCRIPT = """() => {
  const element = document.activeElement;
  const identity = (() => {
    if (element.dataset.target) return `nav:${element.dataset.target}`;
    if (element.dataset.mode) return `mode:${element.dataset.mode}`;
    if (element.dataset.queueId) return `queue:${element.dataset.queueId}`;
    if (element.dataset.hs6) return `record:${element.dataset.hs6}`;
    if (element.dataset.screeningBack) {
      return `screening-back:${element.dataset.screeningBack}`;
    }
    if (element.dataset.screeningPage) {
      return `page:${element.dataset.screeningPage}`;
    }
    if (element.dataset.selectionDetail) {
      return `selection:${element.dataset.selectionDetail}`;
    }
    if (element.getAttribute("href")) {
      return `href:${element.getAttribute("href")}`;
    }
    if (element.id) return `id:${element.id}`;
    if (element.dataset.openId) return `open:${element.dataset.openId}`;
    if (element.dataset.dossierHtml) {
      return `dossier:${element.dataset.dossierHtml}`;
    }
    if (element.dataset.copyJson) return `copy:${element.dataset.copyJson}`;
    return element.tagName.toLowerCase();
  })();
  const style = getComputedStyle(element);
  return {
    identity,
    focusVisible: element.matches(":focus-visible"),
    signature: JSON.stringify({
      outlineStyle: style.outlineStyle,
      outlineWidth: style.outlineWidth,
      outlineColor: style.outlineColor,
      outlineOffset: style.outlineOffset,
      boxShadow: style.boxShadow,
    }),
  };
}"""


def keyboard_focus_report(page: Any) -> KeyboardFocusReport:
    inventory = page.evaluate(_FOCUS_INVENTORY_SCRIPT)
    dom_order = tuple(item["identity"] for item in inventory)
    before = {
        item["identity"]: item["signature"]
        for item in inventory
    }
    page.evaluate(
        """() => {
          document.body.setAttribute("tabindex", "-1");
          document.body.focus();
          document.body.removeAttribute("tabindex");
        }"""
    )
    records: list[FocusRecord] = []
    for expected_identity in dom_order:
        page.keyboard.press("Tab")
        focused = page.evaluate(_FOCUSED_CONTROL_SCRIPT)
        identity = focused["identity"]
        records.append(
            FocusRecord(
                identity=identity,
                focus_visible=bool(focused["focusVisible"]),
                before_signature=before.get(
                    identity,
                    before[expected_identity],
                ),
                focused_signature=focused["signature"],
            )
        )
    page.keyboard.press("Tab")
    wrapped = page.evaluate(_FOCUSED_CONTROL_SCRIPT)
    if wrapped["identity"] == "body":
        page.keyboard.press("Tab")
        wrapped = page.evaluate(_FOCUSED_CONTROL_SCRIPT)
    return KeyboardFocusReport(
        dom_order=dom_order,
        focused_order=tuple(record.identity for record in records),
        wrap_identity=wrapped["identity"],
        records=tuple(records),
    )


def verify_arabic_rendering(page: Any) -> ArabicRenderReport:
    result = page.evaluate(
        """async () => {
          await document.fonts.ready;
          const nodes = Array.from(document.querySelectorAll("[dir='rtl']"))
            .filter((node) => {
              const style = getComputedStyle(node);
              const box = node.getBoundingClientRect();
              return (
                style.display !== "none" &&
                style.visibility !== "hidden" &&
                box.width > 0 &&
                box.height > 0
              );
            })
            .map((node) => {
              const style = getComputedStyle(node);
              const box = node.getBoundingClientRect();
              return {
                direction: style.direction,
                text: node.textContent.trim(),
                width: box.width,
                height: box.height,
                fontFamily: style.fontFamily,
              };
            });
          const fontFamily = nodes[0]?.fontFamily || "sans-serif";
          const sample = "المملكة العربية السعودية";
          const intendedFontLoaded = document.fonts.check(
            '48px "IOR Noto Sans Arabic"',
            sample
          );
          const replacement = "\uFFFD".repeat(Array.from(sample).length);
          const render = (text) => {
            const canvas = document.createElement("canvas");
            canvas.width = 1200;
            canvas.height = 100;
            const context = canvas.getContext("2d");
            context.font = `48px ${fontFamily}`;
            context.textBaseline = "top";
            context.fillStyle = "#000";
            context.fillText(text, 5, 5);
            const pixels = context.getImageData(
              0, 0, canvas.width, canvas.height
            ).data;
            let ink = 0;
            let minX = canvas.width;
            let maxX = -1;
            let minY = canvas.height;
            let maxY = -1;
            let weighted = 0;
            for (let index = 3; index < pixels.length; index += 4) {
              if (pixels[index] === 0) continue;
              const pixel = (index - 3) / 4;
              const x = pixel % canvas.width;
              const y = Math.floor(pixel / canvas.width);
              ink += 1;
              minX = Math.min(minX, x);
              maxX = Math.max(maxX, x);
              minY = Math.min(minY, y);
              maxY = Math.max(maxY, y);
              weighted = (
                weighted + pixels[index] * (x + 17) * (y + 31)
              ) % 2147483647;
            }
            return {
              width: context.measureText(text).width,
              signature: [
                ink, minX, maxX, minY, maxY, weighted,
              ].join(":"),
            };
          };
          const arabic = render(sample);
          const tofu = render(replacement);
          const glyphSignatures = ["س", "ع", "م"].map(
            (glyph) => render(glyph).signature
          );
          return {
            nodes,
            fontFamily,
            documentDirection: getComputedStyle(
              document.documentElement
            ).direction,
            intendedFontLoaded,
            arabic,
            tofu,
            distinctGlyphs: new Set(glyphSignatures).size,
          };
        }"""
    )
    nodes = result["nodes"]
    if not nodes:
        raise AssertionError("no visible RTL nodes were rendered")
    invalid_nodes = [
        node
        for node in nodes
        if (
            node["direction"] != "rtl"
            or not node["text"]
            or not any(
                "\u0600" <= character <= "\u06ff"
                for character in node["text"]
            )
            or node["width"] <= 0
            or node["height"] <= 0
        )
    ]
    if invalid_nodes:
        raise AssertionError(
            "RTL node direction, Arabic text, or dimensions are invalid: "
            f"{json.dumps(invalid_nodes, ensure_ascii=False)}"
        )
    if result["intendedFontLoaded"] is not True:
        raise AssertionError(
            "IOR Noto Sans Arabic did not load for the Arabic sample"
        )
    if not str(result["fontFamily"]).lstrip('"').startswith(
        "IOR Noto Sans Arabic"
    ):
        raise AssertionError(
            "Arabic content did not select IOR Noto Sans Arabic: "
            f"{result['fontFamily']}"
        )
    return ArabicRenderReport(
        visible_rtl_nodes=len(nodes),
        font_family=result["fontFamily"],
        document_direction=result["documentDirection"],
        intended_font_loaded=bool(result["intendedFontLoaded"]),
        arabic_width=float(result["arabic"]["width"]),
        replacement_width=float(result["tofu"]["width"]),
        arabic_pixel_signature=result["arabic"]["signature"],
        replacement_pixel_signature=result["tofu"]["signature"],
        distinct_arabic_glyph_signatures=int(
            result["distinctGlyphs"]
        ),
    )


class BrowserFailureCollector:
    def __init__(self, app_origin: str) -> None:
        self.app_origin = app_origin
        self._records: list[BrowserFailure] = []
        self._seen: set[BrowserFailure] = set()
        self._attached_pages: set[int] = set()

    @property
    def records(self) -> tuple[BrowserFailure, ...]:
        return tuple(self._records)

    def _append(self, record: BrowserFailure) -> None:
        if record in self._seen:
            return
        self._seen.add(record)
        self._records.append(record)

    def record_console(self, message_type: str, text: str) -> None:
        if message_type != "error":
            return
        self._append(
            BrowserFailure(
                category="console-error",
                detail=text,
            )
        )

    def record_page_error(self, message: str) -> None:
        self._append(
            BrowserFailure(
                category="pageerror",
                detail=message,
            )
        )

    def record_request_failed(
        self,
        method: str,
        url: str,
        failure: str | None,
    ) -> None:
        self._append(
            BrowserFailure(
                category="requestfailed",
                method=method,
                url=sanitized_url(url, self.app_origin),
                detail=failure or "request failed",
            )
        )

    def record_response(
        self,
        status: int,
        method: str,
        url: str,
    ) -> None:
        if status < 400 or url_origin(url) != self.app_origin:
            return
        self._append(
            BrowserFailure(
                category="app-http-error",
                method=method,
                status=status,
                url=sanitized_url(url, self.app_origin),
                detail="app response status is at least 400",
            )
        )

    def record_request(self, method: str, url: str) -> None:
        origin = url_origin(url)
        if origin is None or origin == self.app_origin:
            return
        self._append(
            BrowserFailure(
                category="external-request",
                method=method,
                url=sanitized_url(url, self.app_origin),
                detail="non-app HTTP(S) request",
            )
        )

    def attach_page(self, page: Any) -> None:
        page_identity = id(page)
        if page_identity in self._attached_pages:
            return
        self._attached_pages.add(page_identity)
        page.on(
            "console",
            lambda message: self.record_console(
                message.type,
                message.text,
            ),
        )
        page.on(
            "pageerror",
            lambda error: self.record_page_error(str(error)),
        )
        page.on(
            "requestfailed",
            lambda request: self.record_request_failed(
                request.method,
                request.url,
                request.failure,
            ),
        )
        page.on(
            "response",
            lambda response: self.record_response(
                response.status,
                response.request.method,
                response.url,
            ),
        )
        page.on(
            "request",
            lambda request: self.record_request(
                request.method,
                request.url,
            ),
        )

    def attach_context(self, context: Any) -> None:
        context.on("page", self.attach_page)

    def render(self) -> str:
        return "\n".join(record.render() for record in self._records)

    def assert_clean(self) -> None:
        if self._records:
            raise AssertionError(
                "Browser failure collector observed:\n"
                f"{self.render()}"
            )


def build_child_environment(
    root: Path,
    source_environment: Mapping[str, str] | None = None,
) -> dict[str, str]:
    source = os.environ if source_environment is None else source_environment
    environment = {
        key: source[key]
        for key in ("PATH", "HOME")
        if key in source
    }
    environment.update(
        {
            "LANG": "C.UTF-8",
            "PYTHONPATH": str(root / "src"),
            "PYTHONUNBUFFERED": "1",
        }
    )
    return environment


def build_server_command(inherited_fd: int) -> list[str]:
    return [
        sys.executable,
        "-m",
        "uvicorn",
        "ior_mvp.app:app",
        "--fd",
        str(inherited_fd),
        "--log-level",
        "warning",
    ]


def _server_log(log_path: Path) -> str:
    try:
        return log_path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return "server log unavailable"


def wait_for_health(
    server: AppServer,
    timeout_seconds: float = SERVER_START_TIMEOUT_SECONDS,
) -> None:
    deadline = time.monotonic() + timeout_seconds
    health_url = f"{server.base_url}/api/health"
    last_error = "health endpoint not ready"
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(
                health_url,
                timeout=0.25,
            ) as response:
                payload = json.load(response)
            if (
                response.status == 200
                and payload.get("status") == "ok"
                and payload.get("version") == __version__
            ):
                return
            last_error = "health response did not match the contract"
        except (
            OSError,
            urllib.error.URLError,
            json.JSONDecodeError,
        ) as exc:
            last_error = type(exc).__name__

        return_code = server.process.poll()
        if return_code is not None:
            raise RuntimeError(
                "uvicorn exited before health readiness "
                f"(exit {return_code}; {last_error})\n"
                f"{_server_log(server.log_path)}"
            )
    raise RuntimeError(
        "uvicorn did not become healthy before the startup deadline "
        f"({last_error})\n{_server_log(server.log_path)}"
    )


def start_app_server(
    root: Path,
    artifact_dir: Path,
    source_environment: Mapping[str, str] | None = None,
) -> AppServer:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    log_path = artifact_dir / "server.log"
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    process: subprocess.Popen[bytes] | None = None
    try:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        listener.set_inheritable(True)
        inherited_fd = listener.fileno()
        port = int(listener.getsockname()[1])
        with log_path.open("wb") as log_handle:
            process = subprocess.Popen(
                build_server_command(inherited_fd),
                cwd=root,
                env=build_child_environment(
                    root,
                    source_environment,
                ),
                pass_fds=(inherited_fd,),
                stdout=log_handle,
                stderr=subprocess.STDOUT,
            )
    finally:
        listener.close()

    if process is None:
        raise RuntimeError("uvicorn process did not start")
    server = AppServer(
        base_url=f"http://127.0.0.1:{port}",
        process=process,
        log_path=log_path,
    )
    try:
        wait_for_health(server)
    except BaseException:
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
            try:
                process.wait(timeout=SERVER_STOP_TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=SERVER_STOP_TIMEOUT_SECONDS)
        raise
    return server


def is_expected_server_return_code(return_code: int) -> bool:
    return return_code in {0, -signal.SIGTERM}


def stop_app_server(server: AppServer) -> None:
    prior_code = server.process.poll()
    if prior_code is not None:
        raise AssertionError(
            f"uvicorn exited before fixture teardown (exit {prior_code})"
        )
    server.process.send_signal(signal.SIGTERM)
    try:
        return_code = server.process.wait(
            timeout=SERVER_STOP_TIMEOUT_SECONDS
        )
    except subprocess.TimeoutExpired as exc:
        server.process.kill()
        server.process.wait(timeout=SERVER_STOP_TIMEOUT_SECONDS)
        raise AssertionError(
            "uvicorn required forced termination"
        ) from exc
    if not is_expected_server_return_code(return_code):
        raise AssertionError(
            f"uvicorn SIGTERM teardown returned {return_code}"
        )
