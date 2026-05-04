from collections.abc import Callable
from typing import Any
from typing import cast
from typing import overload

import sublime

from .constants import LEVEL_COLORS_FALLBACK
from .constants import PLUGIN_NAME
from .data_types import LevelStyle
from .log import log_warning
from .utils import debounce


def debounce_by_settings[T: Callable](func: T) -> T:
    """Debounce a function so that it's called once in seconds defined in the plugin settings."""

    def debounced(*args: Any, **kwargs: Any) -> Any:
        from .settings import get_debounce_time

        if (time_s := get_debounce_time()) > 0:
            return debounce(time_s)(func)(*args, **kwargs)
        return func(*args, **kwargs)

    return cast(T, debounced)


@overload
def get_plugin_setting(key: str) -> Any: ...
@overload
def get_plugin_setting(key: str, default: None) -> Any: ...
@overload
def get_plugin_setting[T](key: str, default: T) -> T: ...
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
    default_style = "block"
    style = get_plugin_setting("level_style", default_style)
    try:
        return LevelStyle(style)
    except ValueError:
        log_warning(f'Invalid "level_style" setting: {style}. "{default_style}" will be used.')
        return LevelStyle.BLOCK


def get_file_size_limit() -> int:
    return int(get_plugin_setting("file_size_limit", -1))
