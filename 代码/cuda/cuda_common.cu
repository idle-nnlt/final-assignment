
/*
 * CUDA GA 上下文管理：设备内存分配、距离矩阵传输与资源释放。
 */
#include "cuda_common.cuh"
#include <stdio.h>

/*
 * 初始化 CUDA GA 上下文：分配 device 端距离矩阵、双缓冲种群、适应度和随机数状态，
 * 并按行将 host 端距离矩阵拷贝到 device。
 */
void cuda_ga_context_init(CudaGAContext *ctx, const Problem *prob, const GAParams *params) {
    ctx->n = prob->n;
    ctx->pop_size = params->pop_size;
    ctx->generations = params->generations;
    ctx->tournament_k = params->tournament_k;
    ctx->crossover_rate = params->crossover_rate;
    ctx->mutation_rate = params->mutation_rate;
    ctx->elite_size = params->elite_size;
    ctx->seed = params->seed;

    /* 分配 device 内存 */
    CUDA_CHECK(cudaMalloc(&ctx->d_dist, sizeof(double) * prob->n * prob->n));
    CUDA_CHECK(cudaMalloc(&ctx->d_routes, sizeof(int) * params->pop_size * prob->n));
    CUDA_CHECK(cudaMalloc(&ctx->d_new_routes, sizeof(int) * params->pop_size * prob->n));
    CUDA_CHECK(cudaMalloc(&ctx->d_fitness, sizeof(double) * params->pop_size));
    CUDA_CHECK(cudaMalloc(&ctx->d_new_fitness, sizeof(double) * params->pop_size));
    CUDA_CHECK(cudaMalloc(&ctx->d_rng, sizeof(curandState) * params->pop_size));

    /* 拷贝距离矩阵（按行复制，因为 host 端矩阵按 MAX_CITIES 步长存储） */
    for (int i = 0; i < prob->n; i++) {
        CUDA_CHECK(cudaMemcpy(&ctx->d_dist[i * prob->n], prob->dist[i],
                              sizeof(double) * prob->n,
                              cudaMemcpyHostToDevice));
    }
}

/* 释放 CUDA GA 上下文占用的 device 资源 */
void cuda_ga_context_free(CudaGAContext *ctx) {
    cudaFree(ctx->d_dist);
    cudaFree(ctx->d_routes);
    cudaFree(ctx->d_new_routes);
    cudaFree(ctx->d_fitness);
    cudaFree(ctx->d_new_fitness);
    cudaFree(ctx->d_rng);
    memset(ctx, 0, sizeof(*ctx));
}

/* Host 端：找出 fitness 中最小的 k 个索引，简单 O(k*size) 选择，k 通常很小 */
void host_find_top_k_indices(const double *fitness, int size, int k, int *idx) {
    if (k > size) k = size;
    for (int r = 0; r < k; r++) {
        double best_fit = DBL_MAX;
        int best_i = -1;
        for (int i = 0; i < size; i++) {
            int used = 0;
            for (int j = 0; j < r; j++) {
                if (idx[j] == i) { used = 1; break; }
            }
            if (!used && fitness[i] < best_fit) {
                best_fit = fitness[i];
                best_i = i;
            }
        }
        idx[r] = best_i;
    }
}
