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

import json
import dataclasses
from pathlib import Path

from dotenv import load_dotenv
import typer

from biz.dfch.asdste100vocab import Vocab
from biz.dfch.asdste100vocab import Word
from biz.dfch.asdste100vocab import WordType
from biz.dfch.asdste100vocab import WordStatus

from biz.dfch.logging import log
from biz.dfch.text import StringBuilder

from ..schema import Squad
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

    items: list[Squad] = []
    errors: list[str] = []

    v = Vocab()
    words = list(v)

    skip_duplicates: list[str] = []
    for w in words:
        if w.status not in (WordStatus.APPROVED, WordStatus.REJECTED):
            continue

        items.extend(get_rewrite(w))

        if w.name in skip_duplicates:
            continue

        duplicates = v.find(w.name)
        assert 0 < len(duplicates), w.name
        if 1 == len(duplicates):
            squad = get_word_definition(w)
            items.append(squad)
        else:
            skip_duplicates.append(w.name)
            d_squads = [get_word_definition(d) for d in duplicates]
            d_answer = StringBuilder()
            for d in d_squads:
                d_answer.write(d.answers["text"][0])
                d_answer.write(" | ")
            squad = Squad.make(
                title=d_squads[0].title,
                context=d_squads[0].context,
                question=d_squads[0].question,
                answer="It depends on POS. | "
                + d_answer.to_string().strip().strip("|").strip(),
            )
            items.append(squad)

    log.info("errors: '%s'", len(errors))
    log.info("lines: '%s'", len(items))
    for error in errors:
        log.warning("error: %s", error)

    sb = StringBuilder()
    for item in items:
        text = json.dumps(dataclasses.asdict(item))
        sb.write_line(text)

    log.info("[%s] Writing file '%s' ...", len(items), path)
    path.write_text(sb.to_string(), encoding="utf-8")

    return


def _format_type(type_: WordType) -> str:
    vowels_lower = "aeiou"
    return (
        "an" if type_.name[0].lower() in vowels_lower else "a"
    ) + f" '{type_.name}'"


