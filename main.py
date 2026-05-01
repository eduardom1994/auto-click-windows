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
        master.title("Click Auto - locais")

        tk.Label(master, text="Intervalo padrão (s):").grid(row=0, column=0, padx=6, pady=6)
        self.default_interval_var = tk.StringVar(value="1.0")
        tk.Entry(master, textvariable=self.default_interval_var, width=10).grid(row=0, column=1, padx=6, pady=6)

        tk.Label(master, text="Intervalo local (s):").grid(row=1, column=0, padx=6, pady=6)
        self.local_interval_var = tk.StringVar(value="1.0")
        tk.Entry(master, textvariable=self.local_interval_var, width=10).grid(row=1, column=1, padx=6, pady=6)

        tk.Button(master, text="Adicionar local atual", command=self.add_location).grid(
            row=2, column=0, columnspan=2, sticky="we", padx=6, pady=6
        )

        self.locations_listbox = tk.Listbox(master, height=6, width=40)
        self.locations_listbox.grid(row=3, column=0, columnspan=2, padx=6)

        tk.Button(master, text="Remover", command=self.remove_location).grid(row=4, column=0, padx=6, pady=(6, 2))
        tk.Button(master, text="Limpar lista", command=self.clear_locations).grid(row=4, column=1, padx=6, pady=(6, 2))

        self.locations_label = tk.Label(master, text="Locais: 0")
        self.locations_label.grid(row=5, column=0, columnspan=2, padx=6, pady=(0, 6))

        self.start_btn = tk.Button(master, text="Iniciar", command=self.start)
        self.start_btn.grid(row=6, column=0, padx=6, pady=6)

        self.stop_btn = tk.Button(master, text="Parar", command=self.stop, state=tk.DISABLED)
        self.stop_btn.grid(row=6, column=1, padx=6, pady=6)

        self.status_label = tk.Label(master, text="Parado", fg="red")
        self.status_label.grid(row=7, column=0, columnspan=2, padx=6, pady=6)

        self._thread = None
        self._running = threading.Event()
        self._paused = threading.Event()
        self._hotkeys = None
        self._hotkeys_started = False
        self.locations = []
        self.adding = False

        tk.Label(master, text="Hotkeys: F8 = Pausar/Retomar  |  F9 = Adicionar local atual").grid(
            row=8, column=0, columnspan=2, padx=6, pady=(4, 8)
        )

        try:
            self._hotkeys = keyboard.GlobalHotKeys({
                '<f8>': self._on_hotkey_pause,
                '<f9>': self._on_hotkey_add_location,
            })
            self._hotkeys.start()
            self._hotkeys_started = True
        except Exception:
            tk.Label(master, text="(Hotkeys globais não disponíveis)", fg="orange").grid(row=9, column=0, columnspan=2)

        master.bind('<F8>', lambda e: self._on_hotkey_pause())
        master.bind('<F9>', lambda e: self._on_hotkey_add_location())

    def update_locations_listbox(self):
        self.locations_listbox.delete(0, tk.END)
        for index, (x, y, interval) in enumerate(self.locations, start=1):
            if interval is None:
                label = f"{index}. {x}, {y}  @ padrão"
            else:
                label = f"{index}. {x}, {y}  @ {interval:.2f}s"
            self.locations_listbox.insert(tk.END, label)
        self.locations_label.config(text=f"Locais: {len(self.locations)}")

    def add_location(self):
        if self.adding:
            return
        self.adding = True

        x, y = pyautogui.position()
        interval_text = self.local_interval_var.get().strip()
        interval = None

        if interval_text:
            try:
                interval = float(interval_text)
                if interval <= 0:
                    raise ValueError()
            except Exception:
                messagebox.showerror("Erro", "Intervalo local inválido. Use número > 0 ou deixe vazio para usar o padrão.")
                self.adding = False
                return

        self.locations.append((x, y, interval))
        self.update_locations_listbox()
        self.adding = False

    def remove_location(self):
        selection = self.locations_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        del self.locations[index]
        self.update_locations_listbox()

    def clear_locations(self):
        self.locations = []
        self.update_locations_listbox()

    def _on_hotkey_add_location(self):
        try:
            self.master.after(0, self.add_location)
        except Exception:
            pass

    def _on_hotkey_pause(self):
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
                self.master.after(0, lambda: self.master.focus_force())  # Focar a janela ao pausar
            except Exception:
                pass

    def on_key_pause(self, event=None):
        self._on_hotkey_pause()

    def on_key_add_location(self, event=None):
        self._on_hotkey_add_location()

    def start(self):
        try:
            default_interval = float(self.default_interval_var.get())
            if default_interval <= 0:
                raise ValueError()
        except Exception:
            messagebox.showerror("Erro", "Intervalo padrão inválido. Use número > 0")
            return

        if not self.locations:
            if not messagebox.askyesno("Confirmar", "Nenhum local adicionado. Usar posição atual como local único?"):
                return
            self.add_location()

        self._running.set()
        self._thread = threading.Thread(target=self._worker, args=(default_interval,), daemon=True)
        self._thread.start()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Executando", fg="green")

    def toggle_pause(self):
        self._on_hotkey_pause()

    def stop(self):
        self._running.clear()
        self._paused.clear()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Parado", fg="red")

    def _on_close(self):
        try:
            if self._hotkeys_started and self._hotkeys is not None:
                self._hotkeys.stop()
        except Exception:
            pass
        self.master.destroy()

    def _worker(self, default_interval):
        index = 0
        while self._running.is_set():
            if self._paused.is_set():
                time.sleep(0.1)
                continue

            if not self.locations:
                self._running.clear()
                break

            try:
                x, y, interval = self.locations[index]
                pyautogui.click(x, y)
            except Exception:
                self._running.clear()
                break

            actual_sleep = interval if interval is not None else default_interval
            time.sleep(actual_sleep)
            index = (index + 1) % len(self.locations)


def main():
    root = tk.Tk()
    app = AutoClicker(root)
    root.protocol("WM_DELETE_WINDOW", app._on_close)
    root.resizable(False, False)
    root.mainloop()


if __name__ == "__main__":
    main()
