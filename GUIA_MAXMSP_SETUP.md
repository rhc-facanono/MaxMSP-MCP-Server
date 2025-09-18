# 🎹 Guia Completo: Como Configurar o MaxMSP com MCP

## 📋 **Pré-requisitos**
- ✅ MaxMSP 9+ instalado
- ✅ Python 3.8+ instalado
- ✅ Node.js instalado
- ✅ VS Code instalado

---

## 🚀 **Passo 1: Configurar o Ambiente Python**

### 1.1. Instalar uv (se ainda não tiver):
```powershell
Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
```

### 1.2. Adicionar uv ao PATH:
```powershell
$env:PATH = "$env:PATH;C:\Users\$env:USERNAME\.local\bin"
```

### 1.3. Instalar dependências Python:
```powershell
cd "E:\coisas\Composições\Patches Max\MaxMSP-MCP-Server"
uv sync
```

---

## 🎹 **Passo 2: Configurar o MaxMSP**

### 2.1. Abrir o MaxMSP 9+
- Inicie o MaxMSP
- Certifique-se que está na versão 9 ou superior

### 2.2. Carregar o patch de demonstração:
1. No MaxMSP, clique em **File → Open**
2. Navegue até: `MaxMSP_Agent/demo.maxpat`
3. Abra o arquivo `demo.maxpat`

### 2.3. Configurar comunicação Socket.IO:
1. No patch aberto, você verá objetos Node.js
2. Localize o objeto com `script start`
3. **IMPORTANTE**: Clique no botão `script start`
4. Você deve ver mensagens confirmando a conexão

### 2.4. Verificar porta 5002:
- O MaxMSP deve estar escutando na porta 5002
- Se houver conflito, altere a porta no arquivo `server.py`

---

## 💻 **Passo 3: Configurar VS Code**

### 3.1. Instalar e compilar a extensão:
```powershell
.\build_extension.ps1
```

### 3.2. Instalar a extensão no VS Code:
```powershell
code --install-extension .\.vscode-extension
```

### 3.3. Configurar VS Code (opcional):
1. Abra VS Code Settings (Ctrl+,)
2. Procure por "MaxMSP MCP"
3. Configure:
   - **Server Path**: `./server.py`
   - **Port**: `5002`
   - **Auto Start**: `true`

---

## 🔗 **Passo 4: Iniciar o Bridge MCP**

### 4.1. Para VS Code Copilot Chat:
```powershell
# Adicionar uv ao PATH
$env:PATH = "$env:PATH;C:\Users\$env:USERNAME\.local\bin"

# Iniciar bridge
uv run python copilot_chat_bridge.py
```

### 4.2. Para Claude Desktop:
1. Copie o conteúdo de: `claude_desktop_config_CORRETO.json`
2. Cole em: `C:\Users\USERNAME\AppData\Roaming\Claude\claude_desktop_config.json`
3. Reinicie o Claude Desktop

---

## 🧪 **Passo 5: Testar a Conexão**

### 5.1. Verificar MaxMSP:
- ✅ MaxMSP aberto
- ✅ `demo.maxpat` carregado
- ✅ `script start` executado
- ✅ Mensagens de conexão visíveis

### 5.2. Verificar Python MCP:
```powershell
uv run python -c "import server; print('MCP Server OK')"
```

### 5.3. Testar Bridge:
```powershell
uv run python copilot_chat_bridge.py
```
Você deve ver:
```
✅ Servidor MCP importado com sucesso
🎹 MaxMSP MCP Bridge para GitHub Copilot Chat
🔌 Conectando ao MaxMSP em http://127.0.0.1:5002
```

---

## 💬 **Passo 6: Usar o Copilot Chat**

### 6.1. No VS Code Copilot Chat, digite:
```
@github Explique o patch atual no MaxMSP
```

### 6.2. Outros comandos úteis:
- `@github Crie um oscilador de 440Hz`
- `@github O que faz o objeto cycle~?`
- `@github Conecte o cycle~ ao dac~`
- `@github Liste objetos de áudio disponíveis`

---

## 🔧 **Solução de Problemas Comuns**

### ❌ "uv não é reconhecido":
```powershell
$env:PATH = "$env:PATH;C:\Users\$env:USERNAME\.local\bin"
```

### ❌ "Cannot connect to MaxMSP":
1. Verifique se MaxMSP está executando
2. Confirme que `demo.maxpat` está aberto
3. Execute `script start` no MaxMSP
4. Verifique se a porta 5002 está livre

### ❌ "Módulo não encontrado":
```powershell
uv sync
```

### ❌ "Extension não carrega":
```powershell
cd .vscode-extension
npm install
npm run compile
```

---

## 📚 **Arquivos Importantes**

- **`server.py`** - Servidor MCP principal
- **`copilot_chat_bridge.py`** - Bridge para VS Code
- **`MaxMSP_Agent/demo.maxpat`** - Patch de demonstração
- **`MaxMSP_Agent/max_mcp.js`** - Script Node.js para MaxMSP
- **`.vscode-extension/`** - Extensão VS Code

---

## 🎯 **Comandos de Teste Rápido**

### Testar tudo de uma vez:
```powershell
.\fix_problems_clean.ps1
```

### Só testar o bridge:
```powershell
$env:PATH = "$env:PATH;C:\Users\$env:USERNAME\.local\bin"
uv run python copilot_chat_bridge.py
```

### Compilar extensão:
```powershell
.\build_extension.ps1
```

---

## ✅ **Checklist de Verificação**

- [ ] MaxMSP 9+ instalado e executando
- [ ] `demo.maxpat` aberto no MaxMSP
- [ ] `script start` executado no MaxMSP
- [ ] uv instalado e no PATH
- [ ] Dependências Python instaladas (`uv sync`)
- [ ] Bridge executando sem erros
- [ ] VS Code com extensão instalada
- [ ] Copilot Chat respondendo a comandos MaxMSP

**Quando todos os itens estiverem ✅, você pode usar o MaxMSP através do Copilot Chat!** 🎹✨
