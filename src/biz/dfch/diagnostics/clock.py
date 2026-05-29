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

"""Datetime class."""

from __future__ import annotations

from datetime import datetime, timedelta


class Clock:
    """A utility class for returning the current date and time in various
    formats.

    By default, the clock uses the live system time. Use set_datetime() and
    set_frozen() to configure offset or frozen behaviour.

    Usage:
        Clock.now()                    # live system time
        Clock.set_datetime(dt)         # offset clock from dt
        Clock.set_frozen(dt)           # freeze clock to dt
        Clock.reset()                  # back to live system time
    """

    _dt: datetime | None = None
    _frozen: bool = False

    @classmethod
    def _set_datetime(cls, dt: datetime) -> None:
        """Set the clock to count onwards from the specified datetime."""
        cls._dt = dt
        cls._frozen = False

    @classmethod
    def _set_frozen(cls, dt: datetime | None = None) -> None:
        """Freeze the clock to the specified datetime."""
        if dt is None:
            cls._dt = datetime.now()
        else:
            cls._dt = dt
        cls._frozen = True

    @classmethod
    def _reset(cls) -> None:
        """Reset the clock to the live system time."""
        cls._dt = None
        cls._frozen = False

    @classmethod
    def _current(cls) -> datetime:
        """Return the effective current datetime."""
        if cls._dt is None:
            return datetime.now()
        if cls._frozen:
            return cls._dt
        offset = (cls._dt - datetime.now()).total_seconds()
        return datetime.now() + timedelta(seconds=offset)

    @classmethod
    def now(cls) -> datetime:
        """Return the current datetime'."""
        return cls._current()

    @classmethod
    def now_isodate(cls) -> str:
        """Return the current datetime as 'yyyy-MM-dd HH:mm:ss.fff'.

        Example:
            "1927-03-27 08:15:42.123"
        """
        current = cls._current()
        return (
            current.strftime("%Y-%m-%d %H:%M:%S.")
            + f"{current.microsecond // 1000:03d}"
        )

    @classmethod
    def format_isodate(cls, dt: datetime) -> str:
        """Return the specified datetime as 'yyyy-MM-dd HH:mm:ss.fff'.

        Example:
            "1927-03-27 08:15:42.123"
        """
        assert isinstance(dt, datetime), type(dt)

        return (
            dt.strftime("%Y-%m-%d %H:%M:%S.")
            + f"{dt.microsecond // 1000:03d}"
        )

    @classmethod
    def now_file(cls) -> str:
        """Return the current datetime as 'yyyy-MM-dd---HH-mm-ss'.

        Suitable for use in filenames.

        Example:
            "1927-03-27---08-15-42"
        """
        return cls._current().strftime("%Y-%m-%d---%H-%M-%S")

    @classmethod
    def format_file(cls, dt: datetime) -> str:
        """Return the specified datetime as 'yyyy-MM-dd---HH-mm-ss'.

        Suitable for use in filenames.

        Example:
            "1927-03-27---08-15-42"
        """

        assert isinstance(dt, datetime), type(dt)

        return dt.strftime("%Y-%m-%d---%H-%M-%S")
