@echo off
title Demo Durian Leaf AI V2
cd /d "%~dp0\03_Ma_nguon\demo"
echo Dang khoi dong ung dung. Lan dau mat khoang 10-20 giay.
echo Trinh duyet se tu mo tai http://localhost:8501
python -m streamlit run streamlit_app.py
if errorlevel 1 (
  echo Co loi. Neu bao thieu thu vien, chay: python -m pip install streamlit torch torchvision pillow pandas
  pause
)
