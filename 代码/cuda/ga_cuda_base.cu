/*
 * File: ga_cuda_base.cu
 * Description: CUDA 基础遗传算法实现。采用一个 CUDA 线程对应一个个体的
 *              细粒度并行策略，每代通过 evolve_kernel 完成选择、交叉、变异和评估。
 */

#include "ga_cuda_base.cuh"
#include "cuda_common.cuh"
#include "cuda_kernels.cuh"
#include "../common/timer.h"
#include <stdio.h>
#include <stdlib.h>
#include <float.h>

/* 在 host 端查找最优个体索引 */
static int host_find_best(const double *fitness, int size) {
    int best = 0;
    for (int i = 1; i < size; i++) {
        if (fitness[i] < fitness[best]) best = i;
    }
    return best;
}

/*
 * CUDA 基础 GA 求解主函数。
 * 采用一个 CUDA 线程对应一个个体的细粒度并行策略，每代通过 evolve_kernel 完成选择、交叉、变异和评估。
 */
void ga_cuda_base_solve(const Problem *prob, const GAParams *params, GAResult *result, FILE *conv) {
    CudaGAContext ctx;
    cuda_ga_context_init(&ctx, prob, params);

    const int n = prob->n;
    const int pop_size = params->pop_size;
    const int generations = params->generations;

    /* Host 端缓冲区 */
    double *h_fitness = (double *)malloc(sizeof(double) * pop_size);
    if (!h_fitness) {
        fprintf(stderr, "Error: failed to allocate host fitness buffer\n");
        exit(EXIT_FAILURE);
    }

    int elite_size = params->elite_size;
    if (elite_size < 0) elite_size = 0;
    if (elite_size > pop_size) elite_size = pop_size;
    int *h_elite_idx = (int *)malloc(sizeof(int) * elite_size);
    if (elite_size > 0 && !h_elite_idx) {
        fprintf(stderr, "Error: failed to allocate elite index buffer\n");
        free(h_fitness);
        cuda_ga_context_free(&ctx);
        exit(EXIT_FAILURE);
    }

    /* CUDA 配置 */
    int block_size = 256;
    int grid_size = (pop_size + block_size - 1) / block_size;

    Timer timer;
    timer_start(&timer);

    /* 初始化并评估种群 */
    init_population_kernel<<<grid_size, block_size>>>(
        ctx.d_routes, pop_size, n, ctx.d_rng, ctx.seed);
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaDeviceSynchronize());

    evaluate_fitness_kernel<<<grid_size, block_size>>>(
        ctx.d_routes, ctx.d_dist, ctx.d_fitness, pop_size, n);
    CUDA_CHECK(cudaDeviceSynchronize());

    /* 找到初始最优 */
    CUDA_CHECK(cudaMemcpy(h_fitness, ctx.d_fitness,
                          sizeof(double) * pop_size, cudaMemcpyDeviceToHost));
    int best_idx = host_find_best(h_fitness, pop_size);
    if (elite_size > 0) {
        host_find_top_k_indices(h_fitness, pop_size, elite_size, h_elite_idx);
    }

    for (int gen = 0; gen < generations; gen++) {
        /* 精英保留：将前 elite_size 个最优个体复制到新种群前部 */
        for (int e = 0; e < elite_size; e++) {
            int src = h_elite_idx[e];
            CUDA_CHECK(cudaMemcpy(&ctx.d_new_routes[e * n],
                                  &ctx.d_routes[src * n],
                                  sizeof(int) * n,
                                  cudaMemcpyDeviceToDevice));
            CUDA_CHECK(cudaMemcpy(&ctx.d_new_fitness[e],
                                  &ctx.d_fitness[src],
                                  sizeof(double),
                                  cudaMemcpyDeviceToDevice));
        }

        /* 生成其余子代；前 elite_size 个位置由 host 填充 */
        evolve_kernel<<<grid_size, block_size>>>(
            ctx.d_routes, ctx.d_fitness, ctx.d_dist,
            ctx.d_new_routes, ctx.d_new_fitness,
            pop_size, n, elite_size, ctx.tournament_k,
            ctx.crossover_rate, ctx.mutation_rate, ctx.d_rng);
        CUDA_CHECK(cudaDeviceSynchronize());

        /* 双缓冲交换 */
        int *tmp_r = ctx.d_routes;
        ctx.d_routes = ctx.d_new_routes;
        ctx.d_new_routes = tmp_r;

        double *tmp_f = ctx.d_fitness;
        ctx.d_fitness = ctx.d_new_fitness;
        ctx.d_new_fitness = tmp_f;

        /* Host 端找最优并更新精英索引 */
        CUDA_CHECK(cudaMemcpy(h_fitness, ctx.d_fitness,
                              sizeof(double) * pop_size, cudaMemcpyDeviceToHost));
        best_idx = host_find_best(h_fitness, pop_size);
        if (elite_size > 0) {
            host_find_top_k_indices(h_fitness, pop_size, elite_size, h_elite_idx);
        }

        if (conv) {
            fprintf(conv, "%d,%.2f\n", gen + 1, h_fitness[best_idx]);
        }
        if (params->verbose && (gen + 1) % 100 == 0) {
            printf("Gen %d: best = %.2f\n", gen + 1, h_fitness[best_idx]);
        }
    }

    timer_stop(&timer);

    /* 计算平均值 */
    double sum = 0.0;
    for (int i = 0; i < pop_size; i++) sum += h_fitness[i];

    result->best_fitness = h_fitness[best_idx];
    result->avg_fitness = sum / pop_size;
    result->time_ms = timer_elapsed_ms(&timer);
    result->generations = generations;
    result->gap_percent = gap_percent(result->best_fitness, prob->optimal);

    free(h_fitness);
    free(h_elite_idx);
    cuda_ga_context_free(&ctx);
}
