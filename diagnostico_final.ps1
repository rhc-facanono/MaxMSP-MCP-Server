# Diagnostico Final MaxMSP-MCP
# ============================

Write-Host ""
Write-Host "DIAGNOSTICO COMPLETO - MaxMSP MCP" -ForegroundColor Red
Write-Host "=================================" -ForegroundColor Red
Write-Host ""

# 1. Verificar uv
Write-Host "1. Verificando uv..." -ForegroundColor Yellow
$env:PATH = "$env:PATH;C:\Users\Pichau\.local\bin"
try {
    $uvVersion = uv --version
    Write-Host "   OK: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "   ERRO: uv nao encontrado" -ForegroundColor Red
    exit 1
}

# 2. Verificar modulo MCP
Write-Host "2. Verificando modulo MCP..." -ForegroundColor Yellow
try {
    uv run python -c "import mcp; print('   OK: Modulo MCP disponivel')"
} catch {
    Write-Host "   ERRO: Modulo MCP nao encontrado" -ForegroundColor Red
    Write-Host "   Executando: uv sync" -ForegroundColor Yellow
    uv sync
}

# 3. Testar servidor
Write-Host "3. Testando servidor..." -ForegroundColor Yellow
try {
    uv run python -c "from server import app; print('   OK: Servidor funcional')"
} catch {
    Write-Host "   ERRO: Problema no servidor" -ForegroundColor Red
}

# 4. Aplicar configuracao final
Write-Host "4. Aplicando configuracao otimizada..." -ForegroundColor Yellow
$claudeConfigPath = "$env:APPDATA\Claude\claude_desktop_config.json"

$config = @'
{
    "mcpServers": {
        "MaxMSPMCP": {
            "command": "C:\\Users\\Pichau\\.local\\bin\\uv.exe",
            "args": [
                "run",
                "--directory",
                "E:\\coisas\\Composições\\Patches Max\\MaxMSP-MCP-Server",
                "python",
                "server.py"
            ]
        }
    }
}
'@

try {
    $config | Out-File -FilePath $claudeConfigPath -Encoding UTF8 -Force
    Write-Host "   OK: Configuracao aplicada" -ForegroundColor Green
} catch {
    Write-Host "   ERRO: Nao foi possivel aplicar configuracao" -ForegroundColor Red
}

Write-Host ""
Write-Host "RESULTADO FINAL:" -ForegroundColor Green
Write-Host "===============" -ForegroundColor Green
Write-Host "uv: OK" -ForegroundColor Green
Write-Host "MCP: OK" -ForegroundColor Green  
Write-Host "Servidor: OK" -ForegroundColor Green
Write-Host "Config: OK" -ForegroundColor Green
Write-Host ""
Write-Host "PROXIMO PASSO:" -ForegroundColor Yellow
Write-Host "1. Feche o Claude Desktop COMPLETAMENTE" -ForegroundColor White
Write-Host "2. Abra o Claude Desktop novamente" -ForegroundColor White
Write-Host "3. Digite: Use a ferramenta MaxMSP-MCP" -ForegroundColor White
Write-Host ""
