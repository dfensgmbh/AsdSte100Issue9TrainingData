# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Unit tests for the :class:`StringBuilder` class."""

import unittest

from biz.dfch.text import StringBuilder
from biz.dfch.text.string_builder import StringBuilder as DirectStringBuilder


class TestStringBuilder(unittest.TestCase):
    """Unit tests for :class:`StringBuilder`."""

    def test_new_instance_is_empty(self):
        """A freshly constructed builder produces an empty string."""
        sb = StringBuilder()
        self.assertEqual("", sb.to_string())

    def test_package_export_matches_module(self):
        """The class re-exported from the package is the module class."""
        self.assertIs(StringBuilder, DirectStringBuilder)

    def test_write_appends_value(self):
        """`write` appends a single string."""
        sb = StringBuilder()
        sb.write("hello")
        self.assertEqual("hello", sb.to_string())

    def test_write_concatenates_in_order(self):
        """Multiple `write` calls concatenate in call order."""
        sb = StringBuilder()
        sb.write("foo")
        sb.write("bar")
        sb.write("baz")
        self.assertEqual("foobarbaz", sb.to_string())

    def test_write_empty_string_is_noop(self):
        """Writing an empty string does not change the content."""
        sb = StringBuilder()
        sb.write("abc")
        sb.write("")
        self.assertEqual("abc", sb.to_string())

    def test_write_returns_self_for_chaining(self):
        """`write` returns the same instance for fluent chaining."""
        sb = StringBuilder()
        result = sb.write("x")
        self.assertIs(sb, result)

    def test_write_chain_produces_expected_string(self):
        """Chained `write` calls produce the concatenated result."""
        sb = StringBuilder()
        result = sb.write("a").write("b").write("c").to_string()
        self.assertEqual("abc", result)

    def test_write_rejects_non_string(self):
        """`write` raises ``AssertionError`` for non-string values."""
        sb = StringBuilder()
        with self.assertRaises(AssertionError):
            sb.write(123)  # type: ignore[arg-type]

    def test_write_line_appends_value_and_newline(self):
        """`write_line` appends the value followed by a newline."""
        sb = StringBuilder()
        sb.write_line("hello")
        self.assertEqual("hello\n", sb.to_string())

    def test_write_line_default_appends_newline_only(self):
        """`write_line()` without arguments appends only a newline."""
        sb = StringBuilder()
        sb.write_line()
        self.assertEqual("\n", sb.to_string())

    def test_write_line_multiple_calls(self):
        """Successive `write_line` calls produce one line per call."""
        sb = StringBuilder()
        sb.write_line("a").write_line("b").write_line("c")
        self.assertEqual("a\nb\nc\n", sb.to_string())

    def test_write_line_returns_self_for_chaining(self):
        """`write_line` returns the same instance for fluent chaining."""
        sb = StringBuilder()
        result = sb.write_line("x")
        self.assertIs(sb, result)

    def test_write_line_rejects_non_string(self):
        """`write_line` raises ``AssertionError`` for non-string values."""
        sb = StringBuilder()
        with self.assertRaises(AssertionError):
            sb.write_line(42)  # type: ignore[arg-type]

    def test_mixed_write_and_write_line(self):
        """`write` and `write_line` can be mixed and chained."""
        sb = StringBuilder()
        sb.write("a").write_line("b").write("c")
        self.assertEqual("ab\nc", sb.to_string())

    def test_clear_removes_content(self):
        """`clear` resets the builder to an empty state."""
        sb = StringBuilder()
        sb.write("abc").write_line("def")
        sb.clear()
        self.assertEqual("", sb.to_string())

    def test_clear_returns_self_for_chaining(self):
        """`clear` returns the same instance for fluent chaining."""
        sb = StringBuilder()
        sb.write("abc")
        result = sb.clear()
        self.assertIs(sb, result)

    def test_clear_then_write_starts_fresh(self):
        """After `clear`, the builder accepts new content normally."""
        sb = StringBuilder()
        sb.write("old")
        sb.clear()
        sb.write("new")
        self.assertEqual("new", sb.to_string())

    def test_clear_on_empty_builder(self):
        """`clear` on an already-empty builder is a no-op."""
        sb = StringBuilder()
        sb.clear()
        self.assertEqual("", sb.to_string())

    def test_to_string_is_repeatable_and_non_destructive(self):
        """`to_string` may be called multiple times without changing state."""
        sb = StringBuilder()
        sb.write("abc")
        first = sb.to_string()
        second = sb.to_string()
        self.assertEqual("abc", first)
        self.assertEqual(first, second)

    def test_instances_are_independent(self):
        """Separate builders maintain independent buffers."""
        a = StringBuilder()
        b = StringBuilder()
        a.write("a")
        b.write("b")
        self.assertEqual("a", a.to_string())
        self.assertEqual("b", b.to_string())

    # ----- replace ----------------------------------------------------

    def test_replace_single_occurrence(self):
        """`replace` substitutes a single occurrence."""
        sb = StringBuilder()
        sb.write("hello world")
        sb.replace("world", "there")
        self.assertEqual("hello there", sb.to_string())

    def test_replace_all_occurrences(self):
        """`replace` substitutes every occurrence of ``old_value``."""
        sb = StringBuilder()
        sb.write("aaa-bbb-aaa-ccc-aaa")
        sb.replace("aaa", "X")
        self.assertEqual("X-bbb-X-ccc-X", sb.to_string())

    def test_replace_across_segment_boundaries(self):
        """`replace` works even when matches span multiple writes."""
        sb = StringBuilder()
        sb.write("foo").write("bar").write("baz")
        sb.replace("obar", "OBAR")
        self.assertEqual("foOBARbaz", sb.to_string())

    def test_replace_with_empty_new_value_removes(self):
        """`replace` with an empty ``new_value`` removes the matches."""
        sb = StringBuilder()
        sb.write("abc-abc-abc")
        sb.replace("abc", "")
        self.assertEqual("--", sb.to_string())

    def test_replace_no_match_leaves_content_unchanged(self):
        """`replace` is a no-op when ``old_value`` is not present."""
        sb = StringBuilder()
        sb.write("hello")
        sb.replace("xyz", "abc")
        self.assertEqual("hello", sb.to_string())

    def test_replace_returns_self_for_chaining(self):
        """`replace` returns the same instance for fluent chaining."""
        sb = StringBuilder()
        sb.write("a")
        result = sb.replace("a", "b")
        self.assertIs(sb, result)

    def test_replace_empty_old_value_raises(self):
        """`replace` raises ``AssertionError`` when ``old_value`` is empty."""
        sb = StringBuilder()
        sb.write("abc")
        with self.assertRaises(AssertionError):
            sb.replace("", "x")

    def test_replace_rejects_non_string_arguments(self):
        """`replace` raises ``AssertionError`` for non-string arguments."""
        sb = StringBuilder()
        sb.write("abc")
        with self.assertRaises(AssertionError):
            sb.replace(1, "x")  # type: ignore[arg-type]
        with self.assertRaises(AssertionError):
            sb.replace("a", 2)  # type: ignore[arg-type]

    # ----- remove -----------------------------------------------------

    def test_remove_middle_range(self):
        """`remove` deletes a range from the middle of the content."""
        sb = StringBuilder()
        sb.write("abcdef")
        sb.remove(2, 2)
        self.assertEqual("abef", sb.to_string())

    def test_remove_from_start(self):
        """`remove` deletes a range starting at index 0."""
        sb = StringBuilder()
        sb.write("abcdef")
        sb.remove(0, 3)
        self.assertEqual("def", sb.to_string())

    def test_remove_to_end(self):
        """`remove` deletes a range ending at the last character."""
        sb = StringBuilder()
        sb.write("abcdef")
        sb.remove(3, 3)
        self.assertEqual("abc", sb.to_string())

    def test_remove_zero_length_is_noop(self):
        """`remove` with ``length == 0`` leaves content unchanged."""
        sb = StringBuilder()
        sb.write("abcdef")
        sb.remove(2, 0)
        self.assertEqual("abcdef", sb.to_string())

    def test_remove_entire_content(self):
        """`remove` can clear the builder when removing all characters."""
        sb = StringBuilder()
        sb.write("abcdef")
        sb.remove(0, 6)
        self.assertEqual("", sb.to_string())

    def test_remove_across_segment_boundaries(self):
        """`remove` works across previously written segments."""
        sb = StringBuilder()
        sb.write("foo").write("bar").write("baz")
        sb.remove(2, 5)  # remove "obarb" from "foobarbaz"
        self.assertEqual("foaz", sb.to_string())

    def test_remove_returns_self_for_chaining(self):
        """`remove` returns the same instance for fluent chaining."""
        sb = StringBuilder()
        sb.write("abc")
        result = sb.remove(0, 1)
        self.assertIs(sb, result)

    def test_remove_negative_start_index_raises(self):
        """`remove` raises ``ValueError`` when ``start_index`` is negative."""
        sb = StringBuilder()
        sb.write("abc")
        with self.assertRaises(ValueError):
            sb.remove(-1, 1)

    def test_remove_negative_length_raises(self):
        """`remove` raises ``ValueError`` when ``length`` is negative."""
        sb = StringBuilder()
        sb.write("abc")
        with self.assertRaises(ValueError):
            sb.remove(0, -1)

    def test_remove_out_of_range_raises(self):
        """`remove` raises ``ValueError`` when the range exceeds content."""
        sb = StringBuilder()
        sb.write("abc")
        with self.assertRaises(ValueError):
            sb.remove(1, 5)

    def test_remove_rejects_non_int_arguments(self):
        """`remove` raises ``AssertionError`` for non-int arguments."""
        sb = StringBuilder()
        sb.write("abc")
        with self.assertRaises(AssertionError):
            sb.remove("0", 1)  # type: ignore[arg-type]
        with self.assertRaises(AssertionError):
            sb.remove(0, "1")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
