"""pytest configuration: patches the sublime module so plugin modules can import it."""

from __future__ import annotations

import sys

import tests  # the mock module

# Install mock sublime module immediately when conftest is loaded,
# before any test modules are collected.
sys.modules["sublime"] = tests

# Create a minimal sublime_plugin mock with the needed base classes
import types  # noqa: E402

_sublime_plugin = types.ModuleType("sublime_plugin")


class _ViewEventListener:
    """Mock for sublime_plugin.ViewEventListener."""

    def __init__(self) -> None:
        pass


class _TextCommand:
    """Mock for sublime_plugin.TextCommand."""

    def __init__(self, view: tests.View) -> None:
        self.view = view


_sublime_plugin.ViewEventListener = _ViewEventListener
_sublime_plugin.TextCommand = _TextCommand
sys.modules["sublime_plugin"] = _sublime_plugin
