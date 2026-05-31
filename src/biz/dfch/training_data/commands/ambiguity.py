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

"""'ambiguity' command."""

from pathlib import Path


from dotenv import load_dotenv
import typer

from biz.dfch.asdste100vocab import Vocab
from biz.dfch.asdste100vocab import Word
from biz.dfch.asdste100vocab import WordStatus

from biz.dfch.logging import log

from ..ste100approved import STE100Approved
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
def ambiguity(
    ctx: typer.Context,
    output: OutputArg = Path("."),
    file: NameArg = "task01.jsonl",
    overwrite: OverwriteArg = False,
):
    """
    Make the dataset for "Task 1: Ambiguity".

    Issue #1, 
    https://github.com/dfensgmbh/AsdSte100Issue9TrainingData/issues/1

    Iterates over all words in the ASD-STE100 vocabulary and emits one
    JSONL training example per approved usage example (both top-level
    ``ste_example`` entries and per-meaning ``ste_example`` entries).
    Each line is produced via :class:`STE100Approved` and contains the
    sentence, the target word, and its part of speech.

    Args:
        ctx (typer.Context): The Typer context (unused; kept so the
            command participates in the Typer application lifecycle).
        output (OutputArg): Directory in which the dataset file is
            written. Must exist. Defaults to the current directory.
        file (NameArg): Name of the output JSONL file. Defaults to
            ``"task01.jsonl"``.
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
        "ambiguity: output=%s, file=%s, overwrite=%s",
        output,
        file,
        overwrite,
    )

    lines: list[str] = []
    errors: list[str] = []

    v = Vocab()
    words = list(v)

    for w in words:
        if w.status != WordStatus.APPROVED:
            continue

        _lines, _errors = _process_approved_word(w)
        lines.extend(_lines)
        errors.extend(_errors)

    log.info("errors: '%s'", len(errors))
    log.info("lines: '%s'", len(lines))
    for error in errors:
        log.warning("error: %s", error)

    log.info("[%s] Writing file '%s' ...", len(lines), path)
    path.write_text("\n".join(lines), encoding="utf-8")

    return


def _process_approved_word(item: Word) -> tuple[list[str], list[str]]:
    """Process an APPROVED word."""

    assert isinstance(item, Word), type(item)
    assert WordStatus.APPROVED == item.status, item.status

    lines: list[str] = []
    errors: list[str] = []
    result = (lines, errors)

    for s in item.ste_example:
        try:
            line = STE100Approved(
                sentence=s,
                word=item.name,
                pos=item.type_,
            )
            lines.append(str(line))

        except Exception:  # pylint: disable=W0718
            error = f"[{item.name}] ({item.type_} '{s}')"
            errors.append(error)

    for m in item.meanings:
        if m.ste_example is None or not m.ste_example.strip():
            continue
        s = m.ste_example
        try:
            line = STE100Approved(
                sentence=s,
                word=item.name,
                pos=item.type_,
            )
            lines.append(str(line))

        except Exception:  # pylint: disable=W0718
            error = f"[{item.name}] ({item.type_} '{s}')"
            errors.append(error)

    return result
