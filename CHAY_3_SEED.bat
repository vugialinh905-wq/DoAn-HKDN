@echo off
chcp 65001 >nul
title Chay 3 seed mo hinh gop
cd /d "%~dp0\03_Ma_nguon"
set PY=
python -c "import sys" >nul 2>nul && set PY=python
if not defined PY py -c "import sys" >nul 2>nul && set PY=py
if not defined PY if exist "E:\Python312\python.exe" set PY=E:\Python312\python.exe
if not defined PY (echo Khong tim thay Python. & pause & exit /b 1)
echo Dung Python: %PY%
%PY% --version
echo === Cai thu vien (lan dau co the mat vai phut) ===
%PY% -m pip install -r requirements.txt
for %%s in (43 44 45) do (
  echo === Seed %%s bat dau - log: 03_Ma_nguon\results\log_seed%%s.txt ===
  time /t
  %PY% -u train_base.py --source merged --epochs 6 --tag merged_s%%s --seed %%s > results\log_seed%%s.txt 2>&1
  type results\log_seed%%s.txt | findstr /C:"TEST"
)
%PY% seeds_summary.py > results\log_seeds_summary.txt 2>&1
type results\log_seeds_summary.txt
echo === XONG %date% %time% ===
pause
