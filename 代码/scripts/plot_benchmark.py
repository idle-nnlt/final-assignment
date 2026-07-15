#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
根据 benchmark.csv 生成对比图表。
"""
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "results"
FIG_DIR = RESULTS_DIR / "fig"


def load_data():
    """加载 benchmark.csv 并过滤掉没有 best 值的记录。"""
    csv = RESULTS_DIR / "benchmark.csv"
    if not csv.exists():
        print(f"Error: {csv} not found")
        sys.exit(1)
    df = pd.read_csv(csv)
    df = df[df["best"].notna()]
    return df


def plot_gap_by_instance(df):
    """绘制各算法在不同实例上的平均 Gap 柱状图。"""
    FIG_DIR.mkdir(exist_ok=True)
    instances = sorted(df["instance"].unique())
    algs = sorted(df["algorithm"].unique())

    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(instances))
    width = 0.9 / len(algs)

    for i, alg in enumerate(algs):
        sub = df[df["algorithm"] == alg].groupby("instance")["gap_percent"].mean().reindex(instances)
        ax.bar(x + i * width, sub.values, width, label=alg)

    ax.set_xlabel("Instance")
    ax.set_ylabel("Gap to optimal (%)")
    ax.set_title("Average Gap to Optimal by Algorithm")
    ax.set_xticks(x + width * (len(algs) - 1) / 2)
    ax.set_xticklabels(instances, rotation=45, ha="right")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "gap_by_instance.png", dpi=150)
    plt.close(fig)
    print(f"Saved {FIG_DIR / 'gap_by_instance.png'}")


def plot_time_by_instance(df):
    """绘制各算法在不同实例上的平均执行时间柱状图。"""
    FIG_DIR.mkdir(exist_ok=True)
    instances = sorted(df["instance"].unique())
    algs = sorted(df["algorithm"].unique())

    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(instances))
    width = 0.9 / len(algs)

    for i, alg in enumerate(algs):
        sub = df[df["algorithm"] == alg].groupby("instance")["time_ms"].mean().reindex(instances)
        ax.bar(x + i * width, sub.values, width, label=alg)

    ax.set_xlabel("Instance")
    ax.set_ylabel("Time (ms)")
    ax.set_title("Average Execution Time by Algorithm")
    ax.set_yscale("log")
    ax.set_xticks(x + width * (len(algs) - 1) / 2)
    ax.set_xticklabels(instances, rotation=45, ha="right")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "time_by_instance.png", dpi=150)
    plt.close(fig)
    print(f"Saved {FIG_DIR / 'time_by_instance.png'}")


def summary_table(df):
    """输出并保存各算法平均 Gap、时间和 best 的汇总表。"""
    summary = df.groupby("algorithm").agg({
        "gap_percent": "mean",
        "time_ms": "mean",
        "best": "mean"
    }).reset_index()
    summary = summary.sort_values("gap_percent")
    print("\n=== Summary (mean over all instances/seeds) ===")
    print(summary.to_string(index=False))
    summary.to_csv(RESULTS_DIR / "summary.csv", index=False)


def main():
    df = load_data()
    plot_gap_by_instance(df)
    plot_time_by_instance(df)
    summary_table(df)


if __name__ == "__main__":
    main()
