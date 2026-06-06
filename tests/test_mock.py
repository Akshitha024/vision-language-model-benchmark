from __future__ import annotations

import pytest

from vlm.providers.mock import MockVLMProvider


def test_mock_unknown_model_raises() -> None:
    with pytest.raises(ValueError):
        MockVLMProvider(model="nope")


def test_mock_returns_response() -> None:
    p = MockVLMProvider(model="claude-3.5-sonnet")
    r = p.ask("fixtures/test_d3.png", "What is shown?")
    assert r.text
    assert r.latency_ms > 0
    assert r.cost_usd > 0


def test_mock_deterministic_per_item() -> None:
    p = MockVLMProvider(model="gpt-4o")
    r1 = p.ask("fixtures/test_d3.png", "What is shown?")
    r2 = p.ask("fixtures/test_d3.png", "What is shown?")
    assert r1.text == r2.text  # deterministic hashing on (image, question, model)


def test_difficulty_decreases_accuracy() -> None:
    p = MockVLMProvider(model="claude-3.5-sonnet")
    # run many trials at d1 vs d5 to verify expected accuracy gap
    easy = sum(1 for i in range(60) if "[CORRECT]" in p.ask("x_d1.png", f"q{i}").text)
    hard = sum(1 for i in range(60) if "[CORRECT]" in p.ask("x_d5.png", f"q{i}").text)
    assert easy > hard
