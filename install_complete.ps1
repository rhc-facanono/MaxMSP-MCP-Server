# MaxMSP-MCP-Server - Instalação Completa para VS Code Copilot
# ================================================================

Write-Host ""
Write-Host "🎹 MaxMSP-MCP-Server - Instalação Completa" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Função para verificar se um comando existe
function Test-Command($command) {
    try {
        Get-Command $command -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# Verificar Python
Write-Host "🐍 Verificando Python..." -ForegroundColor Yellow
if (-not (Test-Command "python")) {
    Write-Host "❌ Python não encontrado. Instale Python 3.8+ primeiro." -ForegroundColor Red
    exit 1
}
$pythonVersion = python --version
Write-Host "✅ $pythonVersion encontrado" -ForegroundColor Green

# Verificar Node.js
Write-Host "📦 Verificando Node.js..." -ForegroundColor Yellow
if (-not (Test-Command "node")) {
    Write-Host "❌ Node.js não encontrado. Instale Node.js primeiro." -ForegroundColor Red
    exit 1
}
$nodeVersion = node --version
Write-Host "✅ Node.js $nodeVersion encontrado" -ForegroundColor Green

# Instalar uv se necessário
Write-Host "⚡ Verificando uv..." -ForegroundColor Yellow
if (-not (Test-Command "uv")) {
    Write-Host "📥 Instalando uv..." -ForegroundColor Blue
    Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
    
    # Adicionar ao PATH da sessão atual
    $uvPath = "$env:USERPROFILE\.local\bin"
    if (Test-Path $uvPath) {
        $env:PATH = "$uvPath;$env:PATH"
    }
    
    if (-not (Test-Command "uv")) {
        Write-Host "❌ Falha ao instalar uv. Reinicie o PowerShell e tente novamente." -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ uv encontrado" -ForegroundColor Green

# Instalar dependências Python
Write-Host "🔧 Instalando dependências Python..." -ForegroundColor Yellow
uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao instalar dependências Python" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dependências Python instaladas" -ForegroundColor Green

# Instalar dependências Node.js
Write-Host "📱 Instalando dependências Node.js..." -ForegroundColor Yellow
Set-Location MaxMSP_Agent
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao instalar dependências Node.js" -ForegroundColor Red
    exit 1
}
Set-Location ..
Write-Host "✅ Dependências Node.js instaladas" -ForegroundColor Green

# Configurar MCP para VS Code
Write-Host "🔧 Configurando MCP para VS Code..." -ForegroundColor Yellow
uv run python setup_vscode.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao configurar VS Code" -ForegroundColor Red
    exit 1
}
Write-Host "✅ VS Code configurado" -ForegroundColor Green

# Testar instalação
Write-Host "🧪 Testando instalação..." -ForegroundColor Yellow
uv run python -c "from server import MaxMSPConnection, docs; print('✅ Servidor MCP funcionando')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no teste do servidor MCP" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 INSTALAÇÃO COMPLETA COM SUCESSO!" -ForegroundColor Green
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "📋 Próximos Passos:" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 🚀 Inicie o bridge do Copilot:" -ForegroundColor White
Write-Host "   uv run python copilot_chat_bridge.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 🎹 Abra MaxMSP 9+ e carregue:" -ForegroundColor White
Write-Host "   MaxMSP_Agent/demo.maxpat" -ForegroundColor Gray
Write-Host ""
Write-Host "3. ▶️ No MaxMSP, execute:" -ForegroundColor White
Write-Host "   script start" -ForegroundColor Gray
Write-Host ""
Write-Host "4. 💬 No VS Code Copilot Chat, use:" -ForegroundColor White
Write-Host "   @github Explique o patch atual no MaxMSP" -ForegroundColor Gray
Write-Host "   @github Crie um oscilador senoidal simples" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Leia o guia completo em: COPILOT_CHAT_GUIDE.md" -ForegroundColor Magenta
Write-Host ""

# Perguntar se quer iniciar o bridge
$response = Read-Host "Deseja iniciar o bridge agora? (y/N)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host ""
    Write-Host "🚀 Iniciando MaxMSP Copilot Chat Bridge..." -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 Para parar: Pressione Ctrl+C" -ForegroundColor Yellow
    Write-Host "💬 Para usar: Abra Copilot Chat e mencione MaxMSP" -ForegroundColor Yellow
    Write-Host ""
    uv run python copilot_chat_bridge.py
}
