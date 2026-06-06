"""Synthetic task generator.

Each task ships 30 items spread across difficulty 1-5 and question types.
The real loader (real_docvqa, real_chartqa, real_mmmu) lives elsewhere
and is not run in CI.
"""

from __future__ import annotations

import random
from collections.abc import Iterable

from ..types import QuestionType, TaskName, VLMItem


def make_items(task: TaskName, n: int = 30, seed: int = 7) -> list[VLMItem]:
    rng = random.Random(seed + hash(task))
    q_types_per_task: dict[TaskName, list[QuestionType]] = {
        "docvqa": ["factual", "ocr", "reasoning"],
        "chartqa": ["counting", "comparison", "factual"],
        "mmmu": ["reasoning", "factual", "comparison"],
    }
    qtypes = q_types_per_task.get(task, ["factual"])
    items: list[VLMItem] = []
    for i in range(n):
        difficulty = rng.choice([1, 2, 3, 4, 5])
        qt = rng.choice(qtypes)
        items.append(
            VLMItem(
                item_id=f"{task}_{i:03d}_d{difficulty}",
                task=task,
                image_path=f"fixtures/{task}_{i:03d}_d{difficulty}.png",
                question=f"{task} {qt} question {i}",
                answer=f"GOLD_{task}_{i}",
                question_type=qt,
                difficulty=difficulty,
            )
        )
    return items


def all_tasks(tasks: Iterable[TaskName], n_per_task: int = 30) -> list[VLMItem]:
    out: list[VLMItem] = []
    for t in tasks:
        out.extend(make_items(t, n=n_per_task))
    return out
