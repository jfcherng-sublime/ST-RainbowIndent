"""Tests for utility functions (get_circular_nth, camel_to_snake, etc.)."""

from __future__ import annotations

import pytest

from plugin.utils import camel_to_snake
from plugin.utils import get_circular_nth


class TestGetCircularNth:
    def test_normal_access(self) -> None:
        assert get_circular_nth(["a", "b", "c"], 0) == "a"
        assert get_circular_nth(["a", "b", "c"], 1) == "b"
        assert get_circular_nth(["a", "b", "c"], 2) == "c"

    def test_circular_wraparound(self) -> None:
        assert get_circular_nth(["a", "b", "c"], 3) == "a"
        assert get_circular_nth(["a", "b", "c"], 4) == "b"
        assert get_circular_nth(["a", "b", "c"], 5) == "c"

    def test_negative_index(self) -> None:
        assert get_circular_nth(["a", "b", "c"], -1) == "c"

    def test_single_element(self) -> None:
        assert get_circular_nth(["x"], 0) == "x"
        assert get_circular_nth(["x"], 100) == "x"

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="empty sequence"):
            get_circular_nth([], 0)


class TestCamelToSnake:
    def test_simple(self) -> None:
        assert camel_to_snake("CamelCase") == "camel_case"

    def test_already_snake(self) -> None:
        assert camel_to_snake("already_snake") == "already_snake"

    def test_single_word(self) -> None:
        assert camel_to_snake("Hello") == "hello"

    def test_acronyms(self) -> None:
        assert camel_to_snake("HTTPServer") == "h_t_t_p_server"

    def test_numbers(self) -> None:
        assert camel_to_snake("File2Stream") == "file2_stream"
