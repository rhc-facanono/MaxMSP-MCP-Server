@echo off
echo.
echo ======================================================
echo 🎹 Teste do MaxMSP Copilot Chat Bridge
echo ======================================================
echo.

REM Adicionar uv ao PATH se necessário
set PATH=%PATH%;C:\Users\%USERNAME%\.local\bin

echo 🔍 Verificando instalação...
echo.

REM Verificar se uv está disponível
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ uv não encontrado no PATH
    echo Instale o uv primeiro.
    pause
    exit /b 1
)
echo ✅ uv encontrado

REM Verificar se o arquivo bridge existe
if not exist "copilot_chat_bridge.py" (
    echo ❌ copilot_chat_bridge.py não encontrado
    echo Execute o setup_vscode.py primeiro.
    pause
    exit /b 1
)
echo ✅ Bridge encontrado

REM Verificar importações Python
echo.
echo 🧪 Testando importações Python...
uv run python -c "import asyncio; import json; import sys; print('✅ Imports básicos OK')"
if %errorlevel% neq 0 (
    echo ❌ Erro nas importações básicas
    pause
    exit /b 1
)

uv run python -c "from server import MaxMSPConnection, docs, flattened_docs; print('✅ Servidor MCP OK')"
if %errorlevel% neq 0 (
    echo ❌ Erro ao importar servidor MCP
    pause
    exit /b 1
)

echo.
echo 🎉 TODOS OS TESTES PASSARAM!
echo.
echo ======================================================
echo 📋 Como usar o Copilot Chat com MaxMSP:
echo ======================================================
echo.
echo 1. Inicie o bridge:
echo    uv run python copilot_chat_bridge.py
echo.
echo 2. Abra MaxMSP e carregue demo.maxpat
echo.
echo 3. Execute 'script start' no MaxMSP
echo.  
echo 4. No VS Code Copilot Chat, digite:
echo    @github Explique o patch atual no MaxMSP
echo.
echo ======================================================
echo.

choice /C YN /M "Deseja iniciar o bridge agora"
if errorlevel 2 goto end
if errorlevel 1 goto start_bridge

:start_bridge
echo.
echo 🚀 Iniciando MaxMSP Copilot Chat Bridge...
echo.
echo 💡 Para parar: Pressione Ctrl+C
echo 💬 Para usar: Abra Copilot Chat e mencione MaxMSP
echo.
uv run python copilot_chat_bridge.py

:end
echo.
echo 👋 Até logo!
pause
