# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ComptabilityProject is a Python 3.12 application managed with UV (fast Python package manager). This project implements a French Tax Optimization System for freelancers.

## CRITICAL: Implementation Plan

**ALWAYS follow the implementation plan saved in `C:/Users/larai/.claude/plans/crispy-cooking-glade.md`**

- The plan defines 6 phases of implementation with clear structure and requirements
- **Phase 1 (Core Infrastructure)** is COMPLETE ✅
- Before starting any new feature, review the plan to understand the current phase
- Follow the phase order and implementation steps exactly as defined
- Do not deviate from the planned architecture without explicit user approval
- The plan is the source of truth for project structure, dependencies, and implementation approach

When exiting plan mode to begin implementation:
1. Ensure the plan is saved in `~/.claude/plans/` (already done)
2. Review the current phase requirements
3. Follow the implementation steps in order
4. Mark phase completion when all success criteria are met

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
