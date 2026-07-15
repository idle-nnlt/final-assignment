/*
 * File: ga_cuda_memetic.cu
 * Description: CUDA-Memetic 混合算法实现。GPU 执行细粒度 GA 全局搜索，
 *              每隔固定代数将最优个体传回 CPU 执行 2-opt 局部求精。
 */

#include "ga_cuda_memetic.cuh"
#include "cuda_common.cuh"
#include "cuda_kernels.cuh"
#include "../common/two_opt.h"
#include "../common/timer.h"
#include <stdio.h>
#include <stdlib.h>
#include <float.h>

static int host_find_best(const double *fitness, int size) {
    int best = 0;
    for (int i = 1; i < size; i++) {
        if (fitness[i] < fitness[best]) best = i;
    }
    return best;
}

/*
 * CUDA-Memetic 求解主函数。
 * 在 CUDA 基础 GA 的基础上，每隔 opt_interval 代将当前最优个体传回 CPU 执行 2-opt 精炼，
 * 再将改进后的个体写回设备，形成 GPU 全局搜索 + CPU 局部求精的异构协同。
 */
void ga_cuda_memetic_solve(const Problem *prob, const GAParams *params,
                           int opt_interval, GAResult *result, FILE *conv) {
    CudaGAContext ctx;
    cuda_ga_context_init(&ctx, prob, params);

    const int n = prob->n;
    const int pop_size = params->pop_size;
    const int generations = params->generations;

    double *h_fitness = (double *)malloc(sizeof(double) * pop_size);
    int    *h_route   = (int *)malloc(sizeof(int) * n);
    if (!h_fitness || !h_route) {
        fprintf(stderr, "Error: failed to allocate host buffers\n");
        exit(EXIT_FAILURE);
    }

    int elite_size = params->elite_size;
    if (elite_size < 0) elite_size = 0;
    if (elite_size > pop_size) elite_size = pop_size;
    int *h_elite_idx = (int *)malloc(sizeof(int) * elite_size);
    if (elite_size > 0 && !h_elite_idx) {
        fprintf(stderr, "Error: failed to allocate elite index buffer\n");
        free(h_fitness);
        free(h_route);
        cuda_ga_context_free(&ctx);
        exit(EXIT_FAILURE);
    }

    if (opt_interval <= 0) opt_interval = 10;  /* 防止除零 */

    int block_size = 256;
    int grid_size = (pop_size + block_size - 1) / block_size;

    Timer timer;
    timer_start(&timer);

    init_population_kernel<<<grid_size, block_size>>>(
        ctx.d_routes, pop_size, n, ctx.d_rng, ctx.seed);
    CUDA_CHECK(cudaDeviceSynchronize());

    evaluate_fitness_kernel<<<grid_size, block_size>>>(
        ctx.d_routes, ctx.d_dist, ctx.d_fitness, pop_size, n);
    CUDA_CHECK(cudaDeviceSynchronize());

    CUDA_CHECK(cudaMemcpy(h_fitness, ctx.d_fitness,
                          sizeof(double) * pop_size, cudaMemcpyDeviceToHost));
    int best_idx = host_find_best(h_fitness, pop_size);
    if (elite_size > 0) {
        host_find_top_k_indices(h_fitness, pop_size, elite_size, h_elite_idx);
    }

    for (int gen = 0; gen < generations; gen++) {
        /* 精英保留：复制前 elite_size 个最优个体 */
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

        evolve_kernel<<<grid_size, block_size>>>(
            ctx.d_routes, ctx.d_fitness, ctx.d_dist,
            ctx.d_new_routes, ctx.d_new_fitness,
            pop_size, n, elite_size, ctx.tournament_k,
            ctx.crossover_rate, ctx.mutation_rate, ctx.d_rng);
        CUDA_CHECK(cudaDeviceSynchronize());

        int *tmp_r = ctx.d_routes;
        ctx.d_routes = ctx.d_new_routes;
        ctx.d_new_routes = tmp_r;

        double *tmp_f = ctx.d_fitness;
        ctx.d_fitness = ctx.d_new_fitness;
        ctx.d_new_fitness = tmp_f;

        CUDA_CHECK(cudaMemcpy(h_fitness, ctx.d_fitness,
                              sizeof(double) * pop_size, cudaMemcpyDeviceToHost));
        best_idx = host_find_best(h_fitness, pop_size);
        if (elite_size > 0) {
            host_find_top_k_indices(h_fitness, pop_size, elite_size, h_elite_idx);
        }

        /* Memetic 精炼：每 opt_interval 代对当前最优个体执行 2-opt */
        if ((gen + 1) % opt_interval == 0) {
            CUDA_CHECK(cudaMemcpy(h_route, &ctx.d_routes[best_idx * n],
                                  sizeof(int) * n, cudaMemcpyDeviceToHost));
            Individual ind;
            memcpy(ind.path, h_route, sizeof(int) * n);
            ind.fitness = h_fitness[best_idx];
            two_opt_improve(prob, &ind, 0);

            /* 将改进后的个体写回设备 */
            CUDA_CHECK(cudaMemcpy(&ctx.d_routes[best_idx * n], ind.path,
                                  sizeof(int) * n, cudaMemcpyHostToDevice));
            CUDA_CHECK(cudaMemcpy(&ctx.d_fitness[best_idx], &ind.fitness,
                                  sizeof(double), cudaMemcpyHostToDevice));
            h_fitness[best_idx] = ind.fitness;

            /* 精炼后重新计算精英索引，确保改进个体在下一轮被保留 */
            if (elite_size > 0) {
                host_find_top_k_indices(h_fitness, pop_size, elite_size, h_elite_idx);
            }
        }

        if (conv) {
            fprintf(conv, "%d,%.2f\n", gen + 1, h_fitness[best_idx]);
        }
        if (params->verbose && (gen + 1) % 100 == 0) {
            printf("Gen %d: best = %.2f\n", gen + 1, h_fitness[best_idx]);
        }
    }

    timer_stop(&timer);

    double sum = 0.0;
    for (int i = 0; i < pop_size; i++) sum += h_fitness[i];

    result->best_fitness = h_fitness[best_idx];
    result->avg_fitness = sum / pop_size;
    result->time_ms = timer_elapsed_ms(&timer);
    result->generations = generations;
    result->gap_percent = gap_percent(result->best_fitness, prob->optimal);

    free(h_fitness);
    free(h_route);
    free(h_elite_idx);
    cuda_ga_context_free(&ctx);
}
