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

"""STE100 approved word dataclass."""

from dataclasses import dataclass
import json

from biz.dfch.asdste100vocab import WordType


@dataclass(frozen=True)
class STE100Approved:
    """STE100 approved word"""

    sentence: str
    word: str
    pos: WordType
    instruction: str = (
        "Examine if the word in brackets "
        "is an approved word in ASD-STE100 Issue 9."
    )

    def __str__(self) -> str:
        """
        Produces a single line JSON string formatted for ASD-STE100 training.
        """

        # This is not reliable. We must change this.
        sent_with_brackets = self.sentence.replace(self.word, f"[{self.word}]")

        input_text = f"Sentence: {sent_with_brackets}\nWord: {self.word}"

        # 2. Prepare the output: Use the status, word, and pos
        # Using double quotes inside the string as requested in your template
        type_ = self.pos.name.lower()
        type_infix = f"n {type_}" if type_[0] in "aeiou" else f" {type_}"
        output_text = (
            f"Approved. In this sentence, '{self.word}' is a{type_infix}, "
            f"and this use is approved in ASD-STE100 Issue 9."
        )

        data = {
            "instruction": self.instruction,
            "input": input_text,
            "output": output_text,
        }

        return json.dumps(data, ensure_ascii=False)