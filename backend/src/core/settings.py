"""Application settings."""

from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: Annotated[str, Field(description="Human-friendly application name")] = (
        "n8n Strix Report Service"
    )
    api_prefix: Annotated[str, Field(description="Root API prefix")] = "/api/v1"
    artifacts_dir: Annotated[
        str, Field(description="Directory used to store generated artifacts")
    ] = "/tmp/n8n-strix-report-artifacts"
    public_base_url: Annotated[
        str, Field(description="Public base URL used in artifact links")
    ] = "http://localhost:18100"
    llm_base_url: Annotated[str, Field(description="OpenAI-compatible chat API base URL")] = (
        "http://ollama:11434/v1"
    )
    llm_api_key: Annotated[str, Field(description="API key for the OpenAI-compatible endpoint")] = (
        "ollama"
    )
    llm_model: Annotated[str, Field(description="Model name used for report generation")] = (
        "gpt-oss:20b"
    )
    llm_temperature: Annotated[float, Field(description="Sampling temperature")] = 0.2
    llm_timeout_seconds: Annotated[int, Field(description="LLM request timeout in seconds")] = 180
    smtp_host: Annotated[str, Field(description="SMTP host")] = "mailpit"
    smtp_port: Annotated[int, Field(description="SMTP port")] = 1025
    smtp_sender: Annotated[str, Field(description="From address used for report emails")] = (
        "reports@n8n-strix.local"
    )
