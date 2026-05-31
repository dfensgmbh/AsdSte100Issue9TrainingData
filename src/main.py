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

"""Backwards-compatible entry point shim.

The canonical Typer application now lives in
:mod:`biz.dfch.training_data.cli`. This module simply re-exports
``app`` for any caller that still imports ``main:app`` (for example,
the legacy console-script entry in ``pyproject.toml`` or
``src/biz/__main__.py``).

Prefer one of the following invocation styles:

* ``create`` (the installed console script)
* ``python -m biz.dfch.training_data``
* ``python -m biz.dfch.training_data.cli``
"""

from biz.dfch.training_data.cli import app

if __name__ == "__main__":
    app()
