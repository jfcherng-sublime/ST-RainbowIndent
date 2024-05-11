from __future__ import annotations

import sublime

from .constants import PLUGIN_NAME
from .data_types import IndentInfo, IndentStyle
from .settings import get_level_colors


def get_regions_color(level: int) -> str:
    level_color = get_level_colors()
    return level_color[level % len(level_color)]


def get_regions_key(level: int) -> str:
    return f"{PLUGIN_NAME}:level-{level}"


def get_view_indent(view: sublime.View) -> IndentInfo:
    """Gets indent settings of the view."""
    settings = view.settings()

    tab_size = settings.get("tab_size", 4)

    if settings.get("translate_tabs_to_spaces", False):
        style = IndentStyle.SPACE
    else:
        style = IndentStyle.TAB

    return IndentInfo(tab_size=tab_size, style=style)
