"""PDF report generation using ReportLab."""

from __future__ import annotations

import logging
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from paperfinder.models import Paper

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

_styles = getSampleStyleSheet()

TITLE_STYLE = ParagraphStyle(
    "DigestTitle",
    parent=_styles["Title"],
    fontSize=22,
    spaceAfter=20,
    textColor=colors.HexColor("#1a1a2e"),
)

HEADING_STYLE = ParagraphStyle(
    "PaperHeading",
    parent=_styles["Heading2"],
    fontSize=14,
    textColor=colors.HexColor("#16213e"),
    spaceAfter=6,
)

BODY_STYLE = ParagraphStyle(
    "PaperBody",
    parent=_styles["BodyText"],
    fontSize=10,
    leading=14,
    spaceAfter=4,
)

LINK_STYLE = ParagraphStyle(
    "PaperLink",
    parent=_styles["BodyText"],
    fontSize=9,
    textColor=colors.HexColor("#0f3460"),
    spaceAfter=4,
)

META_STYLE = ParagraphStyle(
    "PaperMeta",
    parent=_styles["BodyText"],
    fontSize=9,
    textColor=colors.grey,
    spaceAfter=12,
)


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


def build_pdf(papers: list[Paper], output_path: Path | None = None) -> bytes:
    """Build a digest PDF and return the raw bytes.

    If *output_path* is given the PDF is also written to disk.
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    story: list[Any] = []
    today = datetime.now().strftime("%B %d, %Y")

    # Title
    story.append(Paragraph(f"PaperFinder Digest — {today}", TITLE_STYLE))
    story.append(Spacer(1, 12))

    # Summary table
    summary_data = [
        ["Papers included", str(len(papers))],
        ["Date", today],
    ]
    summary_table = Table(summary_data, colWidths=[2 * inch, 4 * inch])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e2e2e2")),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 20))

    # Paper entries
    for idx, paper in enumerate(papers, 1):
        # Heading
        story.append(Paragraph(f"{idx}. {_escape(paper.title)}", HEADING_STYLE))

        # Source & link
        source_label = f"Source: {_escape(paper.source_name)} | Category: {paper.category}"
        story.append(Paragraph(source_label, META_STYLE))

        if paper.url:
            story.append(
                Paragraph(
                    f'<link href="{paper.display_url}">{_escape(paper.display_url)}</link>',
                    LINK_STYLE,
                )
            )

        # Summary
        summary_text = paper.summary or paper.abstract or "(No summary available)"
        for para in summary_text.split("\n\n"):
            story.append(Paragraph(_escape(para), BODY_STYLE))

        if paper.topics_matched:
            topics_str = ", ".join(paper.topics_matched)
            story.append(Paragraph(f"<i>Matched topics: {_escape(topics_str)}</i>", META_STYLE))

        story.append(Spacer(1, 16))

    doc.build(story)
    pdf_bytes = buf.getvalue()

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(pdf_bytes)
        logger.info("PDF written to %s", output_path)

    return pdf_bytes


def _escape(text: str) -> str:
    """Escape XML special characters for ReportLab paragraphs."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
