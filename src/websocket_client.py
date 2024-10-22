import socketio
import os
from chrome_manager import abrir_chromes_com_perfis, listar_grupos, PASTA_PERFIS, abrir_chromes_de_grupo
from config import carregar_configuracao
config = carregar_configuracao()
# Criação do cliente Socket.IO
sio = socketio.Client()

# Evento de conexão bem-sucedida ao servidor
@sio.event
def connect():
    print('Conectado ao servidor WebSocket!')

# Evento de desconexão do servidor
@sio.event
def disconnect():
    print('Desconectado do servidor WebSocket.')

# Evento para receber parâmetros de configuração via WebSocket
@sio.on('configuracao')
def receber_configuracao(data):
    print(f"Parâmetros recebidos via WebSocket: {data}")
    abrir_chromes_com_perfis(data)

# Evento para responder a solicitação de listar grupos e abrir perfil
@sio.on('CHROME-PROFILE:command')
def handle_command(data):
    event_type = data.get('event')

    # Responder ao pedido de grupos
    if event_type == "getGroups" and data.get('type') == "request":
        print("Solicitação para listar grupos recebida.")
        # Emitir a resposta com os grupos
        sio.emit('CHROME-PROFILE.CHROME-PROFILE:command', {
            'event': 'getGroups',
            'type': 'response',
            'value': listar_grupos()
        })
        
    # Responder ao pedido de abrir grupo
    elif event_type == "openGroup" and data.get('type') == "request":
        group = data.get('value')
        if group:
            print(f"Abrindo o grupo: {group}")
            sio.emit('CHROME-PROFILE.CHROME-PROFILE:command', {
                'event': 'openGroup',
                'type': 'response',
                'success': True
            })
            abrir_chromes_de_grupo(group, config)
        else:
            sio.emit('CHROME-PROFILE.CHROME-PROFILE:command', {
                'event': 'openGroup',
                'type': 'response',
                'success': False,
                'error': 'Nenhum grupo foi informado.'
            })
            print("Nenhum grupo foi informado.")
    
    # Responder ao pedido de criar grupo
    elif event_type == "createGroup" and data.get('type') == "request":
        group_name = data.get('value')
        if group_name:
            group_path = os.path.join(PASTA_PERFIS, group_name)
            
            if not os.path.exists(group_path):
                try:
                    # Criar a pasta do novo grupo
                    os.makedirs(group_path)
                    print(f"Grupo '{group_name}' criado em {group_path}.")
                    
                    # Abrir a pasta do novo grupo
                    os.startfile(group_path)
                    
                    sio.emit('CHROME-PROFILE.CHROME-PROFILE:command', {
                        'event': 'createGroup',
                        'type': 'response',
                        'success': True
                    })
                except Exception as e:
                    print(f"Erro ao criar o grupo '{group_name}': {e}")
                    sio.emit('CHROME-PROFILE.CHROME-PROFILE:command', {
                        'event': 'createGroup',
                        'type': 'response',
                        'success': False,
                        'error': str(e)
                    })
            else:
                print(f"O grupo '{group_name}' já existe.")
                sio.emit('CHROME-PROFILE.CHROME-PROFILE:command', {
                    'event': 'createGroup',
                    'type': 'response',
                    'success': False,
                    'error': 'O grupo já existe.'
                })
        else:
            sio.emit('CHROME-PROFILE.CHROME-PROFILE:command', {
                'event': 'createGroup',
                'type': 'response',
                'success': False,
                'error': 'Nenhum nome de grupo foi informado.'
            })
            print("Nenhum nome de grupo foi informado.")
@sio.on('*')
def handle1_command(evenv,data):
    print([evenv,data])

# Função para conectar ao servidor WebSocket
def conectar_servidor_websocket(url):
    try:
        print(f"Conectando ao servidor WebSocket em {url}...")
        sio.connect(url)
    except Exception as e:
        print(f"Erro ao conectar ao WebSocket: {e}")
