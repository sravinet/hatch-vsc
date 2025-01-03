"""Updates VSCode configuration for Hatch environments."""
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

import tomli


def get_macos_hatch_path() -> Path:
    """Get the path to Hatch environments on macOS.
    
    Returns:
        The path to Hatch environments
    """
    username = os.getenv("USER")
    if not username:
        raise RuntimeError("Could not determine username")
    return Path(f"/Users/{username}/Library/Application Support/hatch/env/virtual")


def get_hatch_env_path() -> Path:
    """Get the path to Hatch environments.
    
    Returns:
        The path to Hatch environments
    """
    if sys.platform == "darwin":
        return get_macos_hatch_path()
    raise NotImplementedError(f"Platform {sys.platform} not supported yet")


def read_pyproject_toml() -> Dict[str, Any]:
    """Read the pyproject.toml file.
    
    Returns:
        The parsed TOML data
    """
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")
    
    with open(pyproject_path, "rb") as f:
        return tomli.load(f)


def get_environment_mappings(config: Dict[str, Any]) -> Dict[str, str]:
    """Get environment mappings from pyproject.toml.
    
    Args:
        config: The parsed pyproject.toml data
        
    Returns:
        A dictionary mapping environment names to directories
    """
    mappings = {}
    envs = config.get("tool", {}).get("hatch", {}).get("envs", {})
    
    for env_name, env_config in envs.items():
        if "vsc-mapping" in env_config:
            mappings[env_name] = env_config["vsc-mapping"]
    
    return mappings


def update_vscode_config(mappings: Dict[str, str]) -> None:
    """Update VSCode configuration files.
    
    Args:
        mappings: Dictionary mapping environment names to directories
    """
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    # Update python.env.json
    env_file = vscode_dir / "python.env.json"
    env_config = {"envFolders": []}
    
    hatch_path = get_hatch_env_path()
    project_name = Path.cwd().name
    
    for env_name, mapping in mappings.items():
        env_config["envFolders"].append({
            "envPath": str(hatch_path / f"{project_name}_{env_name}"),
            "pattern": f"{mapping}/**"
        })
    
    with open(env_file, "w") as f:
        json.dump(env_config, f, indent=2)
    
    # Update settings.json
    settings_file = vscode_dir / "settings.json"
    settings = {}
    if settings_file.exists():
        with open(settings_file) as f:
            settings = json.load(f)
    
    settings["python.analysis.extraPaths"] = [
        str(hatch_path / f"{project_name}_{env_name}")
        for env_name in mappings
    ]
    
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=2)


def main() -> None:
    """Main entry point."""
    try:
        config = read_pyproject_toml()
        mappings = get_environment_mappings(config)
        update_vscode_config(mappings)
        print("✨ Updated VSCode configuration")
    except Exception as e:
        print(f"⚠️  Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 