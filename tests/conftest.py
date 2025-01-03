import json
from pathlib import Path
import pytest


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory with basic structure."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    (project_dir / ".vscode").mkdir()
    return project_dir


@pytest.fixture
def mock_pyproject_toml(temp_project_dir):
    """Create a mock pyproject.toml file."""
    content = {
        "tool": {
            "hatch": {
                "envs": {
                    "test": {
                        "dependencies": ["pytest"],
                        "vsc-mapping": "tests"
                    },
                    "lint": {
                        "dependencies": ["black", "flake8"],
                        "scripts": {
                            "style": "cd scripts && black ."
                        }
                    }
                }
            }
        }
    }
    
    pyproject_file = temp_project_dir / "pyproject.toml"
    with open(pyproject_file, "w") as f:
        json.dump(content, f)
    return pyproject_file 