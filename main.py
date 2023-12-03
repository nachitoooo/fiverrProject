import tkinter as tk
from tkinter import messagebox, ttk
import time
import pywifi
from customtkinter import *
import threading
import psutil
import GPUtil
import platform
import subprocess
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from math import cos, sin, radians
from PIL import Image, ImageDraw, ImageTk


def show_error(message):
    messagebox.showerror("Error", message)

def create_wifi_status_label(root):
    wifi_status_label = tk.Label(root, text="Conectado", bg="green", fg="white", padx=10)
    wifi_status_label.place(relx=1, rely=0, anchor=tk.NE)
    return wifi_status_label

def monitor_wifi_status(wifi_status_label):
    while True:
        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]
        time.sleep(2)
        if iface.status() == pywifi.const.IFACE_CONNECTED:
            update_wifi_status(True, wifi_status_label)
        else:
            update_wifi_status(False, wifi_status_label)
def update_wifi_status(status, wifi_status_label):
    if status:
        wifi_status_label.config(text="Conectado", bg="lightgreen")
    else:
        wifi_status_label.config(text="Desconectado", bg="red")

def scan_wifi_networks():
    wifi_listbox.delete(0, tk.END)
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    time.sleep(2)
    scan_result = iface.scan_results()

    for result in scan_result:
        wifi_listbox.insert(tk.END, result.ssid)

def on_wifi_double_click(event):
    selected_index = wifi_listbox.nearest(event.y)
    selected_network = wifi_listbox.get(selected_index)
    show_password_dialog(selected_network)

def show_password_dialog(selected_network):
    password_dialog = CTkToplevel(root)
    password_dialog.title(f"Ingresar contraseña para {selected_network}")
    password_dialog.geometry("300x200")

    password_entry = CTkEntry(password_dialog, show="*", placeholder_text="Ingrese la contraseña", justify="center")
    password_entry.pack(pady=5)

    connect_button = CTkButton(password_dialog, text="Conectar a Wi-Fi", command=lambda: connect_to_wifi(selected_network, password_entry.get(), password_dialog, wifi_status_label))
    connect_button.pack(pady=10)

def connect_to_wifi(selected_network, password, password_dialog, wifi_status_label):
    if password:
        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]

        profile = pywifi.Profile()
        profile.ssid = selected_network
        profile.auth = pywifi.const.AUTH_ALG_OPEN
        profile.akm.append(pywifi.const.AKM_TYPE_WPA2PSK)
        profile.cipher = pywifi.const.CIPHER_TYPE_CCMP
        profile.key = password

        iface.remove_all_network_profiles()
        temp_profile = iface.add_network_profile(profile)

        iface.connect(temp_profile)

        time.sleep(5)

        if iface.status() == pywifi.const.IFACE_CONNECTED:
            messagebox.showinfo("Conexión exitosa.", f"Conectado a {selected_network}")
            update_wifi_status(True, wifi_status_label)
        else:
            show_error(selected_network)
            update_wifi_status(False, wifi_status_label)
    else:
        show_error("Por favor, ingrese la contraseña.")
        update_wifi_status(False, wifi_status_label)

        password_dialog.destroy()
        
def obtener_temperatura_cpu():
    try:
        if platform.system() == 'Windows':
            # Obtener la temperatura de la CPU en Windows usando WMIC
            result = subprocess.run(['wmic', 'cpu', 'get', 'Temperature'], capture_output=True)
            temperature_str = result.stdout.decode('utf-8').strip().split('\n')[-1].strip()
            if temperature_str:
                temperature = int(temperature_str) // 10  # Convertir de décimas de grado a grados Celsius
                return temperature
            else:
                return None
        elif platform.system() == 'Linux':
            # Obtener la temperatura de la CPU en Linux usando psutil
            temperatures = psutil.sensors_temperatures()
            cpu_temperature = temperatures.get('coretemp', [])
            if cpu_temperature and cpu_temperature[0].current:
                return cpu_temperature[0].current
            else:
                return None
    except Exception as e:
        show_error(f"Error al obtener temperatura de la CPU: {e}")
        return None
    
def obtener_telemetria():
    cpu_info = {
        "nucleos": psutil.cpu_count(logical=False),
        "porcentaje_general": psutil.cpu_percent(),
        "porcentaje_por_nucleo": psutil.cpu_percent(percpu=True),
        "temperatura_cpu": obtener_temperatura_cpu(),
    }

    # Obtener información de GPU
    gpu_info = {
    "porcentaje_trabajo": GPUtil.getGPUs()[0].load * 100,
    "frecuencia": GPUtil.getGPUs()[0].driver,  # Corregir aquí
    "temperatura_gpu": GPUtil.getGPUs()[0].temperature
}

    # Obtener información de RAM
    ram_info = {
        "uso": psutil.virtual_memory().used,
        "total": psutil.virtual_memory().total
    }

    # Obtener información de almacenamiento
    almacenamiento_info = {
    "interno": {
        "usado": psutil.disk_usage('C:/').used,  # Reemplaza 'C:/' con la letra de la unidad correcta en Windows
        "total": psutil.disk_usage('C:/').total
    },
    "sd": {
        "usado": 0,  # Cambia esto según la configuración real en tu sistema Windows
        "total": 0
    }
}

    # Obtener información adicional (reemplaza con tus propias funciones o módulos)
    return cpu_info, gpu_info, ram_info, almacenamiento_info




root = CTk()
root.title("Wi-Fi Escáner")
root.state('zoomed')
scan_button = CTkButton(root, text="Escanear redes Wi-FI", command=scan_wifi_networks)
scan_button.pack(pady=10)

scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL)
wifi_listbox = tk.Listbox(root, selectmode=tk.SINGLE, yscrollcommand=scrollbar.set, height=30, width=100, fg="white", bg="#171718", justify="center", font=("Helvetica", "12", "bold"))
wifi_listbox.pack(pady=10)
wifi_listbox.yview(tk.END)

wifi_status_label = create_wifi_status_label(root)
monitor_thread = threading.Thread(target=monitor_wifi_status, args=(wifi_status_label,), daemon=True)
monitor_thread.start()
class CTkToolbar(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.buttons = []

    def add_button(self, button):
        button.pack(side=tk.LEFT, padx=5)
        self.buttons.append(button)

main_toolbar = CTkToolbar(root, bg="#171718")
main_toolbar.pack(side=tk.TOP, fill=tk.X)

monitor_button = CTkButton(main_toolbar, text="Monitor")
storage_button = CTkButton(main_toolbar, text="Almacenamiento")
settings_button = CTkButton(main_toolbar, text="Configuración")

main_toolbar.add_button(monitor_button)
main_toolbar.add_button(storage_button)
main_toolbar.add_button(settings_button)

wifi_listbox.bind("<Double-Button-1>", on_wifi_double_click)


def mostrar_telemetria_tiempo_real():
    ventana_telemetria = tk.Toplevel(root)
    ventana_telemetria.title("Telemetría en Tiempo Real")
    ventana_telemetria.attributes('-fullscreen', True)
    ventana_telemetria.configure(bg='#2E2E2E')  # Fondo gris oscuro

    frames = []

    # Crear un frame para cada conjunto de etiquetas y porcentajes
    for idx, (label_text, data_key) in enumerate([
        ("Porcentaje CPU:", "porcentaje_general"),
        ("Porcentaje GPU:", "porcentaje_trabajo"),
        ("Uso de RAM:", "uso"),
        ("Uso de almacenamiento interno:", "interno_usado"),
        ("Porcentaje Batería:", "porcentaje_bateria"),
        ("Porcentaje Total:", "porcentaje_total"),
    ]):
        frame = tk.Frame(ventana_telemetria, bg='#0D2E3B')  # Fondo azul oscuro
        frame.grid(row=idx // 2, column=idx % 2, padx=10, pady=10, sticky='we')

        title_label = tk.Label(frame, text=label_text, font=('Helvetica', 18), fg='white', bg='#0D2E3B')  # Texto blanco, fondo azul oscuro
        title_label.pack(pady=(10, 5))  # Aumenté el espaciado superior

        value_label = tk.Label(frame, text="0%", font=('Helvetica', 18), fg='white', bg='#0D2E3B')  # Texto blanco, fondo azul oscuro
        value_label.pack(pady=(0, 10))  # Aumenté el espaciado inferior

        frames.append((value_label, data_key))

    # Configurar las columnas para centrar los elementos horizontalmente
    ventana_telemetria.columnconfigure(0, weight=1)
    ventana_telemetria.columnconfigure(1, weight=1)

    def actualizar_telemetria():
        telemetria = obtener_telemetria()

        porcentaje_general_cpu = telemetria[0]["porcentaje_general"]
        porcentaje_gpu = telemetria[1]["porcentaje_trabajo"]
        uso_ram = telemetria[2]["uso"]
        total_ram = telemetria[2]["total"]
        uso_almacenamiento_interno = telemetria[3]["interno"]["usado"]
        total_almacenamiento_interno = telemetria[3]["interno"]["total"]
        porcentaje_bateria = 50  # Reemplaza esto con la función para obtener el porcentaje de batería

        porcentaje_total = (porcentaje_general_cpu + porcentaje_gpu + (uso_ram / total_ram) * 100 +
                            (uso_almacenamiento_interno / total_almacenamiento_interno) * 100 + porcentaje_bateria) / 5

        frames[-1][0].config(text=f"{porcentaje_total:.2f}%")  # Actualizar "Porcentaje Total"

        for label, data_key in frames[:-1]:  # Excluir la última etiqueta ("Porcentaje Total")
            value = telemetria.get(data_key, "N/A")
            if isinstance(value, (int, float)):
                label.config(text=f"{value:.2f}%")
            else:
                label.config(text=str(value))

        ventana_telemetria.after(1000, actualizar_telemetria)

    actualizar_telemetria()

    ventana_telemetria.mainloop()

tiempo_real_button = CTkButton(main_toolbar, text="Telemetría en Tiempo Real", command=mostrar_telemetria_tiempo_real)
main_toolbar.add_button(tiempo_real_button)
root.mainloop()