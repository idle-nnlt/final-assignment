
#ifndef COMMON_H
#define COMMON_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <float.h>
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
#include <time.h>

#ifdef _OPENMP
#include <omp.h>
#endif

/*
 * 公共常量与类型定义
 * 用于 TSP 遗传算法各实现版本（串行、OpenMP、CUDA）
 */

#define MAX_CITIES      2048    /* 支持的最大城市数 */
#define MAX_POP_SIZE    8192    /* 支持的最大种群规模 */
#define MAX_NAME_LEN    256     /* 实例名称最大长度 */

/* GA 默认参数 */
#define DEFAULT_POP_SIZE        1024
#define DEFAULT_GENERATIONS     1000
#define DEFAULT_TOURNAMENT_K    3
#define DEFAULT_CROSSOVER_RATE  0.90
#define DEFAULT_MUTATION_RATE   0.20
#define DEFAULT_ELITE_SIZE      1

/* 岛屿模型默认参数 */
#define DEFAULT_ISLAND_COUNT    4
#define DEFAULT_MIG_FREQ        50
#define DEFAULT_MIG_SIZE        4

/* 个体：TSP 路径（排列编码） + 适应度 */
typedef struct {
    int     path[MAX_CITIES];   /* 城市访问顺序，path[i] 为城市索引 */
    double  fitness;            /* 路径总长度（越小越好） */
} Individual;

/* TSP 问题实例 */
typedef struct {
    char    name[MAX_NAME_LEN]; /* 实例名 */
    int     n;                  /* 城市数 */
    double  coords[MAX_CITIES][2];  /* 城市坐标 [city][0=x, 1=y] */
    double  dist[MAX_CITIES][MAX_CITIES];   /* 完整距离矩阵 */
    double  optimal;            /* 已知最优解，-1 表示未知 */
} Problem;

/* GA 运行参数 */
typedef struct {
    int     pop_size;           /* 种群大小 */
    int     generations;        /* 迭代代数 */
    int     tournament_k;       /* 锦标赛规模 */
    double  crossover_rate;     /* 交叉概率 */
    double  mutation_rate;      /* 变异概率 */
    int     elite_size;         /* 精英保留数 */
    int     seed;               /* 随机种子 */
    int     island_count;       /* 岛屿数（岛屿模型） */
    int     mig_freq;           /* 迁移频率 */
    int     mig_size;           /* 每次迁移个体数 */
    int     threads;            /* OpenMP 线程数 */
    int     verbose;            /* 是否输出每代信息 */
} GAParams;

/* 运行结果统计 */
typedef struct {
    double  best_fitness;       /* 最终最优解 */
    double  avg_fitness;        /* 最终种群平均适应度 */
    double  time_ms;            /* 总运行时间（毫秒） */
    int     generations;        /* 实际迭代代数 */
    double  gap_percent;        /* 与最优解的相对误差（%） */
} GAResult;

/* 返回默认参数 */
static inline GAParams default_params(void) {
    GAParams p;
    memset(&p, 0, sizeof(p));
    p.pop_size      = DEFAULT_POP_SIZE;
    p.generations   = DEFAULT_GENERATIONS;
    p.tournament_k  = DEFAULT_TOURNAMENT_K;
    p.crossover_rate= DEFAULT_CROSSOVER_RATE;
    p.mutation_rate = DEFAULT_MUTATION_RATE;
    p.elite_size    = DEFAULT_ELITE_SIZE;
    p.seed          = 42;
    p.island_count  = DEFAULT_ISLAND_COUNT;
    p.mig_freq      = DEFAULT_MIG_FREQ;
    p.mig_size      = DEFAULT_MIG_SIZE;
    p.threads       = 0;        /* 0 表示使用系统默认 */
    p.verbose       = 0;
    return p;
}

/* 计算两点间欧氏距离，按 TSPLIB EUC_2D 规范四舍五入 */
static inline double euc2d(double x1, double y1, double x2, double y2) {
    double dx = x1 - x2;
    double dy = y1 - y2;
    return round(sqrt(dx * dx + dy * dy));
}

/* 评估单个个体的路径长度 */
static inline double evaluate_path(const Problem *prob, const int *path) {
    double len = 0.0;
    for (int i = 0; i < prob->n - 1; i++) {
        len += prob->dist[path[i]][path[i + 1]];
    }
    len += prob->dist[path[prob->n - 1]][path[0]];
    return len;
}

/* 个体适应度评估（原地更新） */
static inline void evaluate_individual(const Problem *prob, Individual *ind) {
    ind->fitness = evaluate_path(prob, ind->path);
}

/* 在种群中查找最优个体的索引 */
static inline int find_best_index(const Individual *pop, int size) {
    int best = 0;
    for (int i = 1; i < size; i++) {
        if (pop[i].fitness < pop[best].fitness) best = i;
    }
    return best;
}

/* 交换两个整数 */
static inline void swap_int(int *a, int *b) {
    int t = *a; *a = *b; *b = t;
}

/* 计算相对误差百分比 */
static inline double gap_percent(double best, double optimal) {
    if (optimal <= 0) return -1.0;
    return 100.0 * (best - optimal) / optimal;
}

#ifdef __cplusplus
}
#endif

#endif /* COMMON_H */
