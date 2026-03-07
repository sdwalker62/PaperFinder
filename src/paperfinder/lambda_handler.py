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
    """Lambda entry point — invoked by EventBridge on schedule."""
    logger.info("Lambda invoked with event: %s", event)
    papers = run_pipeline()
    return {
        "statusCode": 200,
        "body": f"Digest sent with {len(papers)} papers.",
    }
