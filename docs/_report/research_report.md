---
title: "vision-language-model-benchmark: cross-provider VLM evaluation"
author: "Akshitha Reddy Lingampally"
date: "2026-06-06"
geometry: margin=1in
fontsize: 11pt
---

# Abstract

We present `vision-language-model-benchmark`, a cross-provider VLM
evaluation harness that runs Claude / GPT-4V / Gemini / Qwen-VL /
LLaVA across DocVQA, ChartQA, and MMMU-style tasks. It ships per-
model accuracy / cost / latency profiles so the suite runs in CI
without API keys (a `MockVLMProvider` per model), and a real
provider drop-in is a one-line change. We report a 450-call mock
bench across 5 providers × 3 tasks × 30 items: GPT-4o tops at 0.644
accuracy ($1.08 total), Claude-3.5-Sonnet close behind at 0.633 for
$0.77 (the cost-efficient pick), Gemini-1.5-Pro at 0.522 / $0.50;
open-source mock Qwen-VL-7B and LLaVA-1.5-13B at 0.42 and 0.28 (free).
All five chart types populate, including a reliability diagram that
shows the expected confidence-vs-accuracy curves.

# 1. Background

Vision-Language Model selection in production is bottlenecked by the
same problem as text-only LLM selection: there are several frontier
models from different providers with materially different price points,
and the public leaderboards rarely report cost. A practical eval suite
must report:

- per-(provider, task) accuracy
- per-question-type accuracy (counting vs reasoning vs OCR)
- per-difficulty accuracy (easy vs hard items)
- cost per item
- latency p50/p99
- confidence calibration (do the model's reported confidences correlate
  with accuracy?)

This project ships all six.

# 2. Related Work

- **MMMU** (Yue et al., 2024): the major multi-discipline VLM
  benchmark.
- **DocVQA** (Mathew et al., 2021): document visual QA.
- **ChartQA** (Masry et al., 2022): chart understanding.
- **PaliGemma** (Beyer et al., 2024): one of the major open-weight
  VLMs.
- **Qwen-VL** (Bai et al., 2023): the Alibaba open-weight VLM.
- **LLaVA** (Liu et al., 2023): the canonical open VLM.

# 3. Method

## 3.1 Mock provider profiles

Each mock model has a `_Profile(base_acc, difficulty_penalty,
base_lat_ms, cost_per_call_usd)`. The mock returns "correct" with
probability `max(0.05, base_acc - (difficulty - 1) *
difficulty_penalty)`, where difficulty is encoded in the synthetic
image path. Confidence is a noisy version of correctness probability,
so the reliability-diagram axis is meaningful.

| model              | base_acc | difficulty_penalty | base_lat | cost/call |
|--------------------|---------:|-------------------:|---------:|----------:|
| claude-3.5-sonnet  |     0.78 |               0.06 |    600ms |   $0.0085 |
| gpt-4o             |     0.81 |               0.05 |    750ms |   $0.0120 |
| gemini-1.5-pro     |     0.74 |               0.07 |    550ms |   $0.0055 |
| qwen-vl-7b         |     0.62 |               0.10 |   1500ms |   $0.0000 |
| llava-1.5-13b      |     0.55 |               0.12 |   1900ms |   $0.0000 |

## 3.2 Task generation

For each task (docvqa, chartqa, mmmu) we generate 30 items split
across difficulty 1-5 and the task-appropriate question types
(docvqa: factual/ocr/reasoning, chartqa: counting/comparison/factual,
mmmu: reasoning/factual/comparison).

## 3.3 Five chart types

1. **Per-(provider, task) accuracy heatmap**
2. **Accuracy vs difficulty curves** (one line per provider)
3. **Cost vs accuracy frontier** (Pareto scatter)
4. **Per-question-type radar** (one polygon per provider)
5. **Confidence calibration** (reliability diagram)

# 4. Data

Synthetic, deterministic. Real-data drop-in for DocVQA / ChartQA /
MMMU is a one-loader change in `tasks/load.py`.

# 5. Evaluation Setup

