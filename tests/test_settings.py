"""Tests for debounce_by_settings — regression tests for the debounce coalescing bugs."""

from __future__ import annotations

import tests as sublime_mock
from plugin.settings import debounce_by_settings


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
