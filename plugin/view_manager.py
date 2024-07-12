from __future__ import annotations

import weakref
from collections import defaultdict
from typing import Iterable, Sequence

import sublime

from .data_types import INDENT_LEVEL, IndentInfo, LevelStyle
from .helpers import get_regions_key
from .indent_renderer import AbstractIndentRenderer, find_indent_renderer
from .settings import get_level_colors, get_level_style


def calcualte_level_regions(
    view: sublime.View,
    *,
    indent_info: IndentInfo | None = None,
    regions: Sequence[sublime.Region] | None = None,
) -> defaultdict[INDENT_LEVEL, list[sublime.Region]]:
    """
    Calculates regions of indents for each level.

    :param      view:         The view.
    :param      indent_info:  The indent information.
                              If `None`, it will be deduced from the `view`.
    :param      regions:      The interested regions of the `view`.
                              They should be whole lines, non-overlapping and sorted in ascending order beforehand.
                              If `None`, the whole region of the `view` will be used.

    :returns:   A dictionary whose keys are the indent level (started from `0`) and values are regions of level indents.
    """
    if indent_info is None:
        indent_info = IndentInfo.from_view(view)
    if regions is None:
        regions = (sublime.Region(0, view.size()),)

    whole_content = view.substr(sublime.Region(0, view.size()))
    level_regions: defaultdict[INDENT_LEVEL, list[sublime.Region]] = defaultdict(list)
    for region in regions:
        for m in indent_info.indent_pattern_compiled.finditer(whole_content, *region.to_tuple()):
            for level, level_pt in enumerate(range(*m.span(), indent_info.indent_length)):
                level_regions[level].append(sublime.Region(level_pt, level_pt + indent_info.indent_length))
    return level_regions


class ViewManager:
    __instances: weakref.WeakKeyDictionary[sublime.View, ViewManager] = weakref.WeakKeyDictionary()
    """A map which maps managed `view` to its manager."""

    def __init__(self, view: sublime.View, *, _from_init: bool = True) -> None:
        if _from_init:
            raise ValueError("Use `get_instance()` instead.")

        self.view = view
        """The managed `view`."""
        self.max_level = -1
        """The max indent level of the managed `view`."""

    @classmethod
    def get_instance(cls, view: sublime.View) -> ViewManager:
        """Gets the manager instance of `view`. (per-view singleton pattern)"""
        if view not in cls.__instances:
            cls.__instances[view] = cls(view, _from_init=False)
        return cls.__instances[view]

    @classmethod
    def clear_all_views(cls, views: Iterable[sublime.View] | None = None) -> None:
        """Clears managed `views`. If `views` is `None`, clear all managed `views`."""
        if views is None:
            views = cls.__instances.keys()  # all managed views

        for view in views:
            if vm := cls.__instances.get(view):
                vm.clear_view()

    def clear_view(self) -> None:
        """Clears the managed `views`."""
        for level in range(self.max_level + 1):
            self.view.erase_regions(get_regions_key(level))
        self.max_level = -1

    def render_view(self) -> None:
        """Renders the managed `view`."""
        renderer = self._get_renderer(get_level_style())

        level_colors = get_level_colors()
        level_regions = calcualte_level_regions(self.view)
        self.max_level = max(level_regions.keys(), default=-1)

        renderer.render(level_colors=level_colors, level_regions=level_regions)

    def _get_renderer(self, level_style: LevelStyle) -> AbstractIndentRenderer:
        if not (renderer_cls := find_indent_renderer(level_style)):
            raise ValueError(f"Unknown level style: {level_style}")
        return renderer_cls(self.view)
