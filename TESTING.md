# Testing Strategy

## Overview

This project aims for meaningful test coverage rather than 100% line coverage. We currently maintain 96% coverage, intentionally excluding certain paths that don't require testing.

## Test Coverage Philosophy

We focus on:
- Testing all main functionality paths
- Testing critical error cases
- Testing edge cases that could occur in production
- Mocking file system operations to ensure tests are reliable

We intentionally don't test:
- Simple error handling with default values
- Entry points without business logic
- Trivial property getters/setters

## Current Coverage (96%)

Uncovered lines are documented and accepted:
- Error handling in `infer_test_directory` (lines 70-71)
- Error handling in `get_environment_mappings` (lines 105, 130)
- The `__main__` entry point (line 227)

## Test Organization

Tests are organized by module:
- `test_config.py`: Configuration parsing and environment mapping
- `test_hooks.py`: Hatch plugin hook registration
- `test_plugin.py`: VSCode environment collector plugin
- `test_vscode.py`: VSCode integration and path handling

## Testing Practices

### Mocking
- File operations are mocked to avoid filesystem dependencies
- External commands are mocked to ensure test reliability
- System environment variables are mocked using `monkeypatch`

### Test Data
- Test configurations use minimal examples
- Each test case focuses on a single aspect
- Test data is inline to make tests self-contained

### Running Tests

```bash
# Run all tests with coverage
hatch run test:pytest

# Run specific test file
hatch run test:pytest tests/test_config.py

# Run specific test
hatch run test:pytest tests/test_config.py::test_get_environment_mappings
```

## Contributing Tests

When adding new tests:
1. Focus on testing behavior, not implementation
2. Mock external dependencies
3. Keep test cases focused and clear
4. Document any intentionally untested code
5. Avoid testing trivial code just for coverage

## Continuous Integration

Tests are run automatically on:
- Pull requests against main branch
- Pushes to main branch
- Release publications

Our CI pipeline:
1. Runs tests on multiple platforms (Linux, macOS, Windows)
2. Tests against multiple Python versions (3.8 to 3.12)
3. Generates coverage reports
4. Uploads coverage data to Codecov

### Coverage Reports

Coverage reports are generated in two formats:
- Terminal output with missing lines highlighted
- XML report for Codecov integration

You can view the coverage reports:
- Locally in the terminal after running tests
- On Codecov for each PR and commit
- In the GitHub Actions workflow artifacts

### CI Configuration

The CI setup is defined in:
- `.github/workflows/test.yml`: GitHub Actions workflow
- `pyproject.toml`: Coverage report configuration
- `codecov.yml`: Codecov settings (coverage thresholds, etc.)
- `.deepsource.toml`: DeepSource analyzer configuration

### Code Quality Tools

We use multiple tools to ensure code quality:

#### Coverage Analysis
- **Codecov**: Tracks test coverage over time and on PRs
- **DeepSource**: Provides additional coverage insights and code quality checks

#### Static Analysis
- **DeepSource Python Analyzer**: 
  - Type checking with mypy
  - Code quality checks
  - Best practices enforcement
  - Maximum line length: 100 characters

#### Code Formatting
- **Black**: Code formatting (via DeepSource transformer)
- **isort**: Import sorting (via DeepSource transformer)

#### Security
- **DeepSource Secrets Analyzer**: Scans for accidentally committed secrets

### Quality Reports

You can find quality reports in several places:
1. GitHub Actions workflow results
2. Codecov dashboard and PR comments
3. DeepSource dashboard showing:
   - Test coverage analysis
   - Code quality issues
   - Security concerns
   - Automated fixes via transformers
