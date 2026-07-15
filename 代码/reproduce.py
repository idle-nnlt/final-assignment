#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
期末作业一键复现脚本（完整版）。
按顺序完成：编译 -> 全部 benchmark -> 全部敏感性/可扩展性/收敛实验 -> 绘图。
所有输出写入项目根目录的 ./results。

本脚本位于 code/ 目录下，项目根目录为其父目录。
"""
import subprocess
import sys
from pathlib import Path

# 本脚本在 code/ 下，项目根目录是上一级目录
ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# 优先使用项目自带的 plot_env 虚拟环境（已安装 pandas/matplotlib/numpy）
VENV_PYTHON = ROOT / "plot_env" / "Scripts" / "python.exe"
PYTHON = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable

SCRIPTS = ROOT / "代码" / "scripts"


def run(name, *args, **kwargs):
    cmd = [PYTHON, str(SCRIPTS / name)] + [str(a) for a in args]
    print("\n$ " + " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True, **kwargs)


def main():
    skip_build = "--skip-build" in sys.argv

    if not skip_build:
        print("=== 1. Build all executables ===")
        build_script = ROOT / "代码" / "build_all.bat"
        if build_script.exists():
            subprocess.run(["cmd", "/c", str(build_script)], cwd=ROOT, check=True)
        else:
            subprocess.run(["make", "-C", "code/serial"], cwd=ROOT, check=True)
            subprocess.run(["make", "-C", "code/openmp"], cwd=ROOT, check=True)
            subprocess.run(["make", "-C", "code/cuda"], cwd=ROOT, check=True)
    else:
        print("=== 1. Build skipped ===")

    print("\n=== 2. Benchmarks ===")
    run("benchmark.py")
    run("plot_benchmark.py")
    run("benchmark_large.py")

    print("\n=== 3. Scalability ===")
    run("scalability.py")
    run("plot_scalability.py")

    print("\n=== 4. Convergence curves ===")
    run("generate_convergence_berlin52.py")
    run("plot_convergence.py")
    run("convergence_multi.py")
    run("plot_convergence_multi.py")
    run("generate_convergence_a280.py")
    run("plot_convergence_a280.py")

    print("\n=== 5. Sensitivity experiments ===")
    run("interval_sensitivity.py")
    run("plot_interval_sensitivity.py")
    run("param_sensitivity.py")
    run("plot_param_sensitivity.py")
    run("topk_experiment.py")
    run("plot_topk.py")
    run("time_to_quality.py")

    print("\n=== 6. Update report tables from CSV ===")
    subprocess.run([PYTHON, str(SCRIPTS / "generate_report_tables.py")], cwd=ROOT, check=True)

    print("\n=== Reproduction finished. See ./results ===")
    print("Note: report/main.tex now uses generated table_*.tex files.")
    print("      Please recompile the PDF with:")
    print("        xelatex -shell-escape report/main.tex")
    print("        bibtex report/main")
    print("        xelatex -shell-escape report/main.tex")
    print("        xelatex -shell-escape report/main.tex")


if __name__ == "__main__":
    main()
