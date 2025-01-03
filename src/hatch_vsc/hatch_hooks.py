from hatchling.plugin import hookimpl

from .plugin import VSCodeEnvironmentCollector

@hookimpl
def hatch_register_environment_collector():
    """Register the VSCode environment collector plugin.
    
    Returns:
        The environment collector class
    """
    print("🔌 VSCode environment collector plugin registered")
    return VSCodeEnvironmentCollector 

