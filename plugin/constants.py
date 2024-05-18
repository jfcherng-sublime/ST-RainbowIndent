from __future__ import annotations

assert __package__

PLUGIN_NAME = __package__.partition(".")[0]

LEVEL_COLORS_FALLBACK = [
    "region.redish",
    "region.orangish",
    "region.yellowish",
    "region.greenish",
    "region.cyanish",
    "region.bluish",
    "region.purplish",
    "region.pinkish",
]
"""
The default scopes for coloring indents.

@see https://www.sublimetext.com/docs/api_reference.html#sublime.View.add_regions
"""

VIEW_KEY_USER_DISABLED = f"{PLUGIN_NAME}.user_disabled"
"""The view setting key to disable the plugin for the view."""
