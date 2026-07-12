"""Mock Sublime Text module for unit testing.

Provides minimal stubs of the Sublime Text API used by RainbowIndent.
Only implements the surface area needed by the plugin's pure functions.
"""

from __future__ import annotations

from collections import UserDict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


class Region:
    """Mock for sublime.Region."""

    def __init__(self, a: int, b: int | None = None) -> None:
        if b is None:
            b = a
        self.a = a
        self.b = b

    def __lt__(self, other: Region) -> bool:
        return (self.a, self.b) < (other.a, other.b)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Region):
            return NotImplemented
        return self.a == other.a and self.b == other.b

    def __repr__(self) -> str:
        return f"Region({self.a}, {self.b})"

    def __hash__(self) -> int:
        return hash((self.a, self.b))

    def to_tuple(self) -> tuple[int, int]:
        return (self.a, self.b)

    def size(self) -> int:
        return self.b - self.a


class Settings(UserDict):
    """Mock for sublime.Settings."""

    def __init__(self) -> None:
        super().__init__()
        self.on_change_callbacks: dict[str, Callable[[], None]] = {}

    def get(self, key: str, default: Any = None) -> Any:  # type: ignore[override]
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def add_on_change(self, tag: str, callback: Callable[[], None]) -> None:
        self.on_change_callbacks[tag] = callback

    def clear_on_change(self, tag: str) -> None:
        self.on_change_callbacks.pop(tag, None)


@dataclass
class Syntax:
    """Mock for sublime.Syntax."""

    path: str
    scope: str
    name: str


class View:
    """Mock for sublime.View."""

    def __init__(self, content: str = "", syntax_scope: str = "text.plain") -> None:
        self._content = content
        self._settings = Settings()
        self._syntax = Syntax(path="", scope=syntax_scope, name="")
        self.regions: dict[str, list[Region]] = {}

    def settings(self) -> Settings:
        return self._settings

    def syntax(self) -> Syntax:
        return self._syntax

    def size(self) -> int:
        return len(self._content)

    def set_content(self, content: str) -> None:
        self._content = content

    def substr(self, region: Region) -> str:
        return self._content[region.a : region.b]

    def line(self, pt: int) -> Region:
        start = self._content.rfind("\n", 0, pt) + 1
        end = self._content.find("\n", pt)
        if end == -1:
            end = len(self._content)
        return Region(start, end)

    def id(self) -> int:
        return id(self)

    def change_count(self) -> int:
        return 0

    def is_valid(self) -> bool:
        return True

    def element(self) -> None:
        return None

    def set_status(self, key: str, value: str) -> None:
        pass

    def sel(self) -> list[Region]:
        return []

    def add_regions(self, key: str, regions: list[Region], scope: str = "", icon: str = "", flags: int = 0) -> None:
        self.regions[key] = list(regions)

    def erase_regions(self, key: str) -> None:
        self.regions.pop(key, None)


class Window:
    """Mock for sublime.Window."""

    def __init__(self, views: list[View] | None = None) -> None:
        self._views = views or []

    def views(self, *, include_transient: bool = False) -> list[View]:
        return list(self._views)


# Mock module-level constants
DRAW_NO_OUTLINE = 0
HIDE_ON_MINIMAP = 0
DRAW_EMPTY = 0

# Mock module-level functions
_windows: list[Window] = []


def windows() -> list[Window]:
    return _windows


# Real `sublime.load_settings()` returns the same object for repeated calls with the
# same `base_name`, rather than reloading from disk; mirror that so callbacks registered
# via `add_on_change`/`clear_on_change` operate on the object other code actually mutates.
_settings_cache: dict[str, Settings] = {}


def load_settings(base_name: str) -> Settings:
    if base_name not in _settings_cache:
        _settings_cache[base_name] = Settings()
    return _settings_cache[base_name]


# Calls scheduled via `set_timeout_async`, in scheduling order.
# Tests can invoke the callbacks manually to simulate timers firing; not auto-run.
scheduled_calls: list[tuple[Callable[[], Any], float]] = []


def set_timeout_async(f: Callable[[], Any], timeout_ms: float = 0) -> None:
    scheduled_calls.append((f, timeout_ms))
