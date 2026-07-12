"""Tests for ViewManager — regression test for the stale-region-on-shrink bug."""

from __future__ import annotations

from sublime import View

from plugin.helpers import get_regions_key
from plugin.view_manager import ViewManager


def _make_view(content: str) -> View:
    view = View(content=content)
    view.settings().set("tab_size", 4)
    view.settings().set("translate_tabs_to_spaces", True)
    return view


class TestViewManagerRenderView:
    def test_render_erases_levels_that_no_longer_exist(self) -> None:
        """Dedenting the buffer must erase the deeper levels' stale regions, not just leave them."""
        view = _make_view("            deep\n")  # 12 spaces -> levels 0, 1, 2
        vm = ViewManager(view)

        vm.render_view()
        assert vm.max_level == 2
        assert get_regions_key(0) in view.regions
        assert get_regions_key(1) in view.regions
        assert get_regions_key(2) in view.regions

        view.set_content("    shallow\n")  # 4 spaces -> level 0 only
        vm.render_view()

        assert vm.max_level == 0
        assert get_regions_key(0) in view.regions
        assert get_regions_key(1) not in view.regions
        assert get_regions_key(2) not in view.regions

    def test_render_with_no_indent_erases_all_previous_levels(self) -> None:
        view = _make_view("        deep\n")  # 8 spaces -> levels 0, 1
        vm = ViewManager(view)

        vm.render_view()
        assert vm.max_level == 1

        view.set_content("no indent at all\n")
        vm.render_view()

        assert vm.max_level == -1
        assert get_regions_key(0) not in view.regions
        assert get_regions_key(1) not in view.regions
