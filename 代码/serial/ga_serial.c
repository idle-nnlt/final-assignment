/*
 * File: ga_serial.c
 * Description: 串行遗传算法实现。初始化种群后循环执行精英保留、锦标赛选择、
 *              OX 交叉、交换变异与适应度评估，无并行优化。
 */

#include "ga_serial.h"
#include "../common/ga_ops.h"
#include "../common/random.h"
#include "../common/timer.h"
#include <stdio.h>

/*
 * 串行 GA 求解主函数。
 * 实现标准遗传算法流程：初始化种群、评估、锦标赛选择、OX 交叉、交换变异、精英保留。
 */
void ga_serial_solve(const Problem *prob, const GAParams *params, GAResult *result, FILE *conv) {
    const int n = prob->n;
    const int pop_size = params->pop_size;
    const int generations = params->generations;

    Individual *pop = (Individual *)malloc(sizeof(Individual) * pop_size);
    Individual *new_pop = (Individual *)malloc(sizeof(Individual) * pop_size);
    if (!pop || !new_pop) {
        fprintf(stderr, "Error: failed to allocate population\n");
        exit(EXIT_FAILURE);
    }

    RngState rng;
    rng_init(&rng, (uint64_t)params->seed);

    /* 初始化种群 */
    for (int i = 0; i < pop_size; i++) {
        init_random_individual(&pop[i], n, &rng);
    }
    evaluate_population(prob, pop, pop_size);

    Timer timer;
    timer_start(&timer);

    int best_idx = find_best_index(pop, pop_size);

    for (int gen = 0; gen < generations; gen++) {
        /* 精英保留：将当前最优个体复制到新一代前 elite_size 个位置 */
        for (int e = 0; e < params->elite_size; e++) {
            copy_individual(&new_pop[e], &pop[best_idx], n);
        }

        for (int i = params->elite_size; i < pop_size; i++) {
            /* 选择两个父代 */
            int p1 = tournament_select(pop, pop_size, params->tournament_k, &rng);
            int p2 = tournament_select(pop, pop_size, params->tournament_k, &rng);

            Individual child;
            if (rng_double(&rng) < params->crossover_rate) {
                int cut1 = rng_range(&rng, 0, n - 1);
                int cut2 = rng_range(&rng, 0, n - 1);
                ox_crossover(&pop[p1], &pop[p2], &child, n, cut1, cut2, &rng);
            } else {
                copy_individual(&child, &pop[p1], n);
            }

            swap_mutation(&child, n, params->mutation_rate, &rng);
            evaluate_individual(prob, &child);
            copy_individual(&new_pop[i], &child, n);
        }

        /* 交换种群指针 */
        Individual *tmp = pop;
        pop = new_pop;
        new_pop = tmp;

        best_idx = find_best_index(pop, pop_size);

        if (conv) {
            fprintf(conv, "%d,%.2f\n", gen + 1, pop[best_idx].fitness);
        }
        if (params->verbose && (gen + 1) % 100 == 0) {
            printf("Gen %d: best = %.2f\n", gen + 1, pop[best_idx].fitness);
        }
    }

    timer_stop(&timer);

    /* 计算平均适应度 */
    double sum = 0.0;
    for (int i = 0; i < pop_size; i++) sum += pop[i].fitness;

    result->best_fitness = pop[best_idx].fitness;
    result->avg_fitness = sum / pop_size;
    result->time_ms = timer_elapsed_ms(&timer);
    result->generations = generations;
    result->gap_percent = gap_percent(result->best_fitness, prob->optimal);

    free(pop);
    free(new_pop);
}
