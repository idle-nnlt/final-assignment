#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
绘制 CUDA-Memetic 参数敏感性图：不同种群规模下 Gap 和时间随迭代代数的变化。
"""
import csv
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = ROOT / "results"
FIG_DIR = RESULTS_DIR / "fig"
FIG_DIR.mkdir(exist_ok=True)

records = []
with open(RESULTS_DIR / "sensitivity.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        records.append({
            "pop": int(row["pop"]),
            "gen": int(row["gen"]),
            "gap": float(row["gap"]),
            "time": float(row["time"]),
        })

# 按 (pop, gen) 聚合
agg_gap = defaultdict(list)
agg_time = defaultdict(list)
for r in records:
    agg_gap[(r["pop"], r["gen"])].append(r["gap"])
    agg_time[(r["pop"], r["gen"])].append(r["time"])

pops = sorted(set(r["pop"] for r in records))
gens = sorted(set(r["gen"] for r in records))

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

for pop in pops:
    gaps = []
    times = []
    for g in gens:
        gap_list = agg_gap.get((pop, g), [])
        time_list = agg_time.get((pop, g), [])
        gaps.append(sum(gap_list) / len(gap_list) if gap_list else 0.0)
        times.append(sum(time_list) / len(time_list) if time_list else 0.0)
    axes[0].plot(gens, gaps, marker='o', label=f"m={pop}")
    axes[1].plot(gens, times, marker='s', label=f"m={pop}")

axes[0].set_xlabel("Generations $G$")
axes[0].set_ylabel("Average Gap (%)")
axes[0].set_title("Gap vs. Generations")
axes[0].set_xticks(gens)
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].set_xlabel("Generations $G$")
axes[1].set_ylabel("Average Time (ms)")
axes[1].set_title("Time vs. Generations")
axes[1].set_xticks(gens)
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
fig.savefig(FIG_DIR / "sensitivity.png", dpi=150)
print(f"Saved {FIG_DIR / 'sensitivity.png'}")
