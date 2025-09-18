# Script para corrigir automaticamente a configuracao do Claude Desktop
# ====================================================================

Write-Host ""
Write-Host "Corrigindo Configuracao do Claude Desktop..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Caminhos dos arquivos
$correctConfigPath = ".\claude_desktop_config_CORRETO.json"
$claudeConfigDir = "$env:APPDATA\Claude"
$claudeConfigPath = "$claudeConfigDir\claude_desktop_config.json"

# Verificar se o arquivo correto existe
if (-not (Test-Path $correctConfigPath)) {
    Write-Host "Arquivo de configuracao correta nao encontrado: $correctConfigPath" -ForegroundColor Red
    exit 1
}

Write-Host "Arquivo de configuracao correta encontrado" -ForegroundColor Green

# Criar diretorio do Claude se nao existir
if (-not (Test-Path $claudeConfigDir)) {
    Write-Host "Criando diretorio do Claude: $claudeConfigDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $claudeConfigDir -Force | Out-Null
}

# Fazer backup do arquivo atual (se existir)
if (Test-Path $claudeConfigPath) {
    $backupPath = "$claudeConfigPath.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Write-Host "Fazendo backup da configuracao atual para: $backupPath" -ForegroundColor Yellow
    Copy-Item $claudeConfigPath $backupPath
}

# Copiar a configuracao correta
Write-Host "Copiando configuracao correta..." -ForegroundColor Yellow
try {
    Copy-Item $correctConfigPath $claudeConfigPath -Force
    Write-Host "Configuracao copiada com sucesso!" -ForegroundColor Green
}
catch {
    Write-Host "Erro ao copiar configuracao: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Verificar se a copia foi bem-sucedida
if (Test-Path $claudeConfigPath) {
    Write-Host "Verificando configuracao..." -ForegroundColor Yellow
    $configContent = Get-Content $claudeConfigPath -Raw
    if ($configContent -match "uv\.exe") {
        Write-Host "Configuracao verificada: uv.exe encontrado" -ForegroundColor Green
    }
    else {
        Write-Host "Aviso: uv.exe nao encontrado na configuracao" -ForegroundColor Yellow
    }
}
else {
    Write-Host "Erro: Arquivo de configuracao nao foi criado" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "====================================" -ForegroundColor Green
Write-Host "Configuracao do Claude Desktop CORRIGIDA!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Proximo passo:" -ForegroundColor Cyan
Write-Host "1. Feche o Claude Desktop completamente" -ForegroundColor White
Write-Host "2. Abra o Claude Desktop novamente" -ForegroundColor White
Write-Host "3. O MaxMSP-MCP deve aparecer como ferramenta disponivel" -ForegroundColor White
Write-Host ""
Write-Host "Para testar:" -ForegroundColor Yellow
Write-Host "Digite no Claude: 'Use a ferramenta MaxMSP para listar objetos'" -ForegroundColor Gray
Write-Host ""
