
/*
 * CUDA GA 程序入口。
 * 支持 base、memetic、memetic-topk 三种模式，统一解析命令行参数并输出结果。
 */
#include "../common/common.h"
#include "../common/tsplib.h"
#include "ga_cuda_base.cuh"
#include "ga_cuda_memetic.cuh"
#include "ga_cuda_memetic_topk.cuh"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void print_usage(const char *prog) {
    printf("Usage: %s <alg> <tsplib_file> [pop_size] [generations] [seed] [arg6] [arg7] [conv.csv]\n", prog);
    printf("  alg: base | memetic | memetic-topk\n");
    printf("  base:           [pop] [gen] [seed] [conv.csv]\n");
    printf("  memetic:        [pop] [gen] [seed] [interval] [conv.csv]\n");
    printf("  memetic-topk:   [pop] [gen] [seed] [interval] [top_k] [conv.csv]\n");
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
    if (argc > 5) p.seed = atoi(argv[5]);
    int interval = (p.generations > 100) ? p.generations / 10 : 10;
    int top_k = 5;
    p.verbose = 1;

    /* 基本参数合法性校验 */
    if (p.pop_size <= 0 || p.generations <= 0) {
        fprintf(stderr, "Error: pop_size and generations must be positive\n");
        free(prob);
        return EXIT_FAILURE;
    }

    /* 按模式解析剩余可选参数；conv.csv 始终为最后一个参数 */
    int conv_idx = -1;
    if (strcmp(alg, "base") == 0) {
        /* base 支持两种形式：
           <pop> <gen> <seed> <conv.csv>  或
           <pop> <gen> <seed> <interval> <conv.csv>（interval 被忽略） */
        if (argc > 7) {
            conv_idx = 7;
        } else if (argc > 6) {
            conv_idx = 6;
        }
    } else if (strcmp(alg, "memetic") == 0) {
        conv_idx = 7;
        if (argc > 6) interval = atoi(argv[6]);
    } else if (strcmp(alg, "memetic-topk") == 0) {
        conv_idx = 8;
        if (argc > 6) interval = atoi(argv[6]);
        if (argc > 7) top_k = atoi(argv[7]);
        if (top_k <= 0) top_k = 5;
    }

    FILE *conv = NULL;
    if (conv_idx > 0 && argc > conv_idx) {
        conv = fopen(argv[conv_idx], "w");
        if (conv) fprintf(conv, "gen,best\n");
    }

    GAResult res;
    if (strcmp(alg, "base") == 0) {
        ga_cuda_base_solve(prob, &p, &res, conv);
        print_result("CUDA-Base", &res);
    } else if (strcmp(alg, "memetic") == 0) {
        ga_cuda_memetic_solve(prob, &p, interval, &res, conv);
        print_result("CUDA-Memetic", &res);
    } else if (strcmp(alg, "memetic-topk") == 0) {
        ga_cuda_memetic_topk_solve(prob, &p, interval, top_k, &res, conv);
        print_result("CUDA-Memetic-TopK", &res);
    } else {
        fprintf(stderr, "Unknown algorithm: %s\n", alg);
        print_usage(argv[0]);
        free(prob);
        return EXIT_FAILURE;
    }

    if (conv) fclose(conv);
    free(prob);
    return EXIT_SUCCESS;
}
