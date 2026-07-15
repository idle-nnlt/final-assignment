
#ifndef TWO_OPT_H
#define TWO_OPT_H

#include "../common/common.h"

#ifdef __cplusplus
extern "C" {
#endif

/*
 * 2-opt 局部搜索
 * 通过翻转路径段来消除交叉边，直至无法改进
 */

/* 对 inout 中的路径执行 2-opt 改进；max_iters 为最大扫描轮数，0 表示无限制 */
void two_opt_improve(const Problem *prob, Individual *inout, int max_iters);

#ifdef __cplusplus
}
#endif

#endif /* TWO_OPT_H */
