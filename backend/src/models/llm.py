"""LLM request and response models."""

from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Single chat message passed to the LLM endpoint."""

    role: Annotated[Literal["system", "user", "assistant"], Field(description="Message role")]
    content: Annotated[str, Field(description="Message content")]


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request."""

    model: Annotated[str, Field(description="Model name")]
    messages: Annotated[list[ChatMessage], Field(description="Ordered chat messages")]
    temperature: Annotated[float, Field(description="Sampling temperature")]
    response_format: Annotated[
        dict[str, str] | None,
        Field(description="Requested response format for JSON mode"),
    ] = None


class ChatCompletionChoiceMessage(BaseModel):
    """Message payload inside an LLM completion choice."""

    role: Annotated[str, Field(description="Role of the returned message")]
    content: Annotated[str, Field(description="Text content of the returned message")]


class ChatCompletionChoice(BaseModel):
    """Single completion choice."""

    index: Annotated[int, Field(description="Choice index")]
    message: Annotated[ChatCompletionChoiceMessage, Field(description="Choice message")]
    finish_reason: Annotated[str | None, Field(description="Finish reason")] = None


class ChatCompletionResponse(BaseModel):
    """OpenAI-compatible chat completion response."""

    id: Annotated[str, Field(description="Completion identifier")]
    object: Annotated[str, Field(description="Response object type")]
    created: Annotated[int, Field(description="Creation timestamp")]
    model: Annotated[str, Field(description="Model used for generation")]
    choices: Annotated[list[ChatCompletionChoice], Field(description="Completion choices")]


class OllamaNativeChatRequest(BaseModel):
    """Native Ollama chat request with structured outputs."""

    model: Annotated[str, Field(description="Model name")]
    messages: Annotated[list[ChatMessage], Field(description="Ordered chat messages")]
    stream: Annotated[bool, Field(description="Whether to stream tokens")] = False
    format: Annotated[dict[str, Any], Field(description="JSON schema for structured output")]
    options: Annotated[dict[str, Any], Field(description="Model options")] = Field(
        default_factory=dict
    )


class OllamaNativeChatResponseMessage(BaseModel):
    """Message payload returned by Ollama's native chat API."""

    role: Annotated[str, Field(description="Role of the returned message")]
    content: Annotated[str, Field(description="Text content returned by the model")]


class OllamaNativeChatResponse(BaseModel):
    """Response payload returned by Ollama's native chat API."""

    model: Annotated[str, Field(description="Model name")]
    message: Annotated[OllamaNativeChatResponseMessage, Field(description="Returned message")]
    done: Annotated[bool, Field(description="Whether generation completed")]
