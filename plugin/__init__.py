from .commands import RainbowIndentViewDisableCommand
from .commands import RainbowIndentViewEnableCommand
from .commands import RainbowIndentViewToggleCommand
from .constants import PLUGIN_NAME
from .indent_renderer import AbstractIndentRenderer
from .listener import RainbowIndentEventListener
from .listener import refresh_all_views
from .settings import get_plugin_settings
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
    get_plugin_settings().add_on_change(PLUGIN_NAME, refresh_all_views)


def plugin_unloaded() -> None:
    """Executed when this plugin is unloaded."""
    get_plugin_settings().clear_on_change(PLUGIN_NAME)
    ViewManager.clear_all_views()
