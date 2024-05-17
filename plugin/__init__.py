from __future__ import annotations

from .commands import (
    RainbowIndentViewDisableCommand,
    RainbowIndentViewEnableCommand,
    RainbowIndentViewToggleCommand,
)
from .indent_renderer import AbstractIndentRenderer
from .listener import RainbowIndentEventListener
from .view_manager import ViewManager

__all__ = (
    # ST: core
    "plugin_loaded",
    "plugin_unloaded",
    # ST: commands
    "RainbowIndentViewDisableCommand",
    "RainbowIndentViewEnableCommand",
    "RainbowIndentViewToggleCommand",
    # ST: listeners
    "RainbowIndentEventListener",
    # public interfaces
    "AbstractIndentRenderer",
)


def plugin_loaded() -> None:
    """Executed when this plugin is loaded."""


def plugin_unloaded() -> None:
    """Executed when this plugin is unloaded."""
    ViewManager.clear_all_views()
