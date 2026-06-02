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

from __future__ import annotations
import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Squad:
    """
    The SQUAD dataset format.

    We only accept a single answer in the `answers` property.
    """

    id: str
    title: str
    context: str
    question: str
    answers: dict[str, list]

    @classmethod
    def make(
        cls,
        context: str,
        question: str,
        answer: str,
        *,
        id_: str | None = None,
        title: str = "",
    ) -> Squad:
        """Create a Squad instance with a single answer."""

        assert isinstance(context, str), context
        assert context.strip(), "'context' must not be empty."
        assert isinstance(question, str), question
        assert question.strip(), "'question' must not be empty."
        assert isinstance(answer, str), answer
        assert answer.strip(), "'answer' must not be empty."

        assert id_ is None or isinstance(id_, str), id_
        assert isinstance(title, str), title
        if id_ is None:
            id_ = str(uuid.uuid4())

        return cls(
            id=id_,
            title=title,
            context=context,
            question=question,
            answers={"text": [answer]},
        )

    @classmethod
    def from_list(cls, data: list[str]) -> "Squad":
        """Create a Squad instance from a list of 5 strings."""

        assert isinstance(data, list), "Input must be a list"
        assert len(data) == 5, f"Expected list of length 5, got {len(data)}"

        id_ = data[0]
        title = data[1]
        context = data[2]
        question = data[3]
        answer = data[4]

        assert isinstance(context, str), context
        assert context.strip(), "'context' must not be empty."
        assert isinstance(question, str), question
        assert question.strip(), "'question' must not be empty."
        assert isinstance(answer, str), answer
        assert answer.strip(), "'answer' must not be empty."
        assert isinstance(id_, str), id_
        assert isinstance(title, str), title

        if id_.strip():
            id_ = str(uuid.uuid4())

        return cls.make(
            id_=id_,
            title=title,
            context=context,
            question=question,
            answer=answer,
        )

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "Squad":
        """Create a Squad instance from a dictionary of 5 items."""

        assert isinstance(data, dict), "Input must be a dictionary"
        assert (
            len(data) == 5
        ), f"Expected dictionary with 5 keys, got {len(data)}"

        id_ = data["id"]
        title = data["title"]
        context = data["context"]
        question = data["question"]
        answer = data["answer"]

        assert isinstance(context, str), context
        assert context.strip(), "'context' must not be empty."
        assert isinstance(question, str), question
        assert question.strip(), "'question' must not be empty."
        assert isinstance(answer, str), answer
        assert answer.strip(), "'answer' must not be empty."
        assert isinstance(id_, str), id_
        assert isinstance(title, str), title

        if id_.strip():
            id_ = str(uuid.uuid4())

        return cls.make(
            id_=id_,
            title=title,
            context=context,
            question=question,
            answer=answer,
        )
