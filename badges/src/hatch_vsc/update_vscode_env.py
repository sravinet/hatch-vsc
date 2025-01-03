"""Updates VSCode configuration for Hatch environments."""
import json
import os
import sys
import platform
import subprocess
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
    base_path = Path(f"/Users/{username}/Library/Application Support/hatch/env/virtual")
    
    # Find the hash directory for this project
    project_name = Path.cwd().name
    project_dir = base_path / project_name
    
    # Find the hash directory (should be the only subdirectory)
    if project_dir.exists():
        hash_dirs = [d for d in project_dir.iterdir() if d.is_dir()]
        if hash_dirs:
            return hash_dirs[0]  # Return the hash directory path
    
    # If no hash directory found, return project directory
    return project_dir


def get_hatch_env_path() -> Path:
    """Get the path to Hatch environments.
    
    Returns:
        The path to Hatch environments
    """
    system = platform.system().lower()
    
    if system == "darwin":
        return get_macos_hatch_path()
    
    # For other systems, use hatch env find
    try:
        result = subprocess.run(['hatch', 'env', 'find'], capture_output=True, text=True)
        if result.returncode == 0:
            return Path(result.stdout.strip()).parent
    except Exception:
        pass
    
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


def infer_test_directory(env_config: Dict[str, Any]) -> str:
    """Infer test directory based on dependencies and configuration.
    
    Args:
        env_config: Environment configuration from pyproject.toml
        
    Returns:
        Inferred test directory or None
    """
    deps = env_config.get("dependencies", [])
    deps_str = " ".join(deps).lower()
    
    # Check for pytest configuration
    if "pytest" in deps_str:
        pytest_args = env_config.get("scripts", {}).get("test", "")
        if isinstance(pytest_args, str) and pytest_args.startswith("pytest"):
            # Extract directory from pytest command if specified
            parts = pytest_args.split()
            for part in parts:
                if part.startswith("tests") or part.endswith("tests"):
                    return part
        return "tests"  # Default pytest directory
    
    # Check for behave configuration
    if "behave" in deps_str:
        behave_args = env_config.get("scripts", {}).get("test", "")
        if isinstance(behave_args, str) and "behave" in behave_args:
            # Extract directory from behave command if specified
            if "cd" in behave_args:
                dir_part = behave_args.split("cd")[1].split("&&")[0].strip()
                return dir_part
        return "features"  # Default behave directory
    
    return None


def get_environment_mappings(config: Dict[str, Any]) -> Dict[str, str]:
    """Get environment mappings from pyproject.toml.
    
    Args:
        config: The parsed pyproject.toml data
        
    Returns:
        A dictionary mapping patterns to environment names
    """
    hatch_config = config.get("tool", {}).get("hatch", {})
    envs = hatch_config.get("envs", {})
    
    # Start with default environment for source files
    mappings = {
        "src/**/*": "default"  # Default environment for source files
    }
    
    # Look for environment-specific directory mappings
    for env_name, env_config in envs.items():
        if env_name == "default":
            continue
        
        # 1. Check for explicit VSCode mapping in env config
        if "vsc-mapping" in env_config:
            mappings[f"{env_config['vsc-mapping']}/**/*"] = env_name
            continue
            
        # 2. Check for script patterns that indicate directory mapping
        scripts = env_config.get("scripts", {})
        for script_cmd in scripts.values():
            if isinstance(script_cmd, str) and script_cmd.startswith("cd "):
                # Extract directory from cd command
                if "$(echo" in script_cmd:
                    # Extract path from $(echo 'path') pattern
                    start = script_cmd.find("'") + 1
                    end = script_cmd.find("'", start)
                    dir_path = script_cmd[start:end]
                else:
                    dir_path = script_cmd.split()[1]
                mappings[f"{dir_path}/**/*"] = env_name
                break
        
        # 3. Try to infer from standard test framework conventions
        if env_name not in mappings.values():
            test_dir = infer_test_directory(env_config)
            if test_dir:
                mappings[f"{test_dir}/**/*"] = env_name
                continue
        
        # 4. If no mapping found, use environment name as directory
        if env_name not in mappings.values():
            mappings[f"{env_name}/**/*"] = env_name
    
    return mappings


def update_vscode_config(mappings: Dict[str, str]) -> None:
    """Update VSCode configuration files.
    
    Args:
        mappings: Dictionary mapping patterns to environment names
    """
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    hatch_path = get_hatch_env_path()
    project_name = Path.cwd().name
    
    # Update python.env.json with environment interpreters
    env_file = vscode_dir / "python.env.json"
    env_config = {
        "python.envInterpreters": {
            pattern: str(hatch_path / (f"{project_name}_{env_name}" if env_name != "default" else project_name) / "bin" / "python")
            for pattern, env_name in mappings.items()
        }
    }
    
    with open(env_file, "w") as f:
        json.dump(env_config, f, indent=2)
    
    # Update settings.json
    settings_file = vscode_dir / "settings.json"
    settings = {}
    if settings_file.exists():
        with open(settings_file) as f:
            settings = json.load(f)
    
    # Set default interpreter and analysis paths
    settings["python.defaultInterpreterPath"] = str(hatch_path / project_name / "bin" / "python")
    settings["python.analysis.extraPaths"] = [
        str(hatch_path / (f"{project_name}_{env_name}" if env_name != "default" else project_name))
        for env_name in set(mappings.values())
    ]
    
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=2)


def main() -> None:
    """Main entry point."""
    try:
        print("Updating VSCode configuration with Hatch environments...")
        config = read_pyproject_toml()
        mappings = get_environment_mappings(config)
        
        print("\nEnvironment mappings (in order of precedence):")
        for pattern, env_name in mappings.items():
            print(f"  {pattern} -> {env_name}")
        
        update_vscode_config(mappings)
        print("\n✨ Updated VSCode configuration")
    except Exception as e:
        print(f"⚠️  Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 