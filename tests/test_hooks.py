"""Tests for Hatch hooks."""
from unittest.mock import Mock, patch

from hatch_vsc.hatch_hooks import hatch_register_environment_collector


def test_hatch_register_environment_collector():
    """Test hook registration."""
    mock_app = Mock()
    mock_app.collector_registry = Mock()
    
    hatch_register_environment_collector(mock_app)
    
    mock_app.collector_registry.register.assert_called_once() 