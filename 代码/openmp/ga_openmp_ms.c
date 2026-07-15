/*
 * File: ga_openmp_ms.c
 * Description: OpenMP 主从模型遗传算法实现。种群按个体静态划分给各线程，
 *              每代并行执行选择、交叉、变异与评估，主线程串行完成精英保留。
 */

#include "ga_openmp_ms.h"
#include "../common/ga_ops.h"
#include "../common/random.h"
#include "../common/timer.h"
#include <stdio.h>
#include <omp.h>

/*
 * OpenMP 主从模型 GA 求解主函数。
 * 将种群按个体静态划分给各线程，每代并行执行选择、交叉、变异和评估；
 * 精英保留和种群指针交换由主线程串行完成。
 */
void ga_openmp_ms_solve(const Problem *prob, const GAParams *params, GAResult *result) {
    const int n = prob->n;
    const int pop_size = params->pop_size;
    const int generations = params->generations;
    const int threads = (params->threads > 0) ? params->threads : omp_get_max_threads();

    Individual *pop = (Individual *)malloc(sizeof(Individual) * pop_size);
    Individual *new_pop = (Individual *)malloc(sizeof(Individual) * pop_size);
    if (!pop || !new_pop) {
        fprintf(stderr, "Error: failed to allocate population\n");
        exit(EXIT_FAILURE);
    }

    Timer timer;
    timer_start(&timer);

    /* 初始化种群，按个体并行 */
    #pragma omp parallel num_threads(threads)
    {
        int tid = omp_get_thread_num();
        RngState rng;
        rng_init(&rng, (uint64_t)params->seed + (uint64_t)tid);

        #pragma omp for schedule(static)
        for (int i = 0; i < pop_size; i++) {
            init_random_individual(&pop[i], n, &rng);
        }
    }
    evaluate_population(prob, pop, pop_size);

    int best_idx = find_best_index(pop, pop_size);

    for (int gen = 0; gen < generations; gen++) {
        /* 精英保留 */
        for (int e = 0; e < params->elite_size; e++) {
            copy_individual(&new_pop[e], &pop[best_idx], n);
        }

        #pragma omp parallel num_threads(threads)
        {
            int tid = omp_get_thread_num();
            RngState rng;
            rng_init(&rng, (uint64_t)params->seed + (uint64_t)tid + (uint64_t)gen * 31U);

            #pragma omp for schedule(static)
            for (int i = params->elite_size; i < pop_size; i++) {
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
        }

        Individual *tmp = pop;
        pop = new_pop;
        new_pop = tmp;

        best_idx = find_best_index(pop, pop_size);

        if (params->verbose && (gen + 1) % 100 == 0) {
            printf("Gen %d: best = %.2f\n", gen + 1, pop[best_idx].fitness);
        }
    }

    timer_stop(&timer);

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
