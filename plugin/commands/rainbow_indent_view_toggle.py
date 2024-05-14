from __future__ import annotations

import sublime
import sublime_plugin

from ..constants import PLUGIN_NAME, VIEW_KEY_USER_DISABLED
from ..listener import refresh_rendering


def set_activation_status(view: sublime.View, enabled: bool) -> None:
    """Sets the activation status of this plugin for the view."""
    view.settings().set(VIEW_KEY_USER_DISABLED, not enabled)
    view.set_status(PLUGIN_NAME, f"{PLUGIN_NAME}: {'Enabled' if enabled else 'Disabled'}")
    refresh_rendering(view)


class RainbowIndentViewDisableCommand(sublime_plugin.TextCommand):
    """Disables this plugin for the current view."""

    def run(self, edit: sublime.Edit) -> None:
        set_activation_status(self.view, False)


class RainbowIndentViewEnableCommand(sublime_plugin.TextCommand):
    """Enables this plugin for the current view."""

    def run(self, edit: sublime.Edit) -> None:
        set_activation_status(self.view, True)


class RainbowIndentViewToggleCommand(sublime_plugin.TextCommand):
    """Toggles the activation status of this plugin for the current view."""

    def run(self, edit: sublime.Edit) -> None:
        set_activation_status(self.view, self.view.settings().get(VIEW_KEY_USER_DISABLED, False))
