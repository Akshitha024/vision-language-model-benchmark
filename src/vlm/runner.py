from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path

from loguru import logger
from tqdm import tqdm

from .providers.base import VLMProvider
from .providers.mock import MockVLMProvider
from .scoring.score import score_item
from .tasks.load import all_tasks
from .types import ScoredItem, TaskName


def build_provider(spec: str) -> VLMProvider:
    if spec.startswith("mock:"):
        _, model = spec.split(":", 1)
        return MockVLMProvider(model=model)
    if spec == "mock":
        return MockVLMProvider()
    raise ValueError(f"unknown provider spec {spec!r}")


def bench(
    provider_specs: list[str], tasks: Iterable[TaskName], out_dir: Path, n_per_task: int = 30
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    items = all_tasks(tasks, n_per_task=n_per_task)
    rows: list[ScoredItem] = []
    for spec in provider_specs:
        if spec == "mock":
            specs_to_run = [
                f"mock:{m}"
                for m in (
                    "claude-3.5-sonnet",
                    "gpt-4o",
                    "gemini-1.5-pro",
                    "qwen-vl-7b",
                    "llava-1.5-13b",
                )
            ]
        else:
            specs_to_run = [spec]
        for s in specs_to_run:
            provider = build_provider(s)
            for item in tqdm(items, desc=f"{provider.model}"):
                resp = provider.ask(item.image_path, item.question)
                rows.append(score_item(item, resp, provider.name, provider.model))

    path = out_dir / "scored.jsonl"
    with path.open("w") as f:
        for r in rows:
            f.write(json.dumps(asdict(r)) + "\n")
    logger.info("wrote {} rows to {}", len(rows), path)
    return path
