import inspect
import threading
from collections.abc import Callable
from collections.abc import Generator
from collections.abc import Iterable
from collections.abc import Sequence
from functools import wraps
from typing import Any
from typing import cast

import sublime


def get_circular_nth[T](seq: Sequence[T], n: int) -> T:
    """Gets the nth element in a sequence circularly."""
    return seq[n % len(seq)]


def list_all_subclasses[T](root: type[T], skip_abstract: bool = False, skip_self: bool = False) -> Generator[type[T]]:
    """Gets all sub-classes of the root class."""
    if not skip_self and not (skip_abstract and inspect.isabstract(root)):
        yield root
    for leaf in root.__subclasses__():
        yield from list_all_subclasses(leaf, skip_self=False, skip_abstract=skip_abstract)


def camel_to_snake(s: str) -> str:
    """Converts "CamelCase" to "snake_case"."""
    return "".join(f"_{c}" if c.isupper() else c for c in s).strip("_").lower()


def snake_to_camel(s: str, *, upper_first: bool = True) -> str:
    """Converts "snake_case" to "CamelCase"."""
    first, *others = s.split("_")
    return (first.title() if upper_first else first.lower()) + "".join(map(str.title, others))


def debounce[T: Callable](time_s: float = 0.3) -> Callable[[T], T]:
    """
    Debounce a function so that it's called after `time_s` seconds.
    If it's called multiple times in the time frame, it will only run the last call.

    Taken and modified from https://github.com/salesforce/decorator-operations
    """

    def decorator(func: T) -> T:
        _timer: threading.Timer | None = None

        @wraps(func)
        def debounced(*args: Any, **kwargs: Any) -> None:
            nonlocal _timer
            if _timer is not None:
                _timer.cancel()

            def call_function() -> Any:
                nonlocal _timer
                _timer = None
                return func(*args, **kwargs)

            _timer = threading.Timer(time_s, call_function)
            _timer.start()

        return cast(T, debounced)

    return decorator


def list_views(
    windows: Iterable[sublime.Window] | None = None,
    *,
    include_transient: bool = False,
) -> Generator[sublime.View]:
    """List all views in `windows`. If `windows` is `None`, then all windows."""
    if windows is None:
        windows = sublime.windows()

    yield from (view for window in windows for view in window.views(include_transient=include_transient))
