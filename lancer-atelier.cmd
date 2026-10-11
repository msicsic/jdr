@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" jeu.py --tui --atelier --cases --debug --model gpt-6-luna %*
) else (
  python jeu.py --tui --atelier --cases --debug --model gpt-6-luna %*
)
pause
