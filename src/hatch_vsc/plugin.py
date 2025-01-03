"""VSCode environment collector plugin for Hatch."""
import sys
from typing import Dict

from hatch.env.collectors.plugin.interface import EnvironmentCollectorInterface

from . import update_vscode_env

class VSCodeEnvironmentCollector(EnvironmentCollectorInterface):
    """Updates VSCode configuration when environments are created."""

    PLUGIN_NAME = 'vscode'
    
    def finalize_config(self, config: Dict[str, Dict]) -> None:
        """Called after environment creation to update VSCode configuration.
        
        Args:
            config: The environment configuration dictionary
        """
        try:
            update_vscode_env.main()
        except Exception as e:
            print(f"⚠️  Warning: Failed to update VSCode configuration: {e}", file=sys.stderr)


