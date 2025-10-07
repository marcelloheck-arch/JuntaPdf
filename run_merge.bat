@echo off
REM run_merge.bat
REM Edite apenas a linha SET PDF_FOLDER=... abaixo com a pasta que contém seus PDFs.
SET PDF_FOLDER=C:\juntaPdf

REM Caminho do script Python (assumindo que merge_numbered_pdfs.py está junto com este .bat)
SET SCRIPT=%~dp0merge_numbered_pdfs.py

echo Verificando Python e dependências...
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python nao encontrado no PATH. Instale Python 3.7+ e marque a opcao "Add to PATH".
    pause
    exit /b 1
)

REM Instalar dependencias se necessario
echo Instalando/checando dependencias pypdf e reportlab (pode demorar na primeira vez)...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install pypdf reportlab --quiet

echo Executando o script...
python "%SCRIPT%" "%PDF_FOLDER%"

echo.
echo Fim.
pause
