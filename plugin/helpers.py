from __future__ import annotations

import sublime

from .constants import PLUGIN_NAME
from .data_types import IndentInfo, IndentStyle
from .settings import get_file_size_limit


def is_renderable_view(view: sublime.View) -> bool:
    return bool(
        view.is_valid()
        and view.element() is None
        and not is_transient_view(view)
        and not (0 <= get_file_size_limit() < view.size())
    )


def is_transient_view(view: sublime.View) -> bool:
    return bool((sheet := view.sheet()) and sheet.is_transient())


def get_regions_key(level: int) -> str:
    return f"{PLUGIN_NAME}:level@{level}"


def get_view_indent(view: sublime.View) -> IndentInfo:
    """Gets indent settings of the view."""
    settings = view.settings()

    tab_size = int(settings.get("tab_size", 4))

    if settings.get("translate_tabs_to_spaces", False):
        style = IndentStyle.SPACE
    else:
        style = IndentStyle.TAB

    return IndentInfo(tab_size=tab_size, style=style)
