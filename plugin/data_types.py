from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import Pattern, Tuple

import sublime
from typing_extensions import Self

POINT = int
TUPLE_REGION = Tuple[POINT, POINT]
INDENT_LEVEL = int

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:

    class StrEnum(str, Enum):
        __str__ = str.__str__  # type: ignore
        __format__ = str.__format__  # type: ignore


@dataclass(frozen=True)
class IndentInfo:
    tab_size: int
    style: IndentStyle

    @cached_property
    def indent_chars(self) -> str:
        if self.style is IndentStyle.SPACE:
            return " " * self.tab_size
        if self.style is IndentStyle.TAB:
            return "\t"
        raise ValueError(f"Unknown indent style: {self.style}")

    @cached_property
    def indent_length(self) -> int:
        return len(self.indent_chars)

    @cached_property
    def indent_pattern(self) -> str:
        return rf"^(?:{self.indent_chars})+"

    @cached_property
    def indent_pattern_compiled(self) -> Pattern[str]:
        return re.compile(self.indent_pattern, flags=re.MULTILINE)

    @classmethod
    def from_view(cls, view: sublime.View) -> Self:
        settings = view.settings()
        tab_size = int(settings.get("tab_size", 4))
        if settings.get("translate_tabs_to_spaces", False):
            style = IndentStyle.SPACE
        else:
            style = IndentStyle.TAB
        return cls(tab_size=tab_size, style=style)


class IndentStyle(StrEnum):
    SPACE = "space"
    TAB = "tab"


class LevelStyle(StrEnum):
    BLOCK = "block"
    LINE = "line"
