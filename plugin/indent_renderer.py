from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Any, Generator, Mapping, Sequence, final

import sublime
from more_itertools import first_true

from .data_types import LevelStyle
from .helpers import get_regions_key
from .utils import camel_to_snake, get_circular_nth, list_all_subclasses, remove_suffix


def find_indent_renderer(obj: Any) -> type[AbstractIndentRenderer] | None:
    return first_true(get_indent_rendereres(), pred=lambda t: t.can_support(obj))


@lru_cache
def get_indent_rendereres() -> tuple[type[AbstractIndentRenderer], ...]:
    return tuple(sorted(list_indent_rendereres(), key=lambda cls: cls.name()))


def list_indent_rendereres() -> Generator[type[AbstractIndentRenderer], None, None]:
    yield from list_all_subclasses(AbstractIndentRenderer, skip_abstract=True)  # type: ignore


class AbstractIndentRenderer(ABC):
    def __init__(self, view: sublime.View) -> None:
        self.view = view

    @final
    @classmethod
    def name(cls) -> str:
        """The nickname of this class. Converts "FooBarIndentRenderer" into "foo_bar" by default."""
        return camel_to_snake(remove_suffix(cls.__name__, "IndentRenderer"))

    @classmethod
    @abstractmethod
    def can_support(cls, style: Any) -> bool:
        """Check if this renderer can support the given style."""

    @abstractmethod
    def render(
        self,
        *,
        level_colors: Sequence[str],
        level_regions: Mapping[int, Sequence[sublime.Region]],
    ) -> None:
        """Render the view based on the points of each level."""


class BlockIndentRenderer(AbstractIndentRenderer):
    __ADD_REGION_FLAGS = sublime.DRAW_NO_OUTLINE | sublime.HIDE_ON_MINIMAP | sublime.NO_UNDO

    @classmethod
    def can_support(cls, style: Any) -> bool:
        return str(style) == LevelStyle.BLOCK

    def render(
        self,
        *,
        level_colors: Sequence[str],
        level_regions: Mapping[int, Sequence[sublime.Region]],
    ) -> None:
        for level, regions in level_regions.items():
            self.view.add_regions(
                get_regions_key(level),
                regions,
                scope=get_circular_nth(level_colors, level),
                flags=self.__ADD_REGION_FLAGS,
            )


class LineIndentRenderer(AbstractIndentRenderer):
    __ADD_REGION_FLAGS = sublime.DRAW_NO_OUTLINE | sublime.HIDE_ON_MINIMAP | sublime.NO_UNDO | sublime.DRAW_EMPTY

    @classmethod
    def can_support(cls, style: Any) -> bool:
        return str(style) == LevelStyle.LINE

    def render(
        self,
        *,
        level_colors: Sequence[str],
        level_regions: Mapping[int, Sequence[sublime.Region]],
    ) -> None:
        for level, regions in level_regions.items():
            self.view.add_regions(
                get_regions_key(level),
                tuple(sublime.Region(region.a) for region in regions),
                scope=get_circular_nth(level_colors, level),
                flags=self.__ADD_REGION_FLAGS,
            )
