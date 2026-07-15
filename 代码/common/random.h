
#ifndef RANDOM_H
#define RANDOM_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * 线性同余随机数生成器（LCG）
 * 每线程可独立维护状态，避免多线程竞争 rand()
 */

typedef struct {
    uint64_t state;
} RngState;

static inline void rng_init(RngState *rng, uint64_t seed) {
    rng->state = seed == 0 ? 123456789ULL : seed;
}

/* 生成 [0, UINT32_MAX] 范围内的伪随机整数 */
static inline uint32_t rng_u32(RngState *rng) {
    rng->state = rng->state * 6364136223846793005ULL + 1;
    return (uint32_t)(rng->state >> 32);
}

/* 生成 [0, 1) 范围内的双精度浮点随机数 */
static inline double rng_double(RngState *rng) {
    return (double)rng_u32(rng) / 4294967296.0;
}

/* 生成 [0, n) 范围内的整数随机数 */
static inline int rng_int(RngState *rng, int n) {
    return (int)(rng_u32(rng) % (uint32_t)n);
}

/* 生成 [a, b] 闭区间内的整数随机数 */
static inline int rng_range(RngState *rng, int a, int b) {
    if (a > b) { int t = a; a = b; b = t; }
    return a + rng_int(rng, b - a + 1);
}

#ifdef __cplusplus
}
#endif

#endif /* RANDOM_H */
