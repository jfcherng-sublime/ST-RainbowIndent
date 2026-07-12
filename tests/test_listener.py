"""Tests for refresh_all_views — regression test for settings changes not reaching open views."""

from __future__ import annotations

import pytest

import plugin.listener as listener_module
import tests as sublime_mock
from plugin.constants import VIEW_KEY_USER_DISABLED
from plugin.listener import refresh_all_views


def _make_disabled_view() -> sublime_mock.View:
    """A view whose is_renderable_view() check short-circuits cheaply, avoiding unmocked ST APIs."""
    view = sublime_mock.View()
    view.settings().set(VIEW_KEY_USER_DISABLED, True)
    return view


class TestRefreshAllViews:
    def test_schedules_a_refresh_for_every_open_view(self) -> None:
        view_a = _make_disabled_view()
        view_b = _make_disabled_view()
        window = sublime_mock.Window([view_a, view_b])

        sublime_mock._windows.clear()
        sublime_mock._windows.append(window)
        sublime_mock.scheduled_calls.clear()
        try:
            refresh_all_views()
        finally:
            sublime_mock._windows.clear()

        assert len(sublime_mock.scheduled_calls) == 2

    def test_no_open_views_schedules_nothing(self) -> None:
        sublime_mock._windows.clear()
        sublime_mock.scheduled_calls.clear()

        refresh_all_views()

        assert sublime_mock.scheduled_calls == []

    def test_one_failing_view_does_not_stop_the_rest(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """One view raising (e.g. already closed, bad syntax) must not abort refreshing the others."""
        bad_view = sublime_mock.View()
        good_view = sublime_mock.View()
        processed: list[int] = []

        def fake_refresh_rendering(view: sublime_mock.View) -> None:
            if view is bad_view:
                raise RuntimeError("boom")
            processed.append(view.id())

        monkeypatch.setattr(listener_module, "refresh_rendering", fake_refresh_rendering)

        window = sublime_mock.Window([bad_view, good_view])
        sublime_mock._windows.clear()
        sublime_mock._windows.append(window)
        try:
            listener_module.refresh_all_views()  # must not raise despite bad_view
        finally:
            sublime_mock._windows.clear()

        assert processed == [good_view.id()]
