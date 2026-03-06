"""OpenAI-compatible chat client tool."""

import json

import httpx
from pydantic import ValidationError

from src.core.exceptions import LlmRequestError
from src.core.settings import Settings
from src.lib.json_extractor import extract_json_object
from src.models.llm import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    OllamaNativeChatRequest,
    OllamaNativeChatResponse,
)
from src.models.report import ReportDraft


class LlmChatTool:
    """Call an OpenAI-compatible chat endpoint and parse a report response."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the chat tool."""
        self._base_url = settings.llm_base_url.rstrip("/")
        self._native_base_url = (
            self._base_url[:-3] if self._base_url.endswith("/v1") else self._base_url
        )
        self._api_key = settings.llm_api_key
        self._model = settings.llm_model
        self._temperature = settings.llm_temperature
        self._timeout_seconds = settings.llm_timeout_seconds

    async def generate_report(self, prompt: str) -> ReportDraft:
        """Generate a report draft using the configured chat endpoint."""
        request = ChatCompletionRequest(
            model=self._model,
            temperature=self._temperature,
            messages=[
                ChatMessage(
                    role="system",
                    content="You produce valid JSON only and never wrap it in markdown.",
                ),
                ChatMessage(role="user", content=prompt),
            ],
            response_format={"type": "json_object"},
        )

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers=headers,
                    json=request.model_dump(),
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LlmRequestError(f"LLM request failed: {exc}") from exc

        parsed_response = ChatCompletionResponse.model_validate(response.json())
        if not parsed_response.choices:
            raise LlmRequestError("LLM returned no completion choices.")

        content = parsed_response.choices[0].message.content
        try:
            return self._parse_report_draft(content)
        except LlmRequestError:
            return await self._generate_report_with_native_schema(prompt=prompt)

    async def _generate_report_with_native_schema(self, prompt: str) -> ReportDraft:
        """Fallback to Ollama's native structured-output API for stricter JSON control."""
        request = OllamaNativeChatRequest(
            model=self._model,
            messages=[
                ChatMessage(
                    role="system",
                    content="Return only JSON that conforms to the provided schema.",
                ),
                ChatMessage(role="user", content=prompt),
            ],
            format=ReportDraft.model_json_schema(),
            options={"temperature": self._temperature},
        )

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(
                    f"{self._native_base_url}/api/chat",
                    headers={"Content-Type": "application/json"},
                    json=request.model_dump(),
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LlmRequestError(f"Ollama structured-output request failed: {exc}") from exc

        parsed_response = OllamaNativeChatResponse.model_validate(response.json())
        return self._parse_report_draft(parsed_response.message.content)

    def _parse_report_draft(self, content: str) -> ReportDraft:
        """Parse and validate report JSON from model output."""
        try:
            json_payload = extract_json_object(content)
            draft_payload = json.loads(json_payload)
            return ReportDraft.model_validate(draft_payload)
        except (ValueError, json.JSONDecodeError, ValidationError) as exc:
            raise LlmRequestError(f"LLM returned invalid JSON: {exc}") from exc
