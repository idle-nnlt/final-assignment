# 基于异构并行的遗传算法求解 TSP：多模型对比与混合优化研究

## 项目简介

本项目围绕旅行商问题（TSP），实现了 8 类求解算法并在 TSPLIB 标准算例上进行对比：

1. 最近邻法（NN）
2. NN + 2-opt 局部搜索
3. 模拟退火（SA）
4. 串行遗传算法（Serial-GA）
5. OpenMP 主从 GA（OpenMP-MS）
6. OpenMP 岛屿 GA（OpenMP-Island）
7. CUDA 基础 GA（CUDA-Base）
8. CUDA-Memetic 混合算法（GPU GA + CPU 2-opt）

实验规模覆盖 52~1304 个城市，包含收敛曲线、参数敏感性、Top-k 精炼、可扩展性和时间-质量权衡等多维度分析。

## 目录结构

```
.
├── 代码/              # 源代码
│   ├── common/        # 公共模块（TSPLIB 解析、遗传算子、2-opt、随机数、计时器）
│   ├── serial/        # 串行算法（NN、NN+2-opt、SA、Serial-GA）
│   ├── openmp/        # OpenMP 并行 GA
│   ├── cuda/          # CUDA 并行 GA
│   ├── scripts/       # benchmark、敏感性实验与绘图脚本
│   ├── build_all.bat  # Windows 一键编译脚本
│   ├── reproduce.py   # 一键复现脚本
│   └── reproduce.bat  # 双击运行复现脚本
├── data/              # TSPLIB 测试实例（12 个）
├── 报告pdf/           # 最终研究报告 PDF
├── requirements.txt   # Python 依赖
└── README.md          # 本文件
```

> 注：`results/`（实验结果 CSV 与图表）由 `reproduce.py` 运行后自动生成，默认不包含在仓库中。

## 运行环境

- Windows 11
- GCC 10.3.0（支持 OpenMP）
- NVCC 13.3（CUDA Toolkit）
- Visual Studio 2026（用于 CUDA 的 host compiler）
- Python 3.10（依赖见 `requirements.txt`）

> 注意：`代码/cuda/build.bat` 默认使用 `CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.3`。
> 若 CUDA 安装路径不同，可在调用 `代码\build_all.bat` 时传入路径与架构：
> ```bash
> 代码\build_all.bat "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6" sm_86
> ```
> 或设置环境变量 `CUDA_PATH` 与 `CUDA_ARCH`。若 Visual Studio 路径不同，可设置 `VCVARS` 指向 `vcvars64.bat`。

## 快速开始

### 1. 编译所有可执行文件

在 Windows 命令提示符或 PowerShell 中：

```bash
代码\build_all.bat
```

或进入 `代码/` 目录后双击 `build_all.bat`。

### 2. 一键复现实验

```bash
python 代码\reproduce.py
```

或进入 `代码/` 目录后双击 `reproduce.bat`。

若已编译完成，可跳过编译步骤：

```bash
python 代码\reproduce.py --skip-build
```

该脚本将依次执行：

- 全部 benchmark（小中规模 + 大规模）
- 可扩展性实验
- 收敛曲线实验
- 2-opt 精炼间隔敏感性
- 种群规模 / 迭代代数敏感性
- Top-k 精炼实验
- 时间-质量权衡实验

所有结果写入 `./results/`。

### 3. 单独运行某项实验

```bash
# 小中规模 benchmark
python 代码/scripts/benchmark.py
python 代码/scripts/plot_benchmark.py

# 大规模 benchmark
python 代码/scripts/benchmark_large.py

# 收敛曲线
python 代码/scripts/generate_convergence_berlin52.py
python 代码/scripts/plot_convergence.py

# 2-opt 精炼间隔敏感性
python 代码/scripts/interval_sensitivity.py
python 代码/scripts/plot_interval_sensitivity.py
```

## 可复现性说明

- 所有随机算法均通过命令行参数固定随机种子。
- 距离计算严格遵循 TSPLIB EUC_2D 规范（四舍五入到整数）。
- 各脚本显式传递 CUDA-Memetic 的 2-opt 精炼间隔（benchmark 使用 `G/10`，收敛/Top-k/时间-质量等实验使用 25），以保证参数含义清晰。
- GPU 绝对运行时间受显卡调度影响可能存在波动，但解质量和相对趋势稳定。
