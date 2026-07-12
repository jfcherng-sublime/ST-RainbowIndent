"""Tests for renderer discovery and rendering (BlockIndentRenderer, LineIndentRenderer)."""

from __future__ import annotations

from sublime import Region
from sublime import View

from plugin.data_types import LevelStyle
from plugin.helpers import get_regions_key
from plugin.indent_renderer import BlockIndentRenderer
from plugin.indent_renderer import LineIndentRenderer
from plugin.indent_renderer import find_indent_renderer


class TestFindIndentRenderer:
    def test_block_style_resolves_to_block_renderer(self) -> None:
        assert find_indent_renderer(LevelStyle.BLOCK) is BlockIndentRenderer

    def test_line_style_resolves_to_line_renderer(self) -> None:
        assert find_indent_renderer(LevelStyle.LINE) is LineIndentRenderer


class TestRendererName:
    def test_block_renderer_name(self) -> None:
        assert BlockIndentRenderer.name() == "block"

    def test_line_renderer_name(self) -> None:
        assert LineIndentRenderer.name() == "line"


class TestCanSupport:
    def test_block_renderer_supports_only_block_style(self) -> None:
        assert BlockIndentRenderer.can_support(LevelStyle.BLOCK) is True
        assert BlockIndentRenderer.can_support(LevelStyle.LINE) is False

    def test_line_renderer_supports_only_line_style(self) -> None:
        assert LineIndentRenderer.can_support(LevelStyle.LINE) is True
        assert LineIndentRenderer.can_support(LevelStyle.BLOCK) is False


class TestBlockIndentRenderer:
    def test_render_adds_the_full_region_per_level(self) -> None:
        view = View()
        renderer = BlockIndentRenderer(view)
        level_regions = {0: [Region(0, 4)], 1: [Region(4, 8)]}

        renderer.render(level_colors=["region.redish", "region.greenish"], level_regions=level_regions)

        assert view.regions[get_regions_key(0)] == [Region(0, 4)]
        assert view.regions[get_regions_key(1)] == [Region(4, 8)]


class TestLineIndentRenderer:
    def test_render_collapses_each_region_to_its_start_point(self) -> None:
        """Line style draws a vertical line at each region's left edge, not the full block."""
        view = View()
        renderer = LineIndentRenderer(view)
        level_regions = {0: [Region(0, 4), Region(10, 14)]}

        renderer.render(level_colors=["region.redish"], level_regions=level_regions)

        assert view.regions[get_regions_key(0)] == [Region(0), Region(10)]
