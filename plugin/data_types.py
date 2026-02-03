from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from functools import cached_property
from re import Pattern
from typing import Self

import sublime

type POINT = int
type TUPLE_REGION = tuple[POINT, POINT]
type INDENT_LEVEL = int


@dataclass(frozen=True)
class IndentInfo:
    tab_size: int
    style: IndentStyle

    @cached_property
    def indent_chars(self) -> str:
        match self.style:
            case IndentStyle.SPACE:
                return " " * self.tab_size
            case IndentStyle.TAB:
                return "\t"

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
        return cls(
            tab_size=int(settings.get("tab_size", 4)),
            style=IndentStyle.SPACE if settings.get("translate_tabs_to_spaces", False) else IndentStyle.TAB,
        )


class IndentStyle(StrEnum):
    SPACE = "space"
    TAB = "tab"


class LevelStyle(StrEnum):
    BLOCK = "block"
    LINE = "line"
