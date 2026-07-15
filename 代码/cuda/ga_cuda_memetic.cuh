
#ifndef GA_CUDA_MEMETIC_CUH
#define GA_CUDA_MEMETIC_CUH

#include "../common/common.h"

/*
 * CUDA Memetic GA：在 CUDA 细粒度 GA 基础上，
 * 每隔 opt_interval 代将当前最优个体传回 CPU 端执行 2-opt 局部搜索精炼。
 */

void ga_cuda_memetic_solve(const Problem *prob, const GAParams *params,
                           int opt_interval, GAResult *result, FILE *conv);

#endif /* GA_CUDA_MEMETIC_CUH */
