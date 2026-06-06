"""Five distinct charts for the VLM benchmark.

- per-(provider, task) accuracy heatmap (rows = providers, cols = tasks)
- difficulty curve (accuracy as difficulty rises, one line per provider)
- cost vs accuracy scatter
- per-question-type radar (accuracy by qtype, one polygon per provider)
- confidence calibration plot (reliability diagram)
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


def _load(p: Path) -> list[dict[str, Any]]:
    if not p.exists():
        return []
    out: list[dict[str, Any]] = []
    with p.open() as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def _model_key(row: dict[str, Any]) -> str:
    return f"{row['provider']}/{row['model']}"


def plot_provider_task_heatmap(scored_path: Path, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = _load(scored_path)
    if not rows:
        out.write_bytes(b"")
        return out
    by_model_task: dict[tuple[str, str], list[bool]] = defaultdict(list)
    for r in rows:
        by_model_task[(_model_key(r), str(r["task"]))].append(bool(r["correct"]))
    models = sorted({k[0] for k in by_model_task})
    tasks = sorted({k[1] for k in by_model_task})
    mat = np.zeros((len(models), len(tasks)))
    for i, m in enumerate(models):
        for j, t in enumerate(tasks):
            corr = by_model_task.get((m, t), [])
            mat[i, j] = float(np.mean(corr)) if corr else 0.0
    fig, ax = plt.subplots(figsize=(max(5, 0.8 * len(tasks) + 3), max(4, 0.5 * len(models) + 2)))
    im = ax.imshow(mat, cmap="YlGn", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(tasks)))
    ax.set_xticklabels(tasks, fontsize=10)
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels(models, fontsize=8)
    for i in range(len(models)):
        for j in range(len(tasks)):
            ax.text(
                j,
                i,
                f"{mat[i, j]:.2f}",
                ha="center",
                va="center",
                fontsize=8,
                color="white" if mat[i, j] < 0.5 else "black",
            )
    fig.colorbar(im, ax=ax, label="accuracy")
    ax.set_title("Per-(provider, task) accuracy")
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.close(fig)
    return out


def plot_difficulty_curves(scored_path: Path, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = _load(scored_path)
    if not rows:
        out.write_bytes(b"")
        return out
    by_model_diff: dict[tuple[str, int], list[bool]] = defaultdict(list)
    for r in rows:
        by_model_diff[(_model_key(r), int(r["difficulty"]))].append(bool(r["correct"]))
    models = sorted({k[0] for k in by_model_diff})
    difficulties = sorted({k[1] for k in by_model_diff})
    fig, ax = plt.subplots(figsize=(7.5, 5))
    for m in models:
        ys = [float(np.mean(by_model_diff.get((m, d), [False]))) for d in difficulties]
        ax.plot(difficulties, ys, marker="o", linewidth=1.8, label=m)
    ax.set_xticks(difficulties)
    ax.set_xlabel("difficulty")
    ax.set_ylabel("accuracy")
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.set_title("Accuracy vs difficulty per provider")
    ax.legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.close(fig)
    return out


def plot_cost_vs_accuracy(scored_path: Path, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = _load(scored_path)
    if not rows:
        out.write_bytes(b"")
        return out
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_model[_model_key(r)].append(r)
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    for m, rs in sorted(by_model.items()):
        acc = float(np.mean([bool(r["correct"]) for r in rs]))
        total_cost = float(np.sum([float(r["cost_usd"]) for r in rs]))
        ax.scatter(total_cost, acc, s=160, alpha=0.8, edgecolor="black")
        ax.annotate(m, (total_cost, acc), textcoords="offset points", xytext=(8, 6), fontsize=9)
    ax.set_xlabel("total cost on this run (USD)")
    ax.set_ylabel("accuracy")
    ax.set_ylim(0, 1.05)
    ax.set_xlim(left=0)
    ax.grid(True, alpha=0.3)
    ax.set_title("Cost vs accuracy per provider")
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.close(fig)
    return out


def plot_question_type_radar(scored_path: Path, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = _load(scored_path)
    if not rows:
        out.write_bytes(b"")
        return out
    by_model_qt: dict[tuple[str, str], list[bool]] = defaultdict(list)
    for r in rows:
        by_model_qt[(_model_key(r), str(r["question_type"]))].append(bool(r["correct"]))
    models = sorted({k[0] for k in by_model_qt})
    qtypes = sorted({k[1] for k in by_model_qt})
    angles = np.linspace(0, 2 * np.pi, len(qtypes), endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"projection": "polar"})
    for m in models:
        vals = [float(np.mean(by_model_qt.get((m, qt), [False]))) for qt in qtypes]
        vals += vals[:1]
        ax.plot(angles, vals, marker="o", linewidth=1.8, label=m)
        ax.fill(angles, vals, alpha=0.08)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(qtypes, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_title("Per-question-type accuracy", pad=24)
    ax.legend(loc="upper right", bbox_to_anchor=(1.45, 1.05), fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.close(fig)
    return out


def plot_calibration(scored_path: Path, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = _load(scored_path)
    if not rows:
        out.write_bytes(b"")
        return out
    by_model: dict[str, list[tuple[float, bool]]] = defaultdict(list)
    for r in rows:
        if r.get("confidence") is None:
            continue
        by_model[_model_key(r)].append((float(r["confidence"]), bool(r["correct"])))
    if not by_model:
        out.write_bytes(b"")
        return out
    fig, ax = plt.subplots(figsize=(7, 6))
    bins = np.linspace(0, 1, 11)
    for m, pairs in sorted(by_model.items()):
        confs = np.array([p[0] for p in pairs])
        accs = np.array([p[1] for p in pairs], dtype=float)
        bin_means_conf: list[float] = []
        bin_means_acc: list[float] = []
        from itertools import pairwise

        for lo, hi in pairwise(bins):
            mask = (confs >= lo) & (confs < hi)
            if mask.sum() < 2:
                continue
            bin_means_conf.append(float(confs[mask].mean()))
            bin_means_acc.append(float(accs[mask].mean()))
        ax.plot(bin_means_conf, bin_means_acc, marker="o", linewidth=1.5, label=m)
    ax.plot([0, 1], [0, 1], "k--", alpha=0.4, label="perfect calibration")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("predicted confidence")
    ax.set_ylabel("observed accuracy")
    ax.grid(True, alpha=0.3)
    ax.set_title("Reliability diagram (confidence vs accuracy)")
    ax.legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.close(fig)
    return out
