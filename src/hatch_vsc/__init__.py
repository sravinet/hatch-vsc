"""Hatch plugin for VSCode integration."""

try:
    from importlib.metadata import version
    __version__ = version("hatch-vsc")
except ImportError:
    # Package is not installed
    __version__ = "0.0.0"