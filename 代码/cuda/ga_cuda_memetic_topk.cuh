
#ifndef GA_CUDA_MEMETIC_TOPK_CUH
#define GA_CUDA_MEMETIC_TOPK_CUH

#include "../common/common.h"

/*
 * CUDA Memetic GA（Top-k 精炼）：每 opt_interval 代将当前适应度最优的 top_k 个个体
 * 传回 CPU 执行 2-opt 精炼，再写回设备。通过增加局部搜索强度进一步提升解质量。
 */
void ga_cuda_memetic_topk_solve(const Problem *prob, const GAParams *params,
                                int opt_interval, int top_k,
                                GAResult *result, FILE *conv);

#endif /* GA_CUDA_MEMETIC_TOPK_CUH */
