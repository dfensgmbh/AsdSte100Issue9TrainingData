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

"""training_data module."""

import json

import litellm
from litellm import Message
from typing import List, Callable, Type, Any

from pydantic_ai import (
    Agent,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    RequestUsage,
    ToolDefinition,
    RetryPromptPart,
    SystemPromptPart,
    TextPart,
    ToolReturnPart,
    ToolCallPart,
    UserPromptPart,
)
from pydantic_ai.models.function import FunctionModel, AgentInfo

from biz.dfch.logging import log


class LiteLlmAgent:
    """A pydantic-ai `Agent` that uses lite-llm to query providers."""

    _url: str
    _api_key: str
    _model: str

    def __init__(
        self,
        url: str,
        api_key: str,
        model: str,
        system_prompt: str | None = None,
    ) -> None:

        assert isinstance(url, str), type(url)
        assert url.strip()
        assert isinstance(model, str), type(model)
        assert model.strip()
        assert isinstance(api_key, str), type(api_key)
        assert api_key.strip()

        self._model = model
        self._url = url
        self._api_key = api_key

        self.model = FunctionModel(self._litellm_bridge)
        if isinstance(system_prompt, str) and system_prompt.strip():
            self.agent = Agent(
                self.model,
                system_prompt=system_prompt,
            )
        else:
            self.agent = Agent(
                self.model,
            )

    def _litellm_bridge(
        self, messages: list[ModelMessage], info: AgentInfo
    ) -> ModelResponse:

        assert isinstance(messages, list), type(messages)
        assert isinstance(info, AgentInfo), type(info)

        converted: list[Message] = []
        c = -1
        for msg in messages:
            c += 1
            log.debug(f"[PYD {c}] '{msg}'")

            if isinstance(msg, ModelResponse):

                tool_calls = []
                content = ""
                for part in msg.parts:
                    if isinstance(part, ToolCallPart):
                        log.debug(f"[PYD {c}:{type(part).__name__}<<<] {part}")
                        x = {
                            "id": part.tool_call_id,
                            "type": "function",
                            "function": {
                                "name": part.tool_name,
                                "arguments": json.dumps(part.args),
                            },
                        }
                        tool_calls.append(x)
                        continue
                    if isinstance(part, TextPart):
                        log.debug(f"[PYD {c}:{type(part).__name__}<<<] {part}")
                        content = part.content
                        continue

                    # Catch all other parts.
                    log.debug(f"[PYD {c}:{type(part).__name__}<<<] {part}")
                    assert False, f"[PYD {c}:{type(part).__name__}<<<] {part}"

                m = Message(
                    content=content,
                    role="assistant",
                    tool_calls=tool_calls,
                )
                converted.append(m)
                continue

            if isinstance(msg, ModelRequest):

                for part in msg.parts:
                    if isinstance(part, SystemPromptPart):
                        log.debug(f"[PYD {c}:{type(part).__name__}>>>] {part}")
                        m = Message(
                            content=str(part.content),
                            role="system",
                        )
                        converted.append(m)
                        continue
                    if isinstance(part, UserPromptPart):
                        log.debug(f"[PYD {c}:{type(part).__name__}>>>] {part}")
                        m = Message(
                            content=str(part.content),
                            role="user",
                        )
                        converted.append(m)
                        continue
                    if isinstance(part, ToolReturnPart):
                        log.debug(f"[PYD {c}:{type(part).__name__}>>>] {part}")
                        converted.append(
                            {  # type: ignore
                                "role": "tool",
                                "tool_call_id": part.tool_call_id,
                                "name": part.tool_name,
                                "content": json.dumps(part.content),
                            }
                        )
                        continue
                    if isinstance(part, RetryPromptPart):
                        log.debug(f"[PYD {c}:{type(part).__name__}>>>] {part}")
                        converted.append(
                            {  # type: ignore
                                "role": "tool",
                                "tool_call_id": part.tool_call_id,
                                "name": part.tool_name,
                                "content": json.dumps(part.content),
                            }
                        )
                        continue

                    # Catch all other parts.
                    log.debug(f"[PYD {c}:{type(part).__name__}>>>] {part}")
                    assert False, f"[PYD {c}:{type(part).__name__}>>>] {part}"

        def _convert_tool(tool: ToolDefinition) -> dict:
            result = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters_json_schema,
                },
            }
            return result

        tools = []
        tools.extend([_convert_tool(t) for t in info.function_tools])
        tools.extend([_convert_tool(t) for t in info.output_tools])

        for t in tools:
            log.debug(f"tool: '{t}'.")
        # for x in self.agent.toolsets:
        #     log.debug(f"toolset: [{type(x)}] {x}")
        for c, msg in enumerate(converted):
            log.debug(f"[LTE {c}] {msg}")

        response = litellm.completion(
            model=f"openai/{self._model}",
            messages=converted,
            tools=tools if tools else None,
            api_base=self._url,
            api_key=self._api_key,
            response_format={"type": "json_object"},
            # **info.model_settings
            tool_choice="auto",
        )

        # Map LiteLLM response back to pydantic-ai ModelResponse
        log.debug(f"response: '{response}'.")
        choice = response.choices[0]  # type: ignore
        finish_reason = choice.finish_reason  # type: ignore
        message: Message = choice.message
        parts = []

        if finish_reason == "tool_calls":
            if message.content:
                pt = TextPart(message.content)
                parts.append(pt)

            assert message.tool_calls is not None
            for tc in message.tool_calls:
                pc = ToolCallPart(
                    tool_call_id=tc.id,
                    tool_name=tc.function.name,
                    args=json.loads(tc.function.arguments),
                )
                parts.append(pc)
        elif finish_reason == "stop":
            if message.content:
                pt = TextPart(message.content)
                parts.append(pt)
        else:
            log.debug(f"finish_reason: '{finish_reason}'.")
            assert False, finish_reason

        usage = RequestUsage(
            input_tokens=getattr(response.usage, "completion_tokens", 0),
            output_tokens=getattr(response.usage, "output_tokens", 0),
        )
        return ModelResponse(parts=parts, run_id=str(response.id), usage=usage)

    def add_tools(self, tool_funcs: List[Callable]):
        """Add tools that the LLM can call."""
        for func in tool_funcs:
            self.agent.tool(func)

    def run(
        self,
        prompt: str,
        *,
        deps: Any | None = None,
        output_type: Type[Any] | None = None,
    ):
        """Start the query with optional output type."""
        return self.agent.run_sync(prompt, deps=deps, output_type=output_type)
