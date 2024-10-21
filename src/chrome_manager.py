import os
import subprocess
import time
from window_manager import fechar_janela_restaurar, listar_chromes_abertos, enviar_enter_para_janelas, maximizar_janelas_chrome

# Caminho fixo para a pasta de perfis
PASTA_PERFIS = "C:\\WSAction\\Perfis"

# Função para listar os grupos na pasta de perfis
def listar_grupos():
    """
    Lista todas as subpastas (grupos) presentes na pasta de perfis.
    
    Returns:
        list: Lista de nomes dos grupos encontrados na pasta de perfis.
    """
    if not os.path.exists(PASTA_PERFIS):
        print(f"A pasta de perfis {PASTA_PERFIS} não existe.")
        return []

    # Lista todas as subpastas (grupos) dentro da pasta de perfis
    grupos = [nome_grupo for nome_grupo in os.listdir(PASTA_PERFIS) if os.path.isdir(os.path.join(PASTA_PERFIS, nome_grupo))]
    
    print(f"Grupos encontrados: {grupos}")
    return grupos


# Função principal para abrir novos Chromes e enviar Enter
def abrir_chromes_com_perfis(config):
    chromes_antes = listar_chromes_abertos()
    print(f"Total de Chromes abertos antes da execução: {len(chromes_antes)}")

    # Obtém os grupos (subpastas) na pasta de perfis
    grupos = listar_grupos()

    if not grupos:
        print(f"Nenhum grupo encontrado na pasta de perfis: {PASTA_PERFIS}")
        return

    url = config['url']

    for grupo in grupos:
        caminho_grupo = os.path.join(PASTA_PERFIS, grupo)
        print(f"Procurando perfis no grupo: {grupo}")

        atalhos_perfis = sorted([arquivo for arquivo in os.listdir(caminho_grupo) if arquivo.endswith(".lnk")])

        if not atalhos_perfis:
            print(f"Nenhum atalho de perfil encontrado no grupo: {grupo}")
            continue

        # Para cada atalho, abre o Chrome com o perfil correspondente
        for atalho in atalhos_perfis:
            caminho_atalho = os.path.join(caminho_grupo, atalho)
            print(f"Abrindo o perfil: {atalho} no grupo: {grupo}")
            subprocess.Popen(f'start "" "{caminho_atalho}" {url}', shell=True)

    delay = config.get("delay_antes_login", 10)
    print(f"Aguardando {delay} segundos antes de enviar 'Enter'.")
    time.sleep(delay)

    fechar_janela_restaurar()

    chromes_depois = listar_chromes_abertos()
    print(f"Total de Chromes abertos após a execução: {len(chromes_depois)}")

    novos_chromes = [janela for janela in chromes_depois if janela not in chromes_antes]
    print(f"Total de novos Chromes abertos: {len(novos_chromes)}")

    enviar_enter_para_janelas(novos_chromes)
    maximizar_janelas_chrome(novos_chromes, config.get('full_screen', False))
