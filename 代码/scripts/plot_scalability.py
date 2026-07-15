#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
绘制可扩展性实验结果。
"""
import csv
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = ROOT / "results"
FIG_DIR = RESULTS_DIR / "fig"
FIG_DIR.mkdir(exist_ok=True)

records = []
with open(RESULTS_DIR / "scalability.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        records.append({
            "alg": row["alg"],
            "threads": int(row["threads"]) if row["threads"] else 1,
            "pop": int(row["pop"]) if row["pop"] else 0,
            "time": float(row["time"]) if row["time"] else 0,
            "best": float(row["best"]) if row["best"] else 0,
        })

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

# OpenMP 可扩展性
omp = [r for r in records if r["alg"] in ("ms", "island")]
for alg, label in [("ms", "OpenMP-MS"), ("island", "OpenMP-Island")]:
    sub = sorted([r for r in omp if r["alg"] == alg], key=lambda x: x["threads"])
    axes[0].plot([r["threads"] for r in sub], [r["time"] for r in sub], marker='o', label=label)

axes[0].set_xlabel("Number of Threads")
axes[0].set_ylabel("Time (ms)")
axes[0].set_title("OpenMP Scalability (ch150)")
axes[0].set_xticks([1, 2, 4, 8])
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# CUDA 种群规模可扩展性
cuda = sorted([r for r in records if r["alg"] == "CUDA-Base"], key=lambda x: x["pop"])
axes[1].plot([r["pop"] for r in cuda], [r["time"] for r in cuda], marker='s', color='C2')
axes[1].set_xlabel("Population Size")
axes[1].set_ylabel("Time (ms)")
axes[1].set_title("CUDA Scalability (ch150)")
axes[1].set_xticks([256, 512, 1024, 2048])
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(FIG_DIR / "scalability.png", dpi=150)
print(f"Saved {FIG_DIR / 'scalability.png'}")
