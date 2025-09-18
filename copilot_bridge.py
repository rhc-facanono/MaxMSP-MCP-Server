#!/usr/bin/env python3
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
                objects_info = "\n".join([f"- {obj}" for obj in result])
                return f"📋 Objetos no patch atual:\n{objects_info}"
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
            docs_text = "\n".join(relevant_docs)
            return f"📚 Documentação relevante:\n{docs_text}"
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
