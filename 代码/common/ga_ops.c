
/*
 * 遗传算法核心算子的实现。
 * 包括随机个体初始化、锦标赛选择、OX 交叉、交换变异和种群评估。
 */
#include "ga_ops.h"

/* 使用 Fisher-Yates 洗牌法生成 [0, n-1] 的随机排列 */
void init_random_individual(Individual *ind, int n, RngState *rng) {
    for (int i = 0; i < n; i++) {
        ind->path[i] = i;
    }
    /* 从后向前随机交换，完成无偏置乱序 */
    for (int i = n - 1; i > 0; i--) {
        int j = rng_int(rng, i + 1);
        swap_int(&ind->path[i], &ind->path[j]);
    }
    ind->fitness = DBL_MAX;
}

int tournament_select(const Individual *pop, int size, int k, RngState *rng) {
    int best = rng_int(rng, size);
    double best_fit = pop[best].fitness;
    for (int i = 1; i < k; i++) {
        int idx = rng_int(rng, size);
        if (pop[idx].fitness < best_fit) {
            best = idx;
            best_fit = pop[idx].fitness;
        }
    }
    return best;
}

void ox_crossover(const Individual *p1, const Individual *p2,
                  Individual *child, int n,
                  int cut1, int cut2, RngState *rng) {
    (void)rng; /* 保持接口一致性，OX 过程无需额外随机数 */

    /* 标记数组，记录子代中已存在的城市 */
    int used[MAX_CITIES] = {0};

    /* 复制 p1[cut1, cut2] 片段到子代对应位置 */
    if (cut1 > cut2) swap_int(&cut1, &cut2);
    for (int i = cut1; i <= cut2; i++) {
        child->path[i] = p1->path[i];
        used[p1->path[i]] = 1;
    }

    /* 按 p2 的顺序填充子代剩余位置 */
    int pos = (cut2 + 1) % n;
    for (int i = 0; i < n; i++) {
        int city = p2->path[(cut2 + 1 + i) % n];
        if (!used[city]) {
            child->path[pos] = city;
            used[city] = 1;
            pos = (pos + 1) % n;
        }
    }
    child->fitness = DBL_MAX;
}

void swap_mutation(Individual *ind, int n, double rate, RngState *rng) {
    if (rng_double(rng) >= rate) return;
    int i = rng_range(rng, 0, n - 1);
    int j = rng_range(rng, 0, n - 1);
    swap_int(&ind->path[i], &ind->path[j]);
}

void evaluate_population(const Problem *prob, Individual *pop, int size) {
    for (int i = 0; i < size; i++) {
        evaluate_individual(prob, &pop[i]);
    }
}
