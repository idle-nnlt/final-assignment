#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据 results/*.csv 自动生成 report/ 下的 LaTeX 表格片段。
运行后会覆盖以下文件（每个文件包含完整的 table 环境）：
  report/table_small.tex
  report/table_large.tex
  report/table_topk.tex
  report/table_parallel.tex
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS = ROOT / "results"
REPORT = ROOT / "report"


def fmt(x, ndigits=2):
    """标准四舍五入（half-up），避免 Python 默认的 round-half-even 导致尾数偏差。"""
    from decimal import Decimal, ROUND_HALF_UP
    d = Decimal(str(float(x)))
    quant = Decimal('1.' + '0' * ndigits)
    return str(d.quantize(quant, rounding=ROUND_HALF_UP))


def write(path, content):
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path.name}")


def gen_small():
    df = pd.read_csv(RESULTS / "benchmark.csv")
    agg = df.groupby("algorithm").agg({"gap_percent": "mean", "time_ms": "mean"}).reset_index()
    agg = agg.sort_values("gap_percent")
    rows = " \n".join(
        f"{row.algorithm} & {fmt(row.gap_percent)} & {fmt(row.time_ms)} \\\\"
        for row in agg.itertuples(index=False)
    )
    tabular = (
        r"\begin{tabular}{lcc}" + "\n"
        r"\toprule" + "\n"
        r"算法 & 平均 Gap (\%) & 平均时间 (ms) \\" + "\n"
        r"\midrule" + "\n"
        f"{rows}\n"
        r"\bottomrule" + "\n"
        r"\end{tabular}"
    )
    return (
        r"\begin{table}[htbp]" + "\n"
        r"\centering" + "\n"
        r"\caption{小中规模实例平均结果}" + "\n"
        r"\label{tab:small}" + "\n"
        f"{tabular}\n"
        r"\end{table}" + "\n"
    )


def gen_large():
    df = pd.read_csv(RESULTS / "benchmark_large.csv")
    agg = (
        df.groupby(["instance", "algorithm"])
        .agg({"gap_percent": "mean", "time_ms": "mean"})
        .reset_index()
    )
    instance_order = ["rat783.tsp", "pr1002.tsp", "u1060.tsp", "rl1304.tsp"]
    alg_order = ["NN+2opt", "CUDA-Memetic", "SA"]
    rows = []
    for inst in instance_order:
        for alg in alg_order:
            sub = agg[(agg["instance"] == inst) & (agg["algorithm"] == alg)]
            if sub.empty:
                continue
            row = sub.iloc[0]
            name = inst.replace(".tsp", "")
            rows.append(f"{name} & {alg} & {fmt(row.gap_percent)} & {fmt(row.time_ms)} \\\\")
    tabular = (
        r"\begin{tabular}{lccc}" + "\n"
        r"\toprule" + "\n"
        r"实例 & 算法 & Gap (\%) & 时间 (ms) \\" + "\n"
        r"\midrule" + "\n"
        + " \n".join(rows) + "\n"
        r"\bottomrule" + "\n"
        r"\end{tabular}"
    )
    return (
        r"\begin{table}[htbp]" + "\n"
        r"\centering" + "\n"
        r"\caption{大规模实例平均结果}" + "\n"
        r"\label{tab:large}" + "\n"
        f"{tabular}\n"
        r"\end{table}" + "\n"
    )


def gen_topk():
    df = pd.read_csv(RESULTS / "topk_experiment.csv")
    agg = df.groupby(["instance", "top_k"]).agg({"gap": "mean", "time": "mean"}).reset_index()
    instances = ["berlin52.tsp", "ch150.tsp"]
    ks = [1, 3, 5, 10]
    rows_gap = []
    rows_time = []
    for inst in instances:
        name = inst.replace(".tsp", "")
        gaps = [fmt(agg[(agg["instance"] == inst) & (agg["top_k"] == k)].iloc[0]["gap"]) for k in ks]
        times = [fmt(agg[(agg["instance"] == inst) & (agg["top_k"] == k)].iloc[0]["time"]) for k in ks]
        rows_gap.append(f"{name} Gap (\\%) & " + " & ".join(gaps) + " \\\\")
        rows_time.append(f"{name} Time (ms) & " + " & ".join(times) + " \\\\")
    tabular = (
        r"\begin{tabular}{lcccc}" + "\n"
        r"\toprule" + "\n"
        r"实例 & $k=1$ & $k=3$ & $k=5$ & $k=10$ \\" + "\n"
        r"\midrule" + "\n"
        + " \n".join(rows_gap + rows_time) + "\n"
        r"\bottomrule" + "\n"
        r"\end{tabular}"
    )
    return (
        r"\begin{table}[htbp]" + "\n"
        r"\centering" + "\n"
        r"\caption{Top-k Memetic 精炼实验结果}" + "\n"
        r"\label{tab:topk}" + "\n"
        f"{tabular}\n"
        r"\end{table}" + "\n"
    )


def gen_parallel():
    df = pd.read_csv(RESULTS / "benchmark.csv")
    ber = df[df["instance"] == "berlin52.tsp"].groupby("algorithm").agg({"time_ms": "mean"}).reset_index()
    alg_order = ["Serial-GA", "OpenMP-Island", "OpenMP-MS", "CUDA-Base", "CUDA-Memetic"]
    serial_time = ber[ber["algorithm"] == "Serial-GA"]["time_ms"].iloc[0]
    rows = []
    for alg in alg_order:
        sub = ber[ber["algorithm"] == alg]
        if sub.empty:
            continue
        t = sub.iloc[0]["time_ms"]
        rows.append(f"{alg} & {fmt(t)} & {fmt(t / serial_time)} \\\\")
    tabular = (
        r"\begin{tabular}{lcc}" + "\n"
        r"\toprule" + "\n"
        r"算法 & 时间 (ms) & 相对串行 GA 倍数 \\" + "\n"
        r"\midrule" + "\n"
        + " \n".join(rows) + "\n"
        r"\bottomrule" + "\n"
        r"\end{tabular}"
    )
    return (
        r"\begin{table}[htbp]" + "\n"
        r"\centering" + "\n"
        r"\caption{并行实现相对串行 GA 的运行时间（berlin52 实例）}" + "\n"
        r"\label{tab:parallel}" + "\n"
        f"{tabular}\n"
        r"\end{table}" + "\n"
    )


def main():
    REPORT.mkdir(exist_ok=True)
    print("Generating report tables from results/*.csv ...")
    write(REPORT / "table_small.tex", gen_small())
    write(REPORT / "table_large.tex", gen_large())
    write(REPORT / "table_topk.tex", gen_topk())
    write(REPORT / "table_parallel.tex", gen_parallel())
    print("Done.")


if __name__ == "__main__":
    main()
