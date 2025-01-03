"""VSCode environment collector plugin."""
from pathlib import Path

from hatch.env.collectors.plugin.interface import EnvironmentCollectorInterface

from .update_vscode_env import update_vscode_config


class VSCodeEnvironmentCollector(EnvironmentCollectorInterface):
    """VSCode environment collector plugin."""

    PLUGIN_NAME = "vscode"
    config_file = "python.env.json"

    def __init__(self, root, config):
        """Initialize the collector.
        
        Args:
            root: The root directory of the project
            config: The project configuration
        """
        super().__init__(root, config)

    def collect(self, app):
        """Collect environment information and update VSCode configuration.
        
        Args:
            app: The Hatch application instance
        """
        update_vscode_config({})


