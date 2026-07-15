@echo off
setlocal enabledelayedexpansion

set PRJDIR=%~dp0
if "%PRJDIR:~-1%"=="\" set PRJDIR=%PRJDIR:~0,-1%

set BUILDDIR=%TEMP%\ga_cuda_build
if exist "%BUILDDIR%" rmdir /s /q "%BUILDDIR%"
mkdir "%BUILDDIR%"
mkdir "%BUILDDIR%\common"

xcopy "%PRJDIR%\*.cu" "%BUILDDIR%\" /I /Q
xcopy "%PRJDIR%\*.cuh" "%BUILDDIR%\" /I /Q
xcopy "%PRJDIR%\..\common\*.c" "%BUILDDIR%\common\" /I /Q
xcopy "%PRJDIR%\..\common\*.h" "%BUILDDIR%\common\" /I /Q

if errorlevel 1 (
    echo Error: failed to copy source files.
    exit /b 1
)

cd /d "%BUILDDIR%"

if not defined CUDA_PATH set CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.3
set NVCC=%CUDA_PATH%\bin\nvcc.exe

if not exist "%NVCC%" (
    echo Error: nvcc not found at %NVCC%
    echo Please set CUDA_PATH to your CUDA installation directory.
    exit /b 1
)

if defined VCVARS (
    set VCVARS_PATH=%VCVARS%
) else (
    set VCVARS_PATH=
    for %%p in (
        "D:\VS\VSBT\VC\Auxiliary\Build\vcvars64.bat"
        "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
        "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat"
        "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvars64.bat"
        "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat"
        "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Auxiliary\Build\vcvars64.bat"
        "C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise\VC\Auxiliary\Build\vcvars64.bat"
    ) do if exist "%%~p" set VCVARS_PATH=%%~p
)

if not exist "%VCVARS_PATH%" (
    echo Error: vcvars64.bat not found.
    echo Please set VCVARS to the full path of vcvars64.bat, or install Visual Studio.
    exit /b 1
)

call "%VCVARS_PATH%"

if defined CUDA_ARCH (
    set ARCH=%CUDA_ARCH%
) else (
    set ARCH=sm_120
)

echo Target compute capability: %ARCH%

set SRCS=main.cu cuda_common.cu cuda_kernels.cu ga_cuda_base.cu ga_cuda_memetic.cu ga_cuda_memetic_topk.cu common\tsplib.c common\two_opt.c
"%NVCC%" -O2 -arch=%ARCH% -std=c++17 -Icommon -use_fast_math %SRCS% -o ga_cuda.exe

if errorlevel 1 (
    echo Build failed.
    exit /b 1
)

copy /Y ga_cuda.exe "%PRJDIR%\ga_cuda.exe" >nul 2>&1
if errorlevel 1 (
    echo Error: failed to copy executable.
    exit /b 1
)

echo Build succeeded: %PRJDIR%\ga_cuda.exe

cd /d "%PRJDIR%"
rmdir /s /q "%BUILDDIR%"
