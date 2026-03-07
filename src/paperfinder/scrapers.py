"""Web scraping: RSS feeds and HTML blog pages."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import feedparser  # type: ignore[import-untyped]
import requests
from bs4 import BeautifulSoup, Tag

from paperfinder.models import Paper

if TYPE_CHECKING:
    from paperfinder.config import ScrapingConfig, SourceEntry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# RSS scraper
# ---------------------------------------------------------------------------


def scrape_rss(source: SourceEntry, cfg: ScrapingConfig, lookback: timedelta) -> list[Paper]:
    """Fetch and parse an RSS/Atom feed, returning papers published within *lookback*."""
    logger.info("Fetching RSS feed: %s", source.url)
    feed = feedparser.parse(
        source.url,
        agent=cfg.user_agent,
    )

    cutoff = datetime.now(tz=UTC) - lookback
    papers: list[Paper] = []

    for entry in feed.entries:
        # Parse published date if available
        published = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            parts = tuple(entry.published_parsed[:6])
            published = datetime(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], tzinfo=UTC)
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            parts = tuple(entry.updated_parsed[:6])
            published = datetime(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], tzinfo=UTC)

        # Skip entries older than lookback window (if we have a date)
        if published and published < cutoff:
            continue

        link = entry.get("link", "")
        # Apply link rewrite rules (e.g. arxiv abs → html)
        if source.link_rewrite and link:
            link = link.replace(source.link_rewrite.pattern, source.link_rewrite.replacement)

        abstract = entry.get("summary", "")
        # Strip HTML tags from abstract
        if abstract:
            abstract = BeautifulSoup(abstract, "lxml").get_text(separator=" ", strip=True)

        papers.append(
            Paper(
                title=entry.get("title", "Untitled"),
                url=link,
                source_name=source.name,
                category=source.category,
                abstract=abstract,
                published=published,
            )
        )

    logger.info("Found %d entries from %s", len(papers), source.name)
    return papers


# ---------------------------------------------------------------------------
# HTML scraper (for blogs without RSS)
# ---------------------------------------------------------------------------


def scrape_html(source: SourceEntry, cfg: ScrapingConfig, lookback: timedelta) -> list[Paper]:
    """Scrape an HTML page using CSS selectors defined in the source config."""
    if not source.selectors:
        logger.warning("No selectors defined for HTML source %s — skipping", source.name)
        return []

    logger.info("Scraping HTML page: %s", source.url)
    resp = requests.get(
        source.url,
        timeout=cfg.request_timeout,
        headers={"User-Agent": cfg.user_agent},
    )
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")
    articles = soup.select(source.selectors.article)
    papers: list[Paper] = []

    for article in articles:
        title_el = article.select_one(source.selectors.title)
        title = title_el.get_text(strip=True) if title_el else "Untitled"

        # Resolve link
        link = ""
        if source.selectors.link_attr == "href":
            # The article element itself may be an <a>
            if article.name == "a":
                link = str(article.get("href", ""))
            else:
                a_tag = article.find("a")
                if isinstance(a_tag, Tag):
                    link = str(a_tag.get("href", ""))
        else:
            link = str(article.get(source.selectors.link_attr, ""))

        if link and source.selectors.link_prefix and not link.startswith("http"):
            link = source.selectors.link_prefix + link

        papers.append(
            Paper(
                title=title,
                url=link,
                source_name=source.name,
                category=source.category,
            )
        )

    logger.info("Found %d entries from %s", len(papers), source.name)
    return papers


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


def scrape_source(source: SourceEntry, cfg: ScrapingConfig, lookback_days: int = 1) -> list[Paper]:
    """Route to the correct scraper based on source type."""
    lookback = timedelta(days=lookback_days)

    if source.type == "rss":
        return scrape_rss(source, cfg, lookback)
    elif source.type == "html":
        return scrape_html(source, cfg, lookback)
    else:
        logger.warning("Unknown source type '%s' for %s", source.type, source.name)
        return []


def scrape_all(
    sources: list[SourceEntry], cfg: ScrapingConfig, lookback_days: int = 1
) -> list[Paper]:
    """Scrape every configured source and return a flat list of papers."""
    all_papers: list[Paper] = []
    for source in sources:
        try:
            papers = scrape_source(source, cfg, lookback_days)
            all_papers.extend(papers)
        except Exception:
            logger.exception("Failed to scrape %s", source.name)
    return all_papers
