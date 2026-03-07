"""LLM integration via LiteLLM — provider-agnostic with cost tracking & budget guards."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

import litellm

from paperfinder.models import Paper

if TYPE_CHECKING:
    from paperfinder.config import LLMConfig

logger = logging.getLogger(__name__)

# Suppress LiteLLM's verbose default logging
litellm.suppress_debug_info = True

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_RELEVANCE_PROMPT = """\
You are an expert ML/AI research assistant.

Given the following list of topics the user cares about:
{topics}

And the following paper/blog post:
Title: {title}
Abstract/Content: {abstract}

Rate the relevance of this paper to the user's topics on a scale of 0.0 to 1.0, \
where 1.0 means extremely relevant and 0.0 means not relevant at all.
Also list which topics this paper matches.

Respond ONLY with valid JSON in this exact schema:
{{"relevance_score": <float>, "topics_matched": [<string>, ...]}}
"""

_SUMMARY_PROMPT = """\
You are an expert ML/AI research assistant. Write a concise but informative summary \
(3-5 paragraphs) of the following paper/blog post. Focus on:
1. The main problem or research question
2. The proposed approach or method
3. Key results and contributions
4. Potential impact or applications

Title: {title}
Source: {source}
Link: {url}
Abstract/Content: {abstract}
"""


# ---------------------------------------------------------------------------
# Cost tracker
# ---------------------------------------------------------------------------


class CostTracker:
    """Accumulates token usage and estimated cost across calls."""

    def __init__(self, max_budget: float) -> None:
        self.max_budget = max_budget
        self.total_cost: float = 0.0
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.call_count: int = 0

    def record(self, response: litellm.ModelResponse) -> None:
        """Extract usage from a LiteLLM response and accumulate."""
        self.call_count += 1
        usage = response.usage  # type: ignore[union-attr]
        if usage:
            self.total_prompt_tokens += usage.prompt_tokens or 0
            self.total_completion_tokens += usage.completion_tokens or 0

        # litellm exposes per-call cost via completion_cost()
        try:
            call_cost = litellm.completion_cost(completion_response=response)
            self.total_cost += call_cost
        except Exception:
            # Cost data not available for every model — continue gracefully
            pass

    @property
    def budget_remaining(self) -> float:
        return max(0.0, self.max_budget - self.total_cost)

    @property
    def budget_exceeded(self) -> bool:
        return self.total_cost >= self.max_budget

    def summary(self) -> dict:
        return {
            "calls": self.call_count,
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens,
            "total_cost_usd": round(self.total_cost, 6),
            "max_budget_usd": self.max_budget,
            "budget_remaining_usd": round(self.budget_remaining, 6),
        }


# ---------------------------------------------------------------------------
# Client wrapper
# ---------------------------------------------------------------------------


class LLMClient:
    """Provider-agnostic LLM client powered by LiteLLM with budget guardrails."""

    def __init__(self, config: LLMConfig) -> None:
        self._model = config.model
        self._max_tokens = config.max_tokens
        self._temperature = config.temperature
        self.cost_tracker = CostTracker(max_budget=config.max_budget_usd)

        # Optional: set API base for self-hosted / proxy endpoints
        if config.api_base:
            litellm.api_base = config.api_base

    # ------------------------------------------------------------------
    def _invoke(self, prompt: str, max_tokens: int | None = None) -> str:
        """Send a single-turn message and return the assistant text."""
        if self.cost_tracker.budget_exceeded:
            raise BudgetExceededError(
                f"LLM budget of ${self.cost_tracker.max_budget:.2f} exceeded "
                f"(spent ${self.cost_tracker.total_cost:.4f}). "
                "Aborting to prevent further charges."
            )

        response = litellm.completion(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens or self._max_tokens,
            temperature=self._temperature,
        )
        self.cost_tracker.record(response)

        logger.debug(
            "LLM call #%d — cost so far: $%.4f / $%.2f",
            self.cost_tracker.call_count,
            self.cost_tracker.total_cost,
            self.cost_tracker.max_budget,
        )

        return response.choices[0].message.content  # type: ignore[union-attr]

    # ------------------------------------------------------------------
    def score_relevance(self, paper: Paper, topics: list[str]) -> Paper:
        """Score a paper's relevance and annotate it in-place."""
        prompt = _RELEVANCE_PROMPT.format(
            topics=", ".join(topics),
            title=paper.title,
            abstract=paper.abstract or "(no abstract available)",
        )
        try:
            raw = self._invoke(prompt, max_tokens=256)
            data = json.loads(raw)
            paper.relevance_score = float(data.get("relevance_score", 0.0))
            paper.topics_matched = data.get("topics_matched", [])
        except BudgetExceededError:
            raise
        except (json.JSONDecodeError, KeyError, TypeError):
            logger.warning("Failed to parse relevance response for '%s'", paper.title)
            paper.relevance_score = 0.0
        return paper

    # ------------------------------------------------------------------
    def summarize(self, paper: Paper) -> Paper:
        """Generate a summary for a paper and store it on the model."""
        prompt = _SUMMARY_PROMPT.format(
            title=paper.title,
            source=paper.source_name,
            url=paper.display_url,
            abstract=paper.abstract or "(no abstract available)",
        )
        try:
            paper.summary = self._invoke(prompt)
        except BudgetExceededError:
            raise
        except Exception:
            logger.exception("Failed to summarize '%s'", paper.title)
            paper.summary = paper.abstract  # fall back to abstract
        return paper


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class BudgetExceededError(RuntimeError):
    """Raised when the configured LLM spend budget has been exceeded."""


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------


def rank_and_filter(
    papers: list[Paper],
    topics: list[str],
    config: LLMConfig,
    max_papers: int = 15,
) -> list[Paper]:
    """Score all papers for relevance, keep the top *max_papers*."""
    llm = LLMClient(config)
    scored: list[Paper] = []
    for paper in papers:
        try:
            scored.append(llm.score_relevance(paper, topics))
        except BudgetExceededError:
            logger.warning("Budget exceeded after scoring %d papers", len(scored))
            break
    scored.sort(key=lambda p: p.relevance_score, reverse=True)

    logger.info("LLM scoring cost: %s", llm.cost_tracker.summary())
    return scored[:max_papers]


def summarize_papers(papers: list[Paper], config: LLMConfig) -> list[Paper]:
    """Generate summaries for a list of papers."""
    llm = LLMClient(config)
    for paper in papers:
        try:
            llm.summarize(paper)
        except BudgetExceededError:
            logger.warning("Budget exceeded — some papers will lack summaries")
            break

    logger.info("LLM summarization cost: %s", llm.cost_tracker.summary())
    return papers
