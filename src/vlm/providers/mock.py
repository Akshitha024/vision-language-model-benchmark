"""Mock provider with model-specific accuracy and cost profiles.

Each mock model has a per-task and per-difficulty success curve so the
chart shapes look realistic without needing real VLM access.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass

from ..types import VLMResponse
from .base import VLMProvider


@dataclass(frozen=True)
class _Profile:
    base_acc: float
    difficulty_penalty: float
    base_lat_ms: float
    cost_per_call_usd: float


_PROFILES = {
    "claude-3.5-sonnet": _Profile(0.78, 0.06, 600, 0.0085),
    "gpt-4o": _Profile(0.81, 0.05, 750, 0.012),
    "gemini-1.5-pro": _Profile(0.74, 0.07, 550, 0.0055),
    "qwen-vl-7b": _Profile(0.62, 0.10, 1500, 0.0),
    "llava-1.5-13b": _Profile(0.55, 0.12, 1900, 0.0),
}


class MockVLMProvider(VLMProvider):
    name = "mock"

    def __init__(self, model: str = "claude-3.5-sonnet", seed: int = 7) -> None:
        if model not in _PROFILES:
            raise ValueError(f"unknown mock model {model}; choose from {list(_PROFILES)}")
        self.model = model
        self.profile = _PROFILES[model]
        self._rng = random.Random(seed)

    def ask(self, image_path: str, question: str) -> VLMResponse:
        # `image_path` and `question` are stable inputs; we use them to make
        # the rng deterministic per-item-per-model
        local = random.Random(hash((image_path, question, self.model)) & 0xFFFFFFFF)
        time.sleep(0.001)  # avoid divide-by-zero in latency-based math
        # difficulty is encoded in the image path suffix (synthetic)
        difficulty = 3
        import contextlib

        with contextlib.suppress(ValueError, IndexError):
            difficulty = int(image_path.rsplit("_d", 1)[-1].split(".")[0])
        # success probability decays with difficulty
        p_correct = max(
            0.05, self.profile.base_acc - (difficulty - 1) * self.profile.difficulty_penalty
        )
        # confidence is a noisy version of correctness probability
        confidence = max(0.0, min(1.0, p_correct + local.gauss(0, 0.05)))
        # produce "correct" answer per-item by reusing the gold answer if
        # the local roll succeeds; we encode that path in answer text
        correct_marker = "[CORRECT]" if local.random() < p_correct else "[WRONG]"
        text = f"{correct_marker} mock answer for: {question[:32]}"
        return VLMResponse(
            text=text,
            latency_ms=self.profile.base_lat_ms + local.uniform(0, 200),
            prompt_tokens=len(question) // 4 + 256,  # +256 ~ image tokens
            completion_tokens=12,
            cost_usd=self.profile.cost_per_call_usd,
            confidence=confidence,
        )
