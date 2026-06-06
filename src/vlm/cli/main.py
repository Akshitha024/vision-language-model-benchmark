from __future__ import annotations

from pathlib import Path
from typing import Annotated, cast

import typer
from tabulate import tabulate

from ..runner import bench
from ..types import TaskName
from ..viz.charts import (
    plot_calibration,
    plot_cost_vs_accuracy,
    plot_difficulty_curves,
    plot_provider_task_heatmap,
    plot_question_type_radar,
)

app = typer.Typer(add_completion=False, help="vlm: VLM evaluation suite")


@app.command("bench")
def cmd_bench(
    providers: Annotated[str, typer.Option(help="provider specs (comma-separated)")] = "mock",
    tasks: Annotated[str, typer.Option(help="comma-separated tasks")] = "docvqa,chartqa,mmmu",
    out_dir: Annotated[Path, typer.Option(help="results dir")] = Path("results"),
    n_per_task: Annotated[int, typer.Option(help="items per task")] = 30,
) -> None:
    p_specs = [p.strip() for p in providers.split(",") if p.strip()]
    t_specs = cast(list[TaskName], [t.strip() for t in tasks.split(",") if t.strip()])
    path = bench(p_specs, t_specs, out_dir, n_per_task=n_per_task)
    typer.echo(f"wrote {path}")


@app.command("plots")
def cmd_plots(
    scored: Annotated[Path, typer.Option(help="scored jsonl")] = Path("results/scored.jsonl"),
    figures_dir: Annotated[Path, typer.Option(help="figures dir")] = Path("results/figures"),
) -> None:
    plot_provider_task_heatmap(scored, figures_dir / "provider_task_heatmap.png")
    plot_difficulty_curves(scored, figures_dir / "difficulty_curves.png")
    plot_cost_vs_accuracy(scored, figures_dir / "cost_vs_accuracy.png")
    plot_question_type_radar(scored, figures_dir / "question_type_radar.png")
    plot_calibration(scored, figures_dir / "calibration.png")
    typer.echo(f"wrote 5 figures to {figures_dir}")


@app.command("summary")
def cmd_summary(
    scored: Annotated[Path, typer.Option(help="scored jsonl")] = Path("results/scored.jsonl"),
) -> None:
    import json
    from collections import defaultdict

    if not scored.exists():
        typer.echo("no results")
        raise typer.Exit(code=1)
    from typing import Any

    rows = [json.loads(line) for line in scored.read_text().splitlines() if line.strip()]
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_model[f"{r['provider']}/{r['model']}"].append(r)
    table = []
    for m, rs in sorted(by_model.items()):
        n = len(rs)
        acc = sum(1 for r in rs if bool(r["correct"])) / n if n else 0
        cost = sum(float(r["cost_usd"]) for r in rs)
        table.append((m, n, f"{acc:.3f}", f"${cost:.4f}"))
    print(tabulate(table, headers=["model", "n", "accuracy", "total cost"], tablefmt="github"))


if __name__ == "__main__":
    app()
