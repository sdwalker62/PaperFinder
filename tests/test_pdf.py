"""Tests for PDF generation."""

from __future__ import annotations

from pathlib import Path

import pytest

from paperfinder.models import Paper
from paperfinder.pdf import _escape, build_pdf


@pytest.fixture()
def sample_papers() -> list[Paper]:
    return [
        Paper(
            title="Paper One",
            url="https://arxiv.org/html/1234",
            source_name="arXiv",
            category="paper",
            summary="This is a summary of paper one.\n\nIt has two paragraphs.",
            topics_matched=["machine learning"],
        ),
        Paper(
            title="Blog Post <Two>",
            url="https://blog.example.com/post-2",
            source_name="Example Blog",
            category="blog",
            abstract="Fallback abstract.",
        ),
    ]


class TestBuildPDF:
    def test_returns_bytes(self, sample_papers: list[Paper]) -> None:
        pdf_bytes = build_pdf(sample_papers)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 100
        # PDF magic bytes
        assert pdf_bytes[:5] == b"%PDF-"

    def test_writes_to_disk(self, sample_papers: list[Paper], tmp_path: Path) -> None:
        out = tmp_path / "test.pdf"
        build_pdf(sample_papers, output_path=out)
        assert out.exists()
        assert out.stat().st_size > 100

    def test_empty_papers_list(self) -> None:
        pdf_bytes = build_pdf([])
        assert pdf_bytes[:5] == b"%PDF-"


class TestEscape:
    def test_escapes_angle_brackets(self) -> None:
        assert _escape("<b>hi</b>") == "&lt;b&gt;hi&lt;/b&gt;"

    def test_escapes_ampersand(self) -> None:
        assert _escape("A & B") == "A &amp; B"
