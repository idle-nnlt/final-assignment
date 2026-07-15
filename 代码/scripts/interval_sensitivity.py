#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CUDA-Memetic 2-opt 精炼间隔敏感性实验。
"""
import subprocess
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"


def run(instance, pop, gen, interval, seed):
    exe = ROOT / "代码" / "cuda" / "ga_cuda.exe"
    file = DATA_DIR / instance
    args = [str(exe), "memetic", str(file), str(pop), str(gen), str(seed), str(interval)]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=300)
        out = proc.stdout + proc.stderr
        m_best = re.search(r"best=([\d.]+)", out)
        m_time = re.search(r"time=([\d.]+)", out)
        m_gap = re.search(r"gap=([\d.]+)%", out)
        return {
            "interval": interval,
            "best": float(m_best.group(1)) if m_best else None,
            "time": float(m_time.group(1)) if m_time else None,
            "gap": float(m_gap.group(1)) if m_gap else None,
        }
    except Exception:
        return None


def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    instance = "berlin52.tsp"
    pop, gen = 256, 1000
    intervals = [10, 25, 50, 100, 200]

    with open(RESULTS_DIR / "interval_sensitivity.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["interval", "best", "time", "gap"])
        writer.writeheader()
        for interval in intervals:
            for seed in [1, 2, 3]:
                print(f"Running interval={interval} seed={seed} ...")
                res = run(instance, pop, gen, interval, seed)
                if res:
                    writer.writerow(res)
                    print(f"  gap={res['gap']:.2f}% time={res['time']:.2f}ms")


if __name__ == "__main__":
    main()
