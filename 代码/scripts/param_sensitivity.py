#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
参数敏感性实验：CUDA-Memetic 在不同种群规模和迭代代数下的表现。
"""
import subprocess
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"


def run_cuda_memetic(instance, pop, gen, seed):
    exe = ROOT / "代码" / "cuda" / "ga_cuda.exe"
    file = DATA_DIR / instance
    interval = gen // 10
    args = [str(exe), "memetic", str(file), str(pop), str(gen), str(seed), str(interval)]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=300)
        out = proc.stdout + proc.stderr
        m_best = re.search(r"best=([\d.]+)", out)
        m_time = re.search(r"time=([\d.]+)", out)
        m_gap = re.search(r"gap=([\d.]+)%", out)
        return {
            "pop": pop, "gen": gen, "seed": seed,
            "best": float(m_best.group(1)) if m_best else None,
            "time": float(m_time.group(1)) if m_time else None,
            "gap": float(m_gap.group(1)) if m_gap else None,
        }
    except Exception as e:
        return None


def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    instance = "berlin52.tsp"
    configs = []
    for pop in [128, 256, 512, 1024]:
        for gen in [250, 500, 1000]:
            for seed in [1, 2]:
                configs.append((pop, gen, seed))

    with open(RESULTS_DIR / "sensitivity.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["pop", "gen", "seed", "best", "time", "gap"])
        writer.writeheader()
        for pop, gen, seed in configs:
            print(f"Running pop={pop} gen={gen} seed={seed} ...")
            res = run_cuda_memetic(instance, pop, gen, seed)
            if res:
                writer.writerow(res)
                print(f"  gap={res['gap']:.2f}% time={res['time']:.2f}ms")


if __name__ == "__main__":
    main()
