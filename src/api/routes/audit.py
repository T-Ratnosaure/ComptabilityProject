"""Audit trail API endpoints for compliance tracking."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models.audit import AuditLog
from src.database.session import get_db

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


class AuditLogSummary(BaseModel):
    """Summary of an audit log for listing."""

    request_id: str
    tax_year: int
    calculation_type: str
    success: bool
    execution_time_ms: int | None = None
    impot_net: float | None = None
    cotisations: float | None = None
    total_burden: float | None = None


class AuditLogDetail(BaseModel):
    """Detailed audit log with all entries."""

    request_id: str
    tax_year: int
    calculation_type: str
    input_hash: str
    rules_version: str
    bareme_source: str | None = None
    execution_time_ms: int | None = None
    success: bool
    error_message: str | None = None
    impot_net: float | None = None
    cotisations: float | None = None
    total_burden: float | None = None
    retained_until: datetime | None = None
    entries: list[dict[str, Any]] = Field(default_factory=list)


class AuditListResponse(BaseModel):
    """Response for listing audit logs."""

    items: list[AuditLogSummary]
    total: int
    page: int
    page_size: int


@router.get("", response_model=AuditListResponse)
async def list_audit_logs(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    tax_year: int | None = Query(None, description="Filter by tax year"),
    success: bool | None = Query(None, description="Filter by success status"),
) -> AuditListResponse:
    """List audit logs with pagination.

    Args:
        db: Database session
        page: Page number (1-indexed)
        page_size: Number of items per page (max 100)
        tax_year: Optional filter by tax year
        success: Optional filter by success status

    Returns:
        Paginated list of audit log summaries
    """
    # Build base query
    query = select(AuditLog).order_by(desc(AuditLog.id))
    count_query = select(func.count(AuditLog.id))

    # Apply filters
    if tax_year is not None:
        query = query.where(AuditLog.tax_year == tax_year)
        count_query = count_query.where(AuditLog.tax_year == tax_year)
    if success is not None:
        query = query.where(AuditLog.success == success)
        count_query = count_query.where(AuditLog.success == success)

    # Get total count
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    logs = result.scalars().all()

    items = [
        AuditLogSummary(
            request_id=log.request_id,
            tax_year=log.tax_year,
            calculation_type=log.calculation_type,
            success=log.success,
            execution_time_ms=log.execution_time_ms,
            impot_net=log.impot_net,
            cotisations=log.cotisations,
            total_burden=log.total_burden,
        )
        for log in logs
    ]

    return AuditListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{request_id}", response_model=AuditLogDetail)
async def get_audit_log(
    request_id: str,
    db: AsyncSession = Depends(get_db),
) -> AuditLogDetail:
    """Get detailed audit log by request ID.

    Args:
        request_id: UUID of the audit trail
        db: Database session

    Returns:
        Detailed audit log with all calculation steps

    Raises:
        HTTPException: If audit log not found
    """
    query = (
        select(AuditLog)
        .where(AuditLog.request_id == request_id)
        .options(selectinload(AuditLog.entries))
    )

    result = await db.execute(query)
    log = result.scalar_one_or_none()

    if log is None:
        raise HTTPException(
            status_code=404,
            detail=f"Audit log not found: {request_id}",
        )

    # Sort entries by step_order
    sorted_entries = sorted(log.entries, key=lambda e: e.step_order)

    entries = [
        {
            "step_order": entry.step_order,
            "step_name": entry.step_name,
            "step_category": entry.step_category,
            "input_summary": entry.input_summary,
            "output_value": entry.output_value,
            "rule_applied": entry.rule_applied,
            "rule_source": entry.rule_source,
            "warnings": entry.warnings,
            "notes": entry.notes,
        }
        for entry in sorted_entries
    ]

    return AuditLogDetail(
        request_id=log.request_id,
        tax_year=log.tax_year,
        calculation_type=log.calculation_type,
        input_hash=log.input_hash,
        rules_version=log.rules_version,
        bareme_source=log.bareme_source,
        execution_time_ms=log.execution_time_ms,
        success=log.success,
        error_message=log.error_message,
        impot_net=log.impot_net,
        cotisations=log.cotisations,
        total_burden=log.total_burden,
        retained_until=log.retained_until,
        entries=entries,
    )


@router.get("/{request_id}/export")
async def export_audit_log(
    request_id: str,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Export audit log as downloadable JSON file.

    Args:
        request_id: UUID of the audit trail
        db: Database session

    Returns:
        JSON file download with complete audit trail

    Raises:
        HTTPException: If audit log not found
    """
    # Get the detailed log
    detail = await get_audit_log(request_id, db)

    # Format for export
    export_data = {
        "export_timestamp": datetime.now(UTC).isoformat(),
        "audit_trail": detail.model_dump(),
        "compliance_note": (
            "This audit trail is retained for French tax compliance purposes. "
            "Retain for minimum 5 years per fiscal regulations."
        ),
    }

    # Return as downloadable file
    return JSONResponse(
        content=export_data,
        headers={
            "Content-Disposition": (
                f'attachment; filename="audit_trail_{request_id[:8]}.json"'
            ),
        },
    )


@router.get("/stats/summary")
async def get_audit_stats(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get summary statistics of audit logs.

    Args:
        db: Database session

    Returns:
        Statistics including total calculations, success rate, average time
    """
    # Get all logs for stats
    result = await db.execute(select(AuditLog))
    logs = result.scalars().all()

    if not logs:
        return {
            "total_calculations": 0,
            "success_rate": 0.0,
            "avg_execution_time_ms": 0,
            "calculations_by_year": {},
        }

    total = len(logs)
    successful = sum(1 for log in logs if log.success)
    exec_times = [
        log.execution_time_ms for log in logs if log.execution_time_ms is not None
    ]

    # Group by year
    by_year: dict[int, int] = {}
    for log in logs:
        by_year[log.tax_year] = by_year.get(log.tax_year, 0) + 1

    return {
        "total_calculations": total,
        "success_rate": (successful / total) * 100 if total > 0 else 0.0,
        "avg_execution_time_ms": (
            sum(exec_times) / len(exec_times) if exec_times else 0
        ),
        "calculations_by_year": by_year,
    }
