"""Semantic Scholar citation enrichment."""

from __future__ import annotations

import logging
import re
import time

import requests

from paperfinder.models import Paper

logger = logging.getLogger(__name__)

_API_BASE = "https://api.semanticscholar.org/graph/v1/paper"
_FIELDS = "citationCount"
_REQUEST_DELAY = 1.1  # seconds between requests (free tier: ~1 req/sec)
_RETRY_WAIT = 65  # seconds to wait after a 429


def _arxiv_id(url: str) -> str | None:
    m = re.search(r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]+)", url, re.I)
    return m.group(1) if m else None


def _get(
    url: str,
    params: dict[str, str | int] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, object] | None:
    """GET with one automatic retry on 429."""
    try:
        resp = requests.get(url, params=params, headers=headers or {}, timeout=10)
        if resp.status_code == 429:
            logger.warning("Semantic Scholar rate limit hit — waiting %ds", _RETRY_WAIT)
            time.sleep(_RETRY_WAIT)
            resp = requests.get(url, params=params, headers=headers or {}, timeout=10)
        if resp.status_code == 200:
            result: dict[str, object] = resp.json()
            return result
        if resp.status_code not in (404, 400):
            logger.warning("Semantic Scholar returned %d for %s", resp.status_code, url)
    except requests.RequestException as exc:
        logger.warning("Semantic Scholar request failed: %s", exc)
    return None


def _fetch_citation_count(paper: Paper, api_key: str = "") -> int | None:
    headers = {"x-api-key": api_key} if api_key else {}

    # 1. arXiv ID lookup (most reliable for research papers)
    arxiv_id = _arxiv_id(paper.url)
    if arxiv_id:
        data = _get(f"{_API_BASE}/arXiv:{arxiv_id}", params={"fields": _FIELDS}, headers=headers)
        if data:
            count = data.get("citationCount")
            if isinstance(count, int):
                return count

    # 2. URL lookup
    data = _get(f"{_API_BASE}/URL:{paper.url}", params={"fields": _FIELDS}, headers=headers)
    if data:
        count = data.get("citationCount")
        if isinstance(count, int):
            return count

    # 3. Title search fallback
    if paper.title:
        data = _get(
            f"{_API_BASE}/search",
            params={"query": paper.title, "fields": _FIELDS, "limit": 1},
            headers=headers,
        )
        if data:
            results = data.get("data", [])
            if isinstance(results, list) and results:
                first = results[0]
                if isinstance(first, dict) and isinstance(first.get("citationCount"), int):
                    return int(first["citationCount"])

    return None


def enrich_citations(papers: list[Paper], api_key: str = "") -> None:
    """Fetch citation counts from Semantic Scholar and set them in-place.

    Silently skips papers where no data is found — citation_count stays 0.
    """
    for i, paper in enumerate(papers):
        if i > 0:
            time.sleep(_REQUEST_DELAY)
        count = _fetch_citation_count(paper, api_key)
        if count is not None:
            paper.citation_count = count
            logger.info("Citations for %r: %d", paper.title[:60], count)
        else:
            logger.debug("No citation data for %r", paper.title[:60])
