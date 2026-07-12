"""Tests for plugin_loaded/plugin_unloaded — regression test for settings changes not reaching open views."""

from __future__ import annotations

import plugin
import tests as sublime_mock
from plugin.constants import PLUGIN_NAME
from plugin.constants import VIEW_KEY_USER_DISABLED
from plugin.settings import get_plugin_settings


def _make_disabled_view() -> sublime_mock.View:
    """A view whose is_renderable_view() check short-circuits cheaply, avoiding unmocked ST APIs."""
    view = sublime_mock.View()
    view.settings().set(VIEW_KEY_USER_DISABLED, True)
    return view


class TestPluginLoadedUnloaded:
    def test_plugin_loaded_refreshes_all_views_when_settings_change(self) -> None:
        view = _make_disabled_view()
        window = sublime_mock.Window([view])

        sublime_mock._windows.clear()
        sublime_mock._windows.append(window)
        sublime_mock.scheduled_calls.clear()
        try:
            plugin.plugin_loaded()

            settings = get_plugin_settings()
            assert PLUGIN_NAME in settings.on_change_callbacks

            # Simulate a user editing a plugin setting, e.g. "level_colors".
            settings.on_change_callbacks[PLUGIN_NAME]()

            assert len(sublime_mock.scheduled_calls) == 1
        finally:
            plugin.plugin_unloaded()
            sublime_mock._windows.clear()

    def test_plugin_unloaded_clears_the_settings_change_callback(self) -> None:
        plugin.plugin_loaded()
        settings = get_plugin_settings()
        assert PLUGIN_NAME in settings.on_change_callbacks

        plugin.plugin_unloaded()

        assert PLUGIN_NAME not in settings.on_change_callbacks
