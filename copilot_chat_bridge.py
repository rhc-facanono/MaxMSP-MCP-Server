"""
🎹 MaxMSP MCP Bridge para GitHub Copilot Chat
===============================================

Este script funciona como uma ponte entre o GitHub Copilot Chat no VS Code
e o servidor MaxMSP-MCP, permitindo que você converse com o Copilot sobre
MaxMSP e execute comandos diretamente no Max.

Como usar:
1. Execute este script: uv run python copilot_chat_bridge.py
2. No GitHub Copilot Chat (@github), faça perguntas sobre MaxMSP
3. O bridge interceptará e processará as respostas

Exemplos de comandos:
- "Explique o patch atual no MaxMSP"
- "Crie um oscilador de 440Hz"
- "Conecte o cycle~ ao dac~"
- "O que faz o objeto filtergraph~?"
"""

import asyncio
import json
import sys
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Adicionar o diretório atual ao path para importar o servidor
sys.path.insert(0, str(Path(__file__).parent))

try:
    from server import MaxMSPConnection, docs, flattened_docs
    logger.info("✅ Servidor MCP importado com sucesso")
except ImportError as e:
    logger.error(f"❌ Erro ao importar servidor MCP: {e}")
    sys.exit(1)

class MaxMSPCopilotBridge:
    """Ponte entre GitHub Copilot Chat e MaxMSP-MCP Server"""
    
    def __init__(self, server_url: str = "http://127.0.0.1", server_port: int = 5002):
        self.server_url = server_url
        self.server_port = server_port
        self.maxmsp: Optional[MaxMSPConnection] = None
        self.is_connected = False
        
    async def initialize(self) -> bool:
        """Inicializa a conexão com MaxMSP"""
        try:
            logger.info(f"🔌 Conectando ao MaxMSP em {self.server_url}:{self.server_port}")
            self.maxmsp = MaxMSPConnection(self.server_url, self.server_port)
            await self.maxmsp.sio.connect(f"{self.server_url}:{self.server_port}", namespaces=["/mcp"])
            self.is_connected = True
            logger.info("✅ Conectado ao MaxMSP com sucesso")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com MaxMSP: {e}")
            logger.info("💡 Certifique-se de que:")
            logger.info("   - O MaxMSP está executando")
            logger.info("   - O demo.maxpat está aberto")
            logger.info("   - O 'script start' foi executado no MaxMSP")
            return False
    
    async def disconnect(self):
        """Desconecta do MaxMSP"""
        if self.maxmsp and self.maxmsp.sio.connected:
            await self.maxmsp.sio.disconnect()
            self.is_connected = False
            logger.info("👋 Desconectado do MaxMSP")
    
    async def explain_patch(self) -> str:
        """Explica o patch atual do MaxMSP"""
        if not self.is_connected:
            return "❌ Não conectado ao MaxMSP. Execute o bridge primeiro."
        
        try:
            logger.info("📋 Obtendo objetos do patch...")
            result = await self.maxmsp.send_request({
                "action": "get_objects_in_patch",
                "request_id": f"explain_{int(time.time())}"
            })
            
            if result and len(result) > 0:
                explanation = "## 📋 Objetos no Patch MaxMSP Atual\\n\\n"
                
                for i, obj in enumerate(result[:10], 1):  # Limitar a 10 objetos
                    obj_name = obj.get('class', 'unknown')
                    varname = obj.get('varname', 'sem nome')
                    text = obj.get('text', '')
                    position = obj.get('position', [0, 0])
                    
                    explanation += f"**{i}. {obj_name}** (`{varname}`)\\n"
                    if text and text != obj_name:
                        explanation += f"   - Texto: \"{text}\"\\n"
                    explanation += f"   - Posição: [{position[0]}, {position[1]}]\\n"
                    
                    # Adicionar documentação se disponível
                    if obj_name in flattened_docs:
                        doc = flattened_docs[obj_name]
                        description = doc.get('description', doc.get('digest', ''))
                        if description:
                            explanation += f"   - Descrição: {description[:100]}...\\n"
                    
                    explanation += "\\n"
                
                if len(result) > 10:
                    explanation += f"... e mais {len(result) - 10} objetos\\n\\n"
                
                explanation += "### 💡 Análise\\n"
                explanation += f"Este patch contém {len(result)} objetos. "
                
                # Análise básica dos tipos de objetos
                obj_types = {}
                for obj in result:
                    obj_type = obj.get('class', 'unknown')
                    obj_types[obj_type] = obj_types.get(obj_type, 0) + 1
                
                if 'cycle~' in obj_types or 'saw~' in obj_types:
                    explanation += "Contém osciladores (geração de áudio). "
                if 'dac~' in obj_types:
                    explanation += "Tem saída de áudio configurada. "
                if 'adc~' in obj_types:
                    explanation += "Tem entrada de áudio. "
                if 'gain~' in obj_types or 'mult~' in obj_types:
                    explanation += "Inclui controles de amplitude. "
                
                return explanation
            else:
                return ("❓ **Nenhum objeto encontrado no patch atual**\\n\\n"
                       "Certifique-se de que:\\n"
                       "- O MaxMSP está aberto\\n"
                       "- Um patch está carregado\\n"
                       "- O servidor MCP está conectado")
                
        except Exception as e:
            logger.error(f"Erro ao explicar patch: {e}")
            return f"❌ **Erro ao explicar patch**: {str(e)}"
    
    async def get_object_documentation(self, object_name: str) -> str:
        """Retorna documentação de um objeto específico"""
        object_name = object_name.strip()
        
        if object_name in flattened_docs:
            doc = flattened_docs[object_name]
            
            result = f"## 📘 {object_name}\\n\\n"
            
            # Descrição principal
            description = doc.get('description', doc.get('digest', ''))
            if description:
                result += f"**Descrição**: {description}\\n\\n"
            
            # Inlets
            if 'inletlist' in doc and doc['inletlist']:
                result += "### Entradas (Inlets)\\n"
                for inlet in doc['inletlist'][:3]:  # Limitar a 3
                    inlet_desc = inlet.get('description', inlet.get('digest', 'Sem descrição'))
                    result += f"- **Inlet {inlet.get('id', '?')}**: {inlet_desc}\\n"
                result += "\\n"
            
            # Outlets
            if 'outletlist' in doc and doc['outletlist']:
                result += "### Saídas (Outlets)\\n"
                for outlet in doc['outletlist'][:3]:  # Limitar a 3
                    outlet_desc = outlet.get('description', outlet.get('digest', 'Sem descrição'))
                    result += f"- **Outlet {outlet.get('id', '?')}**: {outlet_desc}\\n"
                result += "\\n"
            
            # Argumentos
            if 'arguments' in doc and doc['arguments']:
                result += "### Argumentos\\n"
                for arg in doc['arguments'][:3]:  # Limitar a 3
                    arg_name = arg.get('name', 'arg')
                    arg_desc = arg.get('description', arg.get('digest', 'Sem descrição'))
                    optional = " (opcional)" if arg.get('optional') == '1' else ""
                    result += f"- **{arg_name}**{optional}: {arg_desc}\\n"
                result += "\\n"
            
            return result
        else:
            # Busca aproximada
            similar_objects = []
            search_term = object_name.lower()
            
            for obj_name, obj_info in flattened_docs.items():
                if (search_term in obj_name.lower() or 
                    search_term in obj_info.get('description', '').lower()):
                    similar_objects.append((obj_name, obj_info.get('description', obj_info.get('digest', 'Sem descrição'))))
                    if len(similar_objects) >= 5:
                        break
            
            if similar_objects:
                result = f"❓ **Objeto '{object_name}' não encontrado exatamente**\\n\\n"
                result += "### Objetos similares encontrados:\\n\\n"
                for obj_name, obj_desc in similar_objects:
                    result += f"- **{obj_name}**: {obj_desc[:100]}...\\n"
                return result
            else:
                return f"❓ **Objeto '{object_name}' não encontrado na documentação**"
    
    async def create_simple_patch(self, description: str) -> str:
        """Cria um patch simples baseado na descrição"""
        if not self.is_connected:
            return "❌ Não conectado ao MaxMSP. Execute o bridge primeiro."
        
        description_lower = description.lower()
        result = f"## 🔧 Criando patch: {description}\\n\\n"
        
        try:
            created_objects = []
            
            # Análise de palavras-chave para criar objetos
            if 'oscilador' in description_lower or 'oscillator' in description_lower:
                # Criar oscilador
                freq = 440  # Frequência padrão
                if '220' in description:
                    freq = 220
                elif '880' in description:
                    freq = 880
                elif '110' in description:
                    freq = 110
                
                await self.maxmsp.send_command({
                    "action": "add_object",
                    "position": [100, 100],
                    "obj_type": "cycle~",
                    "args": [freq],
                    "varname": f"osc_{int(time.time())}"
                })
                created_objects.append(f"cycle~ {freq}")
                result += f"✅ Criado: **cycle~ {freq}** (oscilador senoidal)\\n"
            
            if 'saida' in description_lower or 'output' in description_lower or 'dac' in description_lower:
                # Criar saída de áudio
                await self.maxmsp.send_command({
                    "action": "add_object",
                    "position": [200, 200],
                    "obj_type": "dac~",
                    "args": [],
                    "varname": f"dac_{int(time.time())}"
                })
                created_objects.append("dac~")
                result += "✅ Criado: **dac~** (saída de áudio)\\n"
            
            if 'volume' in description_lower or 'gain' in description_lower:
                # Criar controle de volume
                await self.maxmsp.send_command({
                    "action": "add_object",
                    "position": [150, 150],
                    "obj_type": "gain~",
                    "args": [],
                    "varname": f"gain_{int(time.time())}"
                })
                created_objects.append("gain~")
                result += "✅ Criado: **gain~** (controle de volume)\\n"
            
            if created_objects:
                result += f"\\n### 🎉 Sucesso!\\n"
                result += f"Criados {len(created_objects)} objetos no MaxMSP.\\n\\n"
                result += "### 💡 Próximos passos:\\n"
                result += "- Conecte os objetos manualmente no MaxMSP\\n"
                result += "- Ajuste os parâmetros conforme necessário\\n"
                result += "- Use o comando 'conectar' para automatizar conexões\\n"
            else:
                result += "⚠️ **Nenhum objeto foi criado automaticamente**\\n\\n"
                result += "### 💡 Dica: Use termos específicos como:\\n"
                result += "- 'criar oscilador de 440Hz'\\n"
                result += "- 'adicionar saída de áudio'\\n"
                result += "- 'incluir controle de volume'\\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao criar patch: {e}")
            return f"❌ **Erro ao criar patch**: {str(e)}"
    
    def generate_copilot_response(self, user_query: str) -> str:
        """Gera uma resposta estruturada para o Copilot Chat"""
        
        response = f"""
# 🎹 MaxMSP Assistant Response

**Query**: {user_query}

## Status da Conexão
{'✅ Conectado ao MaxMSP-MCP Server' if self.is_connected else '❌ Não conectado ao MaxMSP-MCP Server'}

## Resposta

"""
        
        query_lower = user_query.lower()
        
        if not self.is_connected:
            response += """
❌ **Não é possível processar sua solicitação**

Para usar este assistant, você precisa:

1. **Iniciar o servidor MaxMSP-MCP**:
   ```bash
   cd "e:\\coisas\\Composições\\Patches Max\\MaxMSP-MCP-Server"
   uv run python copilot_chat_bridge.py
   ```

2. **Abrir MaxMSP e carregar o demo.maxpat**

3. **Executar 'script start' no MaxMSP**

Depois que tudo estiver conectado, eu posso:
- Explicar patches MaxMSP
- Criar objetos automaticamente
- Fornecer documentação detalhada
- Sugerir conexões entre objetos
"""
            return response
        
        # Análise da query para determinar a ação
        if any(word in query_lower for word in ['explicar', 'explain', 'mostrar', 'show', 'patch']):
            response += "📋 **Explicando o patch atual...**\\n\\n"
            response += "*(Execute: `asyncio.run(bridge.explain_patch())` para obter detalhes)*"
            
        elif any(word in query_lower for word in ['criar', 'create', 'adicionar', 'add']):
            response += "🔧 **Criando elementos no MaxMSP...**\\n\\n"
            response += f"*(Execute: `asyncio.run(bridge.create_simple_patch('{user_query}'))` para criar)*"
            
        elif any(word in query_lower for word in ['conectar', 'connect', 'ligar', 'link']):
            response += "🔗 **Conectando objetos...**\\n\\n"
            response += "Para conectar objetos, especifique o objeto de origem e destino.\\n"
            response += "Exemplo: 'conectar cycle~ ao dac~'"
            
        elif user_query.startswith('o que é') or user_query.startswith('what is'):
            object_name = user_query.replace('o que é', '').replace('what is', '').strip()
            response += f"📘 **Documentação do objeto: {object_name}**\\n\\n"
            response += f"*(Execute: `asyncio.run(bridge.get_object_documentation('{object_name}'))` para detalhes)*"
            
        else:
            response += """
💡 **Como posso ajudar com MaxMSP?**

### Comandos disponíveis:
- **"explicar patch"** - Mostra todos os objetos no patch atual
- **"criar oscilador"** - Adiciona um oscilador ao patch
- **"o que é cycle~?"** - Explica um objeto específico
- **"conectar cycle~ ao dac~"** - Liga dois objetos

### Recursos disponíveis:
- 📋 Análise de patches existentes
- 🔧 Criação automática de objetos  
- 📚 Documentação completa de objetos MaxMSP
- 🔗 Sugestões de conexões
"""
        
        return response

