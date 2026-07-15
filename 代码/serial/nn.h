
#ifndef NN_H
#define NN_H

#include "../common/common.h"

/*
 * 最近邻启发式构造算法
 * 从指定城市出发，每次选择最近的未访问城市
 */

/* 执行最近邻法；start=-1 表示随机起始城市 */
void nearest_neighbor_solve(const Problem *prob, int start, Individual *out);

#endif /* NN_H */
