@echo off
REM Unified build script for serial, openmp and cuda executables.
REM Usage: build_all.bat [CUDA_PATH] [ARCH]
REM Example: build_all.bat "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.3" sm_120
REM Run this script from the code\ directory (or project root via code\build_all.bat).

setlocal
REM Switch to the script's own directory so relative paths work when called from anywhere.
cd /d "%~dp0"

set CUDA_PATH=%~1
if "%CUDA_PATH%"=="" set CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.3

set ARCH=%~2
if "%ARCH%"=="" set ARCH=sm_120

REM Prefer mingw32-make; fall back to make if not found.
set MAKE=mingw32-make
where %MAKE% >nul 2>nul
if errorlevel 1 set MAKE=make

echo [1/3] Building serial baseline ...
%MAKE% -C serial || goto :error

echo [2/3] Building OpenMP GA ...
%MAKE% -C openmp || goto :error

echo [3/3] Building CUDA GA (CUDA_PATH=%CUDA_PATH%, ARCH=%ARCH%) ...
set CUDA_ARCH=%ARCH%
call cuda\build.bat || goto :error

echo.
echo Build completed successfully.
goto :eof

:error
echo.
echo Build failed!
exit /b 1
