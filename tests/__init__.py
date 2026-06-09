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

    def get(self, key: str, default: Any = None) -> Any:  # type: ignore[override]
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value


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

    def settings(self) -> Settings:
        return self._settings

    def syntax(self) -> Syntax:
        return self._syntax

    def size(self) -> int:
        return len(self._content)

    def substr(self, region: Region) -> str:
        return self._content[region.a : region.b]

    def line(self, pt: int) -> Region:
        start = self._content.rfind("\n", 0, pt) + 1
        end = self._content.find("\n", pt)
        if end == -1:
            end = len(self._content)
        return Region(start, end)

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
        pass

    def erase_regions(self, key: str) -> None:
        pass


# Mock module-level constants
DRAW_NO_OUTLINE = 0
HIDE_ON_MINIMAP = 0
DRAW_EMPTY = 0

# Mock module-level functions
_windows: list[Any] = []


def windows() -> list[Any]:
    return _windows


def load_settings(base_name: str) -> Settings:
    return Settings()


def set_timeout_async(f: Callable[[], Any], timeout_ms: float = 0) -> None:
    pass
