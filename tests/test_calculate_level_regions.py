"""Tests for calculate_level_regions — the core indent computation."""

from __future__ import annotations

from sublime import Region
from sublime import View

from plugin.data_types import IndentInfo
from plugin.data_types import IndentStyle
from plugin.view_manager import calculate_level_regions


def _make_view(content: str) -> View:
    view = View(content=content)
    view.settings().set("tab_size", 4)
    view.settings().set("translate_tabs_to_spaces", True)
    return view


class TestCalculateLevelRegions:
    def test_no_indent(self) -> None:
        """No indentation → empty result."""
        view = _make_view("line1\nline2\nline3")
        result = calculate_level_regions(view)
        assert len(result) == 0

    def test_single_level_spaces(self) -> None:
        """4-space indent → level 0 regions."""
        view = _make_view("    hello\n    world")
        result = calculate_level_regions(view)
        assert 0 in result
        assert len(result[0]) == 2  # two lines with indent
        assert result[0][0] == Region(0, 4)
        # "    world" starts at offset 10
        assert result[0][1] == Region(10, 14)

    def test_two_levels_spaces(self) -> None:
        """8-space (2 levels) indent → regions at levels 0 and 1."""
        view = _make_view("        deeply indented")
        result = calculate_level_regions(view)
        assert 0 in result
        assert 1 in result
        assert result[0][0] == Region(0, 4)
        assert result[1][0] == Region(4, 8)

    def test_mixed_indent_levels(self) -> None:
        """Lines at different indent levels produce correct regions per level."""
        content = "    level1\n        level2\nno_indent\n    back_to_1"
        view = _make_view(content)
        result = calculate_level_regions(view)
        assert 0 in result
        assert 1 in result
        # level 0: line "    level1" (0-4), line "        level2" (10-14), line "    back_to_1" (33-37)
        assert len(result[0]) == 3
        # level 1: line "        level2" (14-18)
        assert len(result[1]) == 1

    def test_tab_indent(self) -> None:
        """Tab-based indentation produces correct regions."""
        view = View(content="\t\tdeep")
        view.settings().set("tab_size", 4)
        view.settings().set("translate_tabs_to_spaces", False)
        result = calculate_level_regions(view)
        assert 0 in result
        assert 1 in result
        assert result[0][0] == Region(0, 1)
        assert result[1][0] == Region(1, 2)

    def test_tab_size_2(self) -> None:
        """2-space indent works correctly."""
        view = _make_view("  a\n    b")
        view.settings().set("tab_size", 2)
        result = calculate_level_regions(view)
        assert 0 in result
        assert len(result[0]) == 2  # both lines have at least 2 spaces
        assert result[0][0] == Region(0, 2)
        # "    b" starts at offset 4
        assert result[0][1] == Region(4, 6)

    def test_custom_region(self) -> None:
        """Only processes the specified regions when provided."""
        view = _make_view("    a\n    b\n    c")
        # Region covering only the first line (0-5) -> only that line's indent
        result = calculate_level_regions(view, regions=[Region(0, 5)])
        assert 0 in result
        assert len(result[0]) == 1
        assert result[0][0] == Region(0, 4)
        # No level for line 2 or 3 since they're outside the region
        assert 1 not in result

    def test_custom_indent_info(self) -> None:
        """Accepts pre-computed IndentInfo."""
        view = _make_view("  a\n  b")
        info = IndentInfo(tab_size=2, style=IndentStyle.SPACE)
        result = calculate_level_regions(view, indent_info=info)
        assert 0 in result
        assert len(result[0]) == 2

    def test_zero_tab_size_does_not_crash(self) -> None:
        """A misconfigured tab_size=0 must not raise ValueError from range(step=0)."""
        view = _make_view("    a\n    b")
        view.settings().set("tab_size", 0)
        result = calculate_level_regions(view)  # must not raise
        assert 0 in result
