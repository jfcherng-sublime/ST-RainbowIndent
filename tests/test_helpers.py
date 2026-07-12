"""Tests for is_renderable_view / is_transient_view / get_regions_key — previously untested (0% coverage)."""

from __future__ import annotations

import tests as sublime_mock
from plugin.constants import PLUGIN_NAME
from plugin.constants import VIEW_KEY_USER_DISABLED
from plugin.helpers import get_regions_key
from plugin.helpers import is_renderable_view
from plugin.helpers import is_transient_view
from plugin.settings import get_plugin_settings


def _reset_plugin_settings() -> None:
    settings = get_plugin_settings()
    settings.data.clear()


class TestIsRenderableView:
    def setup_method(self) -> None:
        _reset_plugin_settings()

    def teardown_method(self) -> None:
        # get_plugin_settings() is cached process-wide (mirroring real sublime.load_settings()),
        # so settings mutated here would otherwise leak into tests in other modules.
        _reset_plugin_settings()

    def test_explicit_disable_overrides_everything(self) -> None:
        view = sublime_mock.View(syntax_scope="source.python")
        view.settings().set(VIEW_KEY_USER_DISABLED, True)
        assert is_renderable_view(view) is False

    def test_explicit_enable_overrides_everything(self) -> None:
        """Even a view that would otherwise fail every other check must render when force-enabled."""
        view = sublime_mock.View(content="x" * 100, syntax_scope="text.plain")
        view.settings().set(VIEW_KEY_USER_DISABLED, False)
        get_plugin_settings().set("file_size_limit", 1)  # would normally exclude this view
        assert is_renderable_view(view) is True

    def test_default_selector_matches_source_scope(self) -> None:
        view = sublime_mock.View(syntax_scope="source.python")
        assert is_renderable_view(view) is True

    def test_selector_rejects_non_matching_scope(self) -> None:
        view = sublime_mock.View(syntax_scope="meta.other")
        get_plugin_settings().set("enabled_selector", "source | text | embedding")
        assert is_renderable_view(view) is False

    def test_transient_view_is_not_renderable(self) -> None:
        view = sublime_mock.View(syntax_scope="source.python")
        view._sheet = sublime_mock.Sheet(is_transient=True)
        assert is_renderable_view(view) is False

    def test_non_transient_sheet_does_not_block_rendering(self) -> None:
        view = sublime_mock.View(syntax_scope="source.python")
        view._sheet = sublime_mock.Sheet(is_transient=False)
        assert is_renderable_view(view) is True

    def test_element_view_is_not_renderable(self) -> None:
        """UI element views (find panel input, console, etc.) must never be rendered."""
        view = sublime_mock.View(syntax_scope="source.python")
        view.element = lambda: "find:input"  # type: ignore[method-assign]
        assert is_renderable_view(view) is False

    def test_invalid_view_is_not_renderable(self) -> None:
        view = sublime_mock.View(syntax_scope="source.python")
        view.is_valid = lambda: False  # type: ignore[method-assign]
        assert is_renderable_view(view) is False

    def test_file_size_over_limit_is_not_renderable(self) -> None:
        view = sublime_mock.View(content="x" * 100, syntax_scope="source.python")
        get_plugin_settings().set("file_size_limit", 10)
        assert is_renderable_view(view) is False

    def test_file_size_at_limit_is_renderable(self) -> None:
        """The limit is inclusive: a file exactly at the limit must still render."""
        view = sublime_mock.View(content="x" * 10, syntax_scope="source.python")
        get_plugin_settings().set("file_size_limit", 10)
        assert is_renderable_view(view) is True

    def test_negative_file_size_limit_disables_the_check(self) -> None:
        view = sublime_mock.View(content="x" * 10_000, syntax_scope="source.python")
        get_plugin_settings().set("file_size_limit", -1)
        assert is_renderable_view(view) is True


class TestIsTransientView:
    def test_no_sheet_is_not_transient(self) -> None:
        view = sublime_mock.View()
        assert is_transient_view(view) is False

    def test_transient_sheet(self) -> None:
        view = sublime_mock.View()
        view._sheet = sublime_mock.Sheet(is_transient=True)
        assert is_transient_view(view) is True

    def test_non_transient_sheet(self) -> None:
        view = sublime_mock.View()
        view._sheet = sublime_mock.Sheet(is_transient=False)
        assert is_transient_view(view) is False


class TestGetRegionsKey:
    def test_format(self) -> None:
        assert get_regions_key(0) == f"{PLUGIN_NAME}:level@0"
        assert get_regions_key(3) == f"{PLUGIN_NAME}:level@3"
