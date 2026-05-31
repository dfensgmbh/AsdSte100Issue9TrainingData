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

"""ASD-STE100 word tools module."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic_ai import RunContext
from spacy.language import Language

from biz.dfch.asdste100vocab import Vocab
from biz.dfch.logging import log


@dataclass(frozen=True)
class RunCtxDeps:
    """The `RunContext` dependencies for a `tool_call`."""

    vocab: Vocab
    nlp: Language


class StringBuilder:
    """A `StringBuilder` class."""

    _lines: list[str]

    def __init__(self) -> None:
        self._lines = []

    def clear(self) -> StringBuilder:
        """Remove all content from the `StringBuilder` instance."""

        self._lines.clear()

        return self

    def to_string(self) -> str:
        """Create a string from the `StringBuilder` instance."""

        result = "".join(self._lines)

        return result

    def write(self, value: str) -> StringBuilder:
        """Add text to the `StringBuilder` instance."""

        assert isinstance(value, str), type(value)

        self._lines.append(value)

        return self

    def write_line(self, value: str = "") -> StringBuilder:
        """Add text to and a newline the `StringBuilder` instance."""

        assert isinstance(value, str), type(value)

        self._lines.append(value)
        self._lines.append("\n")

        return self


def get_word_status(ctx: RunContext[None], word: str) -> str:
    """Examine the status of a word lemma in part of speech."""

    assert isinstance(ctx, RunContext), type(ctx)
    assert ctx.deps is not None
    assert ctx.deps.vocab is not None
    assert ctx.deps.nlp is not None

    sb = StringBuilder()

    log.debug(f"#### tool_call: get_word_status(word = '{word}').")

    nlp = ctx.deps.nlp
    doc = nlp(word)
    lemma = None
    for token in doc:
        log.info(f"{token.text} -> {token.lemma_}")
        if not lemma:
            lemma = token.lemma_

    v = ctx.deps.vocab
    assert isinstance(v, Vocab), type(v)
    words = v.find(lemma)
    if words:
        if 1 < len(words):
            sb.write("It depends. ")
        for w in words:
            sb.write(
                f"Status of word '{w.name}' "
                f"as '{w.type_.name}' "
                f"is {w.status.upper()}. "
            )

        result = sb.to_string()
        log.info(result)
        return result

    partial = word
    partials = []
    while partial:
        partials = v.find(partial)
        if partials:
            break
        partial = partial[:-1]

    not_found = (
        f"I could not find this word '{word}' " "in the ASD-STE100 vocabulary. "
    )
    if not partials:
        sb.write(not_found)
        result = sb.to_string()
        log.warning(result)
        return result

    sb.write(not_found)
    sb.write("But I found these similar words: ")
    for w in partials[:5]:
        sb.write(
            f"Status of word '{w.name}' "
            f"as '{w.type_.name}' "
            f"is {w.status.upper()}. "
        )

    result = sb.to_string()
    log.warning(result)
    return result


def get_etymology(ctx: RunContext[None], word: str) -> str:
    """Find the origin of a word."""

    _ = ctx

    log.error(f"#### tool_call: get_etymology(word = '{word}').")

    return f"The word {word} comes from Latin."
