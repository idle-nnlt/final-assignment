#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一基准测试脚本
运行所有算法在指定 TSPLIB 实例上，收集结果到 CSV。
"""
import sys
import os
import subprocess
import csv
import re
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
CODE_DIR = PROJECT_ROOT / "代码"

ALGORITHMS = {
    "NN": (CODE_DIR / "serial" / "serial_baseline.exe", ["nn", "{file}"]),
    "NN+2opt": (CODE_DIR / "serial" / "serial_baseline.exe", ["2opt", "{file}"]),
    "SA": (CODE_DIR / "serial" / "serial_baseline.exe", ["sa", "{file}", "1000.0", "0.995", "100", "{seed}"]),
    "Serial-GA": (CODE_DIR / "serial" / "serial_baseline.exe", ["ga", "{file}", "{pop}", "{gen}", "{seed}"]),
    "OpenMP-MS": (CODE_DIR / "openmp" / "ga_openmp.exe", ["ms", "{file}", "{pop}", "{gen}", "{threads}", "{seed}"]),
    "OpenMP-Island": (CODE_DIR / "openmp" / "ga_openmp.exe", ["island", "{file}", "{pop}", "{gen}", "{islands}", "{threads}", "{seed}"]),
    "CUDA-Base": (CODE_DIR / "cuda" / "ga_cuda.exe", ["base", "{file}", "{pop}", "{gen}", "{seed}"]),
    "CUDA-Memetic": (CODE_DIR / "cuda" / "ga_cuda.exe", ["memetic", "{file}", "{pop}", "{gen}", "{seed}", "{interval}"]),
}


def run_algorithm(name, instance, config):
    """根据 ALGORITHMS 模板调用对应可执行文件，解析输出为字典。"""
    exe, args_template = ALGORITHMS[name]
    file = str(DATA_DIR / instance)
    params = {
        "file": file,
        "pop": config.get("pop_size", 256),
        "gen": config.get("generations", 500),
        "seed": config.get("seed", 1),
        "threads": config.get("threads", 4),
        "islands": config.get("islands", 4),
        "interval": config.get("generations", 500) // 10,
    }
    args = [str(exe)] + [a.format(**params) for a in args_template]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=300, check=True)
        out = proc.stdout + proc.stderr
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        print(f"  ERROR: {e}")
        return None

    res = {"algorithm": name, "instance": instance, **config, "raw": out}

    # 解析输出
    m_best = re.search(r"best=([\d.]+)", out)
    m_avg = re.search(r"avg=([\d.]+)", out)
    m_time = re.search(r"time=([\d.]+)", out)
    m_gap = re.search(r"gap=([\d.]+)%", out)
    m_optimal = re.search(r"Known optimal:\s+([\d.]+)", out)
    m_n = re.search(r"Cities:\s+(\d+)", out)

    if m_best: res["best"] = float(m_best.group(1))
    if m_avg: res["avg"] = float(m_avg.group(1))
    if m_time: res["time_ms"] = float(m_time.group(1))
    if m_gap: res["gap_percent"] = float(m_gap.group(1))
    if m_optimal: res["optimal"] = float(m_optimal.group(1))
    if m_n: res["n"] = int(m_n.group(1))

    return res


def main():
    instances = [
        "berlin52.tsp", "eil76.tsp", "eil101.tsp", "kroA100.tsp",
        "ch150.tsp", "a280.tsp",
    ]
    if len(sys.argv) > 1:
        instances = sys.argv[1:]

    RESULTS_DIR.mkdir(exist_ok=True)
    csv_path = RESULTS_DIR / "benchmark.csv"

    configs = []
    for inst in instances:
        n = int(re.search(r"(\d+)", inst).group(1))
        # 根据规模调整参数
        if n <= 100:
            pop, gen = 256, 500
        elif n <= 500:
            pop, gen = 512, 1000
        else:
            pop, gen = 1024, 1500

        for seed in [1, 2, 3]:
            configs.append({
                "instance": inst, "n": n, "pop_size": pop, "generations": gen,
                "seed": seed, "threads": 8, "islands": 8,
            })

    fieldnames = ["algorithm", "instance", "n", "pop_size", "generations",
                  "seed", "threads", "islands", "best", "avg", "time_ms",
                  "gap_percent", "optimal", "raw"]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for cfg in configs:
            for name in ALGORITHMS:
                # 跳过不适用于大实例的算法以节省时间
                if cfg["n"] > 500 and name in ("NN", "NN+2opt"):
                    continue
                print(f"Running {name} on {cfg['instance']} seed={cfg['seed']} ...")
                res = run_algorithm(name, cfg["instance"], cfg)
                if res:
                    writer.writerow({k: res.get(k, "") for k in fieldnames})
                    f.flush()
                    print(f"  best={res.get('best', 'N/A')} time={res.get('time_ms', 'N/A')}ms gap={res.get('gap_percent', 'N/A')}%")
                else:
                    print(f"  FAILED/TIMEOUT")

    print(f"\nResults saved to {csv_path}")


if __name__ == "__main__":
    main()
