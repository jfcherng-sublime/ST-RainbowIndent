from __future__ import annotations

from typing import Any, TypeVar, overload

import sublime

from .constants import LEVEL_COLORS_FALLBACK, PLUGIN_NAME
from .data_types import LevelStyle

_T = TypeVar("_T")


@overload
def get_plugin_setting(key: str) -> Any: ...
@overload
def get_plugin_setting(key: str, default: None) -> Any: ...
@overload
def get_plugin_setting(key: str, default: _T) -> _T: ...


def get_plugin_setting(key: str, default: Any = None) -> Any:
    return get_plugin_settings().get(key, default)


def get_plugin_settings() -> sublime.Settings:
    return sublime.load_settings(f"{PLUGIN_NAME}.sublime-settings")


def get_debounce_time() -> float:
    return float(get_plugin_setting("debounce", 0.2))


def get_level_colors() -> list[str]:
    return get_plugin_setting("level_colors", []) or LEVEL_COLORS_FALLBACK


def get_level_style() -> LevelStyle:
    return LevelStyle(get_plugin_setting("level_style", "block"))


def get_file_size_limit() -> int:
    return int(get_plugin_setting("file_size_limit", -1))
