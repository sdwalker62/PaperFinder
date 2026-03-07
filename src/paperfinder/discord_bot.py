"""Discord webhook integration for posting digest summaries."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import requests

if TYPE_CHECKING:
    from paperfinder.config import DiscordConfig
    from paperfinder.models import Paper

logger = logging.getLogger(__name__)

MAX_EMBED_DESCRIPTION = 4096
MAX_EMBEDS_PER_MESSAGE = 10


def post_digest(papers: list[Paper], config: DiscordConfig) -> None:
    """Post a digest summary to a Discord channel via webhook.

    Does nothing if Discord is disabled in the configuration.
    """
    if not config.enabled or not config.webhook_url:
        logger.debug("Discord integration disabled — skipping")
        return

    embeds: list[dict[str, Any]] = []
    for paper in papers[:MAX_EMBEDS_PER_MESSAGE]:
        description = paper.summary or paper.abstract or ""
        if len(description) > MAX_EMBED_DESCRIPTION:
            description = description[: MAX_EMBED_DESCRIPTION - 3] + "..."

        embed: dict[str, Any] = {
            "title": paper.title,
            "url": paper.display_url,
            "description": description,
            "color": 0x0F3460,
            "fields": [
                {"name": "Source", "value": paper.source_name, "inline": True},
                {"name": "Category", "value": paper.category, "inline": True},
            ],
        }
        if paper.topics_matched:
            embed["fields"].append(
                {
                    "name": "Matched Topics",
                    "value": ", ".join(paper.topics_matched),
                    "inline": False,
                }
            )
        embeds.append(embed)

    payload = {
        "content": f"📄 **PaperFinder Digest** — {len(papers)} papers",
        "embeds": embeds,
    }

    try:
        resp = requests.post(
            config.webhook_url,
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        logger.info("Digest posted to Discord")
    except requests.RequestException:
        logger.exception("Failed to post digest to Discord")


def post_single_paper(paper: Paper, config: DiscordConfig) -> None:
    """Post a single paper to Discord (for real-time alerts)."""
    if not config.enabled or not config.webhook_url:
        return

    description = paper.summary or paper.abstract or ""
    if len(description) > MAX_EMBED_DESCRIPTION:
        description = description[: MAX_EMBED_DESCRIPTION - 3] + "..."

    payload = {
        "embeds": [
            {
                "title": paper.title,
                "url": paper.display_url,
                "description": description,
                "color": 0x0F3460,
                "fields": [
                    {"name": "Source", "value": paper.source_name, "inline": True},
                    {"name": "Category", "value": paper.category, "inline": True},
                ],
            }
        ]
    }

    try:
        resp = requests.post(config.webhook_url, json=payload, timeout=15)
        resp.raise_for_status()
    except requests.RequestException:
        logger.exception("Failed to post paper to Discord")
