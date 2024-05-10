from __future__ import annotations

import sys
import threading
import weakref
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any, Callable, Mapping, Tuple, TypeVar, cast

import sublime
import sublime_plugin

assert __package__

PLUGIN_NAME = __package__.partition(".")[0]

LEVEL_COLORS_FALLBACK = [
    "region.redish",
    "region.orangish",
    "region.yellowish",
    "region.greenish",
    "region.cyanish",
    "region.bluish",
    "region.purplish",
    "region.pinkish",
]

POINT = int
TUPLE_REGION = Tuple[POINT, POINT]

_T_Callable = TypeVar("_T_Callable", bound=Callable[..., Any])

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:

    class StrEnum(str, Enum):
        __str__ = str.__str__  # type: ignore
        __format__ = str.__format__  # type: ignore


def debounce(time_s: float = 0.3) -> Callable[[_T_Callable], _T_Callable]:
    """
    Debounce a function so that it's called after `time_s` seconds.
    If it's called multiple times in the time frame, it will only run the last call.

    Taken and modified from https://github.com/salesforce/decorator-operations
    """

    def decorator(func: _T_Callable) -> _T_Callable:
        @wraps(func)
        def debounced(*args: Any, **kwargs: Any) -> None:
            def call_function() -> Any:
                delattr(debounced, "_timer")
                return func(*args, **kwargs)

            if timer := getattr(debounced, "_timer", None):
                timer.cancel()

            timer = threading.Timer(time_s, call_function)
            timer.start()
            setattr(debounced, "_timer", timer)

        setattr(debounced, "_timer", None)
        return cast(_T_Callable, debounced)

    return decorator


def configured_debounce(func: _T_Callable) -> _T_Callable:
    """Debounce a function so that it's called once in seconds."""

    def debounced(*args: Any, **kwargs: Any) -> Any:
        if (time_s := get_plugin_setting("debounce", 0.2)) > 0:
            return debounce(time_s)(func)(*args, **kwargs)
        return func(*args, **kwargs)

    return cast(_T_Callable, debounced)


def get_plugin_setting(key: str, default: Any = None) -> Any:
    return get_plugin_settings().get(key, default)


def get_plugin_settings() -> sublime.Settings:
    return sublime.load_settings(f"{PLUGIN_NAME}.sublime-settings")


def get_regions_color(level: int) -> str:
    level_color: list[str] = get_plugin_setting("level_colors", []) or LEVEL_COLORS_FALLBACK
    return level_color[level % len(level_color)]


def get_regions_key(level: int) -> str:
    return f"{PLUGIN_NAME}:level-{level}"


def get_view_indent(view: sublime.View) -> IndentInfo:
    settings = view.settings()

    tab_size = settings.get("tab_size", 4)

    if settings.get("translate_tabs_to_spaces", False):
        style = IndentStyle.SPACE
    else:
        style = IndentStyle.TAB

    return IndentInfo(tab_size=tab_size, style=style)


@dataclass
class IndentInfo:
    tab_size: int
    style: IndentStyle

    @property
    def indent_chars(self) -> str:
        if self.style is IndentStyle.SPACE:
            return " " * self.tab_size
        if self.style is IndentStyle.TAB:
            return "\t"
        raise ValueError(f"Unknown indent style: {self.style}")

    @property
    def indent_length(self) -> int:
        return len(self.indent_chars)

    @property
    def indent_pattern(self) -> str:
        return rf"^({self.indent_chars})+"


class IndentStyle(StrEnum):
    SPACE = "space"
    TAB = "tab"


class LevelStyle(StrEnum):
    BLOCK = "block"
    LINE = "line"


class AbstractIndentRenderer(ABC):
    def __init__(self, view: sublime.View, *, indent_info: IndentInfo) -> None:
        self.view = view
        self.indent_info = indent_info

    @abstractmethod
    def render(self, level_pts: Mapping[int, list[POINT]]) -> None:
        """Render the view based on the points of each level."""


class BlockIndentRenderer(AbstractIndentRenderer):
    __REGION_FLAGS = sublime.DRAW_NO_OUTLINE | sublime.HIDE_ON_MINIMAP | sublime.NO_UNDO

    def render(self, level_pts: Mapping[int, list[POINT]]) -> None:
        for level, pts in level_pts.items():
            self.view.add_regions(
                get_regions_key(level),
                tuple(sublime.Region(pt, pt + self.indent_info.indent_length) for pt in pts),
                scope=get_regions_color(level),
                flags=self.__REGION_FLAGS,
            )


class LineIndentRenderer(AbstractIndentRenderer):
    __REGION_FLAGS = sublime.DRAW_NO_OUTLINE | sublime.HIDE_ON_MINIMAP | sublime.NO_UNDO | sublime.DRAW_EMPTY

    def render(self, level_pts: Mapping[int, list[POINT]]) -> None:
        for level, pts in level_pts.items():
            self.view.add_regions(
                get_regions_key(level),
                tuple(map(sublime.Region, pts)),
                scope=get_regions_color(level),
                flags=self.__REGION_FLAGS,
            )


class ViewManager:
    __instances: dict[weakref.ref[sublime.View], ViewManager] = {}

    def __init__(self, view: sublime.View, *, _from_init: bool = True) -> None:
        if _from_init:
            raise ValueError("Use `get_instance()` instead.")

        self.view = view
        self.max_level = -1

    @classmethod
    def get_instance(cls, view: sublime.View) -> ViewManager:
        view_proxy = weakref.proxy(view)
        view_ref = weakref.ref(view)
        if not cls.__instances.get(view_ref):
            cls.__instances[view_ref] = cls(view_proxy, _from_init=False)
        return cls.__instances[view_ref]

    def clear_view(self) -> None:
        for level in range(self.max_level + 1):
            self.view.erase_regions(get_regions_key(level))

    def render_view(self) -> None:
        indent_info = get_view_indent(self.view)
        level_style = LevelStyle(get_plugin_setting("level_style", "block"))

        renderer: AbstractIndentRenderer
        if level_style is LevelStyle.BLOCK:
            renderer = BlockIndentRenderer(self.view, indent_info=indent_info)
        elif level_style is LevelStyle.LINE:
            renderer = LineIndentRenderer(self.view, indent_info=indent_info)
        else:
            raise ValueError(f"Unknown level style: {level_style}")

        # key = indent level; value = list of begin point of indents
        level_pts: defaultdict[int, list[POINT]] = defaultdict(list)
        for region in self.view.find_all(indent_info.indent_pattern):
            for level in range(region.size() // indent_info.indent_length):
                level_pts[level].append(region.a + level * indent_info.indent_length)
        self.max_level = max(level_pts.keys(), default=-1)

        renderer.render(level_pts)


class RainbowIndent(sublime_plugin.ViewEventListener):
    def on_activated_async(self) -> None:
        self._work(self.view)

    def on_load_async(self) -> None:
        self._work(self.view)

    def on_modified_async(self) -> None:
        self._work(self.view)

    def on_revert_async(self) -> None:
        self._work(self.view)

    @staticmethod
    @configured_debounce
    def _work(view: sublime.View) -> None:
        vm = ViewManager.get_instance(view)
        vm.render_view()
