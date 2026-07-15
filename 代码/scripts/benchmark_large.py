#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
大规模实例 benchmark：只运行表现较好的算法。
"""
import sys
import os
import subprocess
import csv
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
CODE_DIR = PROJECT_ROOT / "代码"

ALGORITHMS = {
    "NN+2opt": (CODE_DIR / "serial" / "serial_baseline.exe", ["2opt", "{file}"]),
    "SA": (CODE_DIR / "serial" / "serial_baseline.exe", ["sa", "{file}", "1000.0", "0.995", "100", "{seed}"]),
    "CUDA-Memetic": (CODE_DIR / "cuda" / "ga_cuda.exe", ["memetic", "{file}", "{pop}", "{gen}", "{seed}", "{interval}"]),
}


def run_algorithm(name, instance, config):
    """根据 ALGORITHMS 模板调用对应可执行文件，解析输出为字典。"""
    exe, args_template = ALGORITHMS[name]
    file = str(DATA_DIR / instance)
    params = {
        "file": file,
        "pop": config.get("pop_size", 1024),
        "gen": config.get("generations", 2000),
        "seed": config.get("seed", 1),
        "interval": config.get("generations", 2000) // 10,
    }
    args = [str(exe)] + [a.format(**params) for a in args_template]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=600, check=True)
        out = proc.stdout + proc.stderr
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        print(f"  ERROR: {e}")
        return None

    res = {"algorithm": name, "instance": instance, **config, "raw": out}
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
    instances = ["rat783.tsp", "pr1002.tsp", "u1060.tsp", "rl1304.tsp"]
    if len(sys.argv) > 1:
        instances = sys.argv[1:]

    RESULTS_DIR.mkdir(exist_ok=True)
    csv_path = RESULTS_DIR / "benchmark_large.csv"

    configs = []
    for inst in instances:
        n = int(re.search(r"(\d+)", inst).group(1))
        pop, gen = 1024, 2000
        for seed in [1, 2]:
            configs.append({
                "instance": inst, "n": n, "pop_size": pop, "generations": gen,
                "seed": seed,
            })

    fieldnames = ["algorithm", "instance", "n", "pop_size", "generations",
                  "seed", "best", "avg", "time_ms", "gap_percent", "optimal", "raw"]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for cfg in configs:
            for name in ALGORITHMS:
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
