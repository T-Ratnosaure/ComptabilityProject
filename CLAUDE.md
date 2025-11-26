# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ComptabilityProject is a Python 3.12 application managed with UV (fast Python package manager). This is an early-stage project with minimal structure.

## Development Commands

### Package Management
- Install dependencies: `uv sync`
- Add a new dependency: `uv add <package-name>`
- Add a dev dependency: `uv add --dev <package-name>`

### Running the Application
- Run main script: `python main.py`
- Or with UV: `uv run python main.py`

## Project Structure

- `main.py` - Application entry point with basic setup
- `pyproject.toml` - Project configuration and dependencies
- `.python-version` - Python version (3.12)
