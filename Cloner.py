import tkinter as tk
from tkinter import filedialog, messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import os
import json
import threading
import time

# Caminho para o arquivo de configuração
CONFIG_FILE = 'cloner_config.json'

# Cores e Estilos
COR_PRIMARIA = '#333333'  # Cor escura para texto
COR_SECUNDARIA = '#ffffff'  # Cor clara para fundo
COR_DESTAQUE = '#4CAF50'  # Cor de destaque
FONTE_PADRAO = ('Arial', 10)
FONTE_DESTAQUE = ('Arial', 10, 'bold')

class Watcher:
    def __init__(self, source_folder, destination_folder, status_label):
        self.observer = Observer()
        self.source_folder = source_folder
        self.destination_folder = destination_folder
        self.status_label = status_label
        self.event_handler = Handler(self.source_folder, self.destination_folder)

    def run(self):
        self.observer.schedule(self.event_handler, self.source_folder, recursive=True)
        self.observer.start()
        self.update_status("Monitoramento Ativo")

    def stop(self):
        self.observer.stop()
        self.observer.join()
        self.update_status("Monitoramento Parado")

    def update_status(self, status):
        if status == "Monitoramento Ativo":
            self.status_label.config(text=status, fg='green')
            start_button.grid_remove()
            stop_button.grid(row=2, column=0, padx=5, pady=5, sticky='ew')
        elif status == "Monitoramento Parado":
            self.status_label.config(text=status, fg='red')
            stop_button.grid_remove()
            start_button.grid(row=2, column=0, padx=5, pady=5, sticky='ew')

class Handler(FileSystemEventHandler):
    def __init__(self, source_folder, destination_folder):
        self.source_folder = source_folder
        self.destination_folder = destination_folder

    def on_any_event(self, event):
        if event.is_directory:
            return None

        source_path = event.src_path
        dest_path = source_path.replace(self.source_folder, self.destination_folder)

        if event.event_type in ['created', 'modified']:
            self.try_copy(source_path, dest_path)
        elif event.event_type == 'deleted':
            if os.path.exists(dest_path):
                os.remove(dest_path)

    def try_copy(self, source, destination, attempts=5, delay=1):
        """Tenta copiar um arquivo, com um número definido de tentativas e atraso entre elas."""
        for _ in range(attempts):
            try:
                shutil.copy2(source, destination)
                break
            except PermissionError:
                time.sleep(delay)

watcher = None

def start_watcher():
    global watcher
    source_path = source_entry.get()
    destination_path = destination_entry.get()
    save_config(source_path, destination_path)
    watcher = Watcher(source_path, destination_path, status_label)
    threading.Thread(target=watcher.run).start()

def stop_watcher():
    global watcher
    if watcher:
        watcher.stop()
        watcher = None

def select_source_folder():
    folder_selected = filedialog.askdirectory()
    source_entry.delete(0, tk.END)
    source_entry.insert(0, folder_selected)

def select_destination_folder():
    folder_selected = filedialog.askdirectory()
    destination_entry.delete(0, tk.END)
    destination_entry.insert(0, folder_selected)

def save_config(source_path, destination_path):
    with open(CONFIG_FILE, 'w') as file:
        json.dump({'source': source_path, 'destination': destination_path}, file)

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
            return config['source'], config['destination']
    except (FileNotFoundError, json.JSONDecodeError):
        return None, None

app = tk.Tk()
app.title("Cloner")
app.configure(bg=COR_SECUNDARIA)

frame = tk.Frame(app, bg=COR_SECUNDARIA)
frame.pack(padx=10, pady=10, fill='both', expand=True)

source_label = tk.Label(frame, text="Pasta de Origem:", fg=COR_PRIMARIA, bg=COR_SECUNDARIA, font=FONTE_PADRAO)
source_label.grid(row=0, column=0, sticky="w")
source_entry = tk.Entry(frame, width=50, font=FONTE_PADRAO)
source_entry.grid(row=0, column=1, padx=5, pady=5)
source_button = tk.Button(frame, text="Selecionar", command=select_source_folder, font=FONTE_PADRAO)
source_button.grid(row=0, column=2)

destination_label = tk.Label(frame, text="Pasta de Destino:", fg=COR_PRIMARIA, bg=COR_SECUNDARIA, font=FONTE_PADRAO)
destination_label.grid(row=1, column=0, sticky="w")
destination_entry = tk.Entry(frame, width=50, font=FONTE_PADRAO)
destination_entry.grid(row=1, column=1, padx=5, pady=5)
destination_button = tk.Button(frame, text="Selecionar", command=select_destination_folder, font=FONTE_PADRAO)
destination_button.grid(row=1, column=2)

start_button = tk.Button(frame, text="Iniciar Monitoramento", command=start_watcher, font=FONTE_PADRAO)
start_button.grid(row=2, column=0, padx=5, pady=5, sticky='ew')

stop_button = tk.Button(frame, text="Parar Monitoramento", command=stop_watcher, font=FONTE_PADRAO)
# Inicialmente, o botão Parar Monitoramento não será exibido

status_label = tk.Label(app, text="Monitoramento Inativo", fg='red', bg=COR_SECUNDARIA, font=FONTE_DESTAQUE)
status_label.pack(side="bottom", fill=tk.X, padx=10, pady=5)

footer_label = tk.Label(app, text="Criado por Waldir Donatti Junior", fg=COR_PRIMARIA, bg=COR_SECUNDARIA, font=FONTE_PADRAO)
footer_label.pack(side="bottom", fill=tk.X, padx=10, pady=5)

# Carregar configurações salvas
saved_source, saved_destination = load_config()
if saved_source and saved_destination:
    source_entry.insert(0, saved_source)
    destination_entry.insert(0, saved_destination)

app.mainloop()
