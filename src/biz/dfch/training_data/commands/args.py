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

"""Shared command arguments."""

from pathlib import Path
from typing import Annotated

import typer


def _validate_output(value: Path) -> Path:
    if not value.exists():
        raise typer.BadParameter(f"Directory '{value}' does not exist.")
    if not value.is_dir():
        raise typer.BadParameter(f"'{value}' is not a directory.")
    return value


OutputArg = Annotated[
    Path,
    typer.Option(
        "--output",
        "-o",
        help="Name of the output directory.",
        show_default=True,
        callback=_validate_output,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        envvar="OUTPUT_PATH",
    ),
]

NameArg = Annotated[
    str,
    typer.Option(
        "--name",
        "-n",
        help="Name of the output file.",
        show_default=True,
        file_okay=True,
        dir_okay=False,
        envvar="OUTPUT_NAME",
    ),
]

OverwriteArg = Annotated[
    bool,
    typer.Option(
        "--overwrite/--no-overwrite",
        "-y/-n",
        help="Overwrite the output file if it already exists.",
        show_default=True,
    ),
]
