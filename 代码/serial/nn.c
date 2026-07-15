
#include "nn.h"
#include "../common/random.h"
#include <string.h>
#include <time.h>

/*
 * 最近邻启发式求解 TSP。
 * 从 start 城市出发，每次选择距离当前城市最近的未访问城市，直到形成完整回路。
 */
void nearest_neighbor_solve(const Problem *prob, int start, Individual *out) {
    const int n = prob->n;
    int visited[MAX_CITIES] = {0};

    if (start < 0 || start >= n) {
        /* start 非法时随机选择一个起始城市，保证多次运行结果不完全相同 */
        RngState rng;
        rng_init(&rng, (uint64_t)time(NULL));
        start = rng_int(&rng, n);
    }

    int current = start;
    out->path[0] = current;
    visited[current] = 1;

    for (int i = 1; i < n; i++) {
        int next = -1;
        double min_dist = DBL_MAX;
        for (int j = 0; j < n; j++) {
            if (!visited[j] && prob->dist[current][j] < min_dist) {
                min_dist = prob->dist[current][j];
                next = j;
            }
        }
        out->path[i] = next;
        visited[next] = 1;
        current = next;
    }

    evaluate_individual(prob, out);
}
