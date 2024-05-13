from __future__ import annotations

from .indent_renderer import AbstractIndentRenderer
from .listener import RainbowIndentEventListener

__all__ = (
    # ST: core
    "plugin_loaded",
    "plugin_unloaded",
    # ST: listeners
    "RainbowIndentEventListener",
    # public interfaces
    "AbstractIndentRenderer",
)


def plugin_loaded() -> None:
    pass


def plugin_unloaded() -> None:
    pass
