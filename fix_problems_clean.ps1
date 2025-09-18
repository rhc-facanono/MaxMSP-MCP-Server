# Script para corrigir problemas comuns do MaxMSP-MCP-Server
# ============================================================

Write-Host ""
Write-Host "Correcao de Problemas - MaxMSP-MCP-Server" -ForegroundColor Red
Write-Host "============================================================" -ForegroundColor Red
Write-Host ""

# 1. Corrigir PATH do uv
Write-Host "Corrigindo PATH do uv..." -ForegroundColor Yellow
$uvPath = "$env:USERPROFILE\.local\bin"
$currentPath = $env:PATH
if (-not $currentPath.Contains($uvPath)) {
    $env:PATH = "$uvPath;$currentPath"
    Write-Host "uv adicionado ao PATH da sessao" -ForegroundColor Green
}
else {
    Write-Host "uv ja esta no PATH" -ForegroundColor Green
}

# 2. Verificar se uv funciona
Write-Host "Testando uv..." -ForegroundColor Yellow
try {
    $uvVersion = uv --version
    Write-Host $uvVersion -ForegroundColor Green
}
catch {
    Write-Host "uv nao encontrado. Reinstalando..." -ForegroundColor Red
    Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
    $env:PATH = "$uvPath;$env:PATH"
}

# 3. Testar dependencias Python
Write-Host "Testando dependencias Python..." -ForegroundColor Yellow
try {
    uv run python -c "import server; print('Servidor MCP OK')"
}
catch {
    Write-Host "Erro nas dependencias. Reinstalando..." -ForegroundColor Red
    uv sync
}

# 4. Configuracao do Claude Desktop
Write-Host "Verificando configuracao do Claude..." -ForegroundColor Yellow
$claudeConfigPath = "$env:APPDATA\Claude\claude_desktop_config.json"
$correctConfigPath = ".\claude_desktop_config_CORRETO.json"

if (Test-Path $correctConfigPath) {
    Write-Host "Arquivo de configuracao correta encontrado:" -ForegroundColor Green
    Write-Host "   $correctConfigPath" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Para corrigir o Claude Desktop:" -ForegroundColor Cyan
    Write-Host "   1. Copie o conteudo de: $correctConfigPath" -ForegroundColor Gray
    Write-Host "   2. Cole em: $claudeConfigPath" -ForegroundColor Gray
    Write-Host "   3. Reinicie o Claude Desktop" -ForegroundColor Gray
    Write-Host ""
    
    $showConfig = Read-Host "Deseja ver a configuracao correta? (y/N)"
    if ($showConfig -eq "y" -or $showConfig -eq "Y") {
        Write-Host ""
        Write-Host "Configuracao correta para o Claude:" -ForegroundColor Cyan
        Write-Host "=======================================" -ForegroundColor Cyan
        Get-Content $correctConfigPath | Write-Host -ForegroundColor White
        Write-Host "=======================================" -ForegroundColor Cyan
    }
}
else {
    Write-Host "Arquivo de configuracao nao encontrado" -ForegroundColor Red
}

# 5. Testar bridge do Copilot
Write-Host ""
Write-Host "Testando bridge do Copilot..." -ForegroundColor Yellow
if (Test-Path "copilot_chat_bridge.py") {
    Write-Host "Bridge encontrado" -ForegroundColor Green
    
    $testBridge = Read-Host "Deseja testar o bridge agora? (y/N)"
    if ($testBridge -eq "y" -or $testBridge -eq "Y") {
        Write-Host ""
        Write-Host "Iniciando bridge..." -ForegroundColor Green
        Write-Host "Para parar: Pressione Ctrl+C" -ForegroundColor Yellow
        Write-Host "Use @github no Copilot Chat para comandos MaxMSP" -ForegroundColor Yellow
        Write-Host ""
        uv run python copilot_chat_bridge.py
    }
}
else {
    Write-Host "Bridge nao encontrado" -ForegroundColor Red
    Write-Host "Execute: uv run python setup_vscode.py" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Documentacao completa em: COPILOT_CHAT_GUIDE.md" -ForegroundColor Magenta
Write-Host ""
