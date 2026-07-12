from typing import override

import sublime
import sublime_plugin

from ..constants import VIEW_KEY_USER_DISABLED
from ..listener import refresh_rendering


def set_activation_status(view: sublime.View, enabled: bool) -> None:
    """Sets the activation status of this plugin for the view."""
    view.settings().set(VIEW_KEY_USER_DISABLED, not enabled)
    refresh_rendering(view)


class RainbowIndentViewDisableCommand(sublime_plugin.TextCommand):
    """Disables rendering for the current view explicitly."""

    @override
    def is_checked(self) -> bool:
        return self.view.settings().get(VIEW_KEY_USER_DISABLED) is True

    @override
    def run(self, edit: sublime.Edit) -> None:
        set_activation_status(self.view, False)


class RainbowIndentViewEnableCommand(sublime_plugin.TextCommand):
    """Enables rendering for the current view explicitly."""

    @override
    def is_checked(self) -> bool:
        # Enabled by default (key unset) or explicitly enabled (key = False)
        return self.view.settings().get(VIEW_KEY_USER_DISABLED) is not True

    @override
    def run(self, edit: sublime.Edit) -> None:
        set_activation_status(self.view, True)


class RainbowIndentViewToggleCommand(sublime_plugin.TextCommand):
    """Toggles the rendering status of this plugin for the current view explicitly."""

    @override
    def run(self, edit: sublime.Edit) -> None:
        current_disabled = self.view.settings().get(VIEW_KEY_USER_DISABLED)
        # If the key is not set, the view is enabled by default -> toggle to disabled
        # If the key IS set, flip the current state.
        # `set_activation_status(view, enabled)` stores `not enabled`, so to flip
        # `current_disabled` we must pass `current_disabled` itself as `enabled`,
        # NOT `not current_disabled` (that cancels out to a no-op every time).
        if current_disabled is None:
            set_activation_status(self.view, False)
        else:
            set_activation_status(self.view, current_disabled)
