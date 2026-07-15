
#ifndef GA_CUDA_BASE_CUH
#define GA_CUDA_BASE_CUH

#include "../common/common.h"

/*
 * CUDA 细粒度并行 GA（一个线程一个个体）
 */

void ga_cuda_base_solve(const Problem *prob, const GAParams *params, GAResult *result, FILE *conv);

#endif /* GA_CUDA_BASE_CUH */
