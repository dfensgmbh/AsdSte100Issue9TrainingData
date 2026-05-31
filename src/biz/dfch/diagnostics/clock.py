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

import threading
from datetime import datetime, timedelta, timezone, tzinfo


class Clock:
    """A utility class for returning the current date and time in various
    formats.

    All datetimes returned by :class:`Clock` are timezone-aware. By
    default the local timezone (as reported by the operating system) is
    used; this can be overridden by calling :meth:`_set_timezone`.

    The clock supports three modes of operation:

    * **Live** (default): returns the current wall-clock time in the
      configured timezone.
    * **Offset**: configured with :meth:`_set_datetime`. A constant
      offset between wall-clock time and a target datetime is captured
      once, and subsequent calls return ``now() + offset`` so the clock
      continues to advance in real time but anchored to the supplied
      datetime.
    * **Frozen**: configured with :meth:`_set_frozen`. The clock is
      pinned to a fixed datetime and does not advance.

    :meth:`_reset` returns the clock to live mode.

        Notes:
        * The class is intended to be used via its class methods; do
          not instantiate it.
        * State is class-level and is therefore process-global. All
          read and write access to that state is serialized by an
          internal :class:`threading.RLock`, so concurrent calls from
          multiple threads are safe.
        * Naive datetimes passed to :meth:`_set_datetime`,
          :meth:`_set_frozen`, :meth:`format_isodate` or
          :meth:`format_file` are assumed to be in the configured
          timezone and are attached accordingly.
        * Millisecond formatting truncates microseconds; it does not
          round.

    Usage:
        Clock.now()                    # live system time (aware)
        Clock._set_datetime(dt)        # offset clock from dt
        Clock._set_frozen(dt)          # freeze clock to dt
        Clock._set_timezone(tz)        # change the active timezone
        Clock._reset()                 # back to live system time
    """

    _dt: datetime | None = None
    _offset: timedelta = timedelta(0)
    _frozen: bool = False
    _tz: tzinfo = datetime.now().astimezone().tzinfo or timezone.utc
    _lock: threading.RLock = threading.RLock()

    @classmethod
    def _ensure_aware(cls, dt: datetime) -> datetime:
        """Return ``dt`` with tzinfo set, assuming the active timezone
        when ``dt`` is naive."""
        assert isinstance(dt, datetime), type(dt)
        if dt.tzinfo is None:
            with cls._lock:
                return dt.replace(tzinfo=cls._tz)
        return dt

    @classmethod
    def _set_timezone(cls, tz: tzinfo) -> None:
        """Set the active timezone used by the clock.

        Affects the timezone returned by :meth:`now` in live mode and
        the timezone attached to naive datetimes passed to the other
        configuration methods.
        """
        assert isinstance(tz, tzinfo), type(tz)
        with cls._lock:
            cls._tz = tz

    @classmethod
    def _set_datetime(cls, dt: datetime) -> None:
        """Set the clock to count onwards from the specified datetime.

        The offset between ``dt`` and the current wall-clock time is
        captured once at the moment of the call; the clock then
        advances in real time anchored to that offset.
        """
        with cls._lock:
            dt = cls._ensure_aware(dt)
            cls._dt = dt
            cls._offset = dt - datetime.now(tz=cls._tz)
            cls._frozen = False

    @classmethod
    def _set_frozen(cls, dt: datetime | None = None) -> None:
        """Freeze the clock to the specified datetime (or to the current
        time when ``dt`` is ``None``)."""
        with cls._lock:
            if dt is None:
                cls._dt = datetime.now(tz=cls._tz)
            else:
                cls._dt = cls._ensure_aware(dt)
            cls._offset = timedelta(0)
            cls._frozen = True

    @classmethod
    def _reset(cls) -> None:
        """Reset the clock to the live system time."""
        with cls._lock:
            cls._dt = None
            cls._offset = timedelta(0)
            cls._frozen = False

    @classmethod
    def _current(cls) -> datetime:
        """Return the effective current datetime (timezone-aware)."""
        with cls._lock:
            if cls._dt is None:
                return datetime.now(tz=cls._tz)
            if cls._frozen:
                return cls._dt
            return datetime.now(tz=cls._tz) + cls._offset

    @classmethod
    def now(cls) -> datetime:
        """Return the current timezone-aware datetime."""
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

        Naive datetimes are treated as being in the active timezone.

        Example:
            "1927-03-27 08:15:42.123"
        """
        assert isinstance(dt, datetime), type(dt)
        dt = cls._ensure_aware(dt)

        return (
            dt.strftime("%Y-%m-%d %H:%M:%S.") + f"{dt.microsecond // 1000:03d}"
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

        Suitable for use in filenames. Naive datetimes are treated as
        being in the active timezone.

        Example:
            "1927-03-27---08-15-42"
        """

        assert isinstance(dt, datetime), type(dt)
        dt = cls._ensure_aware(dt)

        return dt.strftime("%Y-%m-%d---%H-%M-%S")
