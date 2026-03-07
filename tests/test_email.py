"""Tests for email sender (mocked SES)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from paperfinder.config import AWSConfig, EmailConfig
from paperfinder.email_sender import send_digest_email
from paperfinder.models import Paper


@pytest.fixture()
def email_cfg() -> EmailConfig:
    return EmailConfig(
        sender="test@example.com",
        recipients=["user@example.com"],
        subject_prefix="[Test]",
    )


@pytest.fixture()
def aws_cfg() -> AWSConfig:
    return AWSConfig(region="us-east-1")


@pytest.fixture()
def papers() -> list[Paper]:
    return [
        Paper(title="Paper 1", url="https://example.com/1", source_name="s", category="paper"),
    ]


class TestSendDigestEmail:
    @patch("paperfinder.email_sender.boto3.client")
    def test_sends_email(
        self,
        mock_client_ctor: MagicMock,
        papers: list[Paper],
        email_cfg: EmailConfig,
        aws_cfg: AWSConfig,
    ) -> None:
        mock_ses = MagicMock()
        mock_client_ctor.return_value = mock_ses

        send_digest_email(papers, b"%PDF-fake", email_cfg, aws_cfg)

        mock_client_ctor.assert_called_once_with("ses", region_name="us-east-1")
        mock_ses.send_raw_email.assert_called_once()
        call_kwargs = mock_ses.send_raw_email.call_args
        assert "user@example.com" in call_kwargs.kwargs["Destinations"]
