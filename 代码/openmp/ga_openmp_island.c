/*
 * File: ga_openmp_island.c
 * Description: OpenMP 岛屿模型遗传算法实现。全局种群划分为若干子种群，
 *              各岛屿独立演化并按环状拓扑迁移最优个体，减少全局同步。
 */

#include "ga_openmp_island.h"
#include "../common/ga_ops.h"
#include "../common/random.h"
#include "../common/timer.h"
#include <stdio.h>
#include <string.h>
#include <omp.h>

/*
 * 迁移：按环状拓扑将 src 岛屿中最优的 mig_size 个个体复制到 dst 岛屿的最差位置。
 * dst 的前 elite_count 个索引保留为精英，不替换。
 */
static void migrate(Individual *islands, int island_count, int island_size,
                    int n, int mig_size, int elite_count) {
    if (mig_size <= 0) return;
    int *best_idx = (int *)malloc(sizeof(int) * mig_size);
    if (!best_idx) {
        fprintf(stderr, "Error: failed to allocate migration buffer\n");
        exit(EXIT_FAILURE);
    }

    for (int src = 0; src < island_count; src++) {
        int dst = (src + 1) % island_count;
        Individual *src_pop = &islands[src * island_size];
        Individual *dst_pop = &islands[dst * island_size];

        /* 找出 src 中最优 mig_size 个个体 */
        for (int m = 0; m < mig_size; m++) best_idx[m] = -1;
        for (int m = 0; m < mig_size; m++) {
            double best_fit = DBL_MAX;
            int idx = -1;
            for (int i = 0; i < island_size; i++) {
                int used = 0;
                for (int k = 0; k < m; k++) {
                    if (best_idx[k] == i) { used = 1; break; }
                }
                if (!used && src_pop[i].fitness < best_fit) {
                    best_fit = src_pop[i].fitness;
                    idx = i;
                }
            }
            best_idx[m] = idx;
        }

        /* 替换 dst 中最差 mig_size 个个体（保留 elite_count 个精英，跳过已替换位置） */
        int *dst_used = (int *)calloc(island_size, sizeof(int));
        if (!dst_used) {
            fprintf(stderr, "Error: failed to allocate dst_used buffer\n");
            free(best_idx);
            exit(EXIT_FAILURE);
        }
        if (elite_count < 1) elite_count = 1;  /* 至少保留索引 0 */
        if (elite_count > island_size) elite_count = island_size;
        for (int i = 0; i < elite_count; i++) dst_used[i] = 1;
        for (int m = 0; m < mig_size; m++) {
            double worst_fit = -DBL_MAX;
            int idx = -1;
            for (int i = elite_count; i < island_size; i++) {
                if (!dst_used[i] && dst_pop[i].fitness > worst_fit) {
                    worst_fit = dst_pop[i].fitness;
                    idx = i;
                }
            }
            if (best_idx[m] >= 0 && idx >= 0) {
                copy_individual(&dst_pop[idx], &src_pop[best_idx[m]], n);
                dst_used[idx] = 1;
            }
        }
        free(dst_used);
    }
    free(best_idx);
}

/*
 * OpenMP 岛屿模型 GA 求解主函数。
 * 将种群划分为 island_count 个岛屿，每个 OpenMP 线程负责一个岛屿的独立演化，
 * 每隔 mig_freq 代按环状拓扑迁移最优个体。要求 threads == island_count。
 */
