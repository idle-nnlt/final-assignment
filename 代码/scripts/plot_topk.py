#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
绘制 Top-k Memetic 精炼实验结果。
"""
import csv
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = ROOT / "results"
FIG_DIR = RESULTS_DIR / "fig"
FIG_DIR.mkdir(exist_ok=True)

# 读取 CSV
records = []
with open(RESULTS_DIR / "topk_experiment.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        records.append({
            "instance": row["instance"].replace(".tsp", ""),
            "top_k": int(row["top_k"]),
            "gap": float(row["gap"]),
            "time": float(row["time"]),
        })

# 聚合
agg = defaultdict(lambda: {"gap": [], "time": []})
for r in records:
    agg[(r["instance"], r["top_k"])]["gap"].append(r["gap"])
    agg[(r["instance"], r["top_k"])]["time"].append(r["time"])

summary = {}
for (inst, k), v in agg.items():
    summary.setdefault(inst, {})[k] = {
        "gap": sum(v["gap"]) / len(v["gap"]),
        "time": sum(v["time"]) / len(v["time"]),
    }

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

for ax, metric, ylabel in [(axes[0], "gap", "Average Gap (%)"), (axes[1], "time", "Average Time (ms)")]:
    for inst, data in summary.items():
        ks = sorted(data.keys())
        vals = [data[k][metric] for k in ks]
        ax.plot(ks, vals, marker='o', label=inst)
    ax.set_xlabel("Top-k Individuals Refined")
    ax.set_ylabel(ylabel)
    ax.set_xticks([1, 3, 5, 10])
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(FIG_DIR / "topk_sensitivity.png", dpi=150)
print(f"Saved {FIG_DIR / 'topk_sensitivity.png'}")

# 打印汇总表
print(f"{'Instance':<10} {'k':>3} {'Avg Gap (%)':>12} {'Avg Time (ms)':>15}")
for inst, data in summary.items():
    for k in sorted(data.keys()):
        print(f"{inst:<10} {k:>3} {data[k]['gap']:>12.2f} {data[k]['time']:>15.2f}")
