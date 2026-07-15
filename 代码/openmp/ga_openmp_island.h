
#ifndef GA_OPENMP_ISLAND_H
#define GA_OPENMP_ISLAND_H

#include "../common/common.h"

/*
 * OpenMP 岛屿模型并行 GA
 * 全局种群划分为若干子种群，每个线程独立演化并定期迁移
 */

void ga_openmp_island_solve(const Problem *prob, const GAParams *params, GAResult *result);

#endif /* GA_OPENMP_ISLAND_H */
