import inspect
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
    if not seq:
        raise ValueError("Cannot get circular nth from an empty sequence")
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

    Uses a generation counter because ``sublime.set_timeout_async`` callbacks
    cannot be cancelled once scheduled.
    """

    def decorator(func: T) -> T:
        _call_id: int = 0

        @wraps(func)
        def debounced(*args: Any, **kwargs: Any) -> None:
            nonlocal _call_id
            _call_id += 1
            captured_id = _call_id

            def call_function() -> Any:
                nonlocal _call_id
                if captured_id != _call_id:
                    return  # a newer call superseded this one
                return func(*args, **kwargs)

            sublime.set_timeout_async(call_function, int(time_s * 1000))

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
