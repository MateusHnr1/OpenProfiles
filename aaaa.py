import os
import subprocess
import time
import json
import pygetwindow as gw
import win32gui
import win32con
import win32api
import pywinauto
from pywinauto.application import Application

# Função para criar um arquivo de configuração padrão se não existir
def criar_configuracao_padrao():
    config_padrao = {
        "url": "https://bartio.faucet.berachain.com/",
        "pasta_perfis": "./perfis",
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

# Mantém o controle dos PIDs que já receberam "Enter"
pids_com_enter = set()

def enviar_enter_para_janelas():
    # Envia 'Enter' diretamente para as janelas do Chrome, sem procurar campos de login
    janelas = gw.getAllWindows()  # Lista todas as janelas abertas
    print("Janelas detectadas:")

    # Exibe todas as janelas detectadas e seus títulos para depuração
    for janela in janelas:
        print(f"Janela: {janela.title} - PID (Handle): {janela._hWnd}")

    # Tentativa de identificar janelas do Chrome com "bartio.faucet.berachain.com" no título
    for janela in janelas:
        pid = janela._hWnd  # Usa o handle da janela como identificador do processo

        # Verifica se o título contém "bartio.faucet.berachain.com" e se o PID já foi processado
        if pid not in pids_com_enter and 'bartio.faucet.berachain.com' in janela.title.lower():
            print(f"Enviando 'Enter' para a janela: {janela.title} (PID: {pid})")

            # Traz a janela para o primeiro plano e envia a tecla 'Enter'
            win32gui.ShowWindow(janela._hWnd, win32con.SW_RESTORE)  # Restaura a janela se estiver minimizada
            win32gui.SetForegroundWindow(janela._hWnd)  # Traz a janela para o foco

            # Envia a tecla 'Enter' diretamente para a janela
            win32api.SendMessage(janela._hWnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
            win32api.SendMessage(janela._hWnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)

            pids_com_enter.add(pid)  # Marca o PID como processado

    # Exibe todos os PIDs que já receberam o 'Enter'
    print(f"Total de janelas que receberam 'Enter': {len(pids_com_enter)}")
    print(f"PIDs processados: {pids_com_enter}")

def fechar_janela_restaurar():
    print("Verificando a janela 'Restaurar páginas' e fechando se necessário...")
    janelas = gw.getAllWindows()

    for janela in janelas:
        if 'restaurar páginas' in janela.title.lower():
            print(f"Janela de 'Restaurar páginas' encontrada: {janela.title} - Fechando...")
            # Traz a janela de restauração para frente e fecha ela
            win32gui.ShowWindow(janela._hWnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(janela._hWnd)
            win32api.SendMessage(janela._hWnd, win32con.WM_CLOSE, 0, 0)
            print("Janela de restauração fechada.")

def abrir_chromes_com_perfis():
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

    # Para cada atalho, abre o Chrome com o perfil correspondente, sem espera
    for atalho in atalhos_perfis:
        caminho_atalho = os.path.join(pasta_perfis, atalho)
        print(f"Abrindo o perfil: {atalho}")

        # Comando para abrir o atalho do Chrome com a URL desejada
        processo = subprocess.Popen(f'start "" "{caminho_atalho}" {url}', shell=True)
        processos.append(processo)  # Armazena o processo para controle do PID

    # Aguarda 10 segundos para garantir que as janelas do Chrome foram abertas
    time.sleep(10)

    # Fecha a janela de restauração, se necessário
    fechar_janela_restaurar()

    # Envia 'Enter' para todas as janelas de login de proxy, sem intervalos
    print("Enviando 'Enter' para todas as janelas de login.")
    enviar_enter_para_janelas()

    # Após o envio do Enter para todas as janelas, agora maximiza as janelas
    maximizar_janelas_chrome()

    # Espera 20 segundos após os logins para o carregamento das páginas
    print("Aguardando 20 segundos para carregamento completo das páginas...")
    time.sleep(20)

    # Após o carregamento, podemos verificar a caixa do Cloudflare
    verificar_caixa_cloudflare()

def maximizar_janelas_chrome():
    # Verifica as janelas abertas e maximiza as que contêm "bartio.faucet.berachain.com"
    janelas = gw.getWindowsWithTitle("Chrome")
    for janela in janelas:
        if 'bartio.faucet.berachain.com' in janela.title.lower():
            print(f"Maximizando a janela: {janela.title}")
            win32gui.ShowWindow(janela._hWnd, win32con.SW_MAXIMIZE)

def verificar_caixa_cloudflare():
    print("Verificando a caixa do Cloudflare nas janelas abertas.")
    janelas = gw.getAllWindows()
    for janela in janelas:
        if 'bartio.faucet.berachain.com' in janela.title.lower():
            print(f"Interagindo com a janela: {janela.title}")
            app = Application().connect(handle=janela._hWnd)
            window = app.window(handle=janela._hWnd)

            try:
                # Verificar a existência do checkbox de captcha e clicar
                window.click_input(coords=(600, 700))  # Ajustar conforme a posição do CAPTCHA
                print(f"Caixa do Cloudflare clicada com sucesso na janela {janela.title}")
            except Exception as e:
                print(f"Não foi possível clicar no CAPTCHA. Erro: {e}")

# Executa diretamente para abrir os perfis simultaneamente
abrir_chromes_com_perfis()
