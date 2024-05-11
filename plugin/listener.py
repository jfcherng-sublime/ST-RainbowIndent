from __future__ import annotations

import sublime
import sublime_plugin

from .utils import configured_debounce
from .view_manager import ViewManager


class RainbowIndent(sublime_plugin.ViewEventListener):
    def on_activated_async(self) -> None:
        self._work(self.view)

    def on_load_async(self) -> None:
        self._work(self.view)

    def on_modified_async(self) -> None:
        self._work(self.view)

    def on_revert_async(self) -> None:
        self._work(self.view)

    @staticmethod
    @configured_debounce
    def _work(view: sublime.View) -> None:
        vm = ViewManager.get_instance(view)
        vm.render_view()
