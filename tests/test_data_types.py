"""Tests for data types (IndentInfo, IndentStyle, LevelStyle)."""

from __future__ import annotations

import re

import pytest
from sublime import View

from plugin.data_types import IndentInfo
from plugin.data_types import IndentStyle
from plugin.data_types import LevelStyle


class TestIndentStyle:
    def test_str_values(self) -> None:
        assert IndentStyle.SPACE == "space"
        assert IndentStyle.TAB == "tab"


class TestLevelStyle:
    def test_str_values(self) -> None:
        assert LevelStyle.BLOCK == "block"
        assert LevelStyle.LINE == "line"


class TestIndentInfo:
    def test_space_indent_chars(self) -> None:
        info = IndentInfo(tab_size=4, style=IndentStyle.SPACE)
        assert info.indent_chars == "    "
        assert info.indent_length == 4

    def test_tab_indent_chars(self) -> None:
        info = IndentInfo(tab_size=4, style=IndentStyle.TAB)
        assert info.indent_chars == "\t"
        assert info.indent_length == 1

    def test_tab_size_2(self) -> None:
        info = IndentInfo(tab_size=2, style=IndentStyle.SPACE)
        assert info.indent_chars == "  "
        assert info.indent_length == 2

    def test_indent_pattern_spaces(self) -> None:
        info = IndentInfo(tab_size=4, style=IndentStyle.SPACE)
        assert info.indent_pattern == r"^(?:    )+"

    def test_indent_pattern_tabs(self) -> None:
        info = IndentInfo(tab_size=4, style=IndentStyle.TAB)
        # The pattern contains an actual tab character, not the two chars \t
        assert info.indent_pattern == "^(?:\t)+"

    def test_indent_pattern_compiled(self) -> None:
        info = IndentInfo(tab_size=4, style=IndentStyle.SPACE)
        assert isinstance(info.indent_pattern_compiled, re.Pattern)
        assert info.indent_pattern_compiled.match("        hello") is not None
        assert info.indent_pattern_compiled.match("hello") is None

    def test_from_view_spaces(self) -> None:
        view = View(content="    hello")
        view.settings().set("tab_size", 4)
        view.settings().set("translate_tabs_to_spaces", True)
        info = IndentInfo.from_view(view)
        assert info.tab_size == 4
        assert info.style == IndentStyle.SPACE

    def test_from_view_tabs(self) -> None:
        view = View(content="\thello")
        view.settings().set("tab_size", 4)
        view.settings().set("translate_tabs_to_spaces", False)
        info = IndentInfo.from_view(view)
        assert info.tab_size == 4
        assert info.style == IndentStyle.TAB

    def test_from_view_defaults(self) -> None:
        view = View(content="")
        info = IndentInfo.from_view(view)
        assert info.tab_size == 4
        assert info.style == IndentStyle.TAB  # default ST setting

    def test_cached_properties(self) -> None:
        """cached_property should return the same object on repeated access."""
        info = IndentInfo(tab_size=4, style=IndentStyle.SPACE)
        p1 = info.indent_pattern_compiled
        p2 = info.indent_pattern_compiled
        assert p1 is p2  # cached

    def test_frozen(self) -> None:
        """IndentInfo should be immutable."""
        info = IndentInfo(tab_size=4, style=IndentStyle.SPACE)
        with pytest.raises(AttributeError):
            info.tab_size = 2  # type: ignore[misc]
