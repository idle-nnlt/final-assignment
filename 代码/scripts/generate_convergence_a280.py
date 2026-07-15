#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
生成 a280 实例上 CUDA-Base 与 CUDA-Memetic 的收敛曲线 CSV，
供 plot_convergence_a280.py 使用。
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

POP, GEN, SEED, INTERVAL = 512, 1000, 1, 25


def run(cmd):
    print(" ".join(str(x) for x in cmd))
    subprocess.run(cmd, check=True)


# CUDA-Base
run([
    ROOT / "代码" / "cuda" / "ga_cuda.exe",
    "base", DATA_DIR / "a280.tsp",
    str(POP), str(GEN), str(SEED),
    str(INTERVAL),
    RESULTS_DIR / "conv_cuda_base_a280.csv",
])

# CUDA-Memetic
run([
    ROOT / "代码" / "cuda" / "ga_cuda.exe",
    "memetic", DATA_DIR / "a280.tsp",
    str(POP), str(GEN), str(SEED),
    str(INTERVAL),
    RESULTS_DIR / "conv_cuda_memetic_a280.csv",
])

print(f"a280 convergence CSVs saved to {RESULTS_DIR}")
