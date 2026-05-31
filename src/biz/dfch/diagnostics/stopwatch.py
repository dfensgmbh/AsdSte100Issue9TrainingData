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

"""Stopwatch class."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class Stopwatch:
    """A high-resolution stopwatch,
    modelled after .NET System.Diagnostics.Stopwatch.

    Measures elapsed time with microsecond precision using time.perf_counter().
    Supports start/stop/reset/restart and accumulates elapsed time across
    multiple start/stop cycles.

    Example:
        sw = Stopwatch.start_new()
        time.sleep(1.0)
        sw.stop()
        print(sw)  # 1000.123ms
    """

    _start: float = field(default=0.0, init=False, repr=False)
    _elapsed: float = field(default=0.0, init=False, repr=False)
    _running: bool = field(default=False, init=False, repr=False)

    @staticmethod
    def start_new() -> Stopwatch:
        """Create and immediately start a new Stopwatch.

        Equivalent to .NET's Stopwatch.StartNew().

        Returns:
            A new running Stopwatch instance.
        """
        sw = Stopwatch()
        sw.start()
        return sw

    def start(self) -> None:
        """Start or resume the stopwatch.

        Has no effect if the stopwatch is already running.
        Elapsed time accumulates across multiple start/stop cycles.
        """
        if not self._running:
            self._start = time.perf_counter()
            self._running = True

    def stop(self) -> None:
        """Stop the stopwatch.

        Has no effect if the stopwatch is already stopped.
        Elapsed time is preserved and accumulates on the next start().
        """
        if self._running:
            self._elapsed += time.perf_counter() - self._start
            self._running = False

    def reset(self) -> None:
        """Reset elapsed time to zero and stop."""
        self._elapsed = 0.0
        self._running = False

    def restart(self) -> None:
        """Reset and immediately start again."""
        self._elapsed = 0.0
        self._start = time.perf_counter()
        self._running = True

    @property
    def is_running(self) -> bool:
        """bool: True if the stopwatch is currently running."""
        return self._running

    @property
    def elapsed_seconds(self) -> float:
        """float: Total elapsed time in seconds.

        Returns the live value if the stopwatch is still running.
        """
        if self._running:
            return self._elapsed + (time.perf_counter() - self._start)
        return self._elapsed

    @property
    def elapsed_ms(self) -> float:
        """float: Total elapsed time in milliseconds."""
        return self.elapsed_seconds * 1_000

    @property
    def elapsed_us(self) -> float:
        """float: Total elapsed time in microseconds."""
        return self.elapsed_seconds * 1_000_000

    def __str__(self) -> str:
        """Return a human-readable string of the elapsed time in milliseconds.

        Example:
            "1200.123ms"
        """
        return f"{self.elapsed_ms:.3f}ms"
