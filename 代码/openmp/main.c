
#include "../common/common.h"
#include "../common/tsplib.h"
#include "ga_openmp_ms.h"
#include "ga_openmp_island.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void print_usage(const char *prog) {
    printf("Usage:\n");
    printf("  %s ms     <tsplib_file> [pop_size] [generations] [threads] [seed]\n", prog);
    printf("  %s island <tsplib_file> [pop_size] [generations] [islands] [threads] [seed]\n", prog);
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

    GAParams p = default_params();
    if (argc > 3) p.pop_size = atoi(argv[3]);
    if (argc > 4) p.generations = atoi(argv[4]);
    if (strcmp(alg, "island") == 0) {
        if (argc > 5) p.island_count = atoi(argv[5]);
        if (argc > 6) p.threads = atoi(argv[6]);
        if (argc > 7) p.seed = atoi(argv[7]);
    } else {
        if (argc > 5) p.threads = atoi(argv[5]);
        if (argc > 6) p.seed = atoi(argv[6]);
    }
    p.verbose = 1;

    if (p.pop_size <= 0 || p.generations <= 0 || p.threads <= 0) {
        fprintf(stderr, "Error: pop_size, generations and threads must be positive\n");
        free(prob);
        return EXIT_FAILURE;
    }
    if (strcmp(alg, "island") == 0 && p.island_count <= 0) {
        fprintf(stderr, "Error: island_count must be positive\n");
        free(prob);
        return EXIT_FAILURE;
    }

    GAResult res;
    if (strcmp(alg, "ms") == 0) {
        ga_openmp_ms_solve(prob, &p, &res);
        print_result("OpenMP-MS", &res);
    } else if (strcmp(alg, "island") == 0) {
        ga_openmp_island_solve(prob, &p, &res);
        print_result("OpenMP-Island", &res);
    } else {
        fprintf(stderr, "Unknown algorithm: %s\n", alg);
        print_usage(argv[0]);
        free(prob);
        return EXIT_FAILURE;
    }

    free(prob);
    return EXIT_SUCCESS;
}
