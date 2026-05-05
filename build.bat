@echo off
echo Ativando ambiente virtual...
call .venv\Scripts\activate.bat

echo Compilando com PyInstaller...
pyinstaller --clean main.spec

echo Compilacao concluida!
echo Executavel criado em dist/Auto Clique.exe
pause