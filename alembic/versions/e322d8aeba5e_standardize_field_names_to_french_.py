"""Standardize field names to French fiscal terms

Revision ID: e322d8aeba5e
Revises: c9cb3e53add4
Create Date: 2025-11-29 22:57:17.521770

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e322d8aeba5e"
down_revision: str | Sequence[str] | None = "c9cb3e53add4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite doesn't support RENAME COLUMN directly, so we need to:
    # 1. Add new columns (nullable temporarily)
    # 2. Copy data from old columns
    # 3. Drop old columns

    # FREELANCE PROFILES: Add new columns (nullable for now)
    op.add_column(
        "freelance_profiles", sa.Column("chiffre_affaires", sa.Float(), nullable=True)
    )
    op.add_column(
        "freelance_profiles",
        sa.Column("charges_deductibles", sa.Float(), nullable=True),
    )
    op.add_column(
        "freelance_profiles",
        sa.Column("cotisations_sociales", sa.Float(), nullable=True),
    )
    op.add_column(
        "freelance_profiles", sa.Column("autres_revenus", sa.Float(), nullable=True)
    )

    # Copy data from old columns to new columns
    op.execute("""
        UPDATE freelance_profiles
        SET chiffre_affaires = annual_revenue,
            charges_deductibles = annual_expenses,
            cotisations_sociales = social_contributions,
            autres_revenus = other_income
    """)

    # Drop old columns
    op.drop_column("freelance_profiles", "other_income")
    op.drop_column("freelance_profiles", "social_contributions")
    op.drop_column("freelance_profiles", "annual_revenue")
    op.drop_column("freelance_profiles", "annual_expenses")

    # TAX CALCULATIONS: Add new column (nullable for now)
    op.add_column(
        "tax_calculations", sa.Column("cotisations_sociales", sa.Float(), nullable=True)
    )

    # Copy data from old column to new column
    op.execute("""
        UPDATE tax_calculations
        SET cotisations_sociales = social_contributions
    """)

    # Drop old column
    op.drop_column("tax_calculations", "social_contributions")


def downgrade() -> None:
    """Downgrade schema."""
    # Reverse the upgrade: rename columns back to English names

    # TAX CALCULATIONS: Add old column (nullable for now)
    op.add_column(
        "tax_calculations", sa.Column("social_contributions", sa.FLOAT(), nullable=True)
    )

    # Copy data back
    op.execute("""
        UPDATE tax_calculations
        SET social_contributions = cotisations_sociales
    """)

    # Drop new column
    op.drop_column("tax_calculations", "cotisations_sociales")

    # FREELANCE PROFILES: Add old columns (nullable for now)
    op.add_column(
        "freelance_profiles", sa.Column("annual_expenses", sa.FLOAT(), nullable=True)
    )
    op.add_column(
        "freelance_profiles", sa.Column("annual_revenue", sa.FLOAT(), nullable=True)
    )
    op.add_column(
        "freelance_profiles",
        sa.Column("social_contributions", sa.FLOAT(), nullable=True),
    )
    op.add_column(
        "freelance_profiles", sa.Column("other_income", sa.FLOAT(), nullable=True)
    )

    # Copy data back
    op.execute("""
        UPDATE freelance_profiles
        SET annual_revenue = chiffre_affaires,
            annual_expenses = charges_deductibles,
            social_contributions = cotisations_sociales,
            other_income = autres_revenus
    """)

    # Drop new columns
    op.drop_column("freelance_profiles", "autres_revenus")
    op.drop_column("freelance_profiles", "cotisations_sociales")
    op.drop_column("freelance_profiles", "charges_deductibles")
    op.drop_column("freelance_profiles", "chiffre_affaires")
