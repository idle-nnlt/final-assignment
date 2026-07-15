
/*
 * TSPLIB 格式解析器实现。
 * 支持读取 NAME、DIMENSION、EDGE_WEIGHT_TYPE、NODE_COORD_SECTION 以及注入的 OPTIMAL 字段。
 */
#include "tsplib.h"
#include <ctype.h>

/* 读取一行，去除末尾换行符；成功返回 1，EOF 返回 0 */
static int read_line(FILE *fp, char *buf, size_t max_len) {
    if (!fgets(buf, (int)max_len, fp)) return 0;
    size_t len = strlen(buf);
    while (len > 0 && (buf[len - 1] == '\n' || buf[len - 1] == '\r')) {
        buf[--len] = '\0';
    }
    return 1;
}

/* 去除字符串首尾空白 */
static void trim(char *s) {
    char *start = s;
    while (isspace((unsigned char)*start)) start++;
    if (start != s) memmove(s, start, strlen(start) + 1);
    size_t len = strlen(s);
    while (len > 0 && isspace((unsigned char)s[len - 1])) {
        s[--len] = '\0';
    }
}

/* 解析 TSPLIB 文件并填充 Problem 结构；成功返回 0，失败返回 -1 */
int tsplib_load(const char *filename, Problem *prob) {
    FILE *fp = fopen(filename, "r");
    if (!fp) {
        fprintf(stderr, "Error: cannot open %s\n", filename);
        return -1;
    }

    memset(prob, 0, sizeof(*prob));
    prob->optimal = -1.0;
    strcpy(prob->name, "unknown");

    char line[1024];
    int reading_coords = 0;
    int dim = 0;
    int count = 0;
    int edge_weight_type = 0;  /* 1: EUC_2D */
    bool seen[MAX_CITIES] = {0};  /* 记录每个城市索引是否已出现 */

    while (read_line(fp, line, sizeof(line))) {
        trim(line);
        if (strlen(line) == 0) continue;

        if (reading_coords) {
            if (strstr(line, "EOF") != NULL) break;
            /* 允许在坐标段中穿插最优值行 */
            if (strncmp(line, "BEST_KNOWN", 10) == 0 ||
                strncmp(line, "OPTIMAL", 7) == 0) {
                char *p = strchr(line, ':');
                if (p) sscanf(p + 1, "%lf", &prob->optimal);
                continue;
            }
            int idx;
            double x, y;
            if (sscanf(line, "%d %lf %lf", &idx, &x, &y) == 3) {
                if (idx < 1 || idx > dim) {
                    fprintf(stderr, "Error: invalid city index %d\n", idx);
                    fclose(fp);
                    return -1;
                }
                if (seen[idx - 1]) {
                    fprintf(stderr, "Error: duplicate city index %d\n", idx);
                    fclose(fp);
                    return -1;
                }
                seen[idx - 1] = 1;
                prob->coords[idx - 1][0] = x;
                prob->coords[idx - 1][1] = y;
                count++;
            }
            continue;
        }

        if (strncmp(line, "NAME", 4) == 0) {
            char *p = strchr(line, ':');
            if (p) {
                trim(++p);
                strncpy(prob->name, p, MAX_NAME_LEN - 1);
            }
        } else if (strncmp(line, "DIMENSION", 9) == 0) {
            char *p = strchr(line, ':');
            if (p) sscanf(p + 1, "%d", &dim);
            if (dim <= 0 || dim > MAX_CITIES) {
                fprintf(stderr, "Error: dimension %d out of range (1..%d)\n",
                        dim, MAX_CITIES);
                fclose(fp);
                return -1;
            }
        } else if (strncmp(line, "EDGE_WEIGHT_TYPE", 16) == 0) {
            if (strstr(line, "EUC_2D")) edge_weight_type = 1;
        } else if (strncmp(line, "BEST_KNOWN", 10) == 0 ||
                   strncmp(line, "OPTIMAL", 7) == 0) {
            char *p = strchr(line, ':');
            if (p) sscanf(p + 1, "%lf", &prob->optimal);
        } else if (strncmp(line, "NODE_COORD_SECTION", 18) == 0) {
            reading_coords = 1;
        }
    }

    fclose(fp);

    if (dim <= 0 || count != dim) {
        fprintf(stderr, "Error: dimension mismatch or invalid file\n");
        return -1;
    }
    if (!edge_weight_type) {
        fprintf(stderr, "Error: only EUC_2D edge weight type is supported\n");
        return -1;
    }

    prob->n = dim;
    tsplib_compute_distances(prob);
    return 0;
}

void tsplib_compute_distances(Problem *prob) {
    for (int i = 0; i < prob->n; i++) {
        prob->dist[i][i] = 0.0;
        for (int j = i + 1; j < prob->n; j++) {
            double d = euc2d(prob->coords[i][0], prob->coords[i][1],
                              prob->coords[j][0], prob->coords[j][1]);
            prob->dist[i][j] = d;
            prob->dist[j][i] = d;
        }
    }
}

void tsplib_print_summary(const Problem *prob) {
    printf("TSPLIB Instance: %s\n", prob->name);
    printf("  Cities: %d\n", prob->n);
    if (prob->optimal > 0) {
        printf("  Known optimal: %.2f\n", prob->optimal);
    } else {
        printf("  Known optimal: N/A\n");
    }
}
