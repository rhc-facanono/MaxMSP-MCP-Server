@echo off
REM Script para iniciar o MaxMSP-MCP Server no Windows
REM Execute este arquivo para iniciar o servidor MCP

echo 🚀 Iniciando MaxMSP-MCP Server...
echo.

REM Adicionar uv ao PATH se necessário
set PATH=%PATH%;C:\Users\%USERNAME%\.local\bin

REM Verificar se uv está disponível
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ uv não encontrado no PATH
    echo Instale o uv primeiro: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 ^^^| iex"
    pause
    exit /b 1
)

REM Verificar se estamos no diretório correto
if not exist "server.py" (
    echo ❌ Execute este script no diretório raiz do MaxMSP-MCP-Server
    pause
    exit /b 1
)

REM Verificar se o ambiente virtual existe
if not exist ".venv" (
    echo ❌ Ambiente virtual não encontrado
    echo Execute primeiro: uv venv
    pause
    exit /b 1
)

REM Iniciar o servidor
echo ✅ Iniciando servidor MCP...
echo 📡 Servidor será iniciado na porta 5002
echo 🔌 Claude Desktop pode se conectar automaticamente
echo.
echo Para parar o servidor, pressione Ctrl+C
echo.

uv run python server.py

echo.
echo 👋 Servidor finalizado
pause
