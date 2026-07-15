CC = gcc
CFLAGS = -O2 -std=c11 -Wall -Wextra -fopenmp -I../common
LDFLAGS = -lm -fopenmp

COMMON_SRC = ../common/tsplib.c ../common/ga_ops.c
TARGET = ga_openmp

.PHONY: all clean

all: $(TARGET)

$(TARGET): main.c ga_openmp_ms.c ga_openmp_island.c $(COMMON_SRC)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(TARGET) *.exe
