from __future__ import annotations

import inspect
import sys
import threading
from functools import wraps
from typing import Any, Callable, Generator, Iterable, Sequence, TypeVar, cast

import sublime

_T_Callable = TypeVar("_T_Callable", bound=Callable[..., Any])
_T = TypeVar("_T")


def list_all_subclasses(
    root: type[_T],
    skip_abstract: bool = False,
    skip_self: bool = False,
) -> Generator[type[_T], None, None]:
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


if sys.version_info >= (3, 9):
    remove_prefix = str.removeprefix
    remove_suffix = str.removesuffix
else:

    def remove_prefix(s: str, prefix: str) -> str:
        """Remove the prefix from the string. I.e., str.removeprefix in Python 3.9."""
        return s[len(prefix) :] if s.startswith(prefix) else s

    def remove_suffix(s: str, suffix: str) -> str:
        """Remove the suffix from the string. I.e., str.removesuffix in Python 3.9."""
        # suffix="" should not call s[:-0]
        return s[: -len(suffix)] if suffix and s.endswith(suffix) else s


def debounce(time_s: float = 0.3) -> Callable[[_T_Callable], _T_Callable]:
    """
    Debounce a function so that it's called after `time_s` seconds.
    If it's called multiple times in the time frame, it will only run the last call.

    Taken and modified from https://github.com/salesforce/decorator-operations
    """

    def decorator(func: _T_Callable) -> _T_Callable:
        @wraps(func)
        def debounced(*args: Any, **kwargs: Any) -> None:
            def call_function() -> Any:
                delattr(debounced, "_timer")
                return func(*args, **kwargs)

            if timer := getattr(debounced, "_timer", None):
                timer.cancel()

            timer = threading.Timer(time_s, call_function)
            timer.start()
            setattr(debounced, "_timer", timer)

        setattr(debounced, "_timer", None)
        return cast(_T_Callable, debounced)

    return decorator


def configured_debounce(func: _T_Callable) -> _T_Callable:
    """Debounce a function so that it's called once in seconds."""

    def debounced(*args: Any, **kwargs: Any) -> Any:
        from .settings import get_debounce_time

        if (time_s := get_debounce_time()) > 0:
            return debounce(time_s)(func)(*args, **kwargs)
        return func(*args, **kwargs)

    return cast(_T_Callable, debounced)


def list_views(
    windows: Iterable[sublime.Window] | None = None,
    *,
    include_transient: bool = False,
) -> Generator[sublime.View, None, None]:
    """List all views in all windows."""
    if windows is None:
        windows = sublime.windows()

    yield from (view for window in sublime.windows() for view in window.views(include_transient=include_transient))
