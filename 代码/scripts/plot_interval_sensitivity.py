#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
绘制 2-opt 精炼间隔敏感性图（含误差棒）。
"""
import csv
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = ROOT / "results"
FIG_DIR = RESULTS_DIR / "fig"
FIG_DIR.mkdir(exist_ok=True)

# 读取数据
records = []
with open(RESULTS_DIR / "interval_sensitivity.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        records.append({
            "interval": int(row["interval"]),
            "gap": float(row["gap"]),
            "time": float(row["time"]),
        })

# 按 interval 聚合
agg = defaultdict(list)
for r in records:
    agg[r["interval"]].append(r["gap"])

intervals = sorted(agg.keys())
means = []
stds = []
for k in intervals:
    vals = agg[k]
    n = len(vals)
    mean = sum(vals) / n
    var = sum((x - mean) ** 2 for x in vals) / n
    std = var ** 0.5
    means.append(mean)
    stds.append(std)

fig, ax = plt.subplots(figsize=(8, 5))
ax.errorbar(intervals, means, yerr=stds, marker='o', capsize=5, linestyle='-', linewidth=1.5)
ax.set_xlabel("2-opt Refinement Interval $\tau$")
ax.set_ylabel("Average Gap (%)")
ax.set_title("CUDA-Memetic Interval Sensitivity (berlin52, 3 seeds)")
ax.set_xticks(intervals)
ax.grid(True, alpha=0.3)
plt.tight_layout()
fig.savefig(FIG_DIR / "interval_sensitivity.png", dpi=150)
print(f"Saved {FIG_DIR / 'interval_sensitivity.png'}")
