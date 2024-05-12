from __future__ import annotations

import weakref
from collections import defaultdict

import sublime

from .data_types import POINT, IndentInfo, LevelStyle
from .helpers import get_regions_key, get_view_indent
from .indent_renderer import AbstractIndentRenderer, find_indent_renderer
from .settings import get_level_style


def calcualte_level_pts(view: sublime.View, *, indent_info: IndentInfo) -> dict[int, list[POINT]]:
    """
    Calculate the begin point of indents for each level.

    :param      view:         The view.
    :param      indent_info:  The indent information.

    :returns:   A dictionary whose keys are the indent level and values are the begin point of level indents.
    """
    level_pts: defaultdict[int, list[POINT]] = defaultdict(list)
    for region in view.find_all(indent_info.indent_pattern):
        for level in range(region.size() // indent_info.indent_length):
            level_pts[level].append(region.a + level * indent_info.indent_length)
    return level_pts


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
        self.max_level = -1

    def render_view(self) -> None:
        indent_info = get_view_indent(self.view)
        renderer = self._get_renderer(get_level_style())

        level_pts = calcualte_level_pts(self.view, indent_info=indent_info)
        self.max_level = max(level_pts.keys(), default=-1)

        renderer.render(level_pts=level_pts, indent_info=indent_info)

    def _get_renderer(self, level_style: LevelStyle) -> AbstractIndentRenderer:
        if not (renderer_cls := find_indent_renderer(level_style)):
            raise ValueError(f"Unknown level style: {level_style}")
        return renderer_cls(self.view)
