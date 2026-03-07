"""Tests for models."""

from __future__ import annotations

from datetime import UTC, datetime

from paperfinder.models import Paper


class TestPaper:
    def test_default_fields(self) -> None:
        p = Paper(title="Test", url="https://example.com", source_name="src", category="paper")
        assert p.summary == ""
        assert p.relevance_score == 0.0
        assert p.topics_matched == []

    def test_display_url_returns_url(self) -> None:
        p = Paper(
            title="T",
            url="https://arxiv.org/html/1234",
            source_name="arXiv",
            category="paper",
        )
        assert p.display_url == "https://arxiv.org/html/1234"

    def test_published_is_optional(self) -> None:
        p = Paper(title="T", url="", source_name="s", category="blog")
        assert p.published is None

    def test_published_with_datetime(self) -> None:
        dt = datetime(2025, 1, 15, tzinfo=UTC)
        p = Paper(title="T", url="", source_name="s", category="paper", published=dt)
        assert p.published == dt
