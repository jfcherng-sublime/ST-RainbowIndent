from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator, Mapping, Sequence
from functools import cache
from typing import Any, final, override

import sublime
from more_itertools import first_true

from .data_types import INDENT_LEVEL, LevelStyle
from .helpers import get_regions_key
from .utils import camel_to_snake, get_circular_nth, list_all_subclasses


def find_indent_renderer(style: LevelStyle) -> type[AbstractIndentRenderer] | None:
    return first_true(get_indent_rendereres(), pred=lambda t: t.can_support(style))


@cache
def get_indent_rendereres() -> tuple[type[AbstractIndentRenderer], ...]:
    return tuple(sorted(list_indent_rendereres(), key=lambda cls: cls.name()))


def list_indent_rendereres() -> Generator[type[AbstractIndentRenderer]]:
    yield from list_all_subclasses(AbstractIndentRenderer, skip_abstract=True)  # type: ignore[type-abstract]


class AbstractIndentRenderer(ABC):
    def __init__(self, view: sublime.View) -> None:
        self.view = view

    @final
    @classmethod
    def name(cls) -> str:
        """The nickname of this class. Converts "FooBarIndentRenderer" into "foo_bar" by default."""
        return camel_to_snake(cls.__name__.removesuffix("IndentRenderer"))

    @classmethod
    @abstractmethod
    def can_support(cls, style: LevelStyle) -> bool:
        """Check if this renderer can support the given style."""

    @abstractmethod
    def render(
        self,
        *,
        level_colors: Sequence[str],
        level_regions: Mapping[INDENT_LEVEL, Sequence[sublime.Region]],
    ) -> None:
        """Render the view based on the points of each level."""


class BlockIndentRenderer(AbstractIndentRenderer):
    __ADD_REGION_FLAGS = sublime.DRAW_NO_OUTLINE | sublime.HIDE_ON_MINIMAP

    @override
    @classmethod
    def can_support(cls, style: LevelStyle) -> bool:
        return style is LevelStyle.BLOCK

    @override
    def render(
        self,
        *,
        level_colors: Sequence[str],
        level_regions: Mapping[INDENT_LEVEL, Sequence[sublime.Region]],
    ) -> None:
        for level, regions in level_regions.items():
            self.view.add_regions(
                get_regions_key(level),
                regions,
                scope=get_circular_nth(level_colors, level),
                flags=self.__ADD_REGION_FLAGS,
            )


class LineIndentRenderer(AbstractIndentRenderer):
    __ADD_REGION_FLAGS = sublime.DRAW_NO_OUTLINE | sublime.HIDE_ON_MINIMAP | sublime.DRAW_EMPTY

    @override
    @classmethod
    def can_support(cls, style: Any) -> bool:
        return style is LevelStyle.LINE

    @override
    def render(
        self,
        *,
        level_colors: Sequence[str],
        level_regions: Mapping[INDENT_LEVEL, Sequence[sublime.Region]],
    ) -> None:
        for level, regions in level_regions.items():
            self.view.add_regions(
                get_regions_key(level),
                tuple(sublime.Region(region.a) for region in regions),
                scope=get_circular_nth(level_colors, level),
                flags=self.__ADD_REGION_FLAGS,
            )
