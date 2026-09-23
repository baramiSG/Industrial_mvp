"""Read-only executive projection API."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, ValidationError

from . import service
from .models import ExecutiveCase, ExecutiveSummary
from .taxonomy import ExecutiveIntegrityError

router = APIRouter(prefix="/api/executive", tags=["executive"])


class ExecutiveErrorDetail(BaseModel):
    """Stable executive API error detail."""

    model_config = ConfigDict(extra="forbid")

    code: str
    message: str


class ExecutiveErrorResponse(BaseModel):
    """FastAPI error envelope for executive endpoints."""

    model_config = ConfigDict(extra="forbid")

    detail: ExecutiveErrorDetail


INTEGRITY_RESPONSE = {
    422: {
        "model": ExecutiveErrorResponse,
        "description": "Governed executive input integrity failure",
    }
}
CASE_ERROR_RESPONSES = {
    404: {
        "model": ExecutiveErrorResponse,
        "description": "Executive opportunity not found",
    },
    **INTEGRITY_RESPONSE,
}


def _integrity_error(exc: Exception) -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "code": "EXECUTIVE_INTEGRITY_ERROR",
            "message": str(exc),
        },
    )


@router.get(
    "/summary",
    response_model=ExecutiveSummary,
    responses=INTEGRITY_RESPONSE,
)
def executive_summary() -> ExecutiveSummary:
    """Return the mode-independent executive portfolio projection."""

    try:
        return service.build_executive_summary()
    except (ExecutiveIntegrityError, ValidationError) as exc:
        raise _integrity_error(exc) from exc


@router.get(
    "/opportunities/{opportunity_id}",
    response_model=ExecutiveCase,
    responses=CASE_ERROR_RESPONSES,
)
def executive_case(opportunity_id: str) -> ExecutiveCase:
    """Return one mode-independent executive case projection."""

    try:
        return service.build_executive_case(opportunity_id)
    except service.ExecutiveOpportunityNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "EXECUTIVE_OPPORTUNITY_NOT_FOUND",
                "message": str(exc),
            },
        ) from exc
    except (ExecutiveIntegrityError, ValidationError) as exc:
        raise _integrity_error(exc) from exc
