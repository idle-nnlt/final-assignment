
#ifndef TIMER_H
#define TIMER_H

#include <time.h>

#ifdef __cplusplus
extern "C" {
#endif

#ifdef _WIN32
#include <windows.h>
#else
#include <sys/time.h>
#endif

/*
 * 跨平台高精度计时器
 * 返回毫秒级时间戳
 */

typedef struct {
#ifdef _WIN32
    LARGE_INTEGER freq;
    LARGE_INTEGER start;
    LARGE_INTEGER end;
#else
    struct timeval start;
    struct timeval end;
#endif
} Timer;

static inline void timer_start(Timer *t) {
#ifdef _WIN32
    QueryPerformanceFrequency(&t->freq);
    QueryPerformanceCounter(&t->start);
#else
    gettimeofday(&t->start, NULL);
#endif
}

static inline void timer_stop(Timer *t) {
#ifdef _WIN32
    QueryPerformanceCounter(&t->end);
#else
    gettimeofday(&t->end, NULL);
#endif
}

static inline double timer_elapsed_ms(const Timer *t) {
#ifdef _WIN32
    return 1000.0 * (double)(t->end.QuadPart - t->start.QuadPart) / (double)t->freq.QuadPart;
#else
    return (double)(t->end.tv_sec - t->start.tv_sec) * 1000.0 +
           (double)(t->end.tv_usec - t->start.tv_usec) / 1000.0;
#endif
}

#ifdef __cplusplus
}
#endif

#endif /* TIMER_H */
