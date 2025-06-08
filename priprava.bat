@echo off
cd /d "%~dp0"
echo === Vytvářím venv ===
portable-python\python.exe -m venv moje_venv

echo === Aktivuji venv a instaluji balíčky ===
call moje_venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

pause