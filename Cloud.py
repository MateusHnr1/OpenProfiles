import os
import subprocess
import time
import json
import pygetwindow as gw
import win32gui
import win32con
import win32api

# Função para criar um arquivo de configuração padrão se não existir
def criar_configuracao_padrao():
    config_padrao = {
        "url": "https://bartio.faucet.berachain.com/",
        "pasta_perfis": "./perfis",
        "full_screen": False,  # Parâmetro para definir se os Chromes devem ser abertos em tela cheia
        "delay_antes_login": 20  # Parâmetro para definir o tempo de delay antes do login
    }
    with open('config.json', 'w') as config_file:
        json.dump(config_padrao, config_file, indent=4)
    print("Arquivo de configuração 'config.json' criado com valores padrão.")

# Carrega as configurações do arquivo config.json
def carregar_configuracao():
    if not os.path.exists('config.json'):
        criar_configuracao_padrao()
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

config = carregar_configuracao()

# Obtém uma lista de janelas do Chrome abertas
def listar_chromes_abertos():
    janelas_chrome = [janela for janela in gw.getWindowsWithTitle("Chrome")]
    return janelas_chrome

# Função para enviar "Enter" para uma lista de janelas
def enviar_enter_para_janelas(janelas):
    for janela in janelas:
        print(f"Enviando 'Enter' para a janela: {janela.title} (Handle: {janela._hWnd})")
        # Traz a janela para o primeiro plano e envia a tecla 'Enter'
        win32gui.ShowWindow(janela._hWnd, win32con.SW_RESTORE)  # Restaura a janela se estiver minimizada
        win32gui.SetForegroundWindow(janela._hWnd)  # Traz a janela para o foco
        win32api.SendMessage(janela._hWnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
        win32api.SendMessage(janela._hWnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)

# Função para fechar a janela de restauração de páginas, se necessário
def fechar_janela_restaurar():
    print("Verificando a janela 'Restaurar páginas' e fechando se necessário...")
    janelas = gw.getAllWindows()
    for janela in janelas:
        if 'restaurar páginas' in janela.title.lower():
            print(f"Janela de 'Restaurar páginas' encontrada: {janela.title} - Fechando...")
            win32gui.ShowWindow(janela._hWnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(janela._hWnd)
            win32api.SendMessage(janela._hWnd, win32con.WM_CLOSE, 0, 0)
            print("Janela de restauração fechada.")

# Função para maximizar janelas de Chrome em tela cheia se configurado
def maximizar_janelas_chrome(janelas):
    if config.get('full_screen', False):  # Verifica se o parâmetro full_screen está ativo
        for janela in janelas:
            print(f"Maximizando a janela: {janela.title}")
            win32gui.ShowWindow(janela._hWnd, win32con.SW_MAXIMIZE)

# Função principal para abrir novos Chromes e enviar Enter
def abrir_chromes_com_perfis():
    # Lista de janelas do Chrome abertas antes da execução
    chromes_antes = listar_chromes_abertos()
    print(f"Total de Chromes abertos antes da execução: {len(chromes_antes)}")

    # Obtém o caminho para o diretório dos perfis a partir da configuração
    pasta_perfis = os.path.abspath(config['pasta_perfis'])
    print(f"Procurando atalhos de perfis na pasta: {pasta_perfis}")

    # Lista todos os atalhos (.lnk) na pasta
    arquivos_na_pasta = os.listdir(pasta_perfis)
    atalhos_perfis = sorted([arquivo for arquivo in arquivos_na_pasta if arquivo.endswith(".lnk")])

    if not atalhos_perfis:
        print(f"Nenhum atalho de perfil encontrado na pasta: {pasta_perfis}")
        return

    url = config['url']
    processos = []

    # Para cada atalho, abre o Chrome com o perfil correspondente
    for atalho in atalhos_perfis:
        caminho_atalho = os.path.join(pasta_perfis, atalho)
        print(f"Abrindo o perfil: {atalho}")
        subprocess.Popen(f'start "" "{caminho_atalho}" {url}', shell=True)
        processos.append(caminho_atalho)

    # Aguarda o tempo de delay configurado antes de enviar Enter
    delay = config.get("delay_antes_login", 10)  # Pega o valor do delay nas configurações
    print(f"Aguardando {delay} segundos antes de enviar 'Enter'.")
    time.sleep(delay)

    # Fecha a janela de restauração, se necessário
    fechar_janela_restaurar()

    # Lista de janelas do Chrome abertas após a execução
    chromes_depois = listar_chromes_abertos()
    print(f"Total de Chromes abertos após a execução: {len(chromes_depois)}")

    # Obtém a diferença entre os Chromes abertos antes e depois, ou seja, os novos Chromes abertos
    novos_chromes = [janela for janela in chromes_depois if janela not in chromes_antes]
    print(f"Total de novos Chromes abertos: {len(novos_chromes)}")

    # Envia 'Enter' para todos os novos Chromes
    enviar_enter_para_janelas(novos_chromes)

    # Maximiza as novas janelas de Chrome em full screen, se configurado
    maximizar_janelas_chrome(novos_chromes)

# Executa diretamente para abrir os perfis simultaneamente
abrir_chromes_com_perfis()
