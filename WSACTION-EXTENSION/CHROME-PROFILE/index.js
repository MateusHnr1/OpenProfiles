const { spawn } = require('child_process');
/**
 * Módulo da extensão.
 * 
 * @param {import('socket.io').Server} WSIO - Instância do WebSocket IO.
 * @param {import('express').Application} APP - Instância do Express.
 * @param {import('readline').Interface} RL - Instância do Readline.
 * @param {Object} STORAGE - Objeto de armazenamento compartilhado.
 * @param {Object} STORAGE.data - Objeto que contém os dados de armazenamento.
 * @param {Function} STORAGE.save - Função que salva o armazenamento.
 * @param {typeof import('express')} EXPRESS - Classe Express.
 * @param {Array<string>} [WEB_SCRIPTS=['client.js']] - Lista de scripts JavaScript a serem carregados dinamicamente.
 * @param {string} EXTENSION_PATH - Caminho absoluto para a pasta da extensão
 * 
 * @returns {{ start: Function, stop: Function }} - Objeto da extensão com funções `start` e `stop`.
 */
module.exports = (WSIO, APP, RL, STORAGE, EXPRESS, WEB_SCRIPTS = ['client.js'], EXTENSION_PATH = '') => {
    const ROUTER = EXPRESS.Router();
    const NAME = "CHROME-PROFILE";
    const ENABLED = true;
    const IOEVENTS = {
        "CHROME-PROFILE:command": {
            description: "GLABALIZAÇÃO DE EVENTOS",
            _function: (data) => {
                WSIO.emit(`${NAME}:command`, data);
            }
        }
    };
    const COMMANDS = {};

    /**
     * Função que inicia o processo principal.
     */
    const onInitialize = () => {
        const fullPath = `${EXTENSION_PATH}\\UTILITARIO.exe`;
        const startProcess = () => {
            console.log(`Iniciando o processo: ${fullPath}`);
            const options = { cwd: EXTENSION_PATH };
            const processo = spawn(fullPath, [], options);
            processo.stdout.on('data', (data) => {
                console.log(`stdout: ${data}`);
            });
            processo.stderr.on('data', (data) => {
                console.error(`stderr: ${data}`);
            });
            // Quando o processo fechar, reinicia
            processo.on('close', (code) => {
                console.log(`Processo encerrado com código ${code}`);
                console.log('Reiniciando o processo...');
                startProcess(); // Reinicia o processo
            });
        };

        // Iniciar o processo pela primeira vez
        startProcess();
    };

    const onError = (error) => {
        console.error(`${NAME} erro:`, error);
    };

    /**
     * Função para exibir o menu interativo e permitir que o usuário escolha um perfil para abrir
     * Lista os perfis disponíveis e permite a seleção.
     */
    async function showMenu() {}
    
    const CLIENT_LINK = `${NAME}/client`;
    var WEB_SCRIPTS = WEB_SCRIPTS;
    var EXTENSION_PATH = EXTENSION_PATH;

    return {
        NAME,
        ROUTER,
        ENABLED,
        IOEVENTS,
        COMMANDS,
        CLIENT_LINK,
        EXTENSION_PATH,
        WEB_SCRIPTS,
        onInitialize,
        onError
    };
};