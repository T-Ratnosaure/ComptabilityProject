# Testing Guide

## Quick Test Runner (Local Development)

Due to performance issues with pytest + coverage on Windows + uv, we provide a quick test runner for local validation.

### Run Quick Tests

```bash
python test_quick.py
```

This script runs essential tests without pytest overhead:
- Consolidation of extracted fields
- Mapping to TaxCalculationRequest
- Field aliases handling

**Expected output:**
```
>>> Running quick validation tests...

[OK] test_consolidate_single_document PASSED
[OK] test_map_to_tax_request_basic PASSED
[OK] test_field_aliases PASSED

>>> All quick tests PASSED!
```

## Full Test Suite (CI/CD or Manual)

### Without Coverage (Fast)

```bash
uv run pytest
```

Coverage is disabled by default in `pyproject.toml` for local development.

### With Coverage (Slow but Complete)

```bash
uv run pytest --cov=. --cov-report=term-missing --cov-report=html
```

This generates:
- Terminal coverage report
- HTML coverage report in `htmlcov/`
- XML coverage report (for CI/CD)

## Test Organization

```
tests/
├── llm/
│   └── test_context_builder_benefice.py  # LLM context tests
├── services/
│   ├── test_data_mapper.py               # TaxDataMapper tests
│   └── test_validation.py                # Validation tests
├── security/
│   └── test_file_validation.py           # File security tests
└── ...
```

## Pytest Configuration

See `pyproject.toml` section `[tool.pytest.ini_options]` for configuration.

Coverage options are commented out for local dev but can be re-enabled for CI/CD.

## Known Issues

- **Pytest + Coverage on Windows + uv**: Very slow (>15min for simple tests)
  - **Workaround**: Use `python test_quick.py` for quick validation
  - **Long-term**: Use CI/CD with Linux runners for full pytest suite

## CI/CD Recommendations

For GitHub Actions or similar CI/CD:

```yaml
- name: Run tests with coverage
  run: |
    uv run pytest --cov=. --cov-report=xml --cov-report=term-missing

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

Linux runners don't have the performance issues observed on Windows.
