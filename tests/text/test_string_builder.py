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

    # ----- constructor ------------------------------------------------

    def test_ctor_default_value_is_empty(self):
        """The default constructor produces an empty builder."""
        sb = StringBuilder()
        self.assertEqual("", sb.to_string())

    def test_ctor_with_initial_value(self):
        """The constructor seeds the builder with the supplied value."""
        sb = StringBuilder("hello")
        self.assertEqual("hello", sb.to_string())

    def test_ctor_with_empty_string_is_empty(self):
        """An explicit empty string yields an empty builder."""
        sb = StringBuilder("")
        self.assertEqual("", sb.to_string())

    def test_ctor_value_is_followed_by_write(self):
        """Subsequent `write` calls append after the initial value."""
        sb = StringBuilder("hello")
        sb.write(" world")
        self.assertEqual("hello world", sb.to_string())

    def test_ctor_value_is_cleared_by_clear(self):
        """`clear` removes the initial value just like any other content."""
        sb = StringBuilder("hello")
        sb.clear()
        self.assertEqual("", sb.to_string())

    def test_ctor_rejects_non_string_value(self):
        """The constructor raises ``AssertionError`` for non-string values."""
        with self.assertRaises(AssertionError):
            StringBuilder(123)  # type: ignore[arg-type]

    # ----- format -----------------------------------------------------

    def test_format_with_single_string_arg(self):
        """`format` substitutes a single ``%s`` placeholder."""
        sb = StringBuilder()
        sb.format("hello %s", "world")
        self.assertEqual("hello world", sb.to_string())

    def test_format_with_multiple_args(self):
        """`format` substitutes multiple positional placeholders."""
        sb = StringBuilder()
        sb.format("%s = %d", "answer", 42)
        self.assertEqual("answer = 42", sb.to_string())

    def test_format_with_float_precision(self):
        """`format` supports printf-style precision specifiers."""
        sb = StringBuilder()
        sb.format("pi = %.2f", 3.14159)
        self.assertEqual("pi = 3.14", sb.to_string())

    def test_format_without_args_appends_literal(self):
        """`format` without args appends the format string verbatim."""
        sb = StringBuilder()
        sb.format("no placeholders here")
        self.assertEqual("no placeholders here", sb.to_string())

    def test_format_appends_to_existing_content(self):
        """`format` appends to, rather than replaces, existing content."""
        sb = StringBuilder("prefix: ")
        sb.format("%s!", "value")
        self.assertEqual("prefix: value!", sb.to_string())

    def test_format_returns_self_for_chaining(self):
        """`format` returns the same instance for fluent chaining."""
        sb = StringBuilder()
        result = sb.format("%s", "x")
        self.assertIs(sb, result)

    def test_format_chained_with_other_methods(self):
        """`format` mixes cleanly with `write` and `write_line`."""
        sb = StringBuilder()
        sb.write("[").format("%s=%d", "n", 7).write("]")
        self.assertEqual("[n=7]", sb.to_string())

    def test_format_argument_mismatch_raises(self):
        """`format` raises ``TypeError`` when args do not match placeholders."""
        sb = StringBuilder()
        with self.assertRaises(TypeError):
            sb.format("%s %s", "only-one")

    def test_format_rejects_non_string_format(self):
        """`format` raises ``AssertionError`` for a non-string format."""
        sb = StringBuilder()
        with self.assertRaises(AssertionError):
            sb.format(123, "x")  # type: ignore[arg-type]

    # ----- join -------------------------------------------------------

    def test_join_appends_other_content(self):
        """`join` appends the content of another builder."""
        a = StringBuilder("hello ")
        b = StringBuilder("world")
        a.join(b)
        self.assertEqual("hello world", a.to_string())

    def test_join_does_not_modify_other(self):
        """`join` leaves the source builder unchanged."""
        a = StringBuilder("hello ")
        b = StringBuilder("world")
        a.join(b)
        self.assertEqual("world", b.to_string())

    def test_join_with_empty_other_is_noop(self):
        """`join` with an empty source leaves the caller unchanged."""
        a = StringBuilder("abc")
        b = StringBuilder()
        a.join(b)
        self.assertEqual("abc", a.to_string())

    def test_join_into_empty_caller(self):
        """`join` into an empty builder copies the source content."""
        a = StringBuilder()
        b = StringBuilder("abc")
        a.join(b)
        self.assertEqual("abc", a.to_string())

    def test_join_returns_self_for_chaining(self):
        """`join` returns the same instance for fluent chaining."""
        a = StringBuilder("x")
        b = StringBuilder("y")
        result = a.join(b)
        self.assertIs(a, result)

    def test_join_chained_with_other_methods(self):
        """`join` mixes cleanly with the other fluent methods."""
        a = StringBuilder("[")
        b = StringBuilder("payload")
        a.join(b).write("]")
        self.assertEqual("[payload]", a.to_string())

    def test_join_after_source_segmented_writes(self):
        """`join` appends the source's full content regardless of segments."""
        a = StringBuilder("<")
        b = StringBuilder()
        b.write("foo").write("bar").write("baz")
        a.join(b).write(">")
        self.assertEqual("<foobarbaz>", a.to_string())

    def test_join_subsequent_writes_to_other_do_not_affect_caller(self):
        """After `join`, later writes to the source must not leak into the
        caller."""
        a = StringBuilder()
        b = StringBuilder("abc")
        a.join(b)
        b.write("-XYZ")
        self.assertEqual("abc", a.to_string())
        self.assertEqual("abc-XYZ", b.to_string())

    def test_join_with_self_doubles_content(self):
        """`join(self)` appends a snapshot of the current content."""
        sb = StringBuilder("abc")
        sb.join(sb)
        self.assertEqual("abcabc", sb.to_string())

    def test_join_with_self_on_empty_is_noop(self):
        """`join(self)` on an empty builder leaves it empty."""
        sb = StringBuilder()
        sb.join(sb)
        self.assertEqual("", sb.to_string())

    def test_join_rejects_non_string_builder(self):
        """`join` raises ``AssertionError`` for non-``StringBuilder``
        arguments."""
        sb = StringBuilder()
        with self.assertRaises(AssertionError):
            sb.join("not a builder")  # type: ignore[arg-type]
        with self.assertRaises(AssertionError):
            sb.join(None)  # type: ignore[arg-type]

    # ----- insert -----------------------------------------------------

    def test_insert_at_start(self):
        """`insert` at index 0 prepends the value."""
        sb = StringBuilder("world")
        sb.insert(0, "hello ")
        self.assertEqual("hello world", sb.to_string())

    def test_insert_in_middle(self):
        """`insert` at a middle index splices the value into the content."""
        sb = StringBuilder("abcdef")
        sb.write("gj")
        sb.insert(7, "hi")
        self.assertEqual("abcdefghij", sb.to_string())

    def test_insert_at_end_appends(self):
        """`insert` at ``index == length`` appends the value."""
        sb = StringBuilder("abc")
        sb.insert(3, "def")
        self.assertEqual("abcdef", sb.to_string())

    def test_insert_empty_value_is_noop(self):
        """`insert` with an empty value leaves content unchanged."""
        sb = StringBuilder("abc")
        sb.insert(1, "")
        self.assertEqual("abc", sb.to_string())

    def test_insert_into_empty_builder(self):
        """`insert` at 0 on an empty builder seeds the content."""
        sb = StringBuilder()
        sb.insert(0, "abc")
        self.assertEqual("abc", sb.to_string())

    def test_insert_across_segment_boundaries(self):
        """`insert` works across previously written segments."""
        sb = StringBuilder()
        sb.write("foo").write("bar").write("baz")
        sb.insert(3, "-")
        self.assertEqual("foo-barbaz", sb.to_string())

    def test_insert_returns_self_for_chaining(self):
        """`insert` returns the same instance for fluent chaining."""
        sb = StringBuilder("abc")
        result = sb.insert(1, "X")
        self.assertIs(sb, result)

    def test_insert_chained_with_other_methods(self):
        """`insert` mixes cleanly with the other fluent methods."""
        sb = StringBuilder("world")
        sb.insert(0, "hello ").write("!")
        self.assertEqual("hello world!", sb.to_string())

    def test_insert_negative_index_raises(self):
        """`insert` raises ``ValueError`` when ``index`` is negative."""
        sb = StringBuilder("abc")
        with self.assertRaises(ValueError):
            sb.insert(-1, "x")

    def test_insert_index_greater_than_length_raises(self):
        """`insert` raises ``ValueError`` when ``index`` exceeds the length."""
        sb = StringBuilder("abc")
        with self.assertRaises(ValueError):
            sb.insert(4, "x")

    def test_insert_into_empty_with_nonzero_index_raises(self):
        """`insert(1, ...)` on an empty builder raises ``ValueError``."""
        sb = StringBuilder()
        with self.assertRaises(ValueError):
            sb.insert(1, "x")

    def test_insert_rejects_non_int_index(self):
        """`insert` raises ``AssertionError`` for a non-int ``index``."""
        sb = StringBuilder("abc")
        with self.assertRaises(AssertionError):
            sb.insert("0", "x")  # type: ignore[arg-type]

    def test_insert_rejects_non_string_value(self):
        """`insert` raises ``AssertionError`` for a non-string ``value``."""
        sb = StringBuilder("abc")
        with self.assertRaises(AssertionError):
            sb.insert(0, 123)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
