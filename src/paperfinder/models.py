"""Domain models shared across the application."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Paper:
    """A discovered paper or blog post."""

    title: str
    url: str
    source_name: str
    category: str  # "paper" | "blog"
    abstract: str = ""
    published: datetime | None = None
    summary: str = ""
    relevance_score: float = 0.0
    topics_matched: list[str] = field(default_factory=list)

    @property
    def display_url(self) -> str:
        """Return the URL suitable for display (arxiv HTML5 links, etc.)."""
        return self.url
