
#ifndef SA_H
#define SA_H

#include "../common/common.h"

/*
 * 模拟退火算法求解 TSP
 * 使用 2-opt 邻域结构与 Metropolis 准则
 */

/* SA 参数 */
typedef struct {
    double  initial_temp;
    double  cooling_rate;
    int     iterations_per_temp;
    double  min_temp;
    int     seed;
} SAParams;

static inline SAParams default_sa_params(void) {
    SAParams p;
    p.initial_temp = 1000.0;
    p.cooling_rate = 0.995;
    p.iterations_per_temp = 100;
    p.min_temp = 1e-4;
    p.seed = 42;
    return p;
}

/* 执行 SA；结果写入 result；conv 不为 NULL 时输出收敛过程 */
void sa_solve(const Problem *prob, const SAParams *params, GAResult *result, FILE *conv);

#endif /* SA_H */
