import sublime
import sublime_plugin

from .helpers import is_renderable_view
from .log import log_error
from .settings import debounce_by_settings
from .utils import list_views
from .view_manager import ViewManager


@debounce_by_settings
def refresh_rendering(view: sublime.View) -> None:
    vm = ViewManager(view)
    if is_renderable_view(view):
        vm.render_view()
    else:
        vm.clear_view()


def refresh_all_views() -> None:
    """Refreshes rendering for all currently open views, e.g., after a plugin setting changes."""
    for view in list_views():
        try:
            refresh_rendering(view)
        except Exception:
            # e.g., with debounce disabled, refresh_rendering() runs inline; one bad view
            # (already closed, invalid syntax, etc.) shouldn't stop the rest from refreshing.
            log_error(f"Failed to refresh rendering for view {view.id()}")


class RainbowIndentEventListener(sublime_plugin.ViewEventListener):
    def on_activated_async(self) -> None:
        # Skip re-render if the view content hasn't changed since last activation
        vm = ViewManager(self.view)
        if vm.last_change_count != self.view.change_count():
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
