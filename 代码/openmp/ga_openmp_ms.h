
#ifndef GA_OPENMP_MS_H
#define GA_OPENMP_MS_H

#include "../common/common.h"

/*
 * OpenMP 主从模型并行 GA
 * 所有遗传操作按个体静态划分到各线程并行执行
 */

void ga_openmp_ms_solve(const Problem *prob, const GAParams *params, GAResult *result);

#endif /* GA_OPENMP_MS_H */
