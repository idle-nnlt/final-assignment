#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 OpenMP-Island 迁移 bug 后，仅重新运行 OpenMP-Island 并更新 benchmark.csv。
"""
import csv
import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
CODE_DIR = PROJECT_ROOT / "代码"
EXE = CODE_DIR / "openmp" / "ga_openmp.exe"

INSTANCES = [
    ("berlin52.tsp", 256, 500),
    ("eil76.tsp", 256, 500),
    ("eil101.tsp", 256, 500),
    ("kroA100.tsp", 256, 500),
    ("ch150.tsp", 512, 1000),
    ("a280.tsp", 1024, 1500),
]


def run_island(instance, pop, gen, seed):
    args = [
        str(EXE), "island", str(DATA_DIR / instance),
        str(pop), str(gen), "8", "8", str(seed),
    ]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=300, check=True)
        out = proc.stdout + proc.stderr
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        print(f"  ERROR: {e}")
        return None

    m_best = re.search(r"best=([\d.]+)", out)
    m_avg = re.search(r"avg=([\d.]+)", out)
    m_time = re.search(r"time=([\d.]+)", out)
    m_gap = re.search(r"gap=([\d.]+)%", out)
    m_optimal = re.search(r"Known optimal:\s+([\d.]+)", out)
    m_n = re.search(r"Cities:\s+(\d+)", out)

    return {
        "algorithm": "OpenMP-Island",
        "instance": instance,
        "n": int(m_n.group(1)) if m_n else int(re.search(r"(\d+)", instance).group(1)),
        "pop_size": pop,
        "generations": gen,
        "seed": seed,
        "threads": 8,
        "islands": 8,
        "best": float(m_best.group(1)) if m_best else "",
        "avg": float(m_avg.group(1)) if m_avg else "",
        "time_ms": float(m_time.group(1)) if m_time else "",
        "gap_percent": float(m_gap.group(1)) if m_gap else "",
        "optimal": float(m_optimal.group(1)) if m_optimal else "",
        "raw": out,
    }


def main():
    csv_path = RESULTS_DIR / "benchmark.csv"
    fieldnames = ["algorithm", "instance", "n", "pop_size", "generations",
                  "seed", "threads", "islands", "best", "avg", "time_ms",
                  "gap_percent", "optimal", "raw"]

    # 读取已有数据，删除 OpenMP-Island 行
    rows = []
    if csv_path.exists():
        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["algorithm"] != "OpenMP-Island":
                    rows.append(row)

    # 重新运行 OpenMP-Island
    new_rows = []
    for instance, pop, gen in INSTANCES:
        for seed in [1, 2, 3]:
            print(f"Running OpenMP-Island on {instance} seed={seed} ...")
            res = run_island(instance, pop, gen, seed)
            if res:
                new_rows.append({k: res.get(k, "") for k in fieldnames})
                print(f"  best={res['best']} time={res['time_ms']}ms gap={res['gap_percent']}%")
            else:
                print(f"  FAILED")

    # 合并并按原顺序排列：按 algorithm 顺序，再按 instance 顺序，再按 seed
    algorithm_order = ["NN", "NN+2opt", "SA", "Serial-GA", "OpenMP-MS", "OpenMP-Island", "CUDA-Base", "CUDA-Memetic"]
    instance_order = [inst for inst, _, _ in INSTANCES]

    def sort_key(row):
        alg_idx = algorithm_order.index(row["algorithm"]) if row["algorithm"] in algorithm_order else 99
        inst_idx = instance_order.index(row["instance"]) if row["instance"] in instance_order else 99
        return (alg_idx, inst_idx, int(row["seed"]))

    all_rows = rows + new_rows
    all_rows.sort(key=sort_key)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)

    print(f"\nUpdated {csv_path}")


if __name__ == "__main__":
    main()
