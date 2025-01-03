import pytest
from pathlib import Path

from hatch_vsc.update_vscode_env import (
    read_pyproject_toml,
    get_environment_mappings,
    infer_test_directory
)


def test_read_pyproject_toml(mock_pyproject_toml):
    """Test reading pyproject.toml file."""
    config = read_pyproject_toml()
    assert "tool" in config
    assert "hatch" in config["tool"]
    assert "envs" in config["tool"]["hatch"]


def test_get_environment_mappings(mock_pyproject_toml):
    """Test environment mapping generation."""
    config = read_pyproject_toml()
    mappings = get_environment_mappings(config)
    
    # Basic mappings
    assert "src/**/*" in mappings
    assert mappings["src/**/*"] == "default"
    assert "tests/**/*" in mappings
    assert mappings["tests/**/*"] == "test"


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