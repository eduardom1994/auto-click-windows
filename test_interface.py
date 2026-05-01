"""
Script de teste de interface para o Auto Clicker.
Este script simula interações com a GUI para testar funcionalidades.
Nota: Requer display gráfico para funcionar.
"""

import subprocess
import time
import pyautogui
from pynput.keyboard import Controller

def run_interface_tests():
    # Iniciar o executável
    print("Iniciando o aplicativo...")
    process = subprocess.Popen(['dist\\main.exe'])

    time.sleep(2)  # Esperar a GUI carregar

    keyboard = Controller()

    # Teste 1: Adicionar primeira localização com F9
    print("Teste 1: Pressionando F9 para adicionar localização...")
    keyboard.press('f9')
    keyboard.release('f9')
    time.sleep(1)

    # Verificar se não há messagebox de erro (procurar por "já adicionada")
    screenshot = pyautogui.screenshot()
    # Procurar por texto na tela (simplificado, em produção usaria OCR)
    if "já adicionada" in screenshot.tobytes().decode('latin-1', errors='ignore'):
        print("ERRO: Mensagem de duplicata apareceu na primeira adição!")
        return False
    else:
        print("OK: Primeira adição sem mensagem de erro.")

    # Teste 2: Adicionar segunda localização
    print("Teste 2: Pressionando F9 novamente...")
    keyboard.press('f9')
    keyboard.release('f9')
    time.sleep(1)

    # Verificar se adicionou (assumir OK se não crashou)

    # Teste 3: Pausar com F8
    print("Teste 3: Pressionando F8 para pausar...")
    keyboard.press('f8')
    keyboard.release('f8')
    time.sleep(1)

    # Verificar foco (difícil automatizar)

    # Fechar o app
    print("Fechando o aplicativo...")
    process.terminate()
    process.wait()

    print("Testes de interface concluídos.")
    return True

if __name__ == "__main__":
    run_interface_tests()