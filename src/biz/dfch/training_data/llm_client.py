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

"""LLM client using litellm for OpenAI-compatible endpoints."""

import os

from dataclasses import dataclass

from litellm import completion

from biz.dfch.logging import log


@dataclass(frozen=True)
class LlmSettings:
    """
    Configuration for the LLM client.

    Reads from environment variables (or .env file):
      LLM_API_TOKEN   - API token for the LLM provider.
      LLM_API_BASE  - Base URL of the OpenAI-compatible endpoint.
      LLM_MODEL     - Model name (e.g. "openai/gpt-4o").
    """

    api_key: str
    model: str = "openai/route-llm"
    api_base: str = "https://routellm.abacus.ai/v1/"

    @classmethod
    def from_env(cls) -> "LlmSettings":
        """Create an LlmSettings instance from environment variables."""

        api_key = os.environ.get("LLM_API_TOKEN")
        if not api_key:
            raise ValueError("Environment variable 'LLM_API_TOKEN' is not set.")

        api_base = os.environ.get("LLM_API_BASE")
        if not api_base:
            raise ValueError("Environment variable 'LLM_API_BASE' is not set.")

        model = os.environ.get("LLM_MODEL")
        if not model:
            raise ValueError("Environment variable 'LLM_MODEL' is not set.")

        return cls(api_key=api_key, api_base=api_base, model=model)


class LlmClient:
    """
    Client for querying an OpenAI-compatible LLM endpoint via litellm.
    """

    def __init__(self, settings: LlmSettings | None = None) -> None:
        self.settings = settings or LlmSettings.from_env()

        log.debug(
            "LlmClient: api_base=%s, model=%s",
            self.settings.api_base,
            self.settings.model,
        )

    def query(self, prompt: str) -> str:
        """
        Send a prompt to the LLM and return the response text.

        Args:
            prompt: The user prompt to send.

        Returns:
            The text content of the first response choice.
        """

        log.debug("LlmClient.query: prompt=%s", prompt)

        response = completion(
            model=self.settings.model,
            messages=[{"role": "user", "content": prompt}],
            api_key=self.settings.api_key,
            api_base=self.settings.api_base,
        )

        result: str = response.choices[0].message.content

        log.debug("LlmClient.query: result=%s", result)

        return result
