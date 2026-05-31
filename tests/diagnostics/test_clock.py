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

"""Unit tests for the :class:`Clock` class."""

import re
import threading
import time
import unittest
from datetime import datetime, timedelta, timezone

from biz.dfch.diagnostics import Clock
from biz.dfch.diagnostics.clock import Clock as DirectClock


ISO_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}$"
)
FILE_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}---\d{2}-\d{2}-\d{2}$"
)


class TestClock(unittest.TestCase):
    """Unit tests for :class:`Clock`."""

    def setUp(self):
        # Ensure every test starts from the live-mode default.
        Clock._reset()

    def tearDown(self):
        # Don't leak state across tests.
        Clock._reset()

    # ----- package / module identity --------------------------------

    def test_package_export_matches_module(self):
        """The class re-exported from the package is the module class."""
        self.assertIs(Clock, DirectClock)

    # ----- live mode -------------------------------------------------

    def test_now_returns_datetime(self):
        """`now` returns a :class:`datetime.datetime` instance."""
        self.assertIsInstance(Clock.now(), datetime)

    def test_now_is_timezone_aware(self):
        """`now` returns a timezone-aware datetime in live mode."""
        self.assertIsNotNone(Clock.now().tzinfo)

    def test_now_is_close_to_system_time(self):
        """`now` in live mode is close to the OS wall-clock time."""
        before = datetime.now().astimezone()
        value = Clock.now()
        after = datetime.now().astimezone()
        self.assertLessEqual(before - timedelta(seconds=1), value)
        self.assertGreaterEqual(after + timedelta(seconds=1), value)

    def test_now_advances_over_time(self):
        """`now` advances on successive calls in live mode."""
        first = Clock.now()
        time.sleep(0.02)
        second = Clock.now()
        self.assertGreater(second, first)

    # ----- frozen mode ----------------------------------------------

    def test_set_frozen_with_explicit_datetime(self):
        """`_set_frozen(dt)` pins `now` to ``dt``."""
        dt = datetime(2000, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
        Clock._set_frozen(dt)
        self.assertEqual(dt, Clock.now())

    def test_set_frozen_is_stable_over_time(self):
        """A frozen clock returns the same value across successive calls."""
        dt = datetime(2000, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
        Clock._set_frozen(dt)
        first = Clock.now()
        time.sleep(0.02)
        second = Clock.now()
        self.assertEqual(first, second)
        self.assertEqual(dt, second)

    def test_set_frozen_without_argument_uses_now(self):
        """`_set_frozen()` (no arg) pins to the wall-clock time of the call."""
        before = datetime.now().astimezone()
        Clock._set_frozen()
        after = datetime.now().astimezone()
        value = Clock.now()
        self.assertLessEqual(before - timedelta(seconds=1), value)
        self.assertGreaterEqual(after + timedelta(seconds=1), value)
        # Still stable on subsequent calls.
        time.sleep(0.02)
        self.assertEqual(value, Clock.now())

    def test_set_frozen_attaches_active_timezone_to_naive_input(self):
        """A naive datetime passed to `_set_frozen` gets the active tz."""
        Clock._set_timezone(timezone.utc)
        naive = datetime(2000, 1, 2, 3, 4, 5)
        Clock._set_frozen(naive)
        value = Clock.now()
        self.assertEqual(timezone.utc, value.tzinfo)
        self.assertEqual(naive.replace(tzinfo=timezone.utc), value)

    # ----- offset mode ----------------------------------------------

    def test_set_datetime_returns_value_near_target(self):
        """`_set_datetime(dt)` immediately reports a time near ``dt``."""
        target = datetime(2030, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        Clock._set_datetime(target)
        value = Clock.now()
        # Some small amount of wall-clock time elapses between the
        # capture of `_offset` inside `_set_datetime` and the call to
        # `now()` here; that elapsed time is added to `target`.
        self.assertGreaterEqual(value, target)
        self.assertLess(value - target, timedelta(seconds=1))

    def test_set_datetime_advances_in_real_time(self):
        """An offset clock advances at real-time rate."""
        target = datetime(2030, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        Clock._set_datetime(target)
        first = Clock.now()
        time.sleep(0.05)
        second = Clock.now()
        delta = second - first
        self.assertGreaterEqual(delta, timedelta(seconds=0.04))
        self.assertLess(delta, timedelta(seconds=1))

    def test_set_datetime_attaches_active_timezone_to_naive_input(self):
        """`_set_datetime` treats a naive input as the active timezone."""
        Clock._set_timezone(timezone.utc)
        naive = datetime(2030, 6, 1, 12, 0, 0)
        Clock._set_datetime(naive)
        self.assertEqual(timezone.utc, Clock.now().tzinfo)

    # ----- reset -----------------------------------------------------

    def test_reset_returns_to_live_mode_after_frozen(self):
        """`_reset` returns to live mode from a frozen state."""
        Clock._set_frozen(
            datetime(2000, 1, 1, tzinfo=timezone.utc)
        )
        Clock._reset()
        now_after = Clock.now()
        system_now = datetime.now().astimezone()
        self.assertLess(
            abs((now_after - system_now).total_seconds()), 1.0
        )

    def test_reset_returns_to_live_mode_after_offset(self):
        """`_reset` returns to live mode from an offset state."""
        Clock._set_datetime(
            datetime(2030, 1, 1, tzinfo=timezone.utc)
        )
        Clock._reset()
        now_after = Clock.now()
        system_now = datetime.now().astimezone()
        self.assertLess(
            abs((now_after - system_now).total_seconds()), 1.0
        )

    def test_reset_on_live_clock_is_noop(self):
        """Calling `_reset` on an already-live clock is harmless."""
        Clock._reset()
        Clock._reset()
        self.assertIsInstance(Clock.now(), datetime)

    # ----- timezone --------------------------------------------------

    def test_set_timezone_changes_now_tzinfo(self):
        """`_set_timezone` changes the tzinfo returned by `now`."""
        Clock._set_timezone(timezone.utc)
        self.assertEqual(timezone.utc, Clock.now().tzinfo)

        plus5 = timezone(timedelta(hours=5))
        Clock._set_timezone(plus5)
        self.assertEqual(plus5, Clock.now().tzinfo)

    def test_set_timezone_rejects_non_tzinfo(self):
        """`_set_timezone` raises ``AssertionError`` for non-tzinfo."""
        with self.assertRaises(AssertionError):
            Clock._set_timezone("UTC")  # type: ignore[arg-type]

    def test_ensure_aware_passes_through_aware_datetime(self):
        """`_ensure_aware` returns an aware datetime unchanged."""
        aware = datetime(2024, 5, 6, 7, 8, 9, tzinfo=timezone.utc)
        result = Clock._ensure_aware(aware)
        self.assertIs(aware, result)

    def test_ensure_aware_attaches_active_timezone_to_naive(self):
        """`_ensure_aware` attaches the active timezone to a naive value."""
        Clock._set_timezone(timezone.utc)
        naive = datetime(2024, 5, 6, 7, 8, 9)
        result = Clock._ensure_aware(naive)
        self.assertEqual(timezone.utc, result.tzinfo)
        self.assertEqual(naive.replace(tzinfo=timezone.utc), result)

    def test_ensure_aware_rejects_non_datetime(self):
        """`_ensure_aware` raises ``AssertionError`` for non-datetime."""
        with self.assertRaises(AssertionError):
            Clock._ensure_aware("not-a-datetime")  # type: ignore[arg-type]

    # ----- formatting: now_isodate -----------------------------------

    def test_now_isodate_matches_pattern(self):
        """`now_isodate` returns a string in the documented format."""
        self.assertRegex(Clock.now_isodate(), ISO_PATTERN)

    def test_now_isodate_against_frozen_value(self):
        """`now_isodate` formats the frozen datetime correctly."""
        dt = datetime(1927, 3, 27, 8, 15, 42, 123456, tzinfo=timezone.utc)
        Clock._set_frozen(dt)
        self.assertEqual("1927-03-27 08:15:42.123", Clock.now_isodate())

    def test_now_isodate_truncates_milliseconds(self):
        """`now_isodate` truncates microseconds rather than rounding."""
        # 999999 microseconds == 999.999 ms; truncated → 999, not 1000.
        dt = datetime(2024, 1, 1, 0, 0, 0, 999999, tzinfo=timezone.utc)
        Clock._set_frozen(dt)
        self.assertEqual("2024-01-01 00:00:00.999", Clock.now_isodate())

    # ----- formatting: format_isodate --------------------------------

    def test_format_isodate_with_aware_datetime(self):
        """`format_isodate` formats an aware datetime correctly."""
        dt = datetime(1927, 3, 27, 8, 15, 42, 123456, tzinfo=timezone.utc)
        self.assertEqual(
            "1927-03-27 08:15:42.123", Clock.format_isodate(dt)
        )

    def test_format_isodate_with_naive_datetime(self):
        """`format_isodate` accepts a naive datetime (treated as active tz).

        The string content (year/month/day/time) does not depend on the
        timezone, so we just verify the format.
        """
        dt = datetime(1927, 3, 27, 8, 15, 42, 123456)
        self.assertEqual(
            "1927-03-27 08:15:42.123", Clock.format_isodate(dt)
        )

    def test_format_isodate_rejects_non_datetime(self):
        """`format_isodate` raises ``AssertionError`` for non-datetime."""
        with self.assertRaises(AssertionError):
            Clock.format_isodate("2024-01-01")  # type: ignore[arg-type]

    # ----- formatting: now_file --------------------------------------

    def test_now_file_matches_pattern(self):
        """`now_file` returns a string in the documented format."""
        self.assertRegex(Clock.now_file(), FILE_PATTERN)

    def test_now_file_against_frozen_value(self):
        """`now_file` formats the frozen datetime correctly."""
        dt = datetime(1927, 3, 27, 8, 15, 42, tzinfo=timezone.utc)
        Clock._set_frozen(dt)
        self.assertEqual("1927-03-27---08-15-42", Clock.now_file())

    # ----- formatting: format_file -----------------------------------

    def test_format_file_with_aware_datetime(self):
        """`format_file` formats an aware datetime correctly."""
        dt = datetime(1927, 3, 27, 8, 15, 42, tzinfo=timezone.utc)
        self.assertEqual("1927-03-27---08-15-42", Clock.format_file(dt))

    def test_format_file_with_naive_datetime(self):
        """`format_file` accepts a naive datetime (treated as active tz)."""
        dt = datetime(1927, 3, 27, 8, 15, 42)
        self.assertEqual("1927-03-27---08-15-42", Clock.format_file(dt))

    def test_format_file_rejects_non_datetime(self):
        """`format_file` raises ``AssertionError`` for non-datetime."""
        with self.assertRaises(AssertionError):
            Clock.format_file("2024-01-01")  # type: ignore[arg-type]

    # ----- mode transitions ------------------------------------------

    def test_frozen_then_offset_mode_switches_correctly(self):
        """Switching from frozen to offset mode behaves as offset mode."""
        Clock._set_frozen(datetime(2000, 1, 1, tzinfo=timezone.utc))
        target = datetime(2030, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        Clock._set_datetime(target)
        first = Clock.now()
        time.sleep(0.02)
        second = Clock.now()
        self.assertGreaterEqual(first, target)
        self.assertGreater(second, first)

    def test_offset_then_frozen_mode_switches_correctly(self):
        """Switching from offset to frozen mode pins the value."""
        Clock._set_datetime(
            datetime(2030, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        )
        frozen_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
        Clock._set_frozen(frozen_at)
        self.assertEqual(frozen_at, Clock.now())
        time.sleep(0.02)
        self.assertEqual(frozen_at, Clock.now())

    # ----- thread safety ---------------------------------------------

    def test_concurrent_now_calls_are_safe(self):
        """Concurrent `now` calls return valid datetimes from many threads."""
        results: list[datetime] = []
        errors: list[BaseException] = []
        lock = threading.Lock()

        def worker():
            try:
                for _ in range(50):
                    value = Clock.now()
                    with lock:
                        results.append(value)
            except BaseException as ex:  # pragma: no cover - defensive
                with lock:
                    errors.append(ex)

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual([], errors)
        self.assertEqual(8 * 50, len(results))
        for value in results:
            self.assertIsInstance(value, datetime)
            self.assertIsNotNone(value.tzinfo)

    def test_concurrent_mutations_leave_clock_consistent(self):
        """Concurrent reads and writes never produce an invalid state."""
        frozen_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
        stop = threading.Event()
        errors: list[BaseException] = []
        lock = threading.Lock()

        def reader():
            try:
                while not stop.is_set():
                    value = Clock.now()
                    assert isinstance(value, datetime)
                    assert value.tzinfo is not None
            except BaseException as ex:
                with lock:
                    errors.append(ex)

        def writer():
            try:
                for _ in range(100):
                    Clock._set_frozen(frozen_at)
                    Clock._reset()
                    Clock._set_datetime(
                        datetime(
                            2030, 6, 1, 12, 0, 0, tzinfo=timezone.utc
                        )
                    )
                    Clock._reset()
            except BaseException as ex:
                with lock:
                    errors.append(ex)

        readers = [threading.Thread(target=reader) for _ in range(4)]
        writers = [threading.Thread(target=writer) for _ in range(2)]
        for t in readers + writers:
            t.start()
        for t in writers:
            t.join()
        stop.set()
        for t in readers:
            t.join()

        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()