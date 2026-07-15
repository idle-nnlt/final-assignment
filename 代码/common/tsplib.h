
#ifndef TSPLIB_H
#define TSPLIB_H

#include "common.h"

#ifdef __cplusplus
extern "C" {
#endif

/*
 * TSPLIB 格式解析器
 * 支持 EUC_2D 边权类型的对称 TSP 实例
 */

/* 解析指定路径的 TSPLIB 文件，填充 Problem 结构；成功返回 0 */
int tsplib_load(const char *filename, Problem *prob);

/* 从 prob->coords 重新计算 dist 矩阵（按 EUC_2D 规则） */
void tsplib_compute_distances(Problem *prob);

/* 打印实例摘要信息 */
void tsplib_print_summary(const Problem *prob);

#ifdef __cplusplus
}
#endif

#endif /* TSPLIB_H */
