#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间-质量权衡实验：比较 SA 与 CUDA-Memetic 在 berlin52 上达到不同质量所需时间。
"""
import subprocess
import csv
import re
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
FIG_DIR = RESULTS_DIR / "fig"
FIG_DIR.mkdir(exist_ok=True)


def _extract_time(output: str) -> float | None:
    """从程序输出中提取 time=... 字段，未找到返回 None。"""
    m = re.search(r"time=([\d.]+)", output)
    return float(m.group(1)) if m else None


def run_sa() -> tuple[float | None, Path]:
    """运行 SA 并返回 (总时间, 收敛文件路径)。失败时时间为 None。"""
    exe = ROOT / "代码" / "serial" / "serial_baseline.exe"
    file = DATA_DIR / "berlin52.tsp"
    conv_csv = RESULTS_DIR / "conv_sa.csv"
    args = [str(exe), "sa", str(file), "1000", "0.995", "100", "1", str(conv_csv)]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=300, check=True)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"  SA failed: {e}")
        return None, conv_csv
    return _extract_time(proc.stdout + proc.stderr), conv_csv


def run_memetic() -> tuple[float | None, Path]:
    """运行 CUDA-Memetic 并返回 (总时间, 收敛文件路径)。失败时时间为 None。"""
    exe = ROOT / "代码" / "cuda" / "ga_cuda.exe"
    file = DATA_DIR / "berlin52.tsp"
    conv_csv = RESULTS_DIR / "conv_memetic_512.csv"
    args = [str(exe), "memetic", str(file), "512", "1000", "1", "25", str(conv_csv)]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=300, check=True)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"  CUDA-Memetic failed: {e}")
        return None, conv_csv
    return _extract_time(proc.stdout + proc.stderr), conv_csv


def load_curve(csv_path: Path, is_iter: bool) -> list[tuple[int, float]]:
    """读取 (step, best) 曲线，is_iter=True 时使用 'iter' 列，否则使用 'gen' 列。"""
    points = []
    if not csv_path.exists():
        print(f"  Warning: {csv_path} not found")
        return points
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            step = int(row["iter"]) if is_iter else int(row["gen"])
            best = float(row["best"])
            points.append((step, best))
    return points


def sample_curve(points: list[tuple[int, float]], total_time: float,
                 time_points: list[float]) -> list[tuple[float, float]]:
    """按实际时间采样当前最优值。"""
    if not points or total_time is None or total_time <= 0:
        return []
    max_step = points[-1][0]
    results = []
    for t in time_points:
        if t <= 0:
            results.append((t, points[0][1]))
            continue
        step = int(t / total_time * max_step)
        best_at_t = points[0][1]
        for s, v in points:
            if s <= step:
                best_at_t = v
            else:
                break
        results.append((t, best_at_t))
    return results


def main():
    print("Running SA with convergence output ...")
    sa_time, sa_csv = run_sa()
    if sa_time is None:
        print("  SA did not produce valid output, skipping SA curve.")
    else:
        print(f"  SA total time: {sa_time:.2f} ms")

    print("Running CUDA-Memetic with convergence output ...")
    memetic_time, memetic_csv = run_memetic()
    if memetic_time is None:
        print("  CUDA-Memetic did not produce valid output, skipping CUDA curve.")
    else:
        print(f"  CUDA-Memetic total time: {memetic_time:.2f} ms")

    sa_points = load_curve(sa_csv, is_iter=True)
    memetic_points = load_curve(memetic_csv, is_iter=False)

    time_points = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200]
    sa_curve = sample_curve(sa_points, sa_time, time_points) if sa_time else []
    memetic_curve = sample_curve(memetic_points, memetic_time, time_points) if memetic_time else []

    with open(RESULTS_DIR / "time_to_quality.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["alg", "time_ms", "best"])
        writer.writeheader()
        for t, v in sa_curve:
            writer.writerow({"alg": "SA", "time_ms": t, "best": v})
        for t, v in memetic_curve:
            writer.writerow({"alg": "CUDA-Memetic", "time_ms": t, "best": v})

    fig, ax = plt.subplots(figsize=(8, 5))
    if sa_curve:
        ax.plot([t for t, _ in sa_curve], [v for _, v in sa_curve], marker='o', label="SA")
    if memetic_curve:
        ax.plot([t for t, _ in memetic_curve], [v for _, v in memetic_curve],
                marker='s', label="CUDA-Memetic")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Best Fitness")
    ax.set_title("Time-Quality Tradeoff on berlin52")
    ax.set_xscale("log")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "time_to_quality.png", dpi=150)
    print(f"Saved {FIG_DIR / 'time_to_quality.png'}")


if __name__ == "__main__":
    main()