def get_word_definition(item: Word) -> Squad:
    """Process an ASD-STE100 word."""

    assert isinstance(item, Word), type(item)
    assert item.status in (
        WordStatus.APPROVED,
        WordStatus.REJECTED,
    ), item.status

    title = "TASK01A"
    context = "You are an expert on the ASD-STE100 Simplified Technical English Standard."

    # {"prompt":"Give me the ASD-STE100 entry for 'exact' as an adjective.","response":"WORD: exact | POS: adj | STATUS: rejected | ALTERNATIVE_1: ACCURATE (adj) | EXAMPLE_STE_1: IF THE INDICATION IS NOT ACCURATE, DO THE TEST AGAIN. | EXAMPLE_NONSTE_1: If the indication is not exact, do the test again. | ALTERNATIVE_2: CORRECT (adj) | EXAMPLE_STE_2: IF THE INDICATION IS NOT CORRECT, DO THE TEST AGAIN. | EXAMPLE_NONSTE_2: If the indication is not exact, do the test again. | SOURCE: STE100:9"}
    # {"prompt":"Is 'exact' approved as an adjective in ASD-STE100?","response":"No. REJECTED. Use ACCURATE or CORRECT."}
    # {"prompt":"What is the status of 'exact' in ASD-STE100?","response":"As an adjective: REJECTED. Use ACCURATE or CORRECT."}
    # {"prompt":"Rewrite in ASD-STE100: 'If the indication is not exact, do the test again.'","response":"IF THE INDICATION IS NOT ACCURATE, DO THE TEST AGAIN.\nReason: 'exact' as an adjective is REJECTED; use ACCURATE."}

    # {
    #     "prompt": "What does ASD-STE100 define for 'exact'?",
    #     "response": "WORD: exact | POS: adj | STATUS: rejected | "
    #     "ALTERNATIVE_1: ACCURATE (adj) | "
    #     "EXAMPLE_STE_1: IF THE INDICATION IS NOT ACCURATE, DO THE TEST AGAIN. | "
    #     "EXAMPLE_NONSTE_1: If the indication is not exact, do the test again. | "
    #     "ALTERNATIVE_2: CORRECT (adj) | "
    #     "EXAMPLE_STE_2: IF THE INDICATION IS NOT CORRECT, "
    #     "DO THE TEST AGAIN. | EXAMPLE_NONSTE_2: If the indication is not exact, "
    #     "do the test again. | SOURCE: STE100:9"
    # }

    question = f"What does ASD-STE100 define for '{item.name.lower()}'?"
    answer = StringBuilder()

    answer.format(
        "WORD: %s | POS: %s | STATUS: %s | ",
        item.name.lower(),
        item.type_.name.lower(),
        item.status.lower(),
    )

    if WordStatus.REJECTED == item.status:
        for i, a in enumerate(item.alternatives):
            i += 1
            answer.format(
                "ALTERNATIVE_%s: %s (%s) | ",
                i,
                a.name.lower(),
                item.type_.name.lower(),
            )
            for e in a.ste_example:
                answer.format("EXAMPLE_STE_%s: %s | ", i, e)
            for e in a.nonste_example:
                answer.format("EXAMPLE_NONSTE_%s: %s | ", i, e)
        answer.format("SOURCE: %s | ", item.source)

        if 1 == len(item.alternatives):
            answer.replace("ALTERNATIVE_1:", "ALTERNATIVE:")
            answer.replace("EXAMPLE_STE_1:", "EXAMPLE_STE:")
            answer.replace("EXAMPLE_NONSTE_1:", "EXAMPLE_NONSTE:")

    elif WordStatus.APPROVED == item.status:
        for i, m in enumerate(item.meanings):
            i += 1
            if m.value.replace('\u200b', '').strip():
                answer.format("MEANING_%s: %s | ", i, m.value)
            if m.ste_example:
                e = m.ste_example
                answer.format("EXAMPLE_STE_%s: %s | ", i, e)
            if m.nonste_example:
                e = m.nonste_example
                answer.format("EXAMPLE_NONSTE_%s: %s | ", i, e)
        if 1 == len(item.meanings):
            answer.replace("MEANING_1:", "MEANING:")
            answer.replace("EXAMPLE_STE_1:", "EXAMPLE_STE:")
            answer.replace("EXAMPLE_NONSTE_1:", "EXAMPLE_NONSTE:")
    answer.format("SOURCE: %s | ", item.source)

    result = Squad.make(
        title=title,
        context=context,
        question=question,
        answer=answer.to_string().strip().strip("|").strip(),
    )

    return result


def get_rewrite(item: Word) -> list[Squad]:
    """Rewrite in ASD-STE100."""

    assert isinstance(item, Word), type(item)
    assert item.status in (
        WordStatus.APPROVED,
        WordStatus.REJECTED,
    ), item.status

    result: list[Squad] = []

    if WordStatus.APPROVED == item.status:
        return result

    title = "TASK01B"
    context = "You are an expert on the ASD-STE100 Simplified Technical English Standard."

    # {"prompt":"Rewrite in ASD-STE100: 'If the indication is not exact, do the test again.'","response":"IF THE INDICATION IS NOT ACCURATE, DO THE TEST AGAIN.\nReason: 'exact' as an adjective is REJECTED; use ACCURATE."}

    for a in item.alternatives:

        examples = list(zip(a.ste_example, a.nonste_example))
        for ex in examples:
            question = f"Rewrite in ASD-STE100: '{ex[1]}'"
            answer = ex[0]

            squad = Squad.make(
                title=title,
                context=context,
                question=question,
                answer=answer,
            )
            result.append(squad)

    return result


