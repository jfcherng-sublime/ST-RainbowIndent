"""Tests for ViewManager — regression test for the stale-region-on-shrink bug."""

from __future__ import annotations

import pytest
from sublime import View

import plugin.view_manager as view_manager_module
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

    def test_render_view_swallows_exceptions_and_logs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        view = _make_view("    a\n")
        vm = ViewManager(view)

        def boom(*args: object, **kwargs: object) -> None:
            raise RuntimeError("boom")

        monkeypatch.setattr(view_manager_module, "calculate_level_regions", boom)

        vm.render_view()  # must not raise

        assert vm.last_change_count == -1  # unchanged, since the render never completed


class TestViewManagerClearView:
    def test_clear_view_erases_all_rendered_levels(self) -> None:
        view = _make_view("            deep\n")  # 12 spaces -> levels 0, 1, 2
        vm = ViewManager(view)
        vm.render_view()
        assert vm.max_level == 2

        vm.clear_view()

        assert vm.max_level == -1
        assert get_regions_key(0) not in view.regions
        assert get_regions_key(1) not in view.regions
        assert get_regions_key(2) not in view.regions

    def test_clear_view_on_fresh_manager_is_a_no_op(self) -> None:
        view = _make_view("")
        vm = ViewManager(view)

        vm.clear_view()  # must not raise

        assert vm.max_level == -1

    def test_erase_levels_isolates_a_failing_level(self) -> None:
        """One level's erase_regions() raising must not stop the others from being erased."""
        view = _make_view("            deep\n")  # levels 0, 1, 2
        vm = ViewManager(view)
        vm.render_view()

        original_erase_regions = view.erase_regions

        def failing_erase_regions(key: str) -> None:
            if key == get_regions_key(1):
                raise RuntimeError("boom")
            original_erase_regions(key)

        view.erase_regions = failing_erase_regions  # type: ignore[method-assign]

        vm.clear_view()  # must not raise despite level 1 failing

        assert get_regions_key(0) not in view.regions
        assert get_regions_key(2) not in view.regions


class TestViewManagerClearAllViews:
    def test_clears_all_managed_views_by_default(self) -> None:
        view_a = _make_view("    a\n")
        view_b = _make_view("        b\n")
        vm_a = ViewManager(view_a)
        vm_b = ViewManager(view_b)
        vm_a.render_view()
        vm_b.render_view()

        ViewManager.clear_all_views()

        assert vm_a.max_level == -1
        assert vm_b.max_level == -1
        assert view_a.regions == {}
        assert view_b.regions == {}

    def test_clears_only_the_specified_views(self) -> None:
        view_a = _make_view("    a\n")
        view_b = _make_view("        b\n")
        vm_a = ViewManager(view_a)
        vm_b = ViewManager(view_b)
        vm_a.render_view()
        vm_b.render_view()

        ViewManager.clear_all_views([view_a])

        assert vm_a.max_level == -1
        assert vm_b.max_level == 1  # untouched


class TestViewManagerSingleton:
    def test_returns_the_same_instance_for_the_same_view(self) -> None:
        view = _make_view("")
        vm1 = ViewManager(view)
        vm1.max_level = 5  # simulate state accumulated from a prior render

        vm2 = ViewManager(view)

        assert vm1 is vm2
        assert vm2.max_level == 5  # re-construction must not reset existing state

    def test_different_views_get_different_instances(self) -> None:
        view_a = _make_view("")
        view_b = _make_view("")

        assert ViewManager(view_a) is not ViewManager(view_b)


class TestViewManagerGetRenderer:
    def test_unknown_style_raises_value_error(self) -> None:
        view = _make_view("")
        vm = ViewManager(view)

        with pytest.raises(ValueError, match="Unknown level style"):
            vm._get_renderer("not-a-real-style")  # type: ignore[arg-type]
