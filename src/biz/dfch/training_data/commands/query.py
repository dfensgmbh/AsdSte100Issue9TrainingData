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

from datetime import datetime
import json
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from pydantic import BaseModel
import typer
import spacy

from biz.dfch.asdste100vocab import Vocab

from biz.dfch.logging import log
from biz.dfch.diagnostics import Stopwatch


from ..agents.lite_llm_agent import LiteLlmAgent
from ..info import Info
from ..tools import get_word_status, RunCtxDeps

from .args import NameArg, OutputArg, OverwriteArg

load_dotenv()

app = typer.Typer(
    name=Info.name,
    help=Info.description,
    epilog=Info.epilog,
    no_args_is_help=True,
)


class WordStatus(BaseModel):
    """Represents the ASD-STE100 status of a single word as evaluated
    by the LLM.

    Attributes:
        word (str): The original word from the input text.
        summary (str): A brief explanation of the ASD-STE100 status or
            relevance of the word.
        word_status (str): Show the ASD-STE100 status of word.
    """

    word: str
    summary: str
    status: str


class FinalResponse(BaseModel):
    """Represents the final JSON formatted output from the LLM response."""

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

    system = (
        "You are a helpful technical writer. "
        "You MUST respond only in valid JSON format that you see in "
        "the tool 'final_result'. "
        "Do not include any conversational text before or after the "
        "JSON block."
    )
    agent = LiteLlmAgent(
        url=url, api_key=api_token, model=model, system_prompt=system
    )

    agent.add_tools(
        [
            # get_etymology,
            get_word_status,
        ]
    )

    v = Vocab()
    deps = RunCtxDeps(vocab=v, nlp=nlp)
    sw = Stopwatch()
    log.debug("Query LLM ...")
    sw.start()
    result = agent.run(
        text,
        deps=deps,
        output_type=FinalResponse,
    )
    sw.stop()
    log.info("Query LLM OK. [%.3f]", sw.elapsed_seconds)

    log.debug(result)
    assert isinstance(result.output, FinalResponse), type(result.output)
    for w in result.output.words:
        log.debug(f"word: {w.word}")
        log.debug(f"summary: {w.summary}")
        log.debug(f"status: {w.status}")

    return
