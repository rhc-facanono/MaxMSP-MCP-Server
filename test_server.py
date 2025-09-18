#!/usr/bin/env python3
"""
Script de teste para o MaxMSP-MCP Server
Verifica se todas as dependências estão instaladas e o servidor pode ser iniciado
"""

import sys
import os

def test_imports():
    """Testa se todas as importações necessárias funcionam"""
    print("🔍 Testando importações...")
    
    try:
        import mcp
        print("✅ MCP importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar MCP: {e}")
        return False
    
    try:
        import socketio
        print("✅ Socket.IO importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Socket.IO: {e}")
        return False
    
    try:
        from mcp.server.fastmcp import FastMCP
        print("✅ FastMCP importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar FastMCP: {e}")
        return False
    
    return True

def test_server_module():
    """Testa se o módulo do servidor pode ser importado"""
    print("\n🔍 Testando módulo do servidor...")
    
    try:
        import server
        print("✅ Módulo server.py importado com sucesso")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar server.py: {e}")
        return False

def check_files():
    """Verifica se os arquivos necessários existem"""
    print("\n🔍 Verificando arquivos necessários...")
    
    required_files = [
        "server.py",
        "install.py", 
        "requirements.txt",
        "docs.json",
        "MaxMSP_Agent/demo.maxpat",
        "MaxMSP_Agent/max_mcp.js",
        "MaxMSP_Agent/max_mcp_node.js",
        "MaxMSP_Agent/package.json"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - ARQUIVO AUSENTE")
            all_exist = False
    
    return all_exist

def check_venv():
    """Verifica se o ambiente virtual está ativo"""
    print("\n🔍 Verificando ambiente virtual...")
    
    if os.path.exists(".venv"):
        print("✅ Diretório .venv encontrado")
    else:
        print("❌ Diretório .venv não encontrado")
        return False
    
    if os.path.exists(".venv/Scripts/python.exe"):
        print("✅ Python no ambiente virtual encontrado")
        return True
    elif os.path.exists(".venv/bin/python"):
        print("✅ Python no ambiente virtual encontrado (Linux/Mac)")
        return True
    else:
        print("❌ Python no ambiente virtual não encontrado")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do MaxMSP-MCP Server\n")
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("server.py"):
        print("❌ Execute este script no diretório raiz do projeto MaxMSP-MCP-Server")
        sys.exit(1)
    
    all_tests_passed = True
    
    # Executar testes
    all_tests_passed &= check_files()
    all_tests_passed &= check_venv()
    all_tests_passed &= test_imports()
    all_tests_passed &= test_server_module()
    
    print("\n" + "="*50)
    if all_tests_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ O MaxMSP-MCP Server está pronto para uso")
        print("\n📋 Próximos passos:")
        print("1. Abra o MaxMSP 9 ou superior")
        print("2. Abra o arquivo MaxMSP_Agent/demo.maxpat")
        print("3. No primeiro tab, clique 'script npm install'")
        print("4. No segundo tab, clique 'script start'")
        print("5. Use Claude Desktop para interagir com o servidor MCP")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("⚠️  Verifique os erros acima antes de continuar")
        sys.exit(1)

if __name__ == "__main__":
    main()
