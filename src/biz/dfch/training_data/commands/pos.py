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

"""'pos-context' command."""

from pathlib import Path


from dotenv import load_dotenv
import typer

from biz.dfch.logging import log

from .args import NameArg, OutputArg, OverwriteArg

from ..info import Info

load_dotenv()

app = typer.Typer(
    name=Info.name,
    help=Info.description,
    epilog=Info.epilog,
    no_args_is_help=True,
)


@app.command()
def pos(
    ctx: typer.Context,
    output: OutputArg = Path("."),
    file: NameArg = "task03.jsonl",
    overwrite: OverwriteArg = False,
):
    """
    Make the dataset for "Task 3: POS Identification in Context".

    Issue #3, https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/3
    """

    _ = ctx

    assert isinstance(output, Path), type(Path)
    assert output.exists(), f"Path must exist: '{output}'."

    path = Path(output / file).resolve()

    if path.exists() and not overwrite:
        overwrite = typer.confirm(
            f"File '{path}' already exists. Overwrite?",
            default=False,
        )
        if not overwrite:
            raise typer.Abort()

    log.debug(
        "pos_context: output=%s, file=%s, overwrite=%s", output, file, overwrite
    )

    return
