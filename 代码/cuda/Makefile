# CUDA GA Makefile
# Usage:
#   make              # build ga_cuda.exe with default CUDA path and sm_86
#   make CUDA_PATH="C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v13.3" ARCH=sm_120

CUDA_PATH ?= C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v13.3
NVCC      ?= "$(CUDA_PATH)/bin/nvcc.exe"
ARCH      ?= -gencode arch=compute_120,code=sm_120
NVCCFLAGS = -O2 $(ARCH) -I../common -Xcompiler "-O2 -Wall"
LDFLAGS   = -lm

TARGET = ga_cuda

SRC = main.cu cuda_common.cu cuda_kernels.cu ga_cuda_base.cu \
      ga_cuda_memetic.cu ga_cuda_memetic_topk.cu \
      ../common/tsplib.c ../common/two_opt.c

.PHONY: all clean

all: $(TARGET).exe

$(TARGET).exe: $(SRC)
	$(NVCC) $(NVCCFLAGS) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(TARGET) *.exe *.obj *.lib *.exp
