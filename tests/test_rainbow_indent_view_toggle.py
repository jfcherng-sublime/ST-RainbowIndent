"""Tests for the Disable/Enable/Toggle commands — regression test for the toggle no-op bug.

Toggling repeatedly used to get stuck after the first call: `set_activation_status(view, not
current_disabled)` cancels out to `enabled = current_disabled`, a no-op. Previously untested
(0% coverage), which is exactly how that bug slipped through a prior "fix the toggle" commit.
"""

from __future__ import annotations

import tests as sublime_mock
from plugin.commands.rainbow_indent_view_toggle import RainbowIndentViewDisableCommand
from plugin.commands.rainbow_indent_view_toggle import RainbowIndentViewEnableCommand
from plugin.commands.rainbow_indent_view_toggle import RainbowIndentViewToggleCommand
from plugin.constants import VIEW_KEY_USER_DISABLED


class TestToggleCommand:
    def test_repeated_toggles_alternate_disabled_and_enabled(self) -> None:
        view = sublime_mock.View()
        cmd = RainbowIndentViewToggleCommand(view)

        assert view.settings().get(VIEW_KEY_USER_DISABLED) is None

        cmd.run(None)
        assert view.settings().get(VIEW_KEY_USER_DISABLED) is True

        cmd.run(None)
        assert view.settings().get(VIEW_KEY_USER_DISABLED) is False

        cmd.run(None)
        assert view.settings().get(VIEW_KEY_USER_DISABLED) is True

        cmd.run(None)
        assert view.settings().get(VIEW_KEY_USER_DISABLED) is False

    def test_toggle_from_explicitly_enabled_disables(self) -> None:
        view = sublime_mock.View()
        view.settings().set(VIEW_KEY_USER_DISABLED, False)

        RainbowIndentViewToggleCommand(view).run(None)

        assert view.settings().get(VIEW_KEY_USER_DISABLED) is True

    def test_toggle_from_explicitly_disabled_enables(self) -> None:
        view = sublime_mock.View()
        view.settings().set(VIEW_KEY_USER_DISABLED, True)

        RainbowIndentViewToggleCommand(view).run(None)

        assert view.settings().get(VIEW_KEY_USER_DISABLED) is False


class TestDisableCommand:
    def test_run_disables(self) -> None:
        view = sublime_mock.View()
        RainbowIndentViewDisableCommand(view).run(None)
        assert view.settings().get(VIEW_KEY_USER_DISABLED) is True

    def test_is_checked_reflects_disabled_state(self) -> None:
        view = sublime_mock.View()
        cmd = RainbowIndentViewDisableCommand(view)
        assert cmd.is_checked() is False  # unset -> not disabled

        view.settings().set(VIEW_KEY_USER_DISABLED, True)
        assert cmd.is_checked() is True

        view.settings().set(VIEW_KEY_USER_DISABLED, False)
        assert cmd.is_checked() is False


class TestEnableCommand:
    def test_run_enables(self) -> None:
        view = sublime_mock.View()
        view.settings().set(VIEW_KEY_USER_DISABLED, True)

        RainbowIndentViewEnableCommand(view).run(None)

        assert view.settings().get(VIEW_KEY_USER_DISABLED) is False

    def test_is_checked_reflects_enabled_by_default(self) -> None:
        view = sublime_mock.View()
        cmd = RainbowIndentViewEnableCommand(view)
        assert cmd.is_checked() is True  # unset -> enabled by default

        view.settings().set(VIEW_KEY_USER_DISABLED, True)
        assert cmd.is_checked() is False

        view.settings().set(VIEW_KEY_USER_DISABLED, False)
        assert cmd.is_checked() is True
