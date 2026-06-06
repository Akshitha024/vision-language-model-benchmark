from __future__ import annotations

from vlm.tasks.load import all_tasks, make_items


def test_make_items_count() -> None:
    items = make_items("docvqa", n=10)
    assert len(items) == 10
    assert all(i.task == "docvqa" for i in items)


def test_difficulty_in_range() -> None:
    items = make_items("chartqa", n=20)
    assert all(1 <= i.difficulty <= 5 for i in items)


def test_question_types_per_task() -> None:
    docvqa_items = make_items("docvqa", n=30)
    chartqa_items = make_items("chartqa", n=30)
    docvqa_types = {i.question_type for i in docvqa_items}
    chartqa_types = {i.question_type for i in chartqa_items}
    # docvqa is text-heavy; chartqa is numbers-heavy
    assert "ocr" in docvqa_types or "factual" in docvqa_types
    assert "counting" in chartqa_types or "comparison" in chartqa_types


def test_all_tasks_concatenates() -> None:
    items = all_tasks(["docvqa", "chartqa"], n_per_task=5)
    assert len(items) == 10
