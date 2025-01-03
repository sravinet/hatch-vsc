"""Hatch hooks for VSCode integration."""
from .plugin import VSCodeEnvironmentCollector


def hatch_register_environment_collector(app):
    """Register the VSCode environment collector."""
    app.collector_registry.register("vscode", VSCodeEnvironmentCollector) 

