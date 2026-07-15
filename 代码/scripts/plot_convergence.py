#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
绘制收敛曲线对比图。
"""
import sys
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "results"
FIG_DIR = RESULTS_DIR / "fig"

FILES = {
    "Serial-GA": RESULTS_DIR / "conv_serial.csv",
    "CUDA-Base": RESULTS_DIR / "conv_cuda_base.csv",
    "CUDA-Memetic": RESULTS_DIR / "conv_cuda_memetic.csv",
}


def main():
    FIG_DIR.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))

    for label, path in FILES.items():
        if not path.exists():
            print(f"Warning: {path} not found")
            continue
        df = pd.read_csv(path)
        ax.plot(df["gen"], df["best"], label=label, linewidth=1.5)

    ax.set_xlabel("Generation")
    ax.set_ylabel("Best Fitness")
    ax.set_title("Convergence Curves on berlin52")
    ax.legend()
    ax.grid(linestyle="--", alpha=0.5)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "convergence_berlin52.png", dpi=150)
    plt.close(fig)
    print(f"Saved {FIG_DIR / 'convergence_berlin52.png'}")


if __name__ == "__main__":
    main()
