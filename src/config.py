# src/config.py
import os
import json

CONFIG_FILE = 'config.json'

# Função para criar um arquivo de configuração padrão se não existir
def criar_configuracao_padrao():
    config_padrao = {
        "url": "https://bartio.faucet.berachain.com/",
        "full_screen": False,  # Define se os Chromes devem ser abertos em tela cheia
        "delay_antes_login": 20  # Tempo de delay antes do login
    }
    with open(CONFIG_FILE, 'w') as config_file:
        json.dump(config_padrao, config_file, indent=4)
    print(f"Arquivo de configuração '{CONFIG_FILE}' criado com valores padrão.")

# Carrega as configurações do arquivo config.json ou cria um novo
def carregar_configuracao():
    if not os.path.exists(CONFIG_FILE):
        criar_configuracao_padrao()
    with open(CONFIG_FILE, 'r') as config_file:
        return json.load(config_file)
