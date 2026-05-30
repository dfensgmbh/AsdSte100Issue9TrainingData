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

"""'query' command."""

import copy
from datetime import datetime
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Annotated
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel
import typer
import spacy
from spacy.language import Language


from biz.dfch.logging import log
from biz.dfch.asdste100vocab import Vocab

from ..agents.ste100_agent import Ste100Agent
from ..info import Info
from ..tools.word_tools import get_word_status, get_etymology

from .args import NameArg, OutputArg, OverwriteArg

load_dotenv()

app = typer.Typer(
    name=Info.name,
    help=Info.description,
    epilog=Info.epilog,
    no_args_is_help=True,
)


@dataclass(frozen=True)
class Deps:
    vocab: Vocab
    nlp: Language


class FlatBaseModel(BaseModel):
    """Pydantic BaseModel with flattened schema."""

    @staticmethod
    def _inline_refs(schema: dict[str, Any]) -> dict[str, Any]:
        schema = copy.deepcopy(schema)
        defs = schema.pop("$defs", None) or schema.pop("definitions", None) or {}

        def _resolve(node):
            if isinstance(node, dict):
                ref = node.get("$ref")
                if isinstance(ref, str) and ref.startswith("#/$defs/"):
                    name = ref.split("/")[-1]
                    return _resolve(copy.deepcopy(defs[name]))
                return {k: _resolve(v) for k, v in node.items()}
            if isinstance(node, list):
                return [_resolve(x) for x in node]
            return node

        return _resolve(schema)

    @classmethod
    def model_json_schema(cls, *args, **kwargs):
        return FlatBaseModel._inline_refs(super().model_json_schema(*args, **kwargs))

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):  # type: ignore[override]
        return FlatBaseModel._inline_refs(handler(core_schema))


class WordStatus(BaseModel):
    summary: str
    is_approved: bool


class FinalResponse(BaseModel):
    words: list[WordStatus]


@app.command()
def query(
    ctx: typer.Context,
    text: Annotated[
        str, typer.Option("--input", "-i", help="The input string to process.")
    ],
    url: Annotated[
        str,
        typer.Option(
            "--url",
            "-u",
            help="The base URL for the chat service.",
            envvar="CHAT_BASE_URL",
        ),
    ],
    api_token: Annotated[
        str,
        typer.Option(
            "--api-token",
            help="The API token for the chat service.",
            envvar="CHAT_API_TOKEN",
        ),
    ],
    model: Annotated[
        str,
        typer.Option(
            "--model",
            "-m",
            help="The model to use for the query.",
            envvar="CHAT_MODEL",
        ),
    ],
    output: OutputArg = Path("."),
    file: NameArg = None,  # type: ignore
    overwrite: OverwriteArg = False,
):
    """
    Make the dataset for the "Query" task.
    """

    _ = ctx

    assert isinstance(output, Path), type(Path)
    assert output.exists(), f"Path must exist: '{output}'."
    assert isinstance(text, str), type(text)
    assert text.strip(), "Parameter must not be empty: 'text' ."
    assert url.strip(), "Parameter must not be empty: 'url' ."
    assert api_token.strip(), "Parameter must not be empty: 'api_token' ."
    assert model.strip(), "Parameter must not be empty: 'model' ."

    log.info(json.dumps(FinalResponse.model_json_schema(), indent=2))

    nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])

    doc = nlp(text)

    for token in doc:
        log.info(f"{token.text:12} -> {token.lemma_}")
    # return

    if file is None:
        file = f"response-{datetime.now().strftime('%Y-%m-%d---%H-%M-%S')}.json"

    path = Path(output / file).resolve()

    input_file = Path(text)
    if input_file.exists() and input_file.is_file():
        text = input_file.read_text(encoding="utf-8")

    if path.exists() and not overwrite:
        overwrite = typer.confirm(
            f"File '{path}' already exists. Overwrite?",
            default=False,
        )
        if not overwrite:
            raise typer.Abort()

    log.debug("query: url=%s, model=%s", url, model)
    log.debug(f"input: '{text}'")

    agent = Ste100Agent(url=url, api_key=api_token, model=model)

    agent.add_tools(
        [
            # get_etymology,
            get_word_status,
        ]
    )

    v = Vocab()
    deps = Deps(vocab=v, nlp=nlp)
    result = agent.run(
        text,
        deps=deps,
        output_type=FinalResponse,
    )

    log.debug(result)
    assert isinstance(result.output, FinalResponse), type(result.output)
    for w in result.output.words:
        log.debug(f"summary: {w.summary}")
        log.debug(f"is_approved: {w.is_approved}")

    return
