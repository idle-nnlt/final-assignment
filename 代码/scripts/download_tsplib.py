#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 GitHub 镜像下载 TSPLIB 标准算例，并注入已知最优值（BEST_KNOWN）。
"""
import sys
import urllib.request
import os

BASE_URL = "https://raw.githubusercontent.com/mastqe/tsplib/master/{}"

INSTANCES = [
    # 小规模
    "berlin52.tsp", "eil76.tsp", "eil101.tsp", "kroA100.tsp",
    # 中规模
    "ch150.tsp", "a280.tsp", "pcb442.tsp", "rat783.tsp",
    # 大规模
    "pr1002.tsp", "u1060.tsp", "rl1304.tsp", "fl1577.tsp",
]

OPTIMAL = {
    "berlin52": 7542,
    "eil76": 538,
    "eil101": 629,
    "kroA100": 21282,
    "ch150": 6528,
    "a280": 2579,
    "pcb442": 50778,
    "rat783": 8806,
    "pr1002": 259045,
    "u1060": 224094,
    "rl1304": 252778,
    "fl1577": 22249,
}


def download(instance, outdir):
    """下载单个实例并在 NODE_COORD_SECTION 前注入 BEST_KNOWN 行。"""
    url = BASE_URL.format(instance)
    path = os.path.join(outdir, instance)
    try:
        urllib.request.urlretrieve(url, path)
        print(f"Downloaded {instance}")
        name = instance.replace(".tsp", "")
        if name not in OPTIMAL:
            return True

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if any("OPTIMAL" in line or "BEST_KNOWN" in line for line in lines):
            return True

        new_lines = []
        inserted = False
        for line in lines:
            if not inserted and line.strip() == "NODE_COORD_SECTION":
                new_lines.append(f"BEST_KNOWN: {OPTIMAL[name]}\n")
                inserted = True
            new_lines.append(line)

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        return True
    except Exception as e:
        print(f"Failed {instance}: {e}")
        return False


if __name__ == "__main__":
    outdir = sys.argv[1] if len(sys.argv) > 1 else "data"
    os.makedirs(outdir, exist_ok=True)
    for inst in INSTANCES:
        download(inst, outdir)
