
#ifndef GA_OPS_H
#define GA_OPS_H

#include "common.h"
#include "random.h"

#ifdef __cplusplus
extern "C" {
#endif

/*
 * 遗传算法核心算子
 * 被串行、OpenMP、CUDA 各版本复用或作为实现参考
 */

/* 用 Fisher-Yates 洗牌生成随机个体 */
void init_random_individual(Individual *ind, int n, RngState *rng);

/* 锦标赛选择：从 pop 中随机选 tournament_k 个，返回最优者索引 */
int tournament_select(const Individual *pop, int size, int k, RngState *rng);

/* 顺序交叉（OX）：从 p1、p2 生成子代 child */
void ox_crossover(const Individual *p1, const Individual *p2,
                  Individual *child, int n,
                  int cut1, int cut2, RngState *rng);

/* 带概率触发的交换变异 */
void swap_mutation(Individual *ind, int n, double rate, RngState *rng);

/* 复制个体 */
static inline void copy_individual(Individual *dst, const Individual *src, int n) {
    memcpy(dst->path, src->path, n * sizeof(int));
    dst->fitness = src->fitness;
}

/* 评估整个种群 */
void evaluate_population(const Problem *prob, Individual *pop, int size);

#ifdef __cplusplus
}
#endif

#endif /* GA_OPS_H */
