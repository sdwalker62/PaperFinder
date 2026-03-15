"""Tests for scrapers (unit-level with mocked HTTP)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from paperfinder.config import HTMLSelectors, LinkRewrite, ScrapingConfig, SourceEntry
from paperfinder.scrapers import scrape_all, scrape_html, scrape_rss


@pytest.fixture()
def scraping_cfg() -> ScrapingConfig:
    return ScrapingConfig(
        request_timeout=5,
        max_concurrent_requests=1,
        user_agent="test",
        lookback_days=7,
    )


class TestScrapeRSS:
    @patch("paperfinder.scrapers.feedparser.parse")
    def test_parses_entries(self, mock_parse: MagicMock, scraping_cfg: ScrapingConfig) -> None:
        recent = datetime.now(tz=UTC) - timedelta(days=1)
        mock_parse.return_value = MagicMock(
            entries=[
                MagicMock(
                    title="Paper A",
                    link="https://arxiv.org/abs/1234",
                    summary="<p>Abstract</p>",
                    published_parsed=recent.timetuple()[:9],
                    updated_parsed=None,
                    **{
                        "get.side_effect": lambda k, d="": {
                            "title": "Paper A",
                            "link": "https://arxiv.org/abs/1234",
                            "summary": "<p>Abstract</p>",
                        }.get(k, d)
                    },
                )
            ]
        )
        source = SourceEntry(
            name="test",
            type="rss",
            url="https://example.com/feed",
            category="paper",
            link_rewrite=LinkRewrite(
                pattern="https://arxiv.org/abs/",
                replacement="https://arxiv.org/html/",
            ),
        )
        papers = scrape_rss(source, scraping_cfg, timedelta(days=7))
        assert len(papers) == 1
        assert papers[0].title == "Paper A"
        assert "html" in papers[0].url


class TestScrapeHTML:
    @patch("paperfinder.scrapers.requests.get")
    def test_parses_html_page(self, mock_get: MagicMock, scraping_cfg: ScrapingConfig) -> None:
        html = (
            "<html><body>"
            '<div class="post"><a href="/blog/post-1">'
            "<h2>A Deep Dive Into Neural Networks</h2></a></div>"
            '<div class="post"><a href="/blog/post-2">'
            "<h2>Transformers and Attention Mechanisms</h2></a></div>"
            "</body></html>"
        )
        mock_get.return_value = MagicMock(text=html, status_code=200)
        mock_get.return_value.raise_for_status = MagicMock()

        source = SourceEntry(
            name="Blog",
            type="html",
            url="https://example.com/blog",
            category="blog",
            selectors=HTMLSelectors(
                article="div.post",
                title="h2",
                link_attr="href",
                link_prefix="https://example.com",
            ),
        )
        papers = scrape_html(source, scraping_cfg, timedelta(days=1))
        assert len(papers) == 2
        assert papers[0].title == "A Deep Dive Into Neural Networks"
        assert papers[0].url == "https://example.com/blog/post-1"

    def test_no_selectors_returns_empty(self, scraping_cfg: ScrapingConfig) -> None:
        source = SourceEntry(name="NoSel", type="html", url="https://x.com", category="blog")
        result = scrape_html(source, scraping_cfg, timedelta(days=1))
        assert result == []


class TestScrapeAll:
    @patch("paperfinder.scrapers.scrape_source")
    def test_aggregates_results(self, mock_scrape: MagicMock, scraping_cfg: ScrapingConfig) -> None:
        from paperfinder.models import Paper

        mock_scrape.side_effect = [
            [Paper(title="A", url="", source_name="s1", category="paper")],
            [Paper(title="B", url="", source_name="s2", category="blog")],
        ]
        sources = [
            SourceEntry(name="s1", type="rss", url="u1"),
            SourceEntry(name="s2", type="html", url="u2"),
        ]
        result = scrape_all(sources, scraping_cfg, lookback_days=1)
        assert len(result) == 2

    @patch("paperfinder.scrapers.scrape_source", side_effect=Exception("boom"))
    def test_handles_errors_gracefully(
        self, mock_scrape: MagicMock, scraping_cfg: ScrapingConfig
    ) -> None:
        sources = [SourceEntry(name="bad", type="rss", url="u")]
        result = scrape_all(sources, scraping_cfg, lookback_days=1)
        assert result == []
