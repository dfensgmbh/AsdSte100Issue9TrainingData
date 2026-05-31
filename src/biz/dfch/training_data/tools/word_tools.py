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
from biz.dfch.asdste100vocab import Word
from biz.dfch.asdste100vocab import WordType
from biz.dfch.asdste100vocab import WordStatus
from biz.dfch.logging import log

from biz.dfch.text import StringBuilder


class WordTools:
    """ASD-STE100 word tools, usable as Pydantic AI Agent tool functions.

    The instance methods :meth:`get_word_status` and
    :meth:`get_word_alternative` have the signature
    ``(ctx: RunContext[RunCtxDeps], word: str) -> str`` and can be
    registered as tools with a Pydantic AI ``Agent`` as bound methods.
    """

    @dataclass(frozen=True)
    class RunCtxDeps:
        """The `RunContext` dependencies for a `tool_call`."""

        vocab: Vocab
        nlp: Language

    def __init__(self, vocab: Vocab, nlp: Language) -> None:
        """Initialise a :class:`WordTools` instance.

        Builds and stores the :class:`WordTools.RunCtxDeps` instance
        that the tool methods use at call time. The dependencies are
        bound to the instance, so the same :class:`WordTools` object
        can be reused across multiple Pydantic AI ``Agent`` runs.

        Args:
            vocab (Vocab): The ASD-STE100 vocabulary used to look up
                words and their alternatives. Must not be ``None``.
            nlp (Language): A loaded spaCy :class:`Language` pipeline
                used to tokenise and lemmatise the input word. Must
                not be ``None``.

        Raises:
            AssertionError: If ``vocab`` or ``nlp`` is ``None`` or not
                of the expected type.
        """

        assert vocab is not None
        assert nlp is not None
        assert isinstance(vocab, Vocab), type(vocab)
        assert isinstance(nlp, Language), type(nlp)

        self._deps: WordTools.RunCtxDeps = WordTools.RunCtxDeps(
            vocab=vocab, nlp=nlp
        )

    def _format_type(self, type_: WordType) -> str:
        vowels_lower = "aeiou"
        return (
            "an" if type_.name[0].lower() in vowels_lower else "a"
        ) + f" '{type_.name}'"

    @property
    def deps(self) -> "WordTools.RunCtxDeps":
        """The `RunContext` dependencies for tool calls."""
        return self._deps

    def get_word_status(
        self, ctx: RunContext["WordTools.RunCtxDeps"], word: str
    ) -> str:
        """Examine the ASD-STE100 status of a word in part of speech."""

        assert isinstance(ctx, RunContext), type(ctx)

        sb = StringBuilder()

        log.debug(f"#### tool_call: get_word_status(word = '{word}').")

        nlp = self._deps.nlp
        doc = nlp(word)
        lemma = None
        for token in doc:
            log.info(f"{token.text} -> {token.lemma_}")
            if not lemma:
                lemma = token.lemma_
                break

        v = self._deps.vocab
        if lemma is None:
            lemma = word
        words: list[Word] = v.find(lemma)
        if words:
            if 1 < len(words):
                sb.write("It depends. ")
            for w in words:
                assert isinstance(w, Word), type(w)
                sb.write(
                    f"Status of word '{w.name}' "
                    f"as {self._format_type(w.type_)} "
                    f"is {w.status.name}. "
                )
                if WordStatus.REJECTED == w.status:
                    sb.write("It has these alternatives: ")
                    for i, a in enumerate(w.alternatives):
                        i += 1
                        sb.format(
                            "%s) '%s' as %s. ",
                            i,
                            a.name,
                            self._format_type(a.type_),
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
            f"I could not find this word '{word}' "
            "in the ASD-STE100 vocabulary: "
            f"word status is '{WordStatus.UNKNOWN.name}'. "
        )
        if not partials:
            sb.write(not_found)
            result = sb.to_string()
            log.warning(result)
            return result

        sb.write(not_found)
        sb.write("But I found these similar words: ")
        for w in partials[:5]:
            assert isinstance(w, Word), type(w)
            sb.write(
                f"Status of word '{w.name}' "
                f"as {self._format_type(w.type_)} "
                f"is {w.status.name}. "
            )

        result = sb.to_string()
        log.warning(result)
        return result

    def get_word_alternative(
        self, ctx: RunContext["WordTools.RunCtxDeps"], word: str
    ) -> str:
        """Get the ASD-STE100 alternative for a REJECTED word."""

        assert isinstance(ctx, RunContext), type(ctx)

        sb: StringBuilder = StringBuilder()

        if word is None or not word.strip():
            sb.write("'word' is empty. You did not specify a word.")
            result = sb.to_string()
            log.debug(result)
            return result

        _ = ctx

        log.debug(f"#### tool_call: get_word_alternative(word = '{word}').")

        v = self._deps.vocab
        words: list[Word] = v.find(word)
        if not words:
            sb.format("Exact word '%s' is not in ASD-STE100 dictionary.", word)
            result = sb.to_string()
            log.debug(result)
            return result

        for w in words:
            assert isinstance(w, Word), type(w)

            if not w.alternatives:
                sb.format(
                    "Word '%s' as %s with status '%s' has no ASD-STE100 "
                    "alternative. ",
                    w.name,
                    self._format_type(w.type_),
                    w.status.name,
                )
                continue

            sb.format(
                "Word '%s' as %s with status '%s' has these ASD-STE100 "
                "alternatives: ",
                w.name,
                self._format_type(w.type_),
                w.status.name,
            )
            for i, a in enumerate(w.alternatives):
                i += 1
                sb.format("%s) '%s' as %s. ", i, a.name, a.type_.name)

        result = sb.to_string().strip()
        log.debug(result)
        return result