void ga_openmp_island_solve(const Problem *prob, const GAParams *params, GAResult *result) {
    const int n = prob->n;
    const int pop_size = params->pop_size;
    const int generations = params->generations;
    const int island_count = params->island_count;
    const int island_size = pop_size / island_count;
    const int threads = (params->threads > 0) ? params->threads : island_count;

    if (pop_size % island_count != 0) {
        fprintf(stderr, "Error: pop_size must be divisible by island_count\n");
        exit(EXIT_FAILURE);
    }
    /* 每个线程负责一个完整岛屿的演化；线程数与岛屿数不一致会导致部分岛屿未初始化 */
    if (threads != island_count) {
        fprintf(stderr, "Error: OpenMP-Island requires threads == island_count "
                        "(got threads=%d, island_count=%d)\n", threads, island_count);
        exit(EXIT_FAILURE);
    }

    Individual *pop = (Individual *)malloc(sizeof(Individual) * pop_size);
    Individual *new_pop = (Individual *)malloc(sizeof(Individual) * pop_size);
    if (!pop || !new_pop) {
        fprintf(stderr, "Error: failed to allocate population\n");
        exit(EXIT_FAILURE);
    }

    int local_elite = params->elite_size;
    if (local_elite < 0) local_elite = 0;
    if (local_elite >= island_size) local_elite = island_size / 2;
    if (local_elite == 0) local_elite = 1;  /* 岛屿模型至少保留 1 个精英 */

    /* 每个线程独立初始化自己的岛屿 */
    #pragma omp parallel num_threads(threads)
    {
        int tid = omp_get_thread_num();
        RngState rng;
        rng_init(&rng, (uint64_t)params->seed + (uint64_t)tid);
        int start = tid * island_size;
        int end = start + island_size;
        for (int i = start; i < end; i++) {
            init_random_individual(&pop[i], n, &rng);
            evaluate_individual(prob, &pop[i]);
        }
    }

    int global_best = find_best_index(pop, pop_size);

    Timer timer;
    timer_start(&timer);

    for (int gen = 0; gen < generations; gen++) {
        /* 每个线程演化自己的岛屿 */
        #pragma omp parallel num_threads(threads)
        {
            int tid = omp_get_thread_num();
            RngState rng;
            rng_init(&rng, (uint64_t)params->seed + (uint64_t)tid + (uint64_t)gen * 17U);
            int base = tid * island_size;

            /* 复制精英：保留本岛屿中适应度最小的 local_elite 个个体 */
            int selected[island_size];
            memset(selected, 0, sizeof(int) * island_size);
            for (int e = 0; e < local_elite; e++) {
                double best_fit = DBL_MAX;
                int best_i = -1;
                for (int i = 0; i < island_size; i++) {
                    if (!selected[i] && pop[base + i].fitness < best_fit) {
                        best_fit = pop[base + i].fitness;
                        best_i = i;
                    }
                }
                if (best_i >= 0) {
                    selected[best_i] = 1;
                    copy_individual(&new_pop[base + e], &pop[base + best_i], n);
                }
            }

            for (int i = local_elite; i < island_size; i++) {
                int p1 = tournament_select(&pop[base], island_size, params->tournament_k, &rng);
                int p2 = tournament_select(&pop[base], island_size, params->tournament_k, &rng);

                Individual child;
                if (rng_double(&rng) < params->crossover_rate) {
                    int cut1 = rng_range(&rng, 0, n - 1);
                    int cut2 = rng_range(&rng, 0, n - 1);
                    ox_crossover(&pop[base + p1], &pop[base + p2], &child, n, cut1, cut2, &rng);
                } else {
                    copy_individual(&child, &pop[base + p1], n);
                }

                swap_mutation(&child, n, params->mutation_rate, &rng);
                evaluate_individual(prob, &child);
                copy_individual(&new_pop[base + i], &child, n);
            }
        }

        Individual *tmp = pop;
        pop = new_pop;
        new_pop = tmp;

        /* 迁移 */
        if (params->mig_freq > 0 && (gen + 1) % params->mig_freq == 0) {
            migrate(pop, island_count, island_size, n, params->mig_size, local_elite);
        }

        global_best = find_best_index(pop, pop_size);

        if (params->verbose && (gen + 1) % 100 == 0) {
            printf("Gen %d: best = %.2f\n", gen + 1, pop[global_best].fitness);
        }
    }

    timer_stop(&timer);

    double sum = 0.0;
    for (int i = 0; i < pop_size; i++) sum += pop[i].fitness;

    result->best_fitness = pop[global_best].fitness;
    result->avg_fitness = sum / pop_size;
    result->time_ms = timer_elapsed_ms(&timer);
    result->generations = generations;
    result->gap_percent = gap_percent(result->best_fitness, prob->optimal);

    free(pop);
    free(new_pop);
}
