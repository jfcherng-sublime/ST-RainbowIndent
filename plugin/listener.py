from __future__ import annotations

from collections import defaultdict
from itertools import chain
from typing import Generator, Iterable

import sublime
import sublime_plugin

from .data_types import TUPLE_REGION
from .helpers import get_regions_key, is_renderable_view
from .settings import debounce_by_settings, get_level_colors
from .utils import get_circular_nth
from .view_manager import ViewManager, calcualte_level_regions


@debounce_by_settings
def refresh_rendering(view: sublime.View) -> None:
    vm = ViewManager.get_instance(view)
    if is_renderable_view(view):
        vm.render_view()
    else:
        vm.clear_view()


def list_changed_line_regions(
    view: sublime.View,
    changes: Iterable[sublime.TextChange],
) -> Generator[sublime.Region, None, None]:
    """
    Assuming `changes` are sorted in ascending order.

    ```py
    changes = [
        TextChange(
            HistoricPosition(pt=45, row=2, col=9, col_utf16=9, col_utf8=9),
            HistoricPosition(pt=45, row=2, col=9, col_utf16=9, col_utf8=9),
            len_utf16=86,
            len_utf8=86,
            str="inserted_text",  # insertion
        ),
        TextChange(
            HistoricPosition(pt=392, row=16, col=18, col_utf16=18, col_utf8=18),
            HistoricPosition(pt=591, row=19, col=22, col_utf16=22, col_utf8=22),
            len_utf16=199,
            len_utf8=199,
            str="",  # deletion
        ),
        TextChange(
            HistoricPosition(pt=897, row=31, col=14, col_utf16=14, col_utf8=14),
            HistoricPosition(pt=1089, row=34, col=0, col_utf16=0, col_utf8=0),
            len_utf16=192,
            len_utf8=192,
            str="",  # deletion
        ),
    ]
    ```
    """

    def _list_changed_line_ranges(changes: Iterable[sublime.TextChange]) -> Generator[TUPLE_REGION, None, None]:
        """
        Lists the changed ranges for the current after modified view.
        Assuming `changes` are sorted in ascending order.
        """
        pt_bias = 0
        for change in changes:
            base_pt = change.a.pt + pt_bias
            # addition
            if str_len := len(change.str):
                # after addition change, the region of the added text is interested
                yield (base_pt, base_pt + str_len)
                pt_bias += str_len
            # deletion
            else:
                # after deletion change, only the starting point is interested
                yield (base_pt, base_pt)
                pt_bias -= change.b.pt - change.a.pt

    def _list_merged_regions(regions: Iterable[sublime.Region]) -> Generator[sublime.Region, None, None]:
        """
        Lists merged `regions` because they may be overlapping or neighboring.
        Assuming `regions` are sorted in ascending order.
        """
        # `sublime.Region(-1, -2)` is just a non-empty dummy
        regions_it = chain(regions, (sublime.Region(-1, -2),))
        prev_region = next(regions_it)
        while curr_region := next(regions_it, None):
            if prev_region.a <= curr_region.a <= prev_region.b:
                prev_region = sublime.Region(prev_region.a, curr_region.b)
            else:
                yield prev_region
                prev_region = curr_region

    changed_regions_it = (view.full_line(sublime.Region(*r)) for r in _list_changed_line_ranges(changes))
    yield from _list_merged_regions(changed_regions_it)


class RainbowIndentTextChangeListener(sublime_plugin.TextChangeListener):
    def on_text_changed(self, changes: list[sublime.TextChange]) -> None:
        # note that `changes` are guranteed sorted from the end of the view to the begin of the view
        if not self.buffer:
            return
        # no way to know the text change is triggered by which view...?
        view = self.buffer.primary_view()

        if not is_renderable_view(view):
            return

        print(f"{changes = }")

        # calculate changed row ranges (using exclusive right boundary)
        changed_line_regions = list(list_changed_line_regions(view, reversed(changes)))

        print(f"{changed_line_regions = }")

        vm = ViewManager.get_instance(view)

        # new level points due to `changes`
        level_colors = get_level_colors()

        extra_level_regions = calcualte_level_regions(view, regions=changed_line_regions)
        old_level_regions = defaultdict(list, vm.list_indent_level_regions())

        max_level = max(chain(extra_level_regions.keys(), old_level_regions.keys()), default=-1)

        for level in range(max_level + 1):
            final_level_regions = [
                level_region
                for level_region in old_level_regions[level]
                # regions which are not required to be updated
                if not any(
                    level_region.intersects(changed_line_region) or level_region in changed_line_region
                    for changed_line_region in changed_line_regions
                )
            ]
            final_level_regions.extend(extra_level_regions[level])

            view.add_regions(
                get_regions_key(level),
                final_level_regions,
                scope=get_circular_nth(level_colors, level),
            )


class RainbowIndentEventListener(sublime_plugin.ViewEventListener):
    def on_activated_async(self) -> None:
        refresh_rendering(self.view)

    def on_load_async(self) -> None:
        refresh_rendering(self.view)

    def on_modified_async(self) -> None:
        # @todo This can probably be optimized by only updating the changed regions
        #       with `sublime_plugin.TextChangeListener.on_text_changed_async()`.
        # refresh_rendering(self.view)
        pass

    def on_reload_async(self) -> None:
        refresh_rendering(self.view)

    def on_revert_async(self) -> None:
        refresh_rendering(self.view)
