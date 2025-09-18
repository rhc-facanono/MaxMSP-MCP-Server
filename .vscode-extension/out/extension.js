"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const socket_io_client_1 = require("socket.io-client");
const child_process_1 = require("child_process");
class MaxMSPMCPServer {
    constructor() {
        this.serverProcess = null;
        this.socket = null;
        this.isConnected = false;
    }
    async startServer() {
        const config = vscode.workspace.getConfiguration('maxmsp-mcp');
        const serverPath = config.get('serverPath', './server.py');
        const port = config.get('port', 5002);
        try {
            // Start the MCP server
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                throw new Error('No workspace folder found');
            }
            const cwd = workspaceFolder.uri.fsPath;
            this.serverProcess = (0, child_process_1.spawn)('uv', ['run', 'python', serverPath], {
                cwd,
                env: { ...process.env, SOCKETIO_SERVER_PORT: port.toString() }
            });
            this.serverProcess.stdout?.on('data', (data) => {
                console.log(`MaxMSP-MCP Server: ${data}`);
            });
            this.serverProcess.stderr?.on('data', (data) => {
                console.error(`MaxMSP-MCP Server Error: ${data}`);
            });
            // Wait a bit for server to start
            await new Promise(resolve => setTimeout(resolve, 2000));
            // Connect Socket.IO
            this.socket = (0, socket_io_client_1.io)(`http://127.0.0.1:${port}`, {
                path: '/socket.io/',
                transports: ['websocket', 'polling']
            });
            return new Promise((resolve) => {
                this.socket.on('connect', () => {
                    this.isConnected = true;
                    vscode.window.showInformationMessage('MaxMSP-MCP Server connected!');
                    resolve(true);
                });
                this.socket.on('connect_error', (error) => {
                    console.error('Socket.IO connection error:', error);
                    resolve(false);
                });
                // Timeout after 10 seconds
                setTimeout(() => resolve(false), 10000);
            });
        }
        catch (error) {
            console.error('Failed to start MaxMSP-MCP server:', error);
            return false;
        }
    }
    async stopServer() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
        if (this.serverProcess) {
            this.serverProcess.kill();
            this.serverProcess = null;
        }
        this.isConnected = false;
        vscode.window.showInformationMessage('MaxMSP-MCP Server stopped');
    }
    async sendCommand(action, params = {}) {
        if (!this.isConnected || !this.socket) {
            throw new Error('Not connected to MaxMSP-MCP server');
        }
        return new Promise((resolve, reject) => {
            const requestId = Math.random().toString(36).substring(7);
            const command = { action, request_id: requestId, ...params };
            // Set up response listener
            const responseHandler = (data) => {
                if (data.request_id === requestId) {
                    this.socket.off('response', responseHandler);
                    resolve(data.results);
                }
            };
            this.socket.on('response', responseHandler);
            // Send command
            this.socket.emit('command', command);
            // Timeout after 30 seconds
            setTimeout(() => {
                this.socket.off('response', responseHandler);
                reject(new Error('Request timeout'));
            }, 30000);
        });
    }
}
class MaxMSPChatParticipant {
    constructor(mcpServer) {
        this.id = 'maxmsp';
        this.requestHandler = async (request, context, stream, token) => {
            return this.handleRequest(request, context, stream, token);
        };
        this.onDidReceiveFeedback = () => { };
        this.dispose = () => { };
        this.mcpServer = mcpServer;
    }
    async handleRequest(request, context, stream, token) {
        stream.progress('Conectando ao MaxMSP...');
        try {
            const prompt = request.prompt.toLowerCase();
            if (prompt.includes('explicar') || prompt.includes('explain')) {
                await this.explainPatch(stream);
            }
            else if (prompt.includes('criar') || prompt.includes('create')) {
                await this.createPatch(request.prompt, stream);
            }
            else if (prompt.includes('conectar') || prompt.includes('connect')) {
                await this.connectObjects(request.prompt, stream);
            }
            else if (prompt.includes('help') || prompt.includes('ajuda')) {
                await this.showHelp(stream);
            }
            else {
                await this.generalMaxMSPHelp(request.prompt, stream);
            }
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            stream.markdown(`❌ **Erro**: ${errorMessage}`);
        }
    }
    async explainPatch(stream) {
        try {
            const objects = await this.mcpServer.sendCommand('get_objects_in_patch');
            if (objects && objects.length > 0) {
                stream.markdown('## 📋 Objetos no Patch Atual\n\n');
                objects.forEach((obj, index) => {
                    stream.markdown(`${index + 1}. **${obj.class}** (${obj.varname})\n`);
                    if (obj.text) {
                        stream.markdown(`   - Texto: "${obj.text}"\n`);
                    }
                    if (obj.position) {
                        stream.markdown(`   - Posição: [${obj.position[0]}, ${obj.position[1]}]\n`);
                    }
                    stream.markdown('\n');
                });
                stream.markdown('### 💡 Análise do Patch\n\n');
                stream.markdown('Este patch contém os objetos listados acima. ');
                stream.markdown('Posso ajudar você a entender melhor como eles funcionam ou como modificá-los.');
            }
            else {
                stream.markdown('❓ **Nenhum objeto encontrado no patch atual**\n\n');
                stream.markdown('Certifique-se de que:\n');
                stream.markdown('- O MaxMSP está aberto\n');
                stream.markdown('- O demo.maxpat está carregado\n');
                stream.markdown('- O script "start" foi executado no MaxMSP\n');
            }
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            stream.markdown(`❌ **Erro ao explicar patch**: ${errorMessage}`);
        }
    }
    async createPatch(description, stream) {
        stream.markdown('## 🔧 Criando Patch MaxMSP\n\n');
        stream.markdown(`**Descrição**: ${description}\n\n`);
        // Análise simples da descrição para sugerir objetos
        const desc = description.toLowerCase();
        if (desc.includes('oscilador') || desc.includes('oscillator')) {
            stream.markdown('### Sugestão de Objetos:\n\n');
            stream.markdown('1. **cycle~** - Oscilador senoidal\n');
            stream.markdown('2. **dac~** - Saída de áudio\n');
            stream.markdown('3. **gain~** - Controle de volume\n\n');
            try {
                // Tentar criar os objetos
                await this.mcpServer.sendCommand('add_object', {
                    position: [100, 100],
                    obj_type: 'cycle~',
                    args: [440],
                    varname: 'osc1'
                });
                stream.markdown('✅ Oscilador criado com sucesso!\n');
            }
            catch (error) {
                const errorMessage = error instanceof Error ? error.message : String(error);
                stream.markdown(`⚠️ Não foi possível criar automaticamente: ${errorMessage}\n`);
                stream.markdown('Você pode criar manualmente no MaxMSP.\n');
            }
        }
        stream.markdown('### 💡 Dica\n\n');
        stream.markdown('Use comandos mais específicos como:\n');
        stream.markdown('- "criar oscilador de 440Hz"\n');
        stream.markdown('- "criar filtro passa-baixa"\n');
        stream.markdown('- "criar delay de 500ms"\n');
    }
    async connectObjects(description, stream) {
        stream.markdown('## 🔗 Conectando Objetos\n\n');
        stream.markdown(`**Comando**: ${description}\n\n`);
        // Implementar lógica de conexão baseada na descrição
        stream.markdown('Para conectar objetos, especifique:\n');
        stream.markdown('- Objeto de origem\n');
        stream.markdown('- Objeto de destino\n');
        stream.markdown('- Saída e entrada (opcional)\n\n');
        stream.markdown('**Exemplo**: "conectar cycle~ ao dac~"\n');
    }
    async showHelp(stream) {
        stream.markdown('# 🎹 MaxMSP MCP Assistant\n\n');
        stream.markdown('## Comandos Disponíveis:\n\n');
        stream.markdown('### 📋 Análise\n');
        stream.markdown('- **"explicar patch"** - Mostra todos os objetos no patch atual\n');
        stream.markdown('- **"analisar conexões"** - Mostra como os objetos estão conectados\n\n');
        stream.markdown('### 🔧 Criação\n');
        stream.markdown('- **"criar oscilador"** - Adiciona um oscilador\n');
        stream.markdown('- **"criar filtro"** - Adiciona um filtro\n');
        stream.markdown('- **"criar delay"** - Adiciona um delay\n\n');
        stream.markdown('### 🔗 Conexões\n');
        stream.markdown('- **"conectar [objeto1] ao [objeto2]"** - Conecta dois objetos\n');
        stream.markdown('- **"desconectar [objeto1] do [objeto2]"** - Remove conexão\n\n');
        stream.markdown('### 📚 Documentação\n');
        stream.markdown('- **"o que é [objeto]?"** - Explica um objeto específico\n');
        stream.markdown('- **"como usar [objeto]?"** - Mostra exemplos de uso\n\n');
        stream.markdown('### ⚙️ Configuração\n');
        stream.markdown('- Certifique-se que o MaxMSP está executando\n');
        stream.markdown('- Abra o demo.maxpat e execute "script start"\n');
        stream.markdown('- O servidor MCP deve estar conectado\n');
    }
    async generalMaxMSPHelp(query, stream) {
        stream.markdown(`## 🔍 Procurando: "${query}"\n\n`);
        // Simular busca na documentação
        // Em uma implementação real, isso buscaria no docs.json
        const commonObjects = {
            'cycle~': 'Oscilador senoidal - gera formas de onda senoidais',
            'dac~': 'Digital-to-Analog Converter - saída de áudio principal',
            'adc~': 'Analog-to-Digital Converter - entrada de áudio',
            'gain~': 'Controle de ganho/volume para sinais de áudio',
            'filtergraph~': 'Filtro gráfico multibanda',
            'delay~': 'Linha de delay para sinais de áudio',
            'metro': 'Metrônomo - gera bangs em intervalos regulares',
            'random': 'Gerador de números aleatórios',
            'select': 'Seleciona valores específicos',
            'gate': 'Roteador de mensagens'
        };
        const query_lower = query.toLowerCase();
        let found = false;
        for (const [obj, desc] of Object.entries(commonObjects)) {
            if (query_lower.includes(obj.toLowerCase()) || obj.toLowerCase().includes(query_lower)) {
                stream.markdown(`### 📘 ${obj}\n\n`);
                stream.markdown(`${desc}\n\n`);
                found = true;
            }
        }
        if (!found) {
            stream.markdown('❓ **Não encontrei informações específicas sobre sua consulta.**\n\n');
            stream.markdown('Tente perguntar sobre:\n');
            stream.markdown('- Objetos específicos (ex: "cycle~", "dac~")\n');
            stream.markdown('- Conceitos (ex: "oscilador", "filtro")\n');
            stream.markdown('- Operações (ex: "criar patch", "conectar objetos")\n\n');
            stream.markdown('Ou digite **"ajuda"** para ver todos os comandos disponíveis.\n');
        }
    }
}
function activate(context) {
    const mcpServer = new MaxMSPMCPServer();
    // Register commands
    context.subscriptions.push(vscode.commands.registerCommand('maxmsp-mcp.startServer', async () => {
        const success = await mcpServer.startServer();
        if (!success) {
            vscode.window.showErrorMessage('Failed to start MaxMSP-MCP server');
        }
    }));
    context.subscriptions.push(vscode.commands.registerCommand('maxmsp-mcp.stopServer', () => {
        mcpServer.stopServer();
    }));
    // Register chat participant
    const chatParticipant = new MaxMSPChatParticipant(mcpServer);
    context.subscriptions.push(vscode.chat.createChatParticipant('maxmsp', chatParticipant.requestHandler));
    // Auto-start server if configured
    const config = vscode.workspace.getConfiguration('maxmsp-mcp');
    if (config.get('autoStart', true) && vscode.workspace.workspaceFolders) {
        mcpServer.startServer();
    }
    console.log('MaxMSP MCP extension activated');
}
function deactivate() {
    console.log('MaxMSP MCP extension deactivated');
}
//# sourceMappingURL=extension.js.map