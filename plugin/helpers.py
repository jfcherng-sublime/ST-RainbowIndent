from __future__ import annotations

import sublime

from .constants import PLUGIN_NAME, VIEW_KEY_USER_DISABLED
from .settings import get_enabled_selector, get_file_size_limit


def is_renderable_view(view: sublime.View) -> bool:
    # the user may explicitly enable/disable rendering for the current view
    if (is_disabled := view.settings().get(VIEW_KEY_USER_DISABLED)) is not None:
        return not is_disabled
    # activation by plugin's logics
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
