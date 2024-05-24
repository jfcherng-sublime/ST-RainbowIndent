from __future__ import annotations

from .constants import PLUGIN_NAME


def log_debug(message: str) -> None:
    print(f"[{PLUGIN_NAME}][DEBUG] {message}")


def log_info(message: str) -> None:
    print(f"[{PLUGIN_NAME}][INFO] {message}")


def log_warning(message: str) -> None:
    print(f"[{PLUGIN_NAME}][WARNING] {message}")


def log_error(message: str) -> None:
    print(f"[{PLUGIN_NAME}][ERROR] {message}")
