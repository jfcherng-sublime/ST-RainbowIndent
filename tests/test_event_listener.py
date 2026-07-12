"""Tests for RainbowIndentEventListener — event handler wiring to refresh_rendering()."""

from __future__ import annotations

import pytest

import plugin.listener as listener_module
import tests as sublime_mock
from plugin.listener import RainbowIndentEventListener
from plugin.view_manager import ViewManager


class TestRainbowIndentEventListener:
    def test_on_load_async_triggers_refresh(self, monkeypatch: pytest.MonkeyPatch) -> None:
        view = sublime_mock.View()
        calls: list[sublime_mock.View] = []
        monkeypatch.setattr(listener_module, "refresh_rendering", calls.append)

        RainbowIndentEventListener(view).on_load_async()

        assert calls == [view]

    def test_on_modified_async_triggers_refresh(self, monkeypatch: pytest.MonkeyPatch) -> None:
        view = sublime_mock.View()
        calls: list[sublime_mock.View] = []
        monkeypatch.setattr(listener_module, "refresh_rendering", calls.append)

        RainbowIndentEventListener(view).on_modified_async()

        assert calls == [view]

    def test_on_reload_async_triggers_refresh(self, monkeypatch: pytest.MonkeyPatch) -> None:
        view = sublime_mock.View()
        calls: list[sublime_mock.View] = []
        monkeypatch.setattr(listener_module, "refresh_rendering", calls.append)

        RainbowIndentEventListener(view).on_reload_async()

        assert calls == [view]

    def test_on_revert_async_triggers_refresh(self, monkeypatch: pytest.MonkeyPatch) -> None:
        view = sublime_mock.View()
        calls: list[sublime_mock.View] = []
        monkeypatch.setattr(listener_module, "refresh_rendering", calls.append)

        RainbowIndentEventListener(view).on_revert_async()

        assert calls == [view]

    def test_on_activated_async_refreshes_a_view_seen_for_the_first_time(self, monkeypatch: pytest.MonkeyPatch) -> None:
        view = sublime_mock.View()  # fresh ViewManager -> last_change_count == -1
        calls: list[sublime_mock.View] = []
        monkeypatch.setattr(listener_module, "refresh_rendering", calls.append)

        RainbowIndentEventListener(view).on_activated_async()

        assert calls == [view]

    def test_on_activated_async_skips_refresh_when_unchanged_since_last_render(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        view = sublime_mock.View()
        ViewManager(view).last_change_count = view.change_count()  # already rendered, unchanged
        calls: list[sublime_mock.View] = []
        monkeypatch.setattr(listener_module, "refresh_rendering", calls.append)

        RainbowIndentEventListener(view).on_activated_async()

        assert calls == []
