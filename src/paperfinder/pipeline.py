"""Main pipeline orchestrator — ties scraping, LLM, PDF, and delivery together."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

import requests

from paperfinder.config import Settings, WebsiteConfig, load_settings, load_sources
from paperfinder.discord_bot import post_digest
from paperfinder.email_sender import send_digest_email
from paperfinder.enrichment import enrich_citations
from paperfinder.llm import rank_and_filter, summarize_papers
from paperfinder.models import Paper
from paperfinder.pdf import build_pdf
from paperfinder.scrapers import scrape_all

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(os.environ.get("PAPERFINDER_OUTPUT_DIR", "")) or (
    Path(__file__).resolve().parent.parent.parent / "output"
)


def run_pipeline(
    settings: Settings | None = None,
    lookback_days: int | None = None,
    skip_delivery: bool = False,
) -> list[Paper]:
    """Execute the full discovery → rank → summarise → enrich → deliver pipeline.

    Args:
        settings: Loaded settings; if None, loaded from config files + env vars.
        lookback_days: Override scraping.lookback_days (useful for backfills).
        skip_delivery: If True, skip email and Discord delivery (for backfills).

    Returns:
        The list of papers included in the digest.
    """
    if settings is None:
        settings = load_settings()
    sources = load_sources()

    effective_lookback = lookback_days if lookback_days is not None else settings.scraping.lookback_days

    # 1. Scrape all sources
    logger.info("Step 1/6: Scraping %d sources (lookback=%d days) …", len(sources), effective_lookback)
    papers = scrape_all(sources, settings.scraping, lookback_days=effective_lookback)
    logger.info("Collected %d candidate papers/posts", len(papers))

    if not papers:
        logger.warning("No papers found — aborting pipeline")
        return []

    # 2. Rank by relevance
    logger.info("Step 2/6: Scoring relevance via LiteLLM (%s) …", settings.llm.model)
    top_papers = rank_and_filter(
        papers,
        topics=settings.topics,
        config=settings.llm,
        max_papers=settings.max_papers,
    )
    logger.info("Kept top %d papers", len(top_papers))

    # 3. Summarize
    logger.info("Step 3/6: Generating summaries …")
    summarize_papers(top_papers, settings.llm)

    # 4. Citation enrichment via Semantic Scholar
    if settings.enrichment.enabled:
        logger.info("Step 4/6: Enriching citation counts via Semantic Scholar …")
        enrich_citations(top_papers, api_key=settings.enrichment.semantic_scholar_api_key)
    else:
        logger.info("Step 4/6: Citation enrichment disabled — skipping")

    # 5. Persist to website database
    logger.info("Step 5/6: Persisting papers to website …")
    _publish_to_website(top_papers, settings.website)

    # 6. Build PDF and deliver
    if skip_delivery:
        logger.info("Step 6/6: Delivery skipped (backfill mode)")
    else:
        logger.info("Step 6/6: Building PDF and delivering digest …")
        today = datetime.now().strftime("%Y-%m-%d")
        pdf_path = OUTPUT_DIR / f"digest_{today}.pdf"
        pdf_bytes = build_pdf(top_papers, output_path=pdf_path)
        send_digest_email(top_papers, pdf_bytes, settings.email, settings.aws)
        post_digest(top_papers, settings.discord)

    logger.info("Pipeline complete — %d papers processed", len(top_papers))
    return top_papers


def _publish_to_website(papers: list[Paper], config: WebsiteConfig) -> None:
    """POST processed papers to the frontend API so they appear on the website."""
    if not config.api_url or not config.api_key:
        logger.info("Website API not configured — skipping database publish")
        return

    payload = [
        {
            "title": p.title,
            "url": p.url,
            "source_name": p.source_name,
            "category": p.category,
            "abstract": p.abstract,
            "published": p.published.isoformat() if p.published else None,
            "summary": p.summary,
            "relevance_score": p.relevance_score,
            "topics_matched": p.topics_matched,
            "citation_count": p.citation_count,
        }
        for p in papers
    ]

    resp = requests.post(
        config.api_url,
        json=payload,
        headers={"x-api-key": config.api_key, "Content-Type": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    logger.info("Published %d papers to website (status %d)", len(papers), resp.status_code)
