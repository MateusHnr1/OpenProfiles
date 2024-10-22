# src/window_manager.py
import pygetwindow as gw
import win32gui
import win32con
import win32api

# Obtém uma lista de janelas do Chrome abertas
def listar_chromes_abertos():
    return [janela for janela in gw.getWindowsWithTitle("Chrome")]

# Envia "Enter" para uma lista de janelas
def enviar_enter_para_janelas(janelas):
    for janela in janelas:
        print(f"Enviando 'Enter' para a janela: {janela.title} (Handle: {janela._hWnd})")
        win32gui.ShowWindow(janela._hWnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(janela._hWnd)
        win32api.SendMessage(janela._hWnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
        win32api.SendMessage(janela._hWnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)

# Fecha a janela de restauração de páginas, se necessário
def fechar_janela_restaurar():
    print("Verificando a janela 'Restaurar páginas' e fechando se necessário...")
    for janela in gw.getAllWindows():
        if 'restaurar páginas' in janela.title.lower():
            print(f"Fechando janela de restauração: {janela.title}")
            win32gui.ShowWindow(janela._hWnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(janela._hWnd)
            win32api.SendMessage(janela._hWnd, win32con.WM_CLOSE, 0, 0)

# Maximiza as janelas se configurado para full screen
def maximizar_janelas_chrome(janelas, full_screen):
    if full_screen:
        for janela in janelas:
            print(f"Maximizando a janela: {janela.title}")
            win32gui.ShowWindow(janela._hWnd, win32con.SW_MAXIMIZE)
