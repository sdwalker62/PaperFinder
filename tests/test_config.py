"""Tests for the configuration module."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from paperfinder.config import (
    Settings,
    SourceEntry,
    load_settings,
    load_sources,
    load_yaml,
)


@pytest.fixture()
def tmp_config_dir(tmp_path: Path) -> Path:
    """Create a temporary config directory with minimal YAML files."""
    settings_yaml = dedent("""\
        topics:
          - machine learning
          - optimization
        max_papers: 5
        delivery_time: "09:00"
        timezone: "UTC"
        email:
          sender: test@example.com
          recipients:
            - user@example.com
        aws:
          region: us-west-2
        llm:
          model: bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0
          max_tokens: 2048
          temperature: 0.0
          max_budget_usd: 0.50
          api_base: ""
        discord:
          enabled: false
          webhook_url: ""
        scraping:
          request_timeout: 10
          max_concurrent_requests: 3
          user_agent: "test-agent"
          lookback_days: 2
    """)
    sources_yaml = dedent("""\
        sources:
          - name: "Test RSS"
            type: rss
            url: "https://example.com/feed.xml"
            category: paper
            link_rewrite:
              pattern: "/abs/"
              replacement: "/html/"
          - name: "Test HTML"
            type: html
            url: "https://example.com/blog"
            category: blog
            selectors:
              article: "div.post"
              title: "h2"
              link_attr: "href"
              link_prefix: "https://example.com"
    """)
    (tmp_path / "settings.yaml").write_text(settings_yaml)
    (tmp_path / "sources.yaml").write_text(sources_yaml)
    return tmp_path


class TestLoadYaml:
    def test_loads_valid_yaml(self, tmp_path: Path) -> None:
        p = tmp_path / "test.yaml"
        p.write_text("key: value\n")
        result = load_yaml(p)
        assert result == {"key": "value"}

    def test_empty_yaml_returns_empty_dict(self, tmp_path: Path) -> None:
        p = tmp_path / "empty.yaml"
        p.write_text("")
        assert load_yaml(p) == {}


class TestSettings:
    def test_load_settings_from_yaml(self, tmp_config_dir: Path) -> None:
        settings = load_settings(tmp_config_dir)
        assert settings.max_papers == 5
        assert settings.delivery_time == "09:00"
        assert "machine learning" in settings.topics
        assert settings.aws.region == "us-west-2"
        assert settings.llm.max_budget_usd == 0.50
        assert settings.llm.max_tokens == 2048
        assert settings.scraping.lookback_days == 2

    def test_default_settings(self) -> None:
        s = Settings()
        assert s.max_papers == 15
        assert s.timezone == "America/New_York"


class TestSources:
    def test_load_sources(self, tmp_config_dir: Path) -> None:
        sources = load_sources(tmp_config_dir)
        assert len(sources) == 2
        assert sources[0].name == "Test RSS"
        assert sources[0].type == "rss"
        assert sources[0].link_rewrite is not None
        assert sources[1].selectors is not None

    def test_source_entry_defaults(self) -> None:
        s = SourceEntry(name="x", type="rss", url="https://example.com")
        assert s.category == "paper"
        assert s.link_rewrite is None
        assert s.selectors is None
