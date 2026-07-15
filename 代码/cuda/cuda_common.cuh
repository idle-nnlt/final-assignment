
#ifndef CUDA_COMMON_CUH
#define CUDA_COMMON_CUH

#include "../common/common.h"
#include <cuda_runtime.h>
#include <curand_kernel.h>

/*
 * CUDA GA 公共定义与错误检查宏
 */

#define CUDA_CHECK(call) do { \
    cudaError_t err = call; \
    if (err != cudaSuccess) { \
        fprintf(stderr, "CUDA error at %s:%d: %s\n", __FILE__, __LINE__, \
                cudaGetErrorString(err)); \
        exit(EXIT_FAILURE); \
    } \
} while(0)

/* 设备端常量：最大城市数与种群规模 */
#define CUDA_MAX_CITIES     2048
#define CUDA_MAX_POP        8192

/* 设备端个体表示：路径偏移索引 */
typedef struct {
    int     route_offset;   /* 在全局路径数组中的偏移 */
    double  fitness;
} DeviceIndividual;

/* CUDA GA 上下文：集中管理 device 资源 */
typedef struct {
    int     n;              /* 城市数 */
    int     pop_size;       /* 种群大小 */
    int     generations;
    int     tournament_k;
    double  crossover_rate;
    double  mutation_rate;
    int     elite_size;
    int     seed;

    double  *d_dist;        /* 距离矩阵 [n][n] */
    int     *d_routes;      /* 当前种群路径 [pop_size][n] */
    int     *d_new_routes;  /* 新种群路径（双缓冲） */
    double  *d_fitness;     /* 当前种群适应度 */
    double  *d_new_fitness; /* 新种群适应度 */
    curandState *d_rng;     /* 每线程 cuRAND 状态 */
} CudaGAContext;

/* 初始化与释放 */
void cuda_ga_context_init(CudaGAContext *ctx, const Problem *prob, const GAParams *params);
void cuda_ga_context_free(CudaGAContext *ctx);

/* Host 端：找出 fitness[0..size-1] 中最小的 k 个索引，按 fitness 升序写入 idx[0..k-1] */
void host_find_top_k_indices(const double *fitness, int size, int k, int *idx);

#endif /* CUDA_COMMON_CUH */
