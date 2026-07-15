@echo off
REM 双击运行完整复现实验。
REM 本文件位于 code/ 目录下，运行时会自动切换到当前目录并调用 reproduce.py。

cd /d "%~dp0"
python reproduce.py
pause
