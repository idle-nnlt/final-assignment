
#include "sa.h"
#include "../common/ga_ops.h"
#include "../common/random.h"
#include "../common/timer.h"
#include <math.h>

/*
 * 模拟退火求解 TSP。
 * 以随机 2-opt 移动作为邻域操作，按 Metropolis 准则接受劣解，温度按几何方式下降。
 */
void sa_solve(const Problem *prob, const SAParams *params, GAResult *result, FILE *conv) {
    if (params->cooling_rate <= 0.0 || params->cooling_rate >= 1.0) {
        fprintf(stderr, "Error: cooling_rate must be in (0, 1), got %.6f\n",
                params->cooling_rate);
        exit(EXIT_FAILURE);
    }

    const int n = prob->n;
    RngState rng;
    rng_init(&rng, (uint64_t)params->seed);

    /* 初始化：随机路径 */
    Individual current;
    init_random_individual(&current, n, &rng);
    evaluate_individual(prob, &current);

    Individual best;
    copy_individual(&best, &current, n);

    double T = params->initial_temp;
    int total_iters = 0;

    Timer timer;
    timer_start(&timer);

    while (T > params->min_temp) {
        for (int iter = 0; iter < params->iterations_per_temp; iter++) {
            /* 随机选择 2-opt 边 (i, j) */
            int i = rng_range(&rng, 0, n - 2);
            int j = rng_range(&rng, i + 1, n - 1);

            /* 计算 delta */
            int a = current.path[i];
            int b = current.path[i + 1];
            int c = current.path[j];
            int d = current.path[(j + 1) % n];
            double delta = prob->dist[a][c] + prob->dist[b][d]
                         - prob->dist[a][b] - prob->dist[c][d];

            if (delta < 0 || rng_double(&rng) < exp(-delta / T)) {
                /* 接受新解：反转 i+1..j */
                int l = i + 1, r = j;
                while (l < r) {
                    swap_int(&current.path[l], &current.path[r]);
                    l++;
                    r--;
                }
                current.fitness += delta;
                if (current.fitness < best.fitness) {
                    copy_individual(&best, &current, n);
                }
            }
            if (conv && total_iters % 100 == 0) {
                fprintf(conv, "%d,%.2f\n", total_iters, best.fitness);
            }
            total_iters++;
        }
        T *= params->cooling_rate;
    }

    timer_stop(&timer);

    result->best_fitness = best.fitness;
    result->avg_fitness = current.fitness;
    result->time_ms = timer_elapsed_ms(&timer);
    result->generations = total_iters;
    result->gap_percent = gap_percent(best.fitness, prob->optimal);
}