def _process_word(item: Word, v: Vocab) -> tuple[list[Squad], list[str]]:
    """Process an ASD-STE100 word."""

    assert isinstance(item, Word), type(item)
    assert item.status in (
        WordStatus.APPROVED,
        WordStatus.REJECTED,
    ), item.status
    assert isinstance(v, Vocab), type(v)

    items: list[Squad] = []
    errors: list[str] = []
    result = (items, errors)

    title = "TASK01A"
    context = "You are an expert on the ASD-STE100 Simplified Technical English Standard."

    question = f"Is the word '{item.name.lower()}' an APPROVED word when you use it as {_format_type(item.type_)}?"
    if WordStatus.APPROVED == item.status:
        answer = f"Yes, the word '{item.name.lower()}' is an APPROVED word when you use it as {_format_type(item.type_)} in ASD-STE100."
    else:
        answer = f"No, the word '{item.name.lower()}' is a REJECTED word when you use it as {_format_type(item.type_)} in ASD-STE100."

    squad = Squad.make(
        title=title,
        context=context,
        question=question,
        answer=answer,
    )
    items.append(squad)

    question = (
        f"Is the word '{item.name.lower()}' an APPROVED word in ASD-STE100?"
    )
    if WordStatus.APPROVED == item.status:
        answer = f"Yes, the word '{item.name.lower()}' is an APPROVED word when you use it as {_format_type(item.type_)} in ASD-STE100."
    else:
        answer = f"No, the word '{item.name.lower()}' is a REJECTED word when you use it as {_format_type(item.type_)} in ASD-STE100."

    squad = Squad.make(
        title=title,
        context=context,
        question=question,
        answer=answer,
    )
    items.append(squad)

    question = f"Is the word '{item.name.lower()}' a REJECTED word when you use it as {_format_type(item.type_)}?"
    if WordStatus.APPROVED == item.status:
        answer = f"No, the word '{item.name.lower()}' is an APPROVED word when you use it as {_format_type(item.type_)} in ASD-STE100."
    else:
        answer = f"Yes, the word '{item.name.lower()}' is a REJECTED word when you use it as {_format_type(item.type_)} in ASD-STE100."

    squad = Squad.make(
        title=title,
        context=context,
        question=question,
        answer=answer,
    )
    items.append(squad)

    question = (
        f"Is the word '{item.name.lower()}' a REJECTED word in ASD-STE100?"
    )
    if WordStatus.APPROVED == item.status:
        answer = f"No, the word '{item.name.lower()}' is an APPROVED word when you use it as {_format_type(item.type_)} in ASD-STE100."
    else:
        answer = f"Yes, the word '{item.name.lower()}' is a REJECTED word when you use it as {_format_type(item.type_)} in ASD-STE100."

    squad = Squad.make(
        title=title,
        context=context,
        question=question,
        answer=answer,
    )
    items.append(squad)

    words = v.find(item.name)
    question = f"Is the word '{item.name.lower()}' APPROVED or REJECTED word when you use it in ASD-STE100?"
    assert 0 < len(words), len(words)
    if 1 == len(words):
        if WordStatus.APPROVED == item.status:
            answer = f"The word '{item.name.lower()}' is an APPROVED word when you use it as {_format_type(item.type_)} in ASD-STE100."
        else:
            answer = f"The word '{item.name.lower()}' is a REJECTED word when you use it as {_format_type(item.type_)} in ASD-STE100."
        squad = Squad.make(
            title=title,
            context=context,
            question=question,
            answer=answer,
        )
        items.append(squad)
    else:
        sb = StringBuilder(
            "In ASD-STE100, it depends on the context you use it: "
        )
        for word in words:
            sb.write(f"The word '{word.name.lower()}' is ")
            if WordStatus.APPROVED == item.status:
                sb.write("an APPROVED")
            else:
                sb.write("an REJECTED")
            sb.write(
                f" word when you use it as {_format_type(item.type_)} in ASD-STE100. "
            )
        squad = Squad.make(
            title=title,
            context=context,
            question=question,
            answer=sb.to_string().strip(),
        )
        items.append(squad)

    return result


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
