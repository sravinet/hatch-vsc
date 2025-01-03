"""Tests for VSCode plugin."""
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

from hatch_vsc.plugin import VSCodeEnvironmentCollector


def test_vscode_collector_initialization():
    """Test collector initialization."""
    root = Path("/test/root")
    config = {"project": {"name": "test-project"}}
    collector = VSCodeEnvironmentCollector(root=root, config=config)
    assert collector.config_file == "python.env.json"


def test_vscode_collector_collect():
    """Test environment collection."""
    root = Path("/test/root")
    config = {"project": {"name": "test-project"}}
    collector = VSCodeEnvironmentCollector(root=root, config=config)
    mock_app = Mock()
    
    mock_settings = "{}"
    with patch("pathlib.Path.exists", return_value=True), \
         patch("pathlib.Path.mkdir"), \
         patch("hatch_vsc.update_vscode_env.get_hatch_env_path", return_value=Path("/mock/env")), \
         patch("builtins.open", mock_open(read_data=mock_settings)), \
         patch("json.dump"):
        collector.collect(mock_app) 