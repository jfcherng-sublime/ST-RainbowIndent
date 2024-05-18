from __future__ import annotations

import sublime
import sublime_plugin

from .constants import VIEW_KEY_USER_DISABLED
from .helpers import is_renderable_view
from .utils import configured_debounce
from .view_manager import ViewManager


@configured_debounce
def refresh_rendering(view: sublime.View) -> None:
    def _should_render() -> bool:
        # the user may explicitly enable/disable rendering for the current view
        if (is_disabled := v_settings.get(VIEW_KEY_USER_DISABLED)) is not None:
            return not is_disabled
        # activation by plugin's logics
        return is_renderable_view(view)

    v_settings = view.settings()
    vm = ViewManager.get_instance(view)
    if _should_render():
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
