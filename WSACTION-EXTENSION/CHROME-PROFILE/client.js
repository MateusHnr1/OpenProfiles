(async function () {
    /**
     * Function to create a module context with WebSocket, storage, and custom data capabilities.
     * This function returns a context object with methods that allow interaction with WebSocket events, 
     * storage, and custom data management.
     *
     * @param {string} moduleName - The name of the module.
     * @returns {{
    *   MODULE_NAME: string,
    *   SOCKET: object,
    *   KEYBOARD_COMMANDS: Array<object>,
    *   setStorage: (key: string, value: any, isGlobal: boolean) => Promise<object>,
    *   getStorage: (key: string, isGlobal: boolean) => Promise<object>,
    *   getVariable: (variableName: string, defaultValue: any, create: boolean, isGlobal: boolean) => Promise<any>,
    *   setVariable: (variableName: string, value: any, isGlobal: boolean) => Promise<void>,
    *   showMenu: (options: Array<object>) => void,
    *   getCustomData: (key: string) => any,
    *   setCustomData: (key: string, value: any) => void,
    *   setMenuHandler: (handlerFunction: function) => void,
    *   ioEmit: (eventName: string, data: object) => void,
    *   register: (CTXAddons?: object) => Promise<void>
    * }} - The context object with methods for WebSocket, storage, and custom data.
   */
    function createContext(moduleName) {
        return window.WSACTION.createModuleContext(moduleName);
    }

    const CONTEXT = createContext("CHROME-PROFILE");
    const SOCKET = CONTEXT.SOCKET;
    
    // Evento de conexão ao WebSocket
    SOCKET.on('connect', () => {});

    // Evento de desconexão do WebSocket
    SOCKET.on('disconnect', () => {});

    /**
     * Função para exibir o menu interativo usando SweetAlert2 e permitir que o usuário escolha um grupo de perfis
     * ou crie um novo.
     */
    async function showMenu() {
        try {
            const groups = await listarGrupos(); // Solicita a lista de grupos via WebSocket

            // Gerar o HTML do select com os grupos
            const groupOptions = groups.map((group) => `<option value="${group}">${group}</option>`).join('');
            const createNewOption = `<option value="newGroup">Criar Novo Grupo</option>`;

            // Exibir o menu usando SweetAlert2
            const { value: selectedGroup } = await Swal.fire({
                title: 'Selecione um grupo de perfis ou crie um novo',
                html: `
                <select id="group-select" class="swal2-input">
                    ${groupOptions}
                    ${createNewOption}
                </select>`,
                focusConfirm: false,
                showCancelButton: true,
                confirmButtonText: 'Abrir Grupo',
                preConfirm: () => {
                    return document.getElementById('group-select').value;
                }
            });

            if (selectedGroup === 'newGroup') {
                await criarNovoGrupo();
            } else if (selectedGroup) {
                await abrirGrupo(selectedGroup);
                Swal.fire(`Grupo ${selectedGroup} aberto com sucesso!`);
            } else {
                Swal.fire('Ação cancelada.');
            }
        } catch (error) {
            Swal.fire('Erro', 'Erro ao listar ou abrir grupos', 'error');
            console.error("Erro ao listar ou abrir grupos:", error);
        }
    }

    /**
     * Função para solicitar a lista de grupos de perfis via WebSocket e aguardar a resposta
     * @returns {Promise<Array<string>>} - Lista de grupos disponíveis
     */
    async function listarGrupos() {
        return new Promise((resolve, reject) => {
            const requestEvent = `${CONTEXT.MODULE_NAME}:command`;

            CONTEXT.ioEmit(requestEvent, { event: "getGroups", type: "request" });

            // Aguardar a resposta
            SOCKET.on(requestEvent, (data) => {
                if (data.event === "getGroups" && data.type === "response") {
                    if (data && data.value) {
                        resolve(data.value); // Resolve a promise com a lista de grupos
                    } else {
                        reject(new Error('Falha ao obter a lista de grupos.'));
                    }
                }
            });

            // Timeout de segurança para evitar espera indefinida
            setTimeout(() => {
                reject(new Error('Tempo de resposta esgotado.'));
            }, 5000); // 5 segundos de timeout
        });
    }

    /**
     * Função para abrir um grupo de perfis via WebSocket e aguardar a resposta
     * @param {string} group - Nome do grupo de perfis a ser aberto
     * @returns {Promise<void>}
     */
    async function abrirGrupo(group) {
        return new Promise((resolve, reject) => {
            // Emitir o comando para abrir o grupo
            CONTEXT.ioEmit(`${CONTEXT.MODULE_NAME}:command`, { event: "openGroup", type: "request", value: group });

            // Aguardar a resposta
            SOCKET.on(requestEvent, (data) => {
                if (data.event === "openGroup" && data.type === "response") {
                    if (data.success) {
                        resolve(); // Grupo aberto com sucesso
                    } else {
                        reject(new Error('Falha ao abrir o grupo.'));
                    }
                }
            });

            // Timeout de segurança para evitar espera indefinida
            setTimeout(() => {
                reject(new Error('Tempo de resposta esgotado.'));
            }, 5000); // 5 segundos de timeout
        });
    }

    /**
     * Função para criar um novo grupo de perfis
     */
    async function criarNovoGrupo() {
        const { value: newGroupName } = await Swal.fire({
            title: 'Criar Novo Grupo',
            input: 'text',
            inputLabel: 'Digite o nome do novo grupo de perfis',
            inputPlaceholder: 'Nome do novo grupo',
            showCancelButton: true,
            confirmButtonText: 'Criar Grupo',
            preConfirm: (name) => {
                if (!name) {
                    Swal.showValidationMessage('O nome do grupo não pode estar vazio');
                }
                return name;
            }
        });

        if (newGroupName) {
            CONTEXT.ioEmit(`${CONTEXT.MODULE_NAME}:command`, { event: "createGroup", type: "request", value: newGroupName });

            // Aguardar a confirmação da criação do grupo
            SOCKET.on(`${CONTEXT.MODULE_NAME}:command`, (data) => {
                if (data.event === "createGroup" && data.type === "response" && data.success === true) {
                    Swal.fire(`Grupo ${newGroupName} criado com sucesso!`);
                } else {
                    Swal.fire('Erro', 'Falha ao criar o grupo.', 'error');
                }
            });
        } else {
            Swal.fire('Ação cancelada.');
        }
    }

    // Adicionar um evento de teclado para abrir o menu
    document.addEventListener('keydown', (event) => {
        if (event.ctrlKey && event.altKey && event.key.toLowerCase() === 'k') {
            console.log("Atalho Control + Alt + K pressionado. Abrindo o menu...");
            showMenu(); // Exibe o menu quando o atalho é pressionado
        }
    });

    CONTEXT.register();
})();
