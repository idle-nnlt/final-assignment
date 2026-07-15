#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 TSPLIB EUC_2D 格式的随机 TSP 实例。
坐标在 [0, 1000] 范围内随机生成。
"""
import sys
import os
import random


def generate(n, seed=42, name=None):
    """生成 n 个城市的随机 TSP 字符串；name 为空时自动取名。"""
    random.seed(seed)
    if name is None:
        name = f"random{n}"
    lines = [
        f"NAME: {name}",
        "TYPE: TSP",
        f"COMMENT: random {n} cities",
        f"DIMENSION: {n}",
        "EDGE_WEIGHT_TYPE: EUC_2D",
        "NODE_COORD_SECTION",
    ]
    for i in range(1, n + 1):
        x = random.uniform(0, 1000)
        y = random.uniform(0, 1000)
        lines.append(f"{i} {x:.4f} {y:.4f}")
    lines.append("EOF")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: gen_tsp.py <n> <output.tsp> [seed]")
        sys.exit(1)
    n = int(sys.argv[1])
    outfile = sys.argv[2]
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 42
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(generate(n, seed, name=os.path.splitext(os.path.basename(outfile))[0]))
    print(f"Generated {outfile} with {n} cities.")
