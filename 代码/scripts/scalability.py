#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
可扩展性实验：OpenMP 线程数 / CUDA 种群规模变化对性能的影响。
"""
import subprocess
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"


def run_openmp(alg, threads, pop, gen, seed):
    """运行 OpenMP GA（ms 或 island），返回时间/最优值字典；失败返回 None。"""
    exe = ROOT / "代码" / "openmp" / "ga_openmp.exe"
    file = DATA_DIR / "ch150.tsp"
    # 岛屿模型中 island_count 与线程数保持一致，确保每个线程负责一个岛屿
    if alg == "island":
        args = [str(exe), alg, str(file), str(pop), str(gen), str(threads), str(threads), str(seed)]
    else:
        # 主从模型：ms <file> <pop> <gen> <threads> <seed>
        args = [str(exe), alg, str(file), str(pop), str(gen), str(threads), str(seed)]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=300)
        out = proc.stdout + proc.stderr
        m_time = re.search(r"time=([\d.]+)", out)
        m_best = re.search(r"best=([\d.]+)", out)
        return {
            "alg": alg, "threads": threads, "pop": pop, "gen": gen, "seed": seed,
            "time": float(m_time.group(1)) if m_time else None,
            "best": float(m_best.group(1)) if m_best else None,
        }
    except Exception:
        return None


def run_cuda(pop, gen, seed):
    """运行 CUDA-Base，返回时间/最优值字典；失败返回 None。"""
    exe = ROOT / "代码" / "cuda" / "ga_cuda.exe"
    file = DATA_DIR / "ch150.tsp"
    args = [str(exe), "base", str(file), str(pop), str(gen), str(seed)]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=300)
        out = proc.stdout + proc.stderr
        m_time = re.search(r"time=([\d.]+)", out)
        m_best = re.search(r"best=([\d.]+)", out)
        return {
            "alg": "CUDA-Base", "threads": 1, "pop": pop, "gen": gen, "seed": seed,
            "time": float(m_time.group(1)) if m_time else None,
            "best": float(m_best.group(1)) if m_best else None,
        }
    except Exception:
        return None


def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    with open(RESULTS_DIR / "scalability.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["alg", "threads", "pop", "gen", "seed", "time", "best"])
        writer.writeheader()

        # OpenMP 可扩展性：改变线程数
        for threads in [1, 2, 4, 8]:
            for alg in ["ms", "island"]:
                print(f"Running OpenMP-{alg} threads={threads} ...")
                res = run_openmp(alg, threads, 512, 1000, 1)
                if res and res['time'] is not None and res['best'] is not None:
                    writer.writerow(res)
                    print(f"  time={res['time']:.2f}ms best={res['best']:.2f}")
                else:
                    print(f"  Failed OpenMP-{alg} threads={threads}")

        # CUDA 可扩展性：改变种群规模
        for pop in [256, 512, 1024, 2048]:
            print(f"Running CUDA-Base pop={pop} ...")
            res = run_cuda(pop, 1000, 1)
            if res and res['time'] is not None and res['best'] is not None:
                writer.writerow(res)
                print(f"  time={res['time']:.2f}ms best={res['best']:.2f}")
            else:
                print(f"  Failed CUDA-Base pop={pop}")


if __name__ == "__main__":
    main()
