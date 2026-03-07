"""Main pipeline orchestrator — ties scraping, LLM, PDF, and delivery together."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from paperfinder.config import Settings, load_settings, load_sources
from paperfinder.discord_bot import post_digest
from paperfinder.models import Paper
from paperfinder.email_sender import send_digest_email
from paperfinder.llm import rank_and_filter, summarize_papers
from paperfinder.pdf import build_pdf
from paperfinder.scrapers import scrape_all

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "output"


def run_pipeline(settings: Settings | None = None) -> list[Paper]:
    """Execute the full discovery → rank → summarise → deliver pipeline.

    Returns the list of papers included in the digest.
    """
    if settings is None:
        settings = load_settings()
    sources = load_sources()

    # 1. Scrape all sources
    logger.info("Step 1/5: Scraping %d sources …", len(sources))
    papers = scrape_all(
        sources,
        settings.scraping,
        lookback_days=settings.scraping.lookback_days,
    )
    logger.info("Collected %d candidate papers/posts", len(papers))

    if not papers:
        logger.warning("No papers found — aborting pipeline")
        return []

    # 2. Rank by relevance
    logger.info("Step 2/5: Scoring relevance via LiteLLM (%s) …", settings.llm.model)
    top_papers = rank_and_filter(
        papers,
        topics=settings.topics,
        config=settings.llm,
        max_papers=settings.max_papers,
    )
    logger.info("Kept top %d papers", len(top_papers))

    # 3. Summarize
    logger.info("Step 3/5: Generating summaries …")
    summarize_papers(top_papers, settings.llm)

    # 4. Build PDF
    logger.info("Step 4/5: Building PDF digest …")
    today = datetime.now().strftime("%Y-%m-%d")
    pdf_path = OUTPUT_DIR / f"digest_{today}.pdf"
    pdf_bytes = build_pdf(top_papers, output_path=pdf_path)

    # 5. Deliver
    logger.info("Step 5/5: Delivering digest …")
    send_digest_email(top_papers, pdf_bytes, settings.email, settings.aws)

    # Optional: Discord
    post_digest(top_papers, settings.discord)

    logger.info("Pipeline complete — %d papers delivered", len(top_papers))
    return top_papers
