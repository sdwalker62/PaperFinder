"""AWS Lambda handler for SAM / Lambda deployment."""

from __future__ import annotations

import logging
from typing import Any

from paperfinder.pipeline import run_pipeline

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Lambda entry point — invoked by EventBridge on schedule or manually."""
    logger.info("Lambda invoked with event: %s", event)

    from paperfinder.config import load_settings

    settings = load_settings()
    logger.info(
        "Settings loaded — model=%s, email=%s, region=%s",
        settings.llm.model,
        settings.email.sender,
        settings.aws.region,
    )

    lookback_days: int | None = event.get("lookback_days")
    skip_delivery: bool = bool(event.get("skip_delivery", False))

    if lookback_days is not None:
        logger.info("Backfill mode — lookback_days=%d, skip_delivery=%s", lookback_days, skip_delivery)

    papers = run_pipeline(settings, lookback_days=lookback_days, skip_delivery=skip_delivery)
    return {
        "statusCode": 200,
        "body": f"Pipeline complete with {len(papers)} papers.",
    }
