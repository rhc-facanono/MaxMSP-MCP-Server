# Corrigir problema BOM no arquivo JSON do Claude
# ================================================

Write-Host ""
Write-Host "CORRIGINDO PROBLEMA BOM - Claude Desktop" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

$claudeConfigPath = "$env:APPDATA\Claude\claude_desktop_config.json"

# Criar JSON sem BOM
$jsonContent = @'
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

Write-Host "1. Removendo arquivo com BOM..." -ForegroundColor Yellow
if (Test-Path $claudeConfigPath) {
    Remove-Item $claudeConfigPath -Force
    Write-Host "   OK: Arquivo anterior removido" -ForegroundColor Green
}
else {
    Write-Host "   OK: Nenhum arquivo anterior encontrado" -ForegroundColor Green
}

Write-Host "2. Criando arquivo JSON limpo (sem BOM)..." -ForegroundColor Yellow
try {
    # Usar ASCII encoding para evitar BOM
    [System.IO.File]::WriteAllText($claudeConfigPath, $jsonContent, [System.Text.Encoding]::ASCII)
    Write-Host "   OK: Arquivo criado com encoding ASCII" -ForegroundColor Green
}
catch {
    Write-Host "   ERRO: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "3. Verificando arquivo criado..." -ForegroundColor Yellow
if (Test-Path $claudeConfigPath) {
    $fileSize = (Get-Item $claudeConfigPath).Length
    Write-Host "   OK: Arquivo criado ($fileSize bytes)" -ForegroundColor Green
}
else {
    Write-Host "   ERRO: Arquivo nao foi criado" -ForegroundColor Red
    exit 1
}

Write-Host "4. Testando parse JSON..." -ForegroundColor Yellow
try {
    $testContent = Get-Content $claudeConfigPath -Raw
    $testJson = ConvertFrom-Json $testContent
    Write-Host "   OK: JSON valido, sem BOM" -ForegroundColor Green
}
catch {
    Write-Host "   ERRO: JSON ainda com problema" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "PROBLEMA BOM CORRIGIDO!" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green
Write-Host "✓ Arquivo criado sem BOM" -ForegroundColor Green
Write-Host "✓ JSON validado" -ForegroundColor Green
Write-Host "✓ Encoding ASCII usado" -ForegroundColor Green
Write-Host ""
Write-Host "PROXIMO PASSO:" -ForegroundColor Yellow
Write-Host "1. Feche o Claude Desktop COMPLETAMENTE" -ForegroundColor White
Write-Host "2. Abra o Claude Desktop novamente" -ForegroundColor White
Write-Host "3. Verifique se MaxMSP-MCP aparece nas ferramentas" -ForegroundColor White
Write-Host ""
