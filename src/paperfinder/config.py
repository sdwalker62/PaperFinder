"""Configuration loading and validation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

_CONFIG_DIR = Path(
    os.environ.get("PAPERFINDER_CONFIG_DIR")
    or Path(__file__).resolve().parent.parent.parent / "config"
)


# ---------------------------------------------------------------------------
# Pydantic models for structured configuration
# ---------------------------------------------------------------------------


class EmailConfig(BaseModel):
    sender: str = "paperfinder@example.com"
    recipients: str = "dalton@example.com"
    subject_prefix: str = "[PaperFinder]"


class AWSConfig(BaseModel):
    region: str = "us-east-1"


class LLMConfig(BaseModel):
    """LLM provider configuration via LiteLLM."""

    # LiteLLM model string — e.g. "anthropic/claude-sonnet-4-20250514",
    # "openai/gpt-4o", "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0", etc.
    model: str = "anthropic/claude-sonnet-4-20250514"
    max_tokens: int = 4096
    temperature: float = 0.0

    # Budget guardrails — pipeline aborts once this USD limit is reached per run
    max_budget_usd: float = 1.00

    # Optional API base URL (for proxies / self-hosted endpoints)
    api_base: str = ""


class WebsiteConfig(BaseModel):
    """Frontend API for persisting papers to the database."""

    api_url: str = ""  # e.g. "https://paperfinder.netlify.app/api/papers"
    api_key: str = ""


class EnrichmentConfig(BaseModel):
    """Semantic Scholar citation enrichment."""

    enabled: bool = True
    semantic_scholar_api_key: str = ""  # optional — free tier works without one


class DiscordConfig(BaseModel):
    enabled: bool = False
    webhook_url: str = ""


class ScrapingConfig(BaseModel):
    request_timeout: int = 30
    max_concurrent_requests: int = 5
    user_agent: str = "PaperFinder/0.1 (+https://github.com/dalton/PaperFinder)"
    lookback_days: int = 1


class LinkRewrite(BaseModel):
    pattern: str
    replacement: str


class HTMLSelectors(BaseModel):
    article: str
    title: str
    link_attr: str = "href"
    link_prefix: str = ""


class SourceEntry(BaseModel):
    name: str
    type: str  # "rss" | "html" | "api"
    url: str
    category: str = "paper"  # "paper" | "blog"
    link_rewrite: LinkRewrite | None = None
    selectors: HTMLSelectors | None = None


class Settings(BaseSettings):
    """Application-wide settings, loaded from YAML + env vars."""

    topics: list[str] = Field(default_factory=list)
    max_papers: int = 15
    delivery_time: str = "08:00"
    timezone: str = "America/New_York"
    email: EmailConfig = Field(default_factory=EmailConfig)
    aws: AWSConfig = Field(default_factory=AWSConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    website: WebsiteConfig = Field(default_factory=WebsiteConfig)
    enrichment: EnrichmentConfig = Field(default_factory=EnrichmentConfig)
    discord: DiscordConfig = Field(default_factory=DiscordConfig)
    scraping: ScrapingConfig = Field(default_factory=ScrapingConfig)

    model_config = {"env_prefix": "PAPERFINDER_", "env_nested_delimiter": "__"}

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Env vars take priority over init kwargs (YAML values)."""
        return (env_settings, init_settings, dotenv_settings, file_secret_settings)


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file and return its contents as a dict."""
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_settings(config_dir: Path | None = None) -> Settings:
    """Load settings from *config/settings.yaml* merged with env overrides."""
    config_dir = config_dir or _CONFIG_DIR
    raw = load_yaml(config_dir / "settings.yaml")
    return Settings(**raw)


def load_sources(config_dir: Path | None = None) -> list[SourceEntry]:
    """Load and validate the sources list from *config/sources.yaml*."""
    config_dir = config_dir or _CONFIG_DIR
    raw = load_yaml(config_dir / "sources.yaml")
    return [SourceEntry(**s) for s in raw.get("sources", [])]
