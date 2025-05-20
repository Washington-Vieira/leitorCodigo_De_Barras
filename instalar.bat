@echo off
echo 🚀 Iniciando instalacao do Leitor de Codigo de Barras...
echo.

REM Definir pasta de instalação no diretório do usuário
set INSTALL_DIR=%USERPROFILE%\LeitorCodigoBarras

REM Criar pasta de instalação
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Criar pastas necessárias
if not exist "%INSTALL_DIR%\data\excel_importados" mkdir "%INSTALL_DIR%\data\excel_importados"
if not exist "%INSTALL_DIR%\data\relatorios" mkdir "%INSTALL_DIR%\data\relatorios"

REM Copiar executável e arquivos necessários
xcopy /Y /E /I "dist\*.*" "%INSTALL_DIR%"

REM Criar atalho na área de trabalho
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Leitor de Codigo de Barras.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\LeitorCodigoBarras.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

echo ✅ Instalacao concluida!
echo.
echo 📁 Sistema instalado em: %INSTALL_DIR%
echo 📌 Um atalho foi criado na area de trabalho.
echo.
echo Para comecar a usar:
echo 1. Clique duas vezes no atalho na area de trabalho
echo 2. Coloque os arquivos Excel em: %INSTALL_DIR%\data\excel_importados
echo.
pause 