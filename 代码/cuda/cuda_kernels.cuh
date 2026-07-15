
#ifndef CUDA_KERNELS_CUH
#define CUDA_KERNELS_CUH

#include "cuda_common.cuh"

/*
 * CUDA GA 核函数声明
 */

/* 初始化种群：每个线程生成一条随机路径 */
__global__ void init_population_kernel(int *routes, int pop_size, int n,
                                       curandState *rng, int seed);

/* 评估适应度：每个线程计算一条路径长度 */
__global__ void evaluate_fitness_kernel(const int *routes, const double *dist,
                                        double *fitness, int pop_size, int n);

/* 锦标赛选择 + OX 交叉 + 交换变异：每个线程生成一个子代；
   前 elite_size 个位置由 host 端精英保留填充，核函数跳过。 */
__global__ void evolve_kernel(const int *routes, const double *fitness,
                              const double *dist, int *new_routes,
                              double *new_fitness, int pop_size, int n,
                              int elite_size, int tournament_k,
                              double crossover_rate, double mutation_rate,
                              curandState *rng);


#endif /* CUDA_KERNELS_CUH */
