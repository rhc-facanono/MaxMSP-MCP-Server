# Script para compilar e instalar a extensão VS Code MaxMSP-MCP
# ==============================================================

Write-Host ""
Write-Host "Compilando Extensao VS Code MaxMSP-MCP" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Navegar para o diretório da extensão
$extensionDir = ".\.vscode-extension"
if (-not (Test-Path $extensionDir)) {
    Write-Host "Diretorio da extensao nao encontrado: $extensionDir" -ForegroundColor Red
    exit 1
}

Set-Location $extensionDir

# Verificar se npm está disponível
Write-Host "Verificando npm..." -ForegroundColor Yellow
try {
    $npmVersion = npm --version
    Write-Host "npm $npmVersion encontrado" -ForegroundColor Green
}
catch {
    Write-Host "npm nao encontrado. Instale Node.js primeiro." -ForegroundColor Red
    exit 1
}

# Instalar dependências
Write-Host "Instalando dependencias..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao instalar dependencias" -ForegroundColor Red
    exit 1
}
Write-Host "Dependencias instaladas" -ForegroundColor Green

# Compilar TypeScript
Write-Host "Compilando TypeScript..." -ForegroundColor Yellow
npm run compile
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro na compilacao" -ForegroundColor Red
    exit 1
}
Write-Host "Compilacao concluida" -ForegroundColor Green

# Verificar se o arquivo foi compilado
if (Test-Path "out\extension.js") {
    Write-Host "Arquivo extension.js gerado com sucesso" -ForegroundColor Green
}
else {
    Write-Host "Erro: extension.js nao foi gerado" -ForegroundColor Red
    exit 1
}

# Voltar ao diretório principal
Set-Location ..

Write-Host ""
Write-Host "Extensao compilada com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "Para instalar a extensao:" -ForegroundColor Cyan
Write-Host "1. Abra VS Code" -ForegroundColor White
Write-Host "2. Pressione Ctrl+Shift+P" -ForegroundColor White
Write-Host "3. Digite: 'Extensions: Install from VSIX...'" -ForegroundColor White
Write-Host "4. Navegue ate: .vscode-extension" -ForegroundColor White
Write-Host ""
Write-Host "Ou use o comando:" -ForegroundColor Cyan
Write-Host "code --install-extension .\.vscode-extension" -ForegroundColor Gray
Write-Host ""
