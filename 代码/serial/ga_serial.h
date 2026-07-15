
#ifndef GA_SERIAL_H
#define GA_SERIAL_H

#include "../common/common.h"

/*
 * 串行遗传算法求解 TSP
 */

/* 执行串行 GA，结果写入 result；conv 不为 NULL 时输出每代最优值 */
void ga_serial_solve(const Problem *prob, const GAParams *params, GAResult *result, FILE *conv);

#endif /* GA_SERIAL_H */
