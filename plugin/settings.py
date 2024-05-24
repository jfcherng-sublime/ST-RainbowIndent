from __future__ import annotations

from typing import Any, Callable, TypeVar, cast, overload

import sublime

from .constants import LEVEL_COLORS_FALLBACK, PLUGIN_NAME
from .data_types import LevelStyle
from .log import log_warning
from .utils import debounce

_T = TypeVar("_T")
_T_Callable = TypeVar("_T_Callable", bound=Callable[..., Any])


def debounce_by_settings(func: _T_Callable) -> _T_Callable:
    """Debounce a function so that it's called once in seconds defined in the plugin settings."""

    def debounced(*args: Any, **kwargs: Any) -> Any:
        from .settings import get_debounce_time

        if (time_s := get_debounce_time()) > 0:
            return debounce(time_s)(func)(*args, **kwargs)
        return func(*args, **kwargs)

    return cast(_T_Callable, debounced)


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


def get_enabled_selector() -> str:
    return get_plugin_setting("enabled_selector", "")


def get_level_colors() -> list[str]:
    return get_plugin_setting("level_colors", []) or LEVEL_COLORS_FALLBACK


def get_level_style() -> LevelStyle:
    style = get_plugin_setting("level_style", "block")
    try:
        return LevelStyle(style)
    except ValueError:
        log_warning(f'Invalid "level_style" setting: {style}')
        return LevelStyle.BLOCK


def get_file_size_limit() -> int:
    return int(get_plugin_setting("file_size_limit", -1))
