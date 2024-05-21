from __future__ import annotations

import sublime
import sublime_plugin

from .helpers import is_renderable_view
from .settings import debounce_by_settings
from .view_manager import ViewManager


@debounce_by_settings
def refresh_rendering(view: sublime.View) -> None:
    vm = ViewManager.get_instance(view)
    if is_renderable_view(view):
        vm.render_view()
    else:
        vm.clear_view()


class RainbowIndentEventListener(sublime_plugin.ViewEventListener):
    def on_activated_async(self) -> None:
        refresh_rendering(self.view)

    def on_load_async(self) -> None:
        refresh_rendering(self.view)

    def on_modified_async(self) -> None:
        # @todo This can probably be optimized by only updating the changed regions
        #       with `sublime_plugin.TextChangeListener.on_text_changed_async()`.
        refresh_rendering(self.view)

    def on_reload_async(self) -> None:
        refresh_rendering(self.view)

    def on_revert_async(self) -> None:
        refresh_rendering(self.view)
