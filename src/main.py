# src/main.py
from config import carregar_configuracao
from websocket_client import conectar_servidor_websocket
import socketio
import time

# Carregar a configuração local
config = carregar_configuracao()

# Servidor WebSocket para conectar
servidor_websocket = "http://localhost:9514"

# Conectar ao servidor WebSocket
conectar_servidor_websocket(servidor_websocket)

# Manter o programa rodando
socketio.Client().wait()
# Adicionando um loop para manter o cliente rodando e verificando mensagens
try:
    while True:
        time.sleep(5)  # Aguarda 5 segundos e depois imprime novamente (para debug)
except KeyboardInterrupt:
    print("Cliente WebSocket interrompido.")
finally:
    socketio.Client().disconnect()
