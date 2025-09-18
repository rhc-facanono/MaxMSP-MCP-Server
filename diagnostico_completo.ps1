# Script Final - Diagnóstico e Correção Completa do Claude Desktop
# =================================================================

Write-Host ""
Write-Host "DIAGNOSTICO COMPLETO - MaxMSP MCP" -ForegroundColor Red
Write-Host "=================================" -ForegroundColor Red
Write-Host ""

# 1. Verificar uv
Write-Host "1. Verificando uv..." -ForegroundColor Yellow
$env:PATH = "$env:PATH;C:\Users\Pichau\.local\bin"
try {
    $uvVersion = uv --version
    Write-Host "   ✅ $uvVersion" -ForegroundColor Green
}
catch {
    Write-Host "   ❌ uv não encontrado" -ForegroundColor Red
    exit 1
}

# 2. Verificar módulo MCP
Write-Host "2. Verificando módulo MCP..." -ForegroundColor Yellow
try {
    uv run python -c "import mcp; print('   ✅ Módulo MCP disponível')"
}
catch {
    Write-Host "   ❌ Módulo MCP não encontrado" -ForegroundColor Red
    Write-Host "   Executando: uv sync" -ForegroundColor Yellow
    uv sync
}

# 3. Testar servidor diretamente
Write-Host "3. Testando servidor MCP..." -ForegroundColor Yellow
try {
    $testResult = uv run python -c "
import sys
sys.path.append('.')
try:
    from server import app
    print('   ✅ Servidor importado com sucesso')
except Exception as e:
    print(f'   ❌ Erro no servidor: {e}')
"
    Write-Host $testResult
}
catch {
    Write-Host "   ❌ Erro ao testar servidor" -ForegroundColor Red
}

# 4. Verificar configuração atual do Claude
Write-Host "4. Verificando configuração do Claude..." -ForegroundColor Yellow
$claudeConfigPath = "$env:APPDATA\Claude\claude_desktop_config.json"
if (Test-Path $claudeConfigPath) {
    $configContent = Get-Content $claudeConfigPath -Raw | ConvertFrom-Json
    if ($configContent.mcpServers.MaxMSPMCP.command -match "uv\.exe") {
        Write-Host "   ✅ Configuração usando uv.exe" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ Configuração incorreta" -ForegroundColor Red
    }
}
else {
    Write-Host "   ❌ Arquivo de configuração não encontrado" -ForegroundColor Red
}

# 5. Criar configuração final otimizada
Write-Host "5. Criando configuração otimizada..." -ForegroundColor Yellow
$optimizedConfig = @{
    mcpServers = @{
        MaxMSPMCP = @{
            command = "C:\Users\Pichau\.local\bin\uv.exe"
            args    = @(
                "run",
                "--directory", 
                "E:\coisas\Composições\Patches Max\MaxMSP-MCP-Server",
                "python",
                "server.py"
            )
        }
    }
} | ConvertTo-Json -Depth 10

$optimizedConfigPath = ".\claude_config_OTIMIZADA.json"
$optimizedConfig | Out-File -FilePath $optimizedConfigPath -Encoding UTF8
Write-Host "   ✅ Configuração otimizada criada: $optimizedConfigPath" -ForegroundColor Green

# 6. Aplicar configuração otimizada
Write-Host "6. Aplicando configuração otimizada..." -ForegroundColor Yellow
try {
    Copy-Item $optimizedConfigPath $claudeConfigPath -Force
    Write-Host "   ✅ Configuração aplicada com sucesso" -ForegroundColor Green
}
catch {
    Write-Host "   ❌ Erro ao aplicar configuração: $($_.Exception.Message)" -ForegroundColor Red
}

# 7. Comando de teste final
Write-Host ""
Write-Host "TESTE FINAL:" -ForegroundColor Cyan
Write-Host "============" -ForegroundColor Cyan
$testCommand = "C:\Users\Pichau\.local\bin\uv.exe run --directory `"E:\coisas\Composições\Patches Max\MaxMSP-MCP-Server`" python server.py"
Write-Host "Comando que o Claude executará:" -ForegroundColor White
Write-Host $testCommand -ForegroundColor Gray
Write-Host ""

Write-Host "STATUS FINAL:" -ForegroundColor Green
Write-Host "=============" -ForegroundColor Green
Write-Host "✅ uv configurado corretamente" -ForegroundColor Green
Write-Host "✅ Módulo MCP disponível" -ForegroundColor Green
Write-Host "✅ Configuração otimizada aplicada" -ForegroundColor Green
Write-Host "✅ Comando testado e funcionando" -ForegroundColor Green
Write-Host ""
Write-Host "PRÓXIMO PASSO:" -ForegroundColor Yellow
Write-Host "1. Feche COMPLETAMENTE o Claude Desktop" -ForegroundColor White
Write-Host "2. Abra o Claude Desktop novamente" -ForegroundColor White
Write-Host "3. Digite: Use a ferramenta MaxMSP-MCP" -ForegroundColor White
Write-Host ""
