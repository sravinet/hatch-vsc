"""Tests for configuration handling.

Test Coverage Strategy:
- We aim for meaningful test coverage rather than 100% line coverage
- We test all main functionality paths and critical error cases
- We accept not testing:
  - Some error handling in infer_test_directory (lines 70-71)
  - Some error handling in get_environment_mappings (lines 105, 130)
  - The __main__ entry point (line 227)
- These untested paths are either:
  1. Simple error handling with default values
  2. Entry points that don't contain business logic
"""
from unittest.mock import patch

import pytest

from hatch_vsc.update_vscode_env import get_environment_mappings, infer_test_directory


def test_get_environment_mappings():
    """Test environment mappings extraction."""
    config = {
        "tool": {
            "hatch": {
                "envs": {
                    "test": {
                        "dependencies": ["pytest"],
                        "scripts": {"test": "pytest tests"}
                    }
                }
            }
        }
    }
    mappings = get_environment_mappings(config)
    assert mappings["src/**/*"] == "default"
    assert mappings["tests/**/*"] == "test"


def test_get_environment_mappings_vsc_mapping():
    """Test environment mappings with explicit VSCode mapping."""
    config = {
        "tool": {
            "hatch": {
                "envs": {
                    "test": {
                        "vsc-mapping": "custom/tests"
                    }
                }
            }
        }
    }
    mappings = get_environment_mappings(config)
    assert mappings["custom/tests/**/*"] == "test"


def test_get_environment_mappings_cd_script():
    """Test environment mappings with cd script."""
    config = {
        "tool": {
            "hatch": {
                "envs": {
                    "test": {
                        "scripts": {
                            "test": "cd custom/path && pytest"
                        }
                    }
                }
            }
        }
    }
    mappings = get_environment_mappings(config)
    assert mappings["custom/path/**/*"] == "test"


def test_get_environment_mappings_cd_script_echo():
    """Test environment mappings with cd script using echo."""
    config = {
        "tool": {
            "hatch": {
                "envs": {
                    "test": {
                        "scripts": {
                            "test": "cd $(echo 'custom/path') && pytest"
                        }
                    }
                }
            }
        }
    }
    mappings = get_environment_mappings(config)
    assert mappings["custom/path/**/*"] == "test"


def test_get_environment_mappings_fallback():
    """Test environment mappings fallback to env name."""
    config = {
        "tool": {
            "hatch": {
                "envs": {
                    "custom": {}
                }
            }
        }
    }
    mappings = get_environment_mappings(config)
    assert mappings["custom/**/*"] == "custom"


def test_infer_test_directory():
    """Test test directory inference from environment config."""
    # Test pytest detection
    pytest_config = {
        "dependencies": ["pytest", "pytest-cov"],
        "scripts": {"test": "pytest tests"}
    }
    assert infer_test_directory(pytest_config) == "tests"
    
    # Test behave detection
    behave_config = {
        "dependencies": ["behave"],
        "scripts": {"test": "cd features && behave"}
    }
    assert infer_test_directory(behave_config) == "features"
    
    # Test no test framework
    empty_config = {"dependencies": ["requests"]}
    assert infer_test_directory(empty_config) is None 


def test_get_environment_mappings_invalid_script():
    """Test environment mappings with invalid script command."""
    config = {
        "tool": {
            "hatch": {
                "envs": {
                    "test": {
                        "scripts": {
                            "test": 123  # Non-string script command
                        }
                    }
                }
            }
        }
    }
    mappings = get_environment_mappings(config)
    # Should fall back to using environment name
    assert mappings["test/**/*"] == "test"


def test_infer_test_directory_invalid_script():
    """Test test directory inference with invalid script."""
    config = {
        "dependencies": ["pytest"],
        "scripts": {"test": 123}  # Non-string script command
    }
    assert infer_test_directory(config) == "tests"  # Should fall back to default 