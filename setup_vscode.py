#!/usr/bin/env python3
"""
Configuração do MaxMSP-MCP Server para VS Code/GitHub Copilot
Este script configura o servidor MCP para funcionar com VS Code
"""

import os
import json
import argparse
from pathlib import Path

def setup_vscode_mcp():
    """Configura o MCP para VS Code"""
    
    # Caminho para as configurações do VS Code
    if os.name == "posix":
        vscode_settings_path = Path.home() / ".config/Code/User/settings.json"
    else:
        vscode_settings_path = Path(os.environ["APPDATA"]) / "Code/User/settings.json"
    
    # Criar diretório se não existir
    vscode_settings_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Carregar configurações existentes ou criar novas
    if vscode_settings_path.exists():
        with open(vscode_settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    else:
        settings = {}
    
    # Caminho absoluto para o servidor
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir, "server.py")
    venv_path = os.path.join(current_dir, ".venv")
    
    # Configuração MCP para VS Code
    mcp_config = {
        "mcp.servers": {
            "MaxMSPMCP": {
                "command": "uv",
                "args": ["run", "python", server_path],
                "cwd": current_dir,
                "env": {
                    "VIRTUAL_ENV": venv_path,
                    "PATH": f"{venv_path}/Scripts;{venv_path}/bin;{os.environ.get('PATH', '')}"
                }
            }
        }
    }
    
    # Adicionar configuração às settings
    settings.update(mcp_config)
    
    # Salvar configurações
    with open(vscode_settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Configuração MCP adicionada em: {vscode_settings_path}")
    return str(vscode_settings_path)

def create_vscode_launch_config():
    """Cria configuração de launch para VS Code"""
    
    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "MaxMSP-MCP Server",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/server.py",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {
                    "SOCKETIO_SERVER_URL": "http://127.0.0.1",
                    "SOCKETIO_SERVER_PORT": "5002",
                    "NAMESPACE": "/mcp"
                },
                "args": []
            }
        ]
    }
    
    # Criar diretório .vscode se não existir
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    # Salvar launch.json
    launch_file = vscode_dir / "launch.json"
    with open(launch_file, 'w', encoding='utf-8') as f:
        json.dump(launch_config, f, indent=4)
    
    print(f"✅ Configuração de debug criada em: {launch_file}")
    return str(launch_file)

