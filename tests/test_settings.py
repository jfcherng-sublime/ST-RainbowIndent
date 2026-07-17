"""Tests for debounce_by_settings — regression tests for the debounce coalescing bugs."""

from __future__ import annotations

import pytest

import tests as sublime_mock
from plugin.data_types import LevelStyle
from plugin.settings import debounce_by_settings
from plugin.settings import get_debounce_time
from plugin.settings import get_enabled_selector
from plugin.settings import get_file_size_limit
from plugin.settings import get_level_colors
from plugin.settings import get_level_style
from plugin.settings import get_plugin_settings


def _reset_plugin_settings() -> None:
    get_plugin_settings().data.clear()


class TestDebounceBySettings:
    def test_coalesces_rapid_calls_for_the_same_subject(self) -> None:
        """Multiple calls for the same subject (e.g. the same view) collapse into the last one."""
        calls: list[int] = []
        view = sublime_mock.View()

        @debounce_by_settings
        def record(v: sublime_mock.View, n: int) -> None:
            calls.append(n)

        sublime_mock.scheduled_calls.clear()

        record(view, 1)
        record(view, 2)
        record(view, 3)

        # Nothing runs synchronously; every call is deferred via set_timeout_async.
        assert calls == []
        assert len(sublime_mock.scheduled_calls) == 3

        # Simulate every pending timer firing, in scheduling order.
        for callback, _timeout_ms in sublime_mock.scheduled_calls:
            callback()

        # Only the most recent call for that subject should have actually executed.
        assert calls == [3]

    def test_does_not_cancel_a_pending_call_for_a_different_subject(self) -> None:
        """A call for one view must not cancel a still-pending call for a different view."""
        calls: list[str] = []
        view_a = sublime_mock.View()
        view_b = sublime_mock.View()

        @debounce_by_settings
        def record(v: sublime_mock.View, tag: str) -> None:
            calls.append(tag)

        sublime_mock.scheduled_calls.clear()

        record(view_a, "a")
        record(view_b, "b")  # different subject; must not supersede view_a's pending call

        for callback, _timeout_ms in sublime_mock.scheduled_calls:
            callback()

        assert sorted(calls) == ["a", "b"]

    def test_independent_functions_do_not_share_state(self) -> None:
        """Each decorated function must keep its own generation counters."""
        calls_a: list[int] = []
        calls_b: list[int] = []
        view = sublime_mock.View()

        @debounce_by_settings
        def record_a(v: sublime_mock.View, n: int) -> None:
            calls_a.append(n)

        @debounce_by_settings
        def record_b(v: sublime_mock.View, n: int) -> None:
            calls_b.append(n)

        sublime_mock.scheduled_calls.clear()

        record_a(view, 1)
        record_b(view, 1)

        for callback, _timeout_ms in sublime_mock.scheduled_calls:
            callback()

        assert calls_a == [1]
        assert calls_b == [1]

    def test_debounce_disabled_runs_synchronously(self) -> None:
        """A debounce of 0 must bypass scheduling entirely and run inline."""
        calls: list[int] = []
        view = sublime_mock.View()

        @debounce_by_settings
        def record(v: sublime_mock.View, n: int) -> None:
            calls.append(n)

        _reset_plugin_settings()
        get_plugin_settings().set("debounce", 0)
        sublime_mock.scheduled_calls.clear()
        try:
            record(view, 1)
        finally:
            _reset_plugin_settings()

        assert calls == [1]
        assert sublime_mock.scheduled_calls == []


class TestSettingsGetters:
    def setup_method(self) -> None:
        _reset_plugin_settings()

    def teardown_method(self) -> None:
        # get_plugin_settings() is cached process-wide, so leftover values here
        # would otherwise leak into tests in other modules.
        _reset_plugin_settings()

    def test_get_debounce_time_default(self) -> None:
        assert get_debounce_time() == pytest.approx(0.2)

    def test_get_debounce_time_custom(self) -> None:
        get_plugin_settings().set("debounce", 1.5)
        assert get_debounce_time() == pytest.approx(1.5)

    def test_get_enabled_selector_default(self) -> None:
        assert get_enabled_selector() == ""

    def test_get_level_colors_default_falls_back(self) -> None:
        from plugin.constants import LEVEL_COLORS_FALLBACK

        assert get_level_colors() == LEVEL_COLORS_FALLBACK

    def test_get_level_colors_custom(self) -> None:
        get_plugin_settings().set("level_colors", ["region.redish", "region.greenish"])
        assert get_level_colors() == ["region.redish", "region.greenish"]

    def test_get_level_style_default(self) -> None:
        assert get_level_style() is LevelStyle.BLOCK

    def test_get_level_style_line(self) -> None:
        get_plugin_settings().set("level_style", "line")
        assert get_level_style() is LevelStyle.LINE

    def test_get_level_style_invalid_falls_back_to_block(self) -> None:
        get_plugin_settings().set("level_style", "not-a-real-style")
        assert get_level_style() is LevelStyle.BLOCK

    def test_get_file_size_limit_default(self) -> None:
        assert get_file_size_limit() == -1

    def test_get_file_size_limit_custom(self) -> None:
        get_plugin_settings().set("file_size_limit", 1024)
        assert get_file_size_limit() == 1024
