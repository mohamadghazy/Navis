@echo off
echo Starting Navis...
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting application...
echo.
streamlit run Navis.py
pause
