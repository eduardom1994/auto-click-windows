import threading
import time
import tkinter as tk
from tkinter import messagebox

import pyautogui
from pynput import keyboard

pyautogui.FAILSAFE = False


class AutoClicker:
    def __init__(self, master):
        self.master = master
        master.title("Click Auto - simples")

        tk.Label(master, text="Intervalo (s):").grid(row=0, column=0, padx=6, pady=6)
        self.interval_var = tk.StringVar(value="1.0")
        tk.Entry(master, textvariable=self.interval_var, width=10).grid(row=0, column=1, padx=6, pady=6)

        self.pos_label = tk.Label(master, text="Pos: não definida")
        self.pos_label.grid(row=1, column=0, columnspan=2, padx=6)

        tk.Button(master, text="Definir posição (usar mouse atual)", command=self.set_position).grid(
            row=2, column=0, columnspan=2, sticky="we", padx=6, pady=6
        )

        self.follow_var = tk.BooleanVar(value=False)
        tk.Checkbutton(master, text="Seguir mouse (usar posição atual a cada clique)", variable=self.follow_var).grid(
            row=3, column=0, columnspan=2, sticky="w", padx=6
        )

        self.start_btn = tk.Button(master, text="Iniciar", command=self.start)
        self.start_btn.grid(row=4, column=0, padx=6, pady=6)

        self.stop_btn = tk.Button(master, text="Parar", command=self.stop, state=tk.DISABLED)
        self.stop_btn.grid(row=4, column=1, padx=6, pady=6)

        self.status_label = tk.Label(master, text="Parado", fg="red")
        self.status_label.grid(row=4, column=0, columnspan=2, padx=6, pady=6)

        self._thread = None
        self._running = threading.Event()
        self._paused = threading.Event()
        self._hotkeys = None
        self._hotkeys_started = False
        self.position = None

        # mostrar atalhos
        tk.Label(master, text="Hotkeys: F8 = Pausar/Retomar  |  F9 = Definir posição atual").grid(
            row=5, column=0, columnspan=2, padx=6, pady=(4,8)
        )

        # iniciar listener de hotkeys (global) e também binding local como fallback
        try:
            self._hotkeys = keyboard.GlobalHotKeys({
                '<f8>': self._on_hotkey_pause,
                '<f9>': self._on_hotkey_setpos,
            })
            self._hotkeys.start()
            self._hotkeys_started = True
        except Exception:
            # falha no hotkey listener: não crítico, avisamos via label
            tk.Label(master, text="(Hotkeys globais não disponíveis)", fg="orange").grid(row=6, column=0, columnspan=2)

        # bindings locais (funcionam quando a janela tem foco)
        master.bind('<F8>', lambda e: self._on_hotkey_pause())
        master.bind('<F9>', lambda e: self._on_hotkey_setpos())

    def set_position(self):
        x, y = pyautogui.position()
        self.position = (x, y)
        self.pos_label.config(text=f"Pos: {x}, {y}")

    def _on_hotkey_setpos(self):
        # chamado pelo listener de hotkeys ou binding local
        # agendamos no thread principal para evitar chamadas Tkinter de threads em background
        try:
            self.master.after(0, self.set_position)
        except Exception:
            pass

    def _on_hotkey_pause(self):
        # só faz sentido se o worker estiver em execução
        if not self._running.is_set():
            return
        if self._paused.is_set():
            self._paused.clear()
            try:
                self.master.after(0, lambda: self.status_label.config(text="Executando", fg="green"))
            except Exception:
                pass
        else:
            self._paused.set()
            try:
                self.master.after(0, lambda: self.status_label.config(text="Pausado", fg="orange"))
            except Exception:
                pass

    def on_key_pause(self, event=None):
        # binding local usa este wrapper
        self._on_hotkey_pause()

    def on_key_setpos(self, event=None):
        self._on_hotkey_setpos()

    def start(self):
        try:
            interval = float(self.interval_var.get())
            if interval <= 0:
                raise ValueError()
        except Exception:
            messagebox.showerror("Erro", "Intervalo inválido. Use número > 0")
            return

        if self.position is None:
            if not messagebox.askyesno("Confirmar", "Posição não definida: usar posição atual do mouse agora?"):
                return
            self.set_position()

        self._running.set()
        self._thread = threading.Thread(target=self._worker, args=(interval,), daemon=True)
        self._thread.start()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Executando", fg="green")

    def toggle_pause(self):
        # API pública para alternar pausa
        self._on_hotkey_pause()

    def stop(self):
        self._running.clear()
        self._paused.clear()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Parado", fg="red")

    def _on_close(self):
        # garantir que o listener seja parado
        try:
            if self._hotkeys_started and self._hotkeys is not None:
                self._hotkeys.stop()
        except Exception:
            pass
        self.master.destroy()

    def _worker(self, interval):
        while self._running.is_set():
            if self._paused.is_set():
                time.sleep(0.1)
                continue

            try:
                if self.follow_var.get():
                    x, y = pyautogui.position()
                else:
                    if self.position is None:
                        # sem posição definida, captura a atual
                        x, y = pyautogui.position()
                        self.position = (x, y)
                        self.pos_label.config(text=f"Pos: {x}, {y}")
                    else:
                        x, y = self.position

                pyautogui.click(x, y)
            except Exception:
                # Se ocorrer qualquer erro ao clicar, paramos para evitar loops incontroláveis
                self._running.clear()
                break

            time.sleep(interval)


def main():
    root = tk.Tk()
    app = AutoClicker(root)
    root.protocol("WM_DELETE_WINDOW", app._on_close)
    root.resizable(False, False)
    root.mainloop()


if __name__ == "__main__":
    main()
