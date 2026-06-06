"""Scoring: parse the [CORRECT]/[WRONG] markers from the mock provider for the
synthetic suite; real loaders normalize gold + prediction and compare directly.
"""

from __future__ import annotations

from ..types import ScoredItem, VLMItem, VLMResponse


def score_item(item: VLMItem, resp: VLMResponse, provider: str, model: str) -> ScoredItem:
    # in the synthetic suite the mock provider tags answers with [CORRECT]
    # or [WRONG] so the scorer can be unambiguous. Real scorer would do
    # normalize + exact match + ANLS (DocVQA) or numeric tolerance (ChartQA).
    correct = "[CORRECT]" in resp.text
    return ScoredItem(
        item_id=item.item_id,
        task=item.task,
        provider=provider,
        model=model,
        correct=correct,
        question_type=item.question_type,
        difficulty=item.difficulty,
        latency_ms=resp.latency_ms,
        cost_usd=resp.cost_usd,
        confidence=resp.confidence,
        answer_pred=resp.text,
        answer_gold=item.answer,
    )
