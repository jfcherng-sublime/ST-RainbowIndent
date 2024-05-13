from __future__ import annotations

import sublime
import sublime_plugin

from .settings import get_file_size_limit
from .utils import configured_debounce
from .view_manager import ViewManager


class RainbowIndentEventListener(sublime_plugin.ViewEventListener):
    def on_activated_async(self) -> None:
        self._work(self.view)

    def on_load_async(self) -> None:
        self._work(self.view)

    def on_modified_async(self) -> None:
        # @todo This can probably be optimized by only updating the changed regions
        #       with `sublime_plugin.TextChangeListener.on_text_changed_async()`.
        self._work(self.view)

    def on_reload_async(self) -> None:
        self._work(self.view)

    def on_revert_async(self) -> None:
        self._work(self.view)

    @staticmethod
    @configured_debounce
    def _work(view: sublime.View) -> None:
        vm = ViewManager.get_instance(view)

        if 0 <= get_file_size_limit() < view.size():
            vm.clear_view()
            return

        vm.render_view()
