"""Core types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TaskName = Literal["docvqa", "chartqa", "mmmu"]
QuestionType = Literal["counting", "factual", "reasoning", "ocr", "comparison"]


@dataclass(frozen=True)
class VLMItem:
    item_id: str
    task: TaskName
    image_path: str  # may be a fixture path
    question: str
    answer: str  # gold
    question_type: QuestionType
    difficulty: int  # 1-5


@dataclass
class VLMResponse:
    text: str
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    confidence: float | None = None  # if the model returns one


@dataclass
class ScoredItem:
    item_id: str
    task: TaskName
    provider: str
    model: str
    correct: bool
    question_type: QuestionType
    difficulty: int
    latency_ms: float
    cost_usd: float
    confidence: float | None
    answer_pred: str
    answer_gold: str
