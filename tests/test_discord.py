"""Tests for the Discord integration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from paperfinder.config import DiscordConfig
from paperfinder.discord_bot import post_digest, post_single_paper
from paperfinder.models import Paper


@pytest.fixture()
def enabled_cfg() -> DiscordConfig:
    return DiscordConfig(enabled=True, webhook_url="https://discord.com/api/webhooks/test")


@pytest.fixture()
def disabled_cfg() -> DiscordConfig:
    return DiscordConfig(enabled=False, webhook_url="")


@pytest.fixture()
def papers() -> list[Paper]:
    return [
        Paper(
            title="Paper A",
            url="https://example.com/a",
            source_name="src",
            category="paper",
            summary="Summary A",
            topics_matched=["ml"],
        ),
    ]


class TestPostDigest:
    @patch("paperfinder.discord_bot.requests.post")
    def test_posts_when_enabled(
        self, mock_post: MagicMock, papers: list[Paper], enabled_cfg: DiscordConfig
    ) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()
        post_digest(papers, enabled_cfg)
        mock_post.assert_called_once()
        payload = mock_post.call_args.kwargs["json"]
        assert len(payload["embeds"]) == 1

    def test_skips_when_disabled(self, papers: list[Paper], disabled_cfg: DiscordConfig) -> None:
        # Should not raise
        post_digest(papers, disabled_cfg)


class TestPostSinglePaper:
    @patch("paperfinder.discord_bot.requests.post")
    def test_posts_single(
        self, mock_post: MagicMock, papers: list[Paper], enabled_cfg: DiscordConfig
    ) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()
        post_single_paper(papers[0], enabled_cfg)
        mock_post.assert_called_once()

    def test_skips_when_disabled(self, papers: list[Paper], disabled_cfg: DiscordConfig) -> None:
        post_single_paper(papers[0], disabled_cfg)
