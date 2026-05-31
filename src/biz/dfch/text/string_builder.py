# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Provides the :class:`StringBuilder` type for efficient string concatenation.
"""

from __future__ import annotations


class StringBuilder:
    """Represents a mutable string of characters.

    Use this class to build a string by appending substrings without
    creating a new string object for every concatenation. Call
    :meth:`to_string` to obtain the resulting :class:`str`.
    """

    _lines: list[str]

    def __init__(self, value: str = "") -> None:
        """Initializes a new instance of the :class:`StringBuilder` class.

        Args:
            value (str): The initial value of the builder. Defaults to
                an empty string.
        """

        assert isinstance(value, str), type(value)

        self._lines = []
        if value:
            self._lines.append(value)

    def clear(self) -> StringBuilder:
        """Removes all characters from the current instance.

        Returns:
            StringBuilder: This instance, to allow method chaining.
        """

        self._lines.clear()

        return self

    def to_string(self) -> str:
        """Converts the value of this instance to a :class:`str`.

        Returns:
            str: The accumulated string.
        """

        result = "".join(self._lines)

        return result

    def write(self, value: str) -> StringBuilder:
        """Appends a copy of the specified string to this instance.

        Args:
            value (str): The string to append.

        Returns:
            StringBuilder: This instance, to allow method chaining.
        """

        assert isinstance(value, str), type(value)

        self._lines.append(value)

        return self

    def write_line(self, value: str = "") -> StringBuilder:
        """Appends the specified string followed by a newline character.

        Args:
            value (str): The string to append. Defaults to an empty
                string, which appends only the newline.

        Returns:
            StringBuilder: This instance, to allow method chaining.
        """

        assert isinstance(value, str), type(value)

        self._lines.append(value)
        self._lines.append("\n")

        return self

    def replace(self, old_value: str, new_value: str) -> StringBuilder:
        """Replaces all occurrences of a specified string in this instance.

        Args:
            old_value (str): The string to be replaced. Must not be
                empty.
            new_value (str): The string that replaces ``old_value``.

        Returns:
            StringBuilder: This instance, to allow method chaining.
        """

        assert isinstance(old_value, str), type(old_value)
        assert isinstance(new_value, str), type(new_value)
        assert old_value, "Parameter must not be empty: 'old_value'."

        joined = "".join(self._lines)
        replaced = joined.replace(old_value, new_value)
        self._lines = [replaced]

        return self

    def format(self, format_string: str, *args: object) -> StringBuilder:
        """Appends a formatted string to this instance.

        The format string uses ``printf``-style ``%`` placeholders
        (for example ``%s``, ``%d``, ``%.2f``) and is evaluated against
        the supplied positional arguments.

        Args:
            format_string (str): A ``%``-style format string.
            *args (object): Values to substitute into
                ``format_string``.

        Returns:
            StringBuilder: This instance, to allow method chaining.

        Raises:
            TypeError: If ``format_string`` does not match the number
                or type of ``args``.
        """

        assert isinstance(format_string, str), type(format_string)

        if args:
            formatted = format_string % args
        else:
            formatted = format_string

        self._lines.append(formatted)

        return self

    def join(self, other: StringBuilder) -> StringBuilder:
        """Appends the contents of another :class:`StringBuilder`
        to this instance.

        The source instance is not modified.

        Args:
            other (StringBuilder): The builder whose contents are
                appended to this instance.

        Returns:
            StringBuilder: This instance, to allow method chaining.
        """

        assert isinstance(other, StringBuilder), type(other)

        if other is self:
            snapshot = other.to_string()
            if snapshot:
                self._lines.append(snapshot)
            return self

        # pylint: disable=W0212
        self._lines.extend(other._lines)

        return self

    def insert(self, index: int, value: str) -> StringBuilder:
        """Inserts a string into this instance at the specified position.

        Args:
            index (int): The zero-based position at which ``value`` is
                inserted. Must be between ``0`` and the current length
                of this instance, inclusive. An ``index`` equal to the
                current length appends ``value`` at the end.
            value (str): The string to insert.

        Returns:
            StringBuilder: This instance, to allow method chaining.

        Raises:
            ValueError: If ``index`` is negative or greater than the
                current length of this instance.
        """

        assert isinstance(index, int), type(index)
        assert isinstance(value, str), type(value)

        if index < 0:
            raise ValueError(f"'index' must not be negative: {index}.")

        joined = "".join(self._lines)
        if index > len(joined):
            raise ValueError(
                "'index' exceeds the current length: "
                f"{index} > {len(joined)}."
            )

        if not value:
            return self

        self._lines = [joined[:index] + value + joined[index:]]

        return self

    def remove(self, start_index: int, length: int) -> StringBuilder:
        """Removes the specified range of characters from this instance.

        Args:
            start_index (int): The zero-based position at which to
                begin removing characters.
            length (int): The number of characters to remove.

        Returns:
            StringBuilder: This instance, to allow method chaining.

        Raises:
            ValueError: If ``start_index`` or ``length`` is negative,
                or if ``start_index + length`` exceeds the current
                length of this instance.
        """

        assert isinstance(start_index, int), type(start_index)
        assert isinstance(length, int), type(length)

        if start_index < 0:
            raise ValueError(
                f"'start_index' must not be negative: {start_index}."
            )
        if length < 0:
            raise ValueError(f"'length' must not be negative: {length}.")

        joined = "".join(self._lines)
        if start_index + length > len(joined):
            raise ValueError(
                "'start_index' + 'length' exceeds the current length: "
                f"{start_index} + {length} > {len(joined)}."
            )

        self._lines = [joined[:start_index] + joined[start_index + length :]]

        return self
