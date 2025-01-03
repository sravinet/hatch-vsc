# Design Documentation for hatch-vsc

## Overview

hatch-vsc is a Hatch plugin that automatically configures VSCode's Python environment settings when Hatch environments are created or modified. This document explains the key design decisions and architecture.

## Plugin Type Choice

We implemented this as an Environment Collector Plugin rather than other plugin types because:

1. **Environment Collector vs Environment Type**:
   - Environment Collectors can observe and modify environment configurations without changing how environments work
   - Environment Types would create a new kind of environment, which is overkill for our use case
   - We want to "hook into" environment creation, not change how environments work

2. **Why not a Build Hook**:
   - Build hooks run during package building
   - Our functionality is related to development environments, not package building
   - We need to run when environments change, not when building packages

## Architecture

### Core Components

1. **Environment Collector** (`VSCodeEnvironmentCollector`):
   - Implements `EnvironmentCollectorInterface`
   - Hooks into environment creation via `finalize_config()`
   - Triggers VSCode configuration updates after environment setup

2. **Plugin Registration** (`hatch_hooks.py`):
   - Uses Hatch's plugin system via `@hookimpl`
   - Registers the collector through `hatch_register_environment_collector()`
   - Provides debug logging for plugin registration

3. **VSCode Configuration** (`update_vscode_env.py`):
   - Handles the actual VSCode settings updates
   - Manages .vscode/settings.json
   - Updates Python interpreter paths

## Key Design Decisions

1. **Separation of Concerns**:
   - Plugin logic (collector) is separate from VSCode configuration logic
   - Clear distinction between Hatch integration and VSCode functionality

2. **Error Handling**:
   - Graceful failure if VSCode configuration can't be updated
   - Warning messages instead of stopping environment creation
   - Ensures Hatch workflows aren't broken by plugin issues

3. **Configuration Flow**:
   ```
   Hatch Environment Creation
   → Environment Collector Hook
   → VSCode Configuration Update
   → .vscode/settings.json Modified
   ```

## Future Considerations

1. **Configuration Options**:
   - Could add support for custom VSCode settings
   - Potential for workspace-specific configurations

2. **Multi-Environment Support**:
   - Better handling of multiple Python environments
   - Workspace-specific environment mappings

3. **Integration Tests**:
   - Add tests for Hatch plugin integration
   - Mock VSCode configuration updates

## Dependencies

- `hatchling`: Core Hatch plugin support
- `tomli`: TOML file parsing for configurations

## Plugin Registration

The plugin is registered via entry points in `pyproject.toml`:
```toml
[project.entry-points.hatch]
vscode = "hatch_vsc.hatch_hooks:hatch_register_environment_collector"
```

This ensures Hatch discovers and loads the plugin automatically.