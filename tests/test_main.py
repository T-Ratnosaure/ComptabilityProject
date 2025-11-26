"""Tests for main module."""

import pytest

from main import main


def test_main_runs_without_error() -> None:
    """Test that main function executes successfully."""
    main()


def test_main_output(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that main function produces expected output."""
    main()
    captured = capsys.readouterr()
    assert "Hello from comptabilityproject!" in captured.out
