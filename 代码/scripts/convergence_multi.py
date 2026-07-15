#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多实例收敛曲线实验：生成 CUDA-Base 与 CUDA-Memetic 在不同规模实例上的收敛数据。
"""
import subprocess
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
FIG_DIR = RESULTS_DIR / "fig"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def run_conv(alg, instance, pop, gen, seed, interval, out_csv):
    exe = ROOT / "代码" / "cuda" / "ga_cuda.exe"
    file = DATA_DIR / instance
    args = [str(exe), alg, str(file), str(pop), str(gen), str(seed), str(interval), str(out_csv.resolve())]
    try:
        subprocess.run(args, capture_output=True, text=True, timeout=300)
    except Exception as e:
        print(f"Error: {alg} {instance}: {e}")


def main():
    configs = [
        ("berlin52.tsp", 256, 1000, 25),
        ("eil76.tsp", 256, 1000, 25),
        ("ch150.tsp", 512, 1000, 25),
        ("a280.tsp", 512, 1000, 25),
    ]
    for instance, pop, gen, interval in configs:
        name = instance.replace(".tsp", "")
        print(f"Generating convergence for {name} ...")
        run_conv("base", instance, pop, gen, 1, interval, FIG_DIR / f"conv_base_{name}.csv")
        run_conv("memetic", instance, pop, gen, 1, interval, FIG_DIR / f"conv_memetic_{name}.csv")


if __name__ == "__main__":
    main()
