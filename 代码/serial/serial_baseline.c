
/*
 * 串行基准程序入口。
 * 统一封装 NN、NN+2-opt、SA 和 Serial-GA 四种算法，提供一致的命令行接口和输出格式。
 */
#include "../common/common.h"
#include "../common/tsplib.h"
#include "../common/timer.h"
#include "ga_serial.h"
#include "nn.h"
#include "../common/two_opt.h"
#include "sa.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void print_usage(const char *prog) {
    printf("Usage:\n");
    printf("  %s nn    <tsplib_file>\n", prog);
    printf("  %s 2opt  <tsplib_file> [max_iters]\n", prog);
    printf("  %s sa    <tsplib_file> [init_temp] [cooling] [iters_per_temp] [seed] [conv.csv]\n", prog);
    printf("  %s ga    <tsplib_file> [pop_size] [generations] [seed] [conv.csv]\n", prog);
}

static void print_result(const char *alg, const GAResult *res) {
    printf("[%s] best=%.2f avg=%.2f time=%.2f ms iters=%d",
           alg, res->best_fitness, res->avg_fitness,
           res->time_ms, res->generations);
    if (res->gap_percent >= 0) {
        printf(" gap=%.2f%%", res->gap_percent);
    }
    printf("\n");
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        print_usage(argv[0]);
        return EXIT_FAILURE;
    }

    const char *alg = argv[1];
    const char *file = argv[2];

    Problem *prob = (Problem *)malloc(sizeof(Problem));
    if (!prob) {
        fprintf(stderr, "Error: failed to allocate Problem\n");
        return EXIT_FAILURE;
    }
    if (tsplib_load(file, prob) != 0) {
        free(prob);
        return EXIT_FAILURE;
    }
    tsplib_print_summary(prob);

    GAResult res;
    Timer timer;

    if (strcmp(alg, "nn") == 0) {
        Individual ind;
        timer_start(&timer);
        nearest_neighbor_solve(prob, 0, &ind);
        timer_stop(&timer);
        res.best_fitness = ind.fitness;
        res.avg_fitness = ind.fitness;
        res.time_ms = timer_elapsed_ms(&timer);
        res.generations = 1;
        res.gap_percent = gap_percent(ind.fitness, prob->optimal);
        print_result("NN", &res);

    } else if (strcmp(alg, "2opt") == 0) {
        Individual ind;
        nearest_neighbor_solve(prob, 0, &ind);
        int max_iters = (argc > 3) ? atoi(argv[3]) : 0;
        timer_start(&timer);
        two_opt_improve(prob, &ind, max_iters);
        timer_stop(&timer);
        res.best_fitness = ind.fitness;
        res.avg_fitness = ind.fitness;
        res.time_ms = timer_elapsed_ms(&timer);
        res.generations = max_iters;
        res.gap_percent = gap_percent(ind.fitness, prob->optimal);
        print_result("NN+2opt", &res);

    } else if (strcmp(alg, "sa") == 0) {
        SAParams p = default_sa_params();
        if (argc > 3) p.initial_temp = atof(argv[3]);
        if (argc > 4) p.cooling_rate = atof(argv[4]);
        if (argc > 5) p.iterations_per_temp = atoi(argv[5]);
        if (argc > 6) p.seed = atoi(argv[6]);
        if (p.initial_temp <= 0 || p.cooling_rate <= 0 || p.cooling_rate >= 1 ||
            p.iterations_per_temp <= 0) {
            fprintf(stderr, "Error: invalid SA parameters\n");
            free(prob);
            return EXIT_FAILURE;
        }
        FILE *conv = NULL;
        if (argc > 7) {
            conv = fopen(argv[7], "w");
            if (conv) fprintf(conv, "iter,best\n");
        }
        sa_solve(prob, &p, &res, conv);
        if (conv) fclose(conv);
        print_result("SA", &res);

    } else if (strcmp(alg, "ga") == 0) {
        GAParams p = default_params();
        if (argc > 3) p.pop_size = atoi(argv[3]);
        if (argc > 4) p.generations = atoi(argv[4]);
        if (argc > 5) p.seed = atoi(argv[5]);
        if (p.pop_size <= 0 || p.generations <= 0) {
            fprintf(stderr, "Error: pop_size and generations must be positive\n");
            free(prob);
            return EXIT_FAILURE;
        }
        FILE *conv = NULL;
        if (argc > 6) {
            conv = fopen(argv[6], "w");
            if (conv) fprintf(conv, "gen,best\n");
        }
        ga_serial_solve(prob, &p, &res, conv);
        if (conv) fclose(conv);
        print_result("GA", &res);

    } else {
        fprintf(stderr, "Unknown algorithm: %s\n", alg);
        print_usage(argv[0]);
        free(prob);
        return EXIT_FAILURE;
    }

    free(prob);
    return EXIT_SUCCESS;
}
