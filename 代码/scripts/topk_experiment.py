#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Top-k Memetic 精炼实验：比较对最优 1/3/5/10 个个体执行 2-opt 精炼的效果。
"""
import subprocess
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"


def run_cuda_memetic_topk(instance, pop, gen, seed, interval, top_k):
    exe = ROOT / "代码" / "cuda" / "ga_cuda.exe"
    file = DATA_DIR / instance
    args = [str(exe), "memetic-topk", str(file), str(pop), str(gen), str(seed), str(interval), str(top_k)]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=300)
        out = proc.stdout + proc.stderr
        m_time = re.search(r"time=([\d.]+)", out)
        m_best = re.search(r"best=([\d.]+)", out)
        m_gap = re.search(r"gap=([\d.]+)", out)
        return {
            "instance": instance, "pop": pop, "gen": gen, "seed": seed,
            "interval": interval, "top_k": top_k,
            "time": float(m_time.group(1)) if m_time else None,
            "best": float(m_best.group(1)) if m_best else None,
            "gap": float(m_gap.group(1)) if m_gap else None,
        }
    except Exception as e:
        print(f"Error running {instance} top_k={top_k}: {e}")
        return None


def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    configs = [
        ("berlin52.tsp", 256, 1000, [1, 3, 5, 10], 25),
        ("ch150.tsp", 512, 1000, [1, 3, 5, 10], 25),
    ]
    with open(RESULTS_DIR / "topk_experiment.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["instance", "pop", "gen", "seed", "interval", "top_k", "time", "best", "gap"])
        writer.writeheader()
        for instance, pop, gen, top_ks, interval in configs:
            for seed in [1, 2, 3]:
                for top_k in top_ks:
                    print(f"Running {instance} seed={seed} top_k={top_k} ...")
                    res = run_cuda_memetic_topk(instance, pop, gen, seed, interval, top_k)
                    if res:
                        writer.writerow(res)
                        print(f"  time={res['time']:.2f}ms best={res['best']:.2f} gap={res['gap']:.2f}%")


if __name__ == "__main__":
    main()
