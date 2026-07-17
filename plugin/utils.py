import inspect
import weakref
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


def debounce[T: Callable](time_s: float | Callable[[], float] = 0.3) -> Callable[[T], T]:
    """
    Debounce a function so that it's called after `time_s` seconds.
    If it's called multiple times for the same first argument (e.g., the same `sublime.View`)
    within the time frame, only the last call for that argument will run. Calls for a
    different first argument don't affect each other, so debouncing one view's rendering
    can't starve another view's pending render.

    `time_s` may also be a zero-argument callable, re-evaluated on every call, so that
    live setting changes take effect without re-decorating `func`.

    Uses a per-subject generation counter because ``sublime.set_timeout_async`` callbacks
    cannot be cancelled once scheduled.
    """

    def decorator(func: T) -> T:
        call_ids: weakref.WeakKeyDictionary[Any, int] = weakref.WeakKeyDictionary()

        @wraps(func)
        def debounced(*args: Any, **kwargs: Any) -> None:
            subject = args[0]
            captured_id = call_ids[subject] = call_ids.get(subject, 0) + 1

            def call_function() -> Any:
                if call_ids.get(subject) != captured_id:
                    return None  # a newer call for this subject superseded this one
                return func(*args, **kwargs)

            resolved_time_s = time_s() if callable(time_s) else time_s
            sublime.set_timeout_async(call_function, int(resolved_time_s * 1000))

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
