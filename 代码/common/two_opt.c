
/*
 * 2-opt 局部搜索实现。
 * 通过翻转路径段消除交叉边，直到无法改进或达到最大扫描轮数。
 */
#include "two_opt.h"
#include <stdbool.h>
#include <limits.h>

/* 计算翻转段 [i+1, j] 后的路径长度变化量（delta） */
static inline double compute_delta(const Problem *prob, const int *path, int i, int j) {
    const int n = prob->n;
    int a = path[i];
    int b = path[i + 1];
    int c = path[j];
    int d = path[(j + 1) % n];
    /* 原边 ab + cd，新边 ac + bd */
    return prob->dist[a][c] + prob->dist[b][d] - prob->dist[a][b] - prob->dist[c][d];
}

/* 执行翻转：反转 path[i+1 .. j] */
static inline void reverse_segment(int *path, int i, int j) {
    while (i < j) {
        swap_int(&path[i], &path[j]);
        i++;
        j--;
    }
}

/*
 * 对 inout 执行 2-opt 局部搜索。
 * max_iters 为最大扫描轮数；传 0 表示不限制，直到达到局部最优。
 */
void two_opt_improve(const Problem *prob, Individual *inout, int max_iters) {
    const int n = prob->n;
    if (max_iters <= 0) max_iters = INT_MAX;

    bool improved = true;
    int iter = 0;
    while (improved && iter < max_iters) {
        improved = false;
        for (int i = 0; i < n - 1; i++) {
            for (int j = i + 2; j < n; j++) {
                /* 避免相邻边和最后回路的重复计算 */
                if (i == 0 && j == n - 1) continue;
                double delta = compute_delta(prob, inout->path, i, j);
                if (delta < -1e-9) {
                    reverse_segment(inout->path, i + 1, j);
                    inout->fitness += delta;
                    improved = true;
                }
            }
        }
        iter++;
    }
}