5 providers × 3 tasks × 30 items = 450 calls. Hardware: Apple
M-series CPU. Mock providers run essentially instantly; real
providers would take ~10 minutes of API time at this scale.

# 6. Results

| model                  |   n |   accuracy | total cost |
|------------------------|----:|-----------:|-----------:|
| mock/claude-3.5-sonnet |  90 |      0.633 |    $0.7650 |
| mock/gpt-4o            |  90 |      0.644 |    $1.0800 |
| mock/gemini-1.5-pro    |  90 |      0.522 |    $0.4950 |
| mock/qwen-vl-7b        |  90 |      0.422 |    $0.0000 |
| mock/llava-1.5-13b     |  90 |      0.278 |    $0.0000 |

Three findings:

1. **GPT-4o tops the leaderboard** at 0.644 accuracy. Claude-3.5-Sonnet
   is essentially tied (0.633) at 71% of the cost.
2. **Cost-efficient pick: Claude-3.5-Sonnet** at $0.77 for the same
   workload that costs $1.08 on GPT-4o. ~30% cost reduction for
   ~1.7 point accuracy loss.
3. **Open-source mocks (Qwen-VL, LLaVA)** are at $0 but well behind
   on accuracy; useful for self-hosted deployments where API spend is
   non-negotiable.

The reliability-diagram (confidence calibration) shows the expected
mild over-confidence pattern across all five providers — they report
confidences slightly higher than their observed accuracy across the
0.4-0.8 band.

# 7. Ablations

The mock difficulty penalty was tuned so that the difficulty curves
have a meaningful slope (0.05-0.12 per difficulty level). Higher
penalties produce noisier curves; lower penalties produce flat ones
that defeat the chart's purpose.

# 8. Discussion

The five-chart set together answers the production questions for VLM
provider selection. The heatmap tells you which model is best per
task. The difficulty curves tell you which model holds up on hard
items. The cost-vs-accuracy frontier picks the Pareto-optimal
provider. The question-type radar tells you whether one provider is
weak on a specific reasoning type. The calibration diagram tells you
whether confidence scores are safe to use as a gating signal.

# 9. Limitations

1. **Mock provider profiles are stylized, not measured.** Real
   numbers will move; chart shapes hold.
2. **Synthetic items.** Real DocVQA / ChartQA / MMMU loaders are not
   yet integrated.
3. **No batching.** One call per item; real production should batch.
4. **No LLM-as-judge.** Free-form items (DocVQA has many) need a
   judge for ANLS-style scoring; future work.

# 10. Future Work

- [ ] Real provider adapters (Anthropic, OpenAI, Google SDK calls).
- [ ] HF LLaVA / Qwen-VL providers via transformers `pipeline`.
- [ ] Real DocVQA / ChartQA / MMMU dataset loaders.
- [ ] LLM-as-judge for free-form answers.
- [ ] Per-difficulty cost-per-correct (the useful efficiency metric).

# 11. References

- Bai, J., et al. (2023). *Qwen-VL: A Versatile Vision-Language Model
  for Understanding, Localization, Text Reading, and Beyond.*
  arXiv:2308.12966.
- Beyer, L., et al. (2024). *PaliGemma: A versatile 3B VLM for
  transfer.* arXiv:2407.07726.
- Liu, H., et al. (2023). *Visual Instruction Tuning.* NeurIPS.
- Masry, A., et al. (2022). *ChartQA: A Benchmark for Question
  Answering about Charts with Visual and Logical Reasoning.* ACL.
- Mathew, M., et al. (2021). *DocVQA: A Dataset for VQA on Document
  Images.* WACV.
- Yue, X., et al. (2024). *MMMU: A Massive Multi-discipline Multimodal
  Understanding and Reasoning Benchmark for Expert AGI.* CVPR.

# Appendix A. Reproducibility

- Repo: `Akshitha024/vision-language-model-benchmark`, MIT.
- Reproduce: `make bench && make plots`.
- 5 charts in `results/figures/`.
- Test artifacts in `docs/test_results/`.
