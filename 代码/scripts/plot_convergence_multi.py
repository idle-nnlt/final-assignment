#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
绘制多实例收敛曲线对比图。
"""
import csv
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FIG_DIR = ROOT / "results" / "fig"
FIG_DIR.mkdir(parents=True, exist_ok=True)

configs = [
    ("berlin52", 7542),
    ("eil76", 538),
    ("ch150", 6528),
    ("a280", 2579),
]


def load_conv(name, alg):
    """读取单个算法在指定实例上的收敛曲线；文件不存在时返回空列表。"""
    path = FIG_DIR / f"conv_{alg}_{name}.csv"
    gens, bests = [], []
    if not path.exists():
        print(f"Warning: {path} not found")
        return gens, bests
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gens.append(int(row["gen"]))
            bests.append(float(row["best"]))
    return gens, bests


fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes = axes.flatten()

for ax, (name, opt) in zip(axes, configs):
    g1, b1 = load_conv(name, "base")
    g2, b2 = load_conv(name, "memetic")
    if g1:
        ax.plot(g1, b1, label="CUDA-Base", alpha=0.8)
    if g2:
        ax.plot(g2, b2, label="CUDA-Memetic", alpha=0.8)
    ax.axhline(y=opt, color='r', linestyle='--', label="Optimal")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Best Fitness")
    ax.set_title(name)
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(FIG_DIR / "convergence_multi.png", dpi=150)
print(f"Saved {FIG_DIR / 'convergence_multi.png'}")
