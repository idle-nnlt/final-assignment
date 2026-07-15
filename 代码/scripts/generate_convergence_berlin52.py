#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
生成 berlin52 上 Serial-GA、CUDA-Base、CUDA-Memetic 的收敛曲线 CSV，
供 plot_convergence.py 使用。
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

POP, GEN, SEED, INTERVAL = 256, 1000, 1, 25


def run(cmd):
    print(" ".join(str(x) for x in cmd))
    subprocess.run(cmd, check=True)


# Serial-GA
run([
    ROOT / "代码" / "serial" / "serial_baseline.exe",
    "ga", DATA_DIR / "berlin52.tsp",
    str(POP), str(GEN), str(SEED),
    RESULTS_DIR / "conv_serial.csv",
])

# CUDA-Base
run([
    ROOT / "代码" / "cuda" / "ga_cuda.exe",
    "base", DATA_DIR / "berlin52.tsp",
    str(POP), str(GEN), str(SEED),
    str(INTERVAL),
    RESULTS_DIR / "conv_cuda_base.csv",
])

# CUDA-Memetic
run([
    ROOT / "代码" / "cuda" / "ga_cuda.exe",
    "memetic", DATA_DIR / "berlin52.tsp",
    str(POP), str(GEN), str(SEED),
    str(INTERVAL),
    RESULTS_DIR / "conv_cuda_memetic.csv",
])

print(f"Convergence CSVs saved to {RESULTS_DIR}")
