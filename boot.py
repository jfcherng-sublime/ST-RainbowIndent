def reload_plugin() -> None:
    import sys

    # remove all previously loaded plugin modules
    prefix = f"{__package__}."
    for module_name in [m for m in sys.modules if m.startswith(prefix) and m != __name__]:
        del sys.modules[module_name]


reload_plugin()

from .plugin import *  # noqa: F403