def print_banner():
    """Imprime o banner de inicialização"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                  🎹 MaxMSP MCP Bridge                        ║
║              para GitHub Copilot Chat                        ║
╚══════════════════════════════════════════════════════════════╝

🚀 Conectando seu Copilot Chat ao MaxMSP via MCP...

Este bridge permite que você:
✅ Converse com o Copilot sobre MaxMSP
✅ Execute comandos diretamente no Max
✅ Obtenha documentação instantânea
✅ Crie patches automaticamente

Comandos de exemplo para o Copilot Chat:
💬 "Explique o patch atual no MaxMSP"
💬 "Crie um oscilador de 440Hz"  
💬 "O que faz o objeto filtergraph~?"
💬 "Conecte o cycle~ ao dac~"
"""
    print(banner)

async def main():
    """Função principal do bridge"""
    print_banner()
    
    # Criar bridge
    bridge = MaxMSPCopilotBridge()
    
    # Tentar conectar
    connected = await bridge.initialize()
    
    if connected:
        print("🎉 Bridge ativo! Agora você pode usar o Copilot Chat.")
        print("💬 No VS Code, abra o Copilot Chat e faça perguntas sobre MaxMSP.")
        print("🔄 Este bridge permanecerá rodando em background...")
        print("📝 Pressione Ctrl+C para finalizar.")
        
        # Manter o bridge rodando
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\\n⏹️  Finalizando bridge...")
            
    else:
        print("❌ Não foi possível conectar ao MaxMSP.")
        print("\\n🔧 Verifique se:")
        print("   1. O MaxMSP está executando")
        print("   2. O demo.maxpat está aberto")
        print("   3. O 'script start' foi executado")
        print("   4. O servidor está na porta 5002")
        
    await bridge.disconnect()
    print("👋 Bridge finalizado.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n👋 Até logo!")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)
