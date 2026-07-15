#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
绘制 a280 实例上 CUDA-Base 与 CUDA-Memetic 的收敛曲线对比图。
"""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = ROOT / "results"
FIG_DIR = RESULTS_DIR / "fig"
FIG_DIR.mkdir(parents=True, exist_ok=True)

OPTIMAL = 2579
FILES = {
    "CUDA-Base": RESULTS_DIR / "conv_cuda_base_a280.csv",
    "CUDA-Memetic": RESULTS_DIR / "conv_cuda_memetic_a280.csv",
}


def main():
    fig, ax = plt.subplots(figsize=(10, 6))

    for label, path in FILES.items():
        if not path.exists():
            print(f"Warning: {path} not found")
            continue
        df = pd.read_csv(path)
        ax.plot(df["gen"], df["best"], label=label, linewidth=1.5)

    ax.axhline(y=OPTIMAL, color='r', linestyle='--', label="Optimal")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Best Fitness")
    ax.set_title("Convergence Curves on a280")
    ax.legend()
    ax.grid(linestyle="--", alpha=0.5)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "convergence_a280.png", dpi=150)
    plt.close(fig)
    print(f"Saved {FIG_DIR / 'convergence_a280.png'}")


if __name__ == "__main__":
    main()
