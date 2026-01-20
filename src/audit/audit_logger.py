"""Audit logger service for tax calculation compliance tracking."""

import logging
import time
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.audit import (
    AuditEntry,
    AuditLog,
    generate_input_hash,
    generate_uuid,
)

logger = logging.getLogger(__name__)

# Default retention period: 5 years for tax compliance
DEFAULT_RETENTION_YEARS = 5


class AuditLogger:
    """Service for creating and managing audit trails for tax calculations.

    Provides non-blocking audit logging with database persistence.
    Designed for compliance with French tax authority requirements.
    """

    def __init__(self, db_session: AsyncSession | None = None) -> None:
        """Initialize audit logger.

        Args:
            db_session: Optional async database session for persistence.
                       If None, logs are stored in memory only.
        """
        self.db_session = db_session
        self._current_logs: dict[str, AuditLog] = {}
        self._current_entries: dict[str, list[AuditEntry]] = {}
        self._step_counters: dict[str, int] = {}
        self._start_times: dict[str, float] = {}

    async def start_calculation(
        self,
        payload: dict[str, Any],
        tax_year: int,
        calculation_type: str = "full_calculation",
        rules_version: str = "2025",
        bareme_source: str | None = None,
    ) -> str:
        """Start a new audit trail for a calculation.

        Args:
            payload: Input data for the calculation
            tax_year: Tax year being calculated
            calculation_type: Type of calculation (full, comparison, etc.)
            rules_version: Version of tax rules being used
            bareme_source: Source URL for tax brackets

        Returns:
            request_id: Unique identifier for this audit trail
        """
        # Generate request_id explicitly (SQLAlchemy default only runs on flush)
        request_id = generate_uuid()

        # Create audit log
        audit_log = AuditLog(
            request_id=request_id,
            tax_year=tax_year,
            calculation_type=calculation_type,
            input_hash=generate_input_hash(payload),
            rules_version=rules_version,
            bareme_source=bareme_source,
            retained_until=datetime.now(UTC)
            + timedelta(days=365 * DEFAULT_RETENTION_YEARS),
        )

        # Store in memory
        self._current_logs[request_id] = audit_log
        self._current_entries[request_id] = []
        self._step_counters[request_id] = 0
        self._start_times[request_id] = time.perf_counter()

        # Log initial entry
        await self.log_step(
            request_id=request_id,
            step_name="calculation_started",
            step_category="lifecycle",
            input_summary={
                "tax_year": tax_year,
                "calculation_type": calculation_type,
                "payload_keys": list(payload.keys()),
            },
        )

        logger.debug(f"Started audit trail: {request_id[:8]}...")
        return request_id

    async def log_step(
        self,
        request_id: str,
        step_name: str,
        step_category: str = "calculation",
        input_summary: dict[str, Any] | None = None,
        output_value: dict[str, Any] | None = None,
        rule_applied: str | None = None,
        rule_source: str | None = None,
        warnings: list[str] | None = None,
        notes: str | None = None,
    ) -> None:
        """Log a calculation step in the audit trail.

        Args:
            request_id: Audit trail identifier
            step_name: Name of the calculation step
            step_category: Category (calculation, validation, etc.)
            input_summary: Summary of inputs for this step
            output_value: Output/result of this step
            rule_applied: Name of rule/formula applied
            rule_source: Source reference for the rule
            warnings: Any warnings generated
            notes: Additional notes
        """
        if request_id not in self._current_logs:
            logger.warning(f"Audit trail not found: {request_id}")
            return

        # Increment step counter
        self._step_counters[request_id] += 1
        step_order = self._step_counters[request_id]

        # Create entry
        entry = AuditEntry(
            step_order=step_order,
            step_name=step_name,
            step_category=step_category,
            input_summary=input_summary,
            output_value=output_value,
            rule_applied=rule_applied,
            rule_source=rule_source,
            warnings=warnings,
            notes=notes,
        )

        self._current_entries[request_id].append(entry)
        logger.debug(f"Logged step {step_order}: {step_name}")

    async def complete_calculation(
        self,
        request_id: str,
        result: dict[str, Any],
        success: bool = True,
        error_message: str | None = None,
    ) -> AuditLog | None:
        """Complete an audit trail and persist to database.

        Args:
            request_id: Audit trail identifier
            result: Final calculation result
            success: Whether calculation succeeded
            error_message: Error message if failed

        Returns:
            Completed AuditLog or None if not found
        """
        if request_id not in self._current_logs:
            logger.warning(f"Audit trail not found: {request_id}")
            return None

        audit_log = self._current_logs[request_id]

        # Calculate execution time
        if request_id in self._start_times:
            elapsed = time.perf_counter() - self._start_times[request_id]
            audit_log.execution_time_ms = int(elapsed * 1000)

        # Update audit log
        audit_log.success = success
        audit_log.error_message = error_message

        # Extract summary values from result
        if success and result:
            impot_data = result.get("impot", {})
            socials_data = result.get("socials", {})

            audit_log.impot_net = impot_data.get("impot_net")
            audit_log.cotisations = socials_data.get("urssaf_expected")

            if audit_log.impot_net is not None and audit_log.cotisations is not None:
                audit_log.total_burden = audit_log.impot_net + audit_log.cotisations

        # Log completion entry
        await self.log_step(
            request_id=request_id,
            step_name="calculation_completed",
            step_category="lifecycle",
            output_value={
                "success": success,
                "execution_time_ms": audit_log.execution_time_ms,
                "impot_net": audit_log.impot_net,
                "cotisations": audit_log.cotisations,
            },
        )

        # Persist to database if session available
        if self.db_session:
            await self._persist_audit_log(request_id)

        # Cleanup memory
        completed_log = self._cleanup(request_id)

        logger.info(
            f"Completed audit trail: {request_id[:8]}... "
            f"({audit_log.execution_time_ms}ms, success={success})"
        )

        return completed_log

    async def log_error(
        self,
        request_id: str,
        error: Exception,
    ) -> AuditLog | None:
        """Log an error and complete the audit trail.

        Args:
            request_id: Audit trail identifier
            error: Exception that occurred

        Returns:
            Completed AuditLog or None
        """
        await self.log_step(
            request_id=request_id,
            step_name="error_occurred",
            step_category="error",
            output_value={
                "error_type": type(error).__name__,
                "error_message": str(error),
            },
        )

        return await self.complete_calculation(
            request_id=request_id,
            result={},
            success=False,
            error_message=f"{type(error).__name__}: {error}",
        )

    async def _persist_audit_log(self, request_id: str) -> None:
        """Persist audit log and entries to database."""
        if not self.db_session:
            return

        audit_log = self._current_logs[request_id]
        entries = self._current_entries[request_id]

        # Link entries to audit log
        for entry in entries:
            entry.audit_log = audit_log
            audit_log.entries.append(entry)

        self.db_session.add(audit_log)
        await self.db_session.flush()

        logger.debug(
            f"Persisted audit log {request_id[:8]}... with {len(entries)} entries"
        )

    def _cleanup(self, request_id: str) -> AuditLog | None:
        """Clean up in-memory storage after completion."""
        audit_log = self._current_logs.pop(request_id, None)
        self._current_entries.pop(request_id, None)
        self._step_counters.pop(request_id, None)
        self._start_times.pop(request_id, None)
        return audit_log

    def get_in_progress_count(self) -> int:
        """Get count of in-progress audit trails."""
        return len(self._current_logs)


# Global instance for convenience (without DB persistence)
_global_audit_logger: AuditLogger | None = None


def get_audit_logger(db_session: AsyncSession | None = None) -> AuditLogger:
    """Get or create an audit logger instance.

    Args:
        db_session: Optional database session for persistence

    Returns:
        AuditLogger instance
    """
    global _global_audit_logger

    if db_session:
        # Return new instance with DB session
        return AuditLogger(db_session)

    if _global_audit_logger is None:
        _global_audit_logger = AuditLogger()

    return _global_audit_logger
