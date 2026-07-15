
/*
 * CUDA 遗传算法核函数。
 * 包含种群初始化、适应度评估、锦标赛选择、OX 交叉、交换变异等设备的并行实现。
 */
#include "cuda_kernels.cuh"
#include <float.h>

/* 访问距离矩阵 */
#define DMAT(i, j) dist[(i) * n + (j)]
#define ROUTE(buf, idx, k) buf[(idx) * n + (k)]

/* 设备端：计算单条路径长度 */
__device__ static double device_evaluate_path(const int *route, const double *dist, int n) {
    double len = 0.0;
    for (int i = 0; i < n - 1; i++) {
        len += DMAT(route[i], route[i + 1]);
    }
    len += DMAT(route[n - 1], route[0]);
    return len;
}

/* 设备端：生成 [0, n) 随机整数 */
__device__ static int device_rng_int(curandState *s, int n) {
    return curand(s) % n;
}

/* 设备端：生成 [a, b] 随机整数 */
__device__ static int device_rng_range(curandState *s, int a, int b) {
    return a + (curand(s) % (b - a + 1));
}

/* 初始化种群：Fisher-Yates 洗牌 */
__global__ void init_population_kernel(int *routes, int pop_size, int n,
                                       curandState *rng, int seed) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= pop_size) return;

    curandState local_state;
    curand_init(seed, idx, 0, &local_state);
    rng[idx] = local_state;

    for (int i = 0; i < n; i++) {
        ROUTE(routes, idx, i) = i;
    }
    for (int i = n - 1; i > 0; i--) {
        int j = device_rng_int(&local_state, i + 1);
        int tmp = ROUTE(routes, idx, i);
        ROUTE(routes, idx, i) = ROUTE(routes, idx, j);
        ROUTE(routes, idx, j) = tmp;
    }
}

/* 评估适应度 */
__global__ void evaluate_fitness_kernel(const int *routes, const double *dist,
                                        double *fitness, int pop_size, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= pop_size) return;
    fitness[idx] = device_evaluate_path(&ROUTE(routes, idx, 0), dist, n);
}

/* 锦标赛选择 */
__device__ static int device_tournament_select(const double *fitness, int pop_size,
                                                int k, curandState *s) {
    int best = device_rng_int(s, pop_size);
    double best_fit = fitness[best];
    for (int i = 1; i < k; i++) {
        int idx = device_rng_int(s, pop_size);
        if (fitness[idx] < best_fit) {
            best = idx;
            best_fit = fitness[idx];
        }
    }
    return best;
}

/* 设备端 OX 交叉。
   used[] 与 child[] 的大小为 CUDA_MAX_CITIES；项目限制 n <= 2048。 */
__device__ static void device_ox_crossover(const int *p1, const int *p2, int *child,
                                           int n, int cut1, int cut2) {
    if (cut1 > cut2) { int t = cut1; cut1 = cut2; cut2 = t; }

    int used[CUDA_MAX_CITIES];
    for (int i = 0; i < n; i++) used[i] = 0;

    for (int i = cut1; i <= cut2; i++) {
        child[i] = p1[i];
        used[p1[i]] = 1;
    }

    int pos = (cut2 + 1) % n;
    for (int i = 0; i < n; i++) {
        int city = p2[(cut2 + 1 + i) % n];
        if (!used[city]) {
            child[pos] = city;
            used[city] = 1;
            pos = (pos + 1) % n;
        }
    }
}

/* 设备端交换变异 */
__device__ static void device_swap_mutation(int *route, int n, double rate,
                                            curandState *s) {
    if (curand_uniform_double(s) >= rate) return;
    int i = device_rng_range(s, 0, n - 1);
    int j = device_rng_range(s, 0, n - 1);
    int tmp = route[i];
    route[i] = route[j];
    route[j] = tmp;
}

/* 单线程生成一个子代：选择 + 交叉 + 变异 + 评估 */
__global__ void evolve_kernel(const int *routes, const double *fitness,
                              const double *dist, int *new_routes,
                              double *new_fitness, int pop_size, int n,
                              int elite_size, int tournament_k,
                              double crossover_rate, double mutation_rate,
                              curandState *rng) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < elite_size || idx >= pop_size) return;

    /* 从全局内存恢复随机状态 */
    curandState local_state = rng[idx];

    int p1 = device_tournament_select(fitness, pop_size, tournament_k, &local_state);
    int p2 = device_tournament_select(fitness, pop_size, tournament_k, &local_state);

    int child[CUDA_MAX_CITIES];  /* 受 CUDA_MAX_CITIES 限制 */
    if (curand_uniform_double(&local_state) < crossover_rate) {
        int cut1 = device_rng_range(&local_state, 0, n - 1);
        int cut2 = device_rng_range(&local_state, 0, n - 1);
        device_ox_crossover(&ROUTE(routes, p1, 0),
                            &ROUTE(routes, p2, 0),
                            child, n, cut1, cut2);
    } else {
        for (int i = 0; i < n; i++) {
            child[i] = ROUTE(routes, p1, i);
        }
    }

    device_swap_mutation(child, n, mutation_rate, &local_state);

    /* 写回新种群 */
    for (int i = 0; i < n; i++) {
        ROUTE(new_routes, idx, i) = child[i];
    }
    new_fitness[idx] = device_evaluate_path(child, dist, n);

    /* 保存随机状态 */
    rng[idx] = local_state;
}

