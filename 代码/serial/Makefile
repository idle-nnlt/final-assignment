CC = gcc
CFLAGS = -O2 -std=c11 -Wall -Wextra -I../common
LDFLAGS = -lm

COMMON_SRC = ../common/tsplib.c ../common/ga_ops.c ../common/two_opt.c
SERIAL_SRC = ga_serial.c nn.c sa.c
TARGET = serial_baseline

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SERIAL_SRC) serial_baseline.c $(COMMON_SRC)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(TARGET) *.exe
