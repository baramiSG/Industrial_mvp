from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .ai_extraction import run_extraction_golden_set
from .case_selection_view import CaseSelectionIntegrityError, case_selection_view
from .config import (
    PROJECT_ROOT,
    UIStringConfigurationError,
    UnsupportedUILocaleError,
    project_config,
    thresholds_config,
    ui_strings_bundle,
)
from .data_repository import RepositoryError
from .decision_engine import analyze, list_opportunities
from .dossier import build_dossier, render_dossier_html
from .evidence import EvidenceIntegrityError
from .genui import build_ui_manifest
from .graph.api import router as graph_router
from .narratives import NarrativeCatalogueError
from .screening.api import router as screening_router


STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="Industrial Opportunity Resolution Engine MVP",
    description="Public-evidence decision resolution with an isolated synthetic Ministry demonstration layer.",
    version=__version__,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(screening_router)
app.include_router(graph_router)


def _evidence_integrity_http_exception(
    exc: EvidenceIntegrityError | NarrativeCatalogueError,
) -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "code": "EVIDENCE_INTEGRITY_ERROR",
            "message": str(exc),
        },
    )


def _safe_analysis(
    opportunity_id: str,
    mode: Literal["public", "simulated"],
) -> dict[str, Any]:
    try:
        return analyze(opportunity_id, mode)
    except (EvidenceIntegrityError, NarrativeCatalogueError) as exc:
        raise _evidence_integrity_http_exception(exc) from exc
    except (RepositoryError, ValueError) as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "version": __version__,
        "project_root": str(PROJECT_ROOT),
        "evidence_boundary": "public real decision / isolated synthetic simulation",
    }


@app.get("/api/project")
def project() -> dict:
    return project_config()


@app.get("/api/thresholds")
def thresholds() -> dict:
    return thresholds_config()


@app.get("/api/ui-strings/{locale}")
def ui_strings(locale: str) -> dict[str, Any]:
    try:
        return ui_strings_bundle(locale)
    except UnsupportedUILocaleError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "UI_LOCALE_NOT_FOUND",
                "locale": locale,
            },
        ) from exc
    except UIStringConfigurationError as exc:
        raise HTTPException(
            status_code=500,
            detail={"code": "UI_CATALOGUE_INTEGRITY_ERROR"},
        ) from exc


@app.get("/api/case-selection")
def case_selection() -> dict[str, Any]:
    try:
        return case_selection_view()
    except CaseSelectionIntegrityError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "CASE_SELECTION_INTEGRITY_ERROR",
                "message": str(exc),
            },
        ) from exc


@app.get("/api/opportunities")
def opportunities(
    mode: Literal["public", "simulated"] = Query(default="public")
) -> list[dict]:
    try:
        return list_opportunities(mode)
    except (EvidenceIntegrityError, NarrativeCatalogueError) as exc:
        raise _evidence_integrity_http_exception(exc) from exc
    except (RepositoryError, ValueError) as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@app.get("/api/opportunities/{opportunity_id}")
def opportunity(
    opportunity_id: str,
    mode: Literal["public", "simulated"] = Query(default="public"),
) -> dict:
    return _safe_analysis(opportunity_id, mode)


@app.get("/api/opportunities/{opportunity_id}/ui-manifest")
def ui_manifest(
    opportunity_id: str,
    mode: Literal["public", "simulated"] = Query(default="public"),
) -> dict:
    return build_ui_manifest(_safe_analysis(opportunity_id, mode))


@app.get("/api/opportunities/{opportunity_id}/dossier")
def dossier(
    opportunity_id: str,
    mode: Literal["public", "simulated"] = Query(default="public"),
) -> dict:
    return build_dossier(_safe_analysis(opportunity_id, mode))


@app.get("/api/opportunities/{opportunity_id}/dossier.html", response_class=HTMLResponse)
def dossier_html(
    opportunity_id: str,
    mode: Literal["public", "simulated"] = Query(default="public"),
    locale: Literal["en", "ar"] = Query(default="en"),
) -> HTMLResponse:
    dossier_value = build_dossier(_safe_analysis(opportunity_id, mode))
    return HTMLResponse(
        render_dossier_html(dossier_value, locale=locale)
    )


@app.get("/api/extraction-demo")
def extraction_demo() -> dict:
    return run_extraction_golden_set()


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/{path:path}", include_in_schema=False)
def spa_fallback(path: str) -> FileResponse:
    static_root = STATIC_DIR.resolve()
    candidate = (STATIC_DIR / path).resolve()
    if candidate.is_file() and candidate.is_relative_to(static_root):
        return FileResponse(candidate)
    return FileResponse(STATIC_DIR / "index.html")
