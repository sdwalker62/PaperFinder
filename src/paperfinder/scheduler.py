"""Scheduler — runs the pipeline at a configured time each day."""

from __future__ import annotations

import logging
import time

import schedule

from paperfinder.config import load_settings
from paperfinder.pipeline import run_pipeline

logger = logging.getLogger(__name__)


def start_scheduler() -> None:  # pragma: no cover
    """Block forever, running the pipeline at the configured delivery time."""
    settings = load_settings()
    delivery_time = settings.delivery_time
    logger.info("Scheduling daily run at %s (%s)", delivery_time, settings.timezone)

    schedule.every().day.at(delivery_time).do(run_pipeline, settings=settings)

    # Also run immediately on startup for testing / first run
    logger.info("Running initial pipeline …")
    run_pipeline(settings)

    while True:
        schedule.run_pending()
        time.sleep(60)
