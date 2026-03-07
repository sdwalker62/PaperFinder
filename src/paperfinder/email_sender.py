"""Email delivery via AWS SES."""

from __future__ import annotations

import logging
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import TYPE_CHECKING

import boto3  # noqa: F401 — stubs via boto3-stubs

if TYPE_CHECKING:
    from paperfinder.config import AWSConfig, EmailConfig
    from paperfinder.models import Paper

logger = logging.getLogger(__name__)


def send_digest_email(
    papers: list[Paper],
    pdf_bytes: bytes,
    email_cfg: EmailConfig,
    aws_cfg: AWSConfig,
) -> None:
    """Send the digest PDF as an email attachment via SES."""
    ses = boto3.client("ses", region_name=aws_cfg.region)
    today = datetime.now().strftime("%Y-%m-%d")
    subject = f"{email_cfg.subject_prefix} Daily Digest — {today}"

    # Plain-text body with paper list
    body_lines = [f"PaperFinder Digest for {today}", "", f"Papers included: {len(papers)}", ""]
    for idx, paper in enumerate(papers, 1):
        body_lines.append(f"{idx}. {paper.title}")
        body_lines.append(f"   {paper.display_url}")
        body_lines.append(f"   Source: {paper.source_name} ({paper.category})")
        body_lines.append("")
    body_lines.append("Full summaries are attached as a PDF.")
    body_text = "\n".join(body_lines)

    # Build MIME message
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = email_cfg.sender
    msg["To"] = ", ".join(email_cfg.recipients)

    msg.attach(MIMEText(body_text, "plain"))

    attachment = MIMEApplication(pdf_bytes)
    attachment.add_header(
        "Content-Disposition",
        "attachment",
        filename=f"paperfinder_digest_{today}.pdf",
    )
    msg.attach(attachment)

    ses.send_raw_email(
        Source=email_cfg.sender,
        Destinations=email_cfg.recipients,
        RawMessage={"Data": msg.as_string()},
    )
    logger.info("Digest email sent to %s", email_cfg.recipients)
