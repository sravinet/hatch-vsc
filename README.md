# hatch-vsc

[![Tests](../../actions/workflows/test.yml/badge.svg)](../../actions/workflows/test.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/sravinet/hatch-vsc/gh-pages/badges/coverage-badge.json)](../../actions/workflows/test.yml)

A Hatch plugin for VSCode integration that automatically updates VSCode configuration when Hatch environments are created.

## Warning

Don't use it yet unless you want to contribute - it is Alpha code.

## Installation

```bash
pip install hatch-vsc
```

## Usage

Add the plugin to your project's `pyproject.toml`:

```toml
[tool.hatch.env]
requires = [
    "hatch-vsc"
]
```

Then configure your environments with VSCode mappings:

```toml
[tool.hatch.envs.test]
dependencies = [
    "pytest",
    "pytest-cov"
]
vsc-mapping = "tests"  # Maps this environment to the tests directory

[tool.hatch.envs.scripts]
dependencies = [
    "black",
    "mypy"
]
vsc-mapping = "scripts"  # Maps this environment to the scripts directory
```

The plugin will automatically update your VSCode configuration whenever you create a new environment:

```bash
hatch env create test
```

## License

MIT 
