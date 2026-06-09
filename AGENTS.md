# AGENTS.md

This file provides guidance to coding agents when working with code in this repository.

## Project Overview

ST-RainbowIndent is a Sublime Text 4 plugin that colorizes indentation levels for easier reading (clone of VSCode's "Indent Rainbow"). Requires Sublime Text build 4169+ and Python 3.13+.

## Development Commands

```bash
# Install dependencies (uses uv package manager)
make install-dev          # Dev dependencies only
make install-all          # All dependency groups

# Run all CI checks (mypy + ruff lint + ruff format)
make ci-check

# Individual checks
uv run --dev mypy -p plugin
uv run --dev ruff check --diff .
uv run --dev ruff format --diff .

# Auto-fix lint and format issues
make ci-fix               # Safe fixes only
make ci-fix-unsafe        # Include unsafe fixes

# Generate changelog from conventional commits
make update-changelog
```

There are no unit tests in this project. CI runs mypy and ruff only.

## Architecture

**Entry flow:** `boot.py` → reloads all plugin submodules → imports `plugin/__init__.py` which exports ST entry points (`plugin_loaded`, `plugin_unloaded`), commands, and the event listener.

**Core rendering pipeline:**

1. `RainbowIndentEventListener` (listener.py) — receives ST view events (`on_activated`, `on_modified`, etc.), debounced via settings
2. `helpers.is_renderable_view()` — gates rendering based on syntax selector, file size, user disable flag
3. `ViewManager` (view_manager.py) — singleton per view (via `WeakKeyDictionary`), orchestrates rendering
4. `calculate_level_regions()` (view_manager.py) — regex-based computation of indent regions per level
5. `AbstractIndentRenderer` subclasses (indent_renderer.py) — `BlockIndentRenderer` (background blocks) or `LineIndentRenderer` (vertical lines), selected by `LevelStyle` enum; discovered via subclass registry pattern

**Settings:** `settings.py` wraps `sublime.load_settings()` for the plugin's `.sublime-settings` file. Settings include debounce time, level colors (scope names), level style (block/line), enabled selector, and file size limit.

**Commands:** `plugin/commands/` — three view commands (enable/disable/toggle) that set a per-view activation flag.

## Code Conventions

- Python 3.14+ features: lazy annotation evaluation via PEP 649 (no `from __future__ import annotations` needed), `match` statements, `type` aliases, `@override`, `Self`
- Strict mypy with custom type stubs in `typings/`
- Ruff: line length 120, preview mode, rules: E/F/W/I/UP/FURB/SIM
- Conventional commits (`feat:`, `fix:`, `refactor:`, `chore:`, etc.)
- Frozen dataclasses for value objects, `@cache`/`@cached_property` for memoization
- 4-space indentation for Python/JSON, 2-space for TOML/Markdown (see `.editorconfig`)

## Approach

- Think before acting. Read existing files before writing code.
- Be concise in output but thorough in reasoning.
- Prefer editing over rewriting whole files.
- Do not re-read files you have already read unless the file may have changed.
- Test your code before declaring done.
- No sycophantic openers or closing fluff.
- Keep solutions simple and direct.
- User instructions always override this file.
