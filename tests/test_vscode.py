"""Tests for VSCode environment handling."""
import json
import os
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from hatch_vsc.update_vscode_env import (
    get_hatch_env_path,
    get_macos_hatch_path,
    infer_test_directory,
    read_pyproject_toml,
    update_vscode_config
)


@pytest.fixture
def mock_env_path():
    """Create a mock Hatch environment path."""
    return Path("/mock/hatch/env/virtual")


def test_get_macos_hatch_path(monkeypatch):
    """Test macOS Hatch path detection."""
    test_user = "testuser"
    test_project = "test-project"
    monkeypatch.setenv("USER", test_user)
    
    # Create mock paths
    base_str = f"/Users/{test_user}/Library/Application Support/hatch/env/virtual"
    project_str = f"{base_str}/{test_project}"
    env_str = f"{project_str}/{test_project}"  # Default environment
    
    class MockPath:
        def __init__(self, path_str):
            self.path_str = path_str
        
        def __str__(self):
            return self.path_str
        
        def __truediv__(self, other):
            if self.path_str == base_str and other == test_project:
                return MockPath(project_str)
            return MockPath(env_str)
        
        @property
        def name(self):
            return os.path.basename(self.path_str)
        
        def exists(self):
            # Base path and project directory should exist
            return self.path_str in [base_str, project_str]
        
        def is_dir(self):
            # All paths in our test should be directories
            return True
        
        def iterdir(self):
            if self.path_str == project_str:
                # Create a mock environment directory
                mock_env = Mock()
                mock_env.__str__ = lambda x: env_str
                mock_env.name = test_project  # Default environment name
                mock_env.is_dir = lambda: True
                return [mock_env]
            return []
        
        def cwd(self):
            return MockPath(f"/test/path/{test_project}")
    
    with patch("pathlib.Path", side_effect=MockPath), \
         patch.object(Path, "cwd", return_value=MockPath(f"/test/path/{test_project}")):
        path = get_macos_hatch_path()
        assert path.name == test_project  # Should be the project name for default env
        assert base_str in str(path)


def test_get_macos_hatch_path_no_user(monkeypatch):
    """Test macOS path detection with no user."""
    monkeypatch.delenv("USER", raising=False)
    
    with pytest.raises(RuntimeError, match="Could not determine username"):
        get_macos_hatch_path()


def test_get_hatch_env_path(monkeypatch):
    """Test Hatch environment path detection."""
    with patch("platform.system", return_value="Darwin"), \
         patch("pathlib.Path.exists", return_value=True):
        path = get_hatch_env_path()
        assert "hatch/env/virtual" in str(path)


def test_get_hatch_env_path_unsupported():
    """Test environment path detection on unsupported platform."""
    with patch("platform.system", return_value="Windows"), \
         patch("subprocess.run", side_effect=Exception("Command failed")):
        with pytest.raises(NotImplementedError, match="Platform .* not supported yet"):
            get_hatch_env_path()


def test_get_hatch_env_path_subprocess():
    """Test environment path detection using subprocess."""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = "/path/to/env\n"
    
    with patch("platform.system", return_value="Linux"), \
         patch("subprocess.run", return_value=mock_result):
        path = get_hatch_env_path()
        assert str(path) == "/path/to"


def test_read_pyproject_toml_missing():
    """Test reading missing pyproject.toml."""
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError, match="pyproject.toml not found"):
            read_pyproject_toml()


def test_infer_test_directory_behave_cd():
    """Test test directory inference for behave with cd."""
    config = {
        "dependencies": ["behave"],
        "scripts": {"test": "cd features/acceptance && behave"}
    }
    assert infer_test_directory(config) == "features/acceptance"


def test_update_vscode_config(mock_env_path):
    """Test VSCode configuration update."""
    mock_project_dir = Path("/mock/project")
    
    mappings = {
        "src/**/*": "default",
        "tests/**/*": "test"
    }
    
    mock_settings = "{}"
    
    with patch("pathlib.Path.exists", return_value=True), \
         patch("pathlib.Path.mkdir"), \
         patch("hatch_vsc.update_vscode_env.get_hatch_env_path", return_value=mock_env_path), \
         patch("pathlib.Path.cwd", return_value=mock_project_dir), \
         patch("builtins.open", mock_open(read_data=mock_settings)), \
         patch("json.dump") as mock_dump:
        update_vscode_config(mappings)
        
        # Verify json.dump was called with correct arguments
        assert mock_dump.call_count == 2  # Once for each config file
        
        # First call should be for python.env.json
        env_config_call = mock_dump.call_args_list[0]
        env_config = env_config_call[0][0]  # First argument of first call
        assert "python.envInterpreters" in env_config
        
        # Second call should be for settings.json
        settings_call = mock_dump.call_args_list[1]
        settings = settings_call[0][0]  # First argument of second call
        assert "python.defaultInterpreterPath" in settings
        assert "python.analysis.extraPaths" in settings


def test_update_vscode_config_existing_settings(mock_env_path):
    """Test VSCode configuration update with existing settings."""
    mock_project_dir = Path("/mock/project")
    
    mappings = {
        "src/**/*": "default",
        "tests/**/*": "test"
    }
    
    existing_settings = {
        "python.linting.enabled": True,
        "python.formatting.provider": "black"
    }
    mock_settings = json.dumps(existing_settings)
    
    with patch("pathlib.Path.exists", return_value=True), \
         patch("pathlib.Path.mkdir"), \
         patch("hatch_vsc.update_vscode_env.get_hatch_env_path", return_value=mock_env_path), \
         patch("pathlib.Path.cwd", return_value=mock_project_dir), \
         patch("builtins.open", mock_open(read_data=mock_settings)), \
         patch("json.dump") as mock_dump:
        update_vscode_config(mappings)
        
        # Verify json.dump was called with correct arguments
        assert mock_dump.call_count == 2
        
        # Check settings.json preserves existing settings
        settings_call = mock_dump.call_args_list[1]
        settings = settings_call[0][0]
        assert settings["python.linting.enabled"] is True
        assert settings["python.formatting.provider"] == "black"
        assert "python.defaultInterpreterPath" in settings
        assert "python.analysis.extraPaths" in settings 


def test_main_success():
    """Test successful main execution."""
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
    
    mock_settings = "{}"
    with patch("hatch_vsc.update_vscode_env.read_pyproject_toml", return_value=config), \
         patch("pathlib.Path.exists", return_value=True), \
         patch("pathlib.Path.mkdir"), \
         patch("hatch_vsc.update_vscode_env.get_hatch_env_path", return_value=Path("/mock/env")), \
         patch("builtins.open", mock_open(read_data=mock_settings)), \
         patch("json.dump"), \
         patch("builtins.print") as mock_print:
        from hatch_vsc.update_vscode_env import main
        main()
        
        # Verify output
        mock_print.assert_any_call("Updating VSCode configuration with Hatch environments...")
        mock_print.assert_any_call("\nEnvironment mappings (in order of precedence):")
        mock_print.assert_any_call("\n✨ Updated VSCode configuration")


def test_main_error():
    """Test main execution with error."""
    with patch("hatch_vsc.update_vscode_env.read_pyproject_toml", side_effect=Exception("Test error")), \
         patch("sys.exit") as mock_exit, \
         patch("builtins.print") as mock_print:
        from hatch_vsc.update_vscode_env import main
        main()
        
        # Verify error handling
        mock_print.assert_any_call("⚠️  Error: Test error", file=sys.stderr)
        mock_exit.assert_called_once_with(1) 