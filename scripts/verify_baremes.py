#!/usr/bin/env python3
"""Barème verification script for tax data integrity.

This script verifies the freshness and integrity of barème JSON files.
It checks:
- Verification dates are not stale
- Required fields are present
- Checklist items are all verified
- Sources are documented

Usage:
    python scripts/verify_baremes.py [--strict]

Options:
    --strict    Fail if any verification is overdue
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Expected barème structure
REQUIRED_FIELDS = [
    "year",
    "source",
    "source_date",
    "verification",
    "income_tax_brackets",
    "abattements",
    "plafonds_micro",
    "urssaf_rates",
    "quotient_familial",
]

REQUIRED_VERIFICATION_FIELDS = [
    "verified_date",
    "verified_by",
    "verification_sources",
    "next_verification_due",
    "checklist",
]

REQUIRED_CHECKLIST_ITEMS = [
    "income_tax_brackets",
    "urssaf_rates",
    "abattements",
    "plafonds_micro",
    "per_plafonds",
    "quotient_familial",
]


def load_bareme(path: Path) -> dict | None:
    """Load a barème JSON file."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"  ERROR: Failed to load {path}: {e}")
        return None


def check_required_fields(bareme: dict, path: Path) -> list[str]:
    """Check that all required fields are present."""
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in bareme:
            errors.append(f"Missing required field: {field}")
    return errors


def check_verification_metadata(bareme: dict, path: Path) -> list[str]:
    """Check verification metadata is complete."""
    errors = []
    verification = bareme.get("verification", {})

    if not verification:
        errors.append("Missing 'verification' section")
        return errors

    for field in REQUIRED_VERIFICATION_FIELDS:
        if field not in verification:
            errors.append(f"Missing verification field: {field}")

    # Check checklist
    checklist = verification.get("checklist", {})
    for item in REQUIRED_CHECKLIST_ITEMS:
        if item not in checklist:
            errors.append(f"Missing checklist item: {item}")
        elif not checklist[item]:
            errors.append(f"Checklist item not verified: {item}")

    return errors


def check_verification_freshness(bareme: dict, strict: bool = False) -> list[str]:
    """Check if verification is still fresh."""
    errors = []
    warnings = []
    verification = bareme.get("verification", {})

    next_due = verification.get("next_verification_due")
    if next_due:
        try:
            due_date = datetime.strptime(next_due, "%Y-%m-%d")
            today = datetime.now()

            if today > due_date:
                msg = f"Verification overdue since {next_due}"
                if strict:
                    errors.append(msg)
                else:
                    warnings.append(msg)
            else:
                days_until = (due_date - today).days
                if days_until < 30:
                    warnings.append(
                        f"Verification due soon ({days_until} days remaining)"
                    )
        except ValueError:
            errors.append(f"Invalid date format for next_verification_due: {next_due}")

    return errors, warnings


def check_bracket_consistency(bareme: dict) -> list[str]:
    """Check that tax brackets are consistent (no gaps or overlaps)."""
    errors = []
    brackets = bareme.get("income_tax_brackets", [])

    if not brackets:
        errors.append("No income tax brackets defined")
        return errors

    # Check first bracket starts at 0
    if brackets[0].get("lower_bound", 0) != 0:
        errors.append("First bracket should start at 0")

    # Check continuity
    for i in range(len(brackets) - 1):
        current_upper = brackets[i].get("upper_bound")
        next_lower = brackets[i + 1].get("lower_bound")

        if current_upper is None:
            if i < len(brackets) - 1:
                errors.append(f"Bracket {i} has null upper_bound but is not the last")
        elif current_upper != next_lower:
            errors.append(
                f"Gap or overlap between brackets {i} and {i + 1}: "
                f"{current_upper} vs {next_lower}"
            )

    # Check rates are increasing
    prev_rate = -1
    for i, bracket in enumerate(brackets):
        rate = bracket.get("rate", 0)
        if rate < prev_rate:
            errors.append(
                f"Bracket {i} rate ({rate}) is lower than previous ({prev_rate})"
            )
        prev_rate = rate

    return errors


def verify_bareme(
    path: Path, strict: bool = False
) -> tuple[bool, list[str], list[str]]:
    """Verify a single barème file.

    Returns:
        Tuple of (success, errors, warnings)
    """
    errors = []
    warnings = []

    bareme = load_bareme(path)
    if bareme is None:
        return False, ["Failed to load file"], []

    year = bareme.get("year", "unknown")
    print(f"\n  Verifying barème {year}...")

    # Check required fields
    errors.extend(check_required_fields(bareme, path))

    # Check verification metadata
    errors.extend(check_verification_metadata(bareme, path))

    # Check freshness
    freshness_errors, freshness_warnings = check_verification_freshness(bareme, strict)
    errors.extend(freshness_errors)
    warnings.extend(freshness_warnings)

    # Check bracket consistency
    errors.extend(check_bracket_consistency(bareme))

    # Print verification info
    verification = bareme.get("verification", {})
    if verification:
        print(f"    Last verified: {verification.get('verified_date', 'unknown')}")
        print(f"    Next due: {verification.get('next_verification_due', 'unknown')}")
        print(f"    Sources: {len(verification.get('verification_sources', []))}")

    return len(errors) == 0, errors, warnings


def main():
    """Main entry point."""
    strict = "--strict" in sys.argv

    print("=" * 60)
    print("Barème Verification Report")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Mode: {'STRICT' if strict else 'NORMAL'}")

    # Find barème files
    data_dir = Path(__file__).parent.parent / "src" / "tax_engine" / "data"
    bareme_files = list(data_dir.glob("baremes_*.json"))

    if not bareme_files:
        print("\nERROR: No barème files found!")
        sys.exit(1)

    print(f"\nFound {len(bareme_files)} barème file(s)")

    all_success = True
    total_errors = []
    total_warnings = []

    for path in sorted(bareme_files):
        success, errors, warnings = verify_bareme(path, strict)

        if not success:
            all_success = False

        for error in errors:
            print(f"    ERROR: {error}")
            total_errors.append(f"{path.name}: {error}")

        for warning in warnings:
            print(f"    WARNING: {warning}")
            total_warnings.append(f"{path.name}: {warning}")

        if success and not warnings:
            print("    Status: OK")

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Files checked: {len(bareme_files)}")
    print(f"Errors: {len(total_errors)}")
    print(f"Warnings: {len(total_warnings)}")

    if total_errors:
        print("\nErrors found:")
        for error in total_errors:
            print(f"  - {error}")

    if total_warnings:
        print("\nWarnings:")
        for warning in total_warnings:
            print(f"  - {warning}")

    if all_success:
        print("\n[OK] All bareme files passed verification")
        sys.exit(0)
    else:
        print("\n[FAIL] Verification failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
