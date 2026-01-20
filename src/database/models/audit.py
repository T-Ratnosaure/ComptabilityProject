"""SQLAlchemy models for audit trail."""

import hashlib
import json
from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid4())


def generate_input_hash(data: dict[str, Any]) -> str:
    """Generate SHA256 hash of input data for integrity verification."""
    json_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(json_str.encode()).hexdigest()


class AuditLog(Base):
    """Main audit log container for a tax calculation request.

    Stores metadata about each calculation request for compliance tracking.
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, default=generate_uuid
    )

    # Calculation context
    tax_year: Mapped[int] = mapped_column(Integer, nullable=False)
    calculation_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="full_calculation"
    )

    # Input integrity
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    # Rules versioning
    rules_version: Mapped[str] = mapped_column(String(20), nullable=False)
    bareme_source: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Execution metadata
    execution_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Summary results (for quick access without loading full trail)
    impot_net: Mapped[float | None] = mapped_column(Float, nullable=True)
    cotisations: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_burden: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Retention
    retained_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    entries: Mapped[list["AuditEntry"]] = relationship(
        "AuditEntry", back_populates="audit_log", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<AuditLog(id={self.id}, request_id={self.request_id[:8]}..., "
            f"year={self.tax_year}, success={self.success})>"
        )


class AuditEntry(Base):
    """Individual calculation step in the audit trail.

    Records each computation with inputs, outputs, and rules applied.
    Immutable after creation for compliance.
    """

    __tablename__ = "audit_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    audit_log_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("audit_logs.id"), nullable=False
    )

    # Step identification
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    step_name: Mapped[str] = mapped_column(String(100), nullable=False)
    step_category: Mapped[str] = mapped_column(
        String(50), nullable=False, default="calculation"
    )

    # Calculation data (stored as JSON for flexibility)
    input_summary: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    output_value: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Rule application tracking
    rule_applied: Mapped[str | None] = mapped_column(String(100), nullable=True)
    rule_source: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Warnings/notes
    warnings: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationship
    audit_log: Mapped["AuditLog"] = relationship("AuditLog", back_populates="entries")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<AuditEntry(id={self.id}, step={self.step_order}, name={self.step_name})>"
        )
