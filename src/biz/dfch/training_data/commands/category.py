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

"""'category' command."""

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
def category(
    ctx: typer.Context,
    output: OutputArg = Path("."),
    file: NameArg = "task11.jsonl",
    overwrite: OverwriteArg = False,
):
    """
    Make the dataset for "Task 11: Category-Based Word Restrictions".

    Issue #11,
    https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/11

    Generates training examples that explain why a word is rejected
    based on general ASD-STE100 categories (for example "compound
    verbs" or "helping verbs") and that name the approved direct verb
    or alternative.

    Args:
        ctx (typer.Context): The Typer context (unused; required so the
            command integrates with the parent Typer application).
        output (OutputArg): Directory in which the dataset file is
            written. Must exist. Defaults to the current directory.
        file (NameArg): Name of the output JSONL file. Defaults to
            ``"task11.jsonl"``.
        overwrite (OverwriteArg): When ``True``, an existing output
            file is replaced without prompting. When ``False`` and the
            file exists, the user is asked for confirmation.

    Raises:
        AssertionError: If ``output`` is not a :class:`Path` or does
            not exist on disk.
        typer.Abort: If the output file exists and the user declines
            to overwrite it.

    Returns:
        None: The dataset is written to disk as a side effect.
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
        "category: output=%s, file=%s, overwrite=%s", output, file, overwrite
    )

    return