def create_copilot_wrapper():
    """Cria um wrapper para integrar com GitHub Copilot"""
    
    wrapper_code = '''#!/usr/bin/env python3
"""
GitHub Copilot Wrapper para MaxMSP-MCP Server
Este script atua como uma ponte entre o Copilot Chat e o servidor MCP
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Adicionar o diretório atual ao path para importar o servidor
sys.path.insert(0, str(Path(__file__).parent))

try:
    from server import MaxMSPConnection, mcp, docs, flattened_docs
    print("✅ Servidor MCP importado com sucesso", file=sys.stderr)
except ImportError as e:
    print(f"❌ Erro ao importar servidor MCP: {e}", file=sys.stderr)
    sys.exit(1)

class CopilotMCPBridge:
    """Ponte entre GitHub Copilot e MaxMSP-MCP Server"""
    
    def __init__(self):
        self.maxmsp = None
        
    async def initialize(self):
        """Inicializa a conexão com MaxMSP"""
        try:
            self.maxmsp = MaxMSPConnection("http://127.0.0.1", 5002)
            await self.maxmsp.sio.connect("http://127.0.0.1:5002", namespaces=["/mcp"])
            print("✅ Conectado ao MaxMSP", file=sys.stderr)
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar com MaxMSP: {e}", file=sys.stderr)
            return False
    
    async def process_command(self, command: str) -> str:
        """Processa um comando do Copilot"""
        try:
            # Aqui você pode implementar a lógica para processar comandos
            # Por exemplo, se o comando contém "explicar patch"
            if "explicar" in command.lower() or "explain" in command.lower():
                return await self.explain_patch()
            elif "criar" in command.lower() or "create" in command.lower():
                return await self.create_patch(command)
            elif "conectar" in command.lower() or "connect" in command.lower():
                return await self.connect_objects(command)
            else:
                return await self.general_maxmsp_help(command)
                
        except Exception as e:
            return f"Erro ao processar comando: {e}"
    
    async def explain_patch(self) -> str:
        """Explica o patch atual"""
        try:
            # Obter objetos do patch
            result = await self.maxmsp.send_request({
                "action": "get_objects_in_patch",
                "request_id": "explain_patch"
            })
            
            if result:
                objects_info = "\\n".join([f"- {obj}" for obj in result])
                return f"📋 Objetos no patch atual:\\n{objects_info}"
            else:
                return "❌ Não foi possível obter informações do patch"
                
        except Exception as e:
            return f"❌ Erro ao explicar patch: {e}"
    
    async def create_patch(self, description: str) -> str:
        """Cria objetos baseado na descrição"""
        # Implementar lógica de criação baseada na descrição
        return f"🔧 Criando patch baseado em: {description}"
    
    async def connect_objects(self, command: str) -> str:
        """Conecta objetos no patch"""
        return f"🔗 Conectando objetos: {command}"
    
    async def general_maxmsp_help(self, query: str) -> str:
        """Fornece ajuda geral sobre MaxMSP"""
        # Buscar na documentação
        relevant_docs = []
        query_lower = query.lower()
        
        for obj_name, obj_info in flattened_docs.items():
            if query_lower in obj_name.lower() or query_lower in obj_info.get("description", "").lower():
                relevant_docs.append(f"**{obj_name}**: {obj_info.get('description', 'Sem descrição')}")
                if len(relevant_docs) >= 5:  # Limitar a 5 resultados
                    break
        
        if relevant_docs:
            docs_text = "\\n".join(relevant_docs)
            return f"📚 Documentação relevante:\\n{docs_text}"
        else:
            return f"❓ Não encontrei informações específicas sobre: {query}"

async def main():
    """Função principal do wrapper"""
    bridge = CopilotMCPBridge()
    
    # Inicializar conexão
    if not await bridge.initialize():
        print("❌ Falha na inicialização")
        return
    
    print("🚀 GitHub Copilot ↔ MaxMSP Bridge iniciado!")
    print("💬 Digite comandos ou 'quit' para sair:")
    
    try:
        while True:
            try:
                # Ler comando do stdin
                command = input("Copilot> ").strip()
                
                if command.lower() in ['quit', 'exit', 'sair']:
                    break
                
                if command:
                    result = await bridge.process_command(command)
                    print(f"MaxMSP: {result}")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
                
    finally:
        if bridge.maxmsp and bridge.maxmsp.sio.connected:
            await bridge.maxmsp.sio.disconnect()
        print("👋 Bridge finalizado")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    wrapper_file = Path("copilot_bridge.py")
    with open(wrapper_file, 'w', encoding='utf-8') as f:
        f.write(wrapper_code)
    
    print(f"✅ Wrapper do Copilot criado em: {wrapper_file}")
    return str(wrapper_file)

def create_vscode_extension_config():
    """Cria configuração para usar com extensões MCP do VS Code"""
    
    # Configuração para a extensão MCP (se existir)
    mcp_extension_config = {
        "mcp-client": {
            "servers": {
                "MaxMSPMCP": {
                    "command": "uv",
                    "args": ["run", "python", "server.py"],
                    "cwd": "${workspaceFolder}",
                    "env": {
                        "SOCKETIO_SERVER_URL": "http://127.0.0.1",
                        "SOCKETIO_SERVER_PORT": "5002"
                    }
                }
            }
        }
    }
    
    # Criar arquivo de configuração
    config_file = Path(".vscode/mcp-config.json")
    config_file.parent.mkdir(exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(mcp_extension_config, f, indent=4)
    
    print(f"✅ Configuração MCP extension criada em: {config_file}")
    return str(config_file)

def main():
    """Função principal"""
    print("🔧 Configurando MaxMSP-MCP Server para VS Code/GitHub Copilot")
    print()
    
    try:
        # 1. Configurar VS Code settings
        vscode_settings = setup_vscode_mcp()
        
        # 2. Criar launch configuration
        launch_config = create_vscode_launch_config()
        
        # 3. Criar wrapper do Copilot
        copilot_wrapper = create_copilot_wrapper()
        
        # 4. Criar configuração para extensões MCP
        extension_config = create_vscode_extension_config()
        
        print()
        print("🎉 Configuração concluída!")
        print()
        print("📋 Para usar com GitHub Copilot:")
        print("1. Instale uma extensão MCP para VS Code (se disponível)")
        print("2. Ou use o wrapper criado:")
        print(f"   uv run python copilot_bridge.py")
        print()
        print("3. Para debug direto no VS Code:")
        print("   - Pressione F5 ou vá em Run > Start Debugging")
        print("   - Selecione 'MaxMSP-MCP Server'")
        print()
        print("📁 Arquivos criados:")
        print(f"   - {vscode_settings}")
        print(f"   - {launch_config}")
        print(f"   - {copilot_wrapper}")
        print(f"   - {extension_config}")
        
    except Exception as e:
        print(f"❌ Erro durante configuração: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
