"""Tests for the LLM module (mocked LiteLLM calls)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from paperfinder.config import LLMConfig
from paperfinder.llm import BudgetExceededError, CostTracker, LLMClient, rank_and_filter
from paperfinder.models import Paper


@pytest.fixture()
def llm_cfg() -> LLMConfig:
    return LLMConfig(
        model="anthropic/claude-sonnet-4-20250514",
        max_tokens=1024,
        temperature=0.0,
        max_budget_usd=1.00,
    )


@pytest.fixture()
def sample_paper() -> Paper:
    return Paper(
        title="Attention Is All You Need",
        url="https://arxiv.org/html/1706.03762",
        source_name="arXiv",
        category="paper",
        abstract="We propose a new architecture based entirely on attention mechanisms.",
    )


def _mock_response(text: str, prompt_tokens: int = 100, completion_tokens: int = 50):
    """Build a fake litellm.ModelResponse-like object."""
    msg = MagicMock()
    msg.content = text
    choice = MagicMock()
    choice.message = msg
    usage = MagicMock()
    usage.prompt_tokens = prompt_tokens
    usage.completion_tokens = completion_tokens
    resp = MagicMock()
    resp.choices = [choice]
    resp.usage = usage
    return resp


class TestCostTracker:
    def test_starts_at_zero(self) -> None:
        ct = CostTracker(max_budget=5.0)
        assert ct.total_cost == 0.0
        assert ct.budget_exceeded is False
        assert ct.budget_remaining == 5.0

    def test_budget_exceeded(self) -> None:
        ct = CostTracker(max_budget=0.01)
        ct.total_cost = 0.02
        assert ct.budget_exceeded is True
        assert ct.budget_remaining == 0.0

    def test_summary(self) -> None:
        ct = CostTracker(max_budget=2.0)
        ct.total_cost = 0.5
        ct.total_prompt_tokens = 1000
        ct.total_completion_tokens = 500
        ct.call_count = 3
        s = ct.summary()
        assert s["calls"] == 3
        assert s["total_cost_usd"] == 0.5
        assert s["max_budget_usd"] == 2.0


class TestLLMClient:
    @patch("paperfinder.llm.litellm.completion")
    @patch("paperfinder.llm.litellm.completion_cost", return_value=0.001)
    def test_score_relevance(
        self,
        mock_cost: MagicMock,
        mock_completion: MagicMock,
        llm_cfg: LLMConfig,
        sample_paper: Paper,
    ) -> None:
        mock_completion.return_value = _mock_response(
            json.dumps(
                {"relevance_score": 0.95, "topics_matched": ["transformers", "deep learning"]}
            )
        )
        llm = LLMClient(llm_cfg)
        llm.score_relevance(sample_paper, ["deep learning", "transformers"])
        assert sample_paper.relevance_score == 0.95
        assert "transformers" in sample_paper.topics_matched

    @patch("paperfinder.llm.litellm.completion")
    @patch("paperfinder.llm.litellm.completion_cost", return_value=0.001)
    def test_score_relevance_handles_bad_json(
        self,
        mock_cost: MagicMock,
        mock_completion: MagicMock,
        llm_cfg: LLMConfig,
        sample_paper: Paper,
    ) -> None:
        mock_completion.return_value = _mock_response("not json")
        llm = LLMClient(llm_cfg)
        llm.score_relevance(sample_paper, ["ml"])
        assert sample_paper.relevance_score == 0.0

    @patch("paperfinder.llm.litellm.completion")
    @patch("paperfinder.llm.litellm.completion_cost", return_value=0.002)
    def test_summarize(
        self,
        mock_cost: MagicMock,
        mock_completion: MagicMock,
        llm_cfg: LLMConfig,
        sample_paper: Paper,
    ) -> None:
        mock_completion.return_value = _mock_response("This paper proposes the Transformer.")
        llm = LLMClient(llm_cfg)
        llm.summarize(sample_paper)
        assert "Transformer" in sample_paper.summary

    @patch("paperfinder.llm.litellm.completion")
    @patch("paperfinder.llm.litellm.completion_cost", return_value=0.001)
    def test_budget_exceeded_raises(
        self,
        mock_cost: MagicMock,
        mock_completion: MagicMock,
        sample_paper: Paper,
    ) -> None:
        cfg = LLMConfig(max_budget_usd=0.0)  # zero budget
        llm = LLMClient(cfg)
        with pytest.raises(BudgetExceededError):
            llm.score_relevance(sample_paper, ["ml"])

    @patch("paperfinder.llm.litellm.completion")
    @patch("paperfinder.llm.litellm.completion_cost", return_value=0.001)
    def test_cost_accumulates(
        self,
        mock_cost: MagicMock,
        mock_completion: MagicMock,
        llm_cfg: LLMConfig,
        sample_paper: Paper,
    ) -> None:
        mock_completion.return_value = _mock_response(
            json.dumps({"relevance_score": 0.5, "topics_matched": []})
        )
        llm = LLMClient(llm_cfg)
        llm.score_relevance(sample_paper, ["ml"])
        assert llm.cost_tracker.call_count == 1
        assert llm.cost_tracker.total_cost > 0


class TestRankAndFilter:
    @patch("paperfinder.llm.litellm.completion")
    @patch("paperfinder.llm.litellm.completion_cost", return_value=0.001)
    def test_returns_top_n(
        self, mock_cost: MagicMock, mock_completion: MagicMock, llm_cfg: LLMConfig
    ) -> None:
        scores = [0.9, 0.3, 0.7]
        call_count = {"n": 0}

        def fake_completion(**kwargs):  # type: ignore[no-untyped-def]
            idx = call_count["n"]
            call_count["n"] += 1
            return _mock_response(
                json.dumps({"relevance_score": scores[idx], "topics_matched": ["ml"]})
            )

        mock_completion.side_effect = fake_completion

        papers = [
            Paper(title=f"P{i}", url="", source_name="s", category="paper", abstract="x")
            for i in range(3)
        ]
        result = rank_and_filter(papers, ["ml"], llm_cfg, max_papers=2)
        assert len(result) == 2
        assert result[0].relevance_score >= result[1].relevance_score

    @patch("paperfinder.llm.litellm.completion")
    @patch("paperfinder.llm.litellm.completion_cost", return_value=0.50)
    def test_stops_on_budget(self, mock_cost: MagicMock, mock_completion: MagicMock) -> None:
        """With a $0.50 budget and $0.50/call cost, only 1 paper should be scored."""
        cfg = LLMConfig(max_budget_usd=0.50)
        mock_completion.return_value = _mock_response(
            json.dumps({"relevance_score": 0.8, "topics_matched": ["ml"]})
        )
        papers = [
            Paper(title=f"P{i}", url="", source_name="s", category="paper", abstract="x")
            for i in range(5)
        ]
        result = rank_and_filter(papers, ["ml"], cfg, max_papers=5)
        # After the first call, cost hits $0.50 = budget, so second call raises
        assert len(result) == 1
