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
import clr  # Import the pythonnet clr module
clr.AddReference('OpenHardwareMonitorLib')
from OpenHardwareMonitor import Hardware


def get_cpu_temperatures():
    handle = Hardware.Computer()
    handle.CPUEnabled = True 
    handle.Open()  #
    temperature_data = []

    for hardware_item in handle.Hardware:
        hardware_item.Update()  # Update the hardware data
        if hardware_item.HardwareType == Hardware.HardwareType.CPU:
            for sensor in hardware_item.Sensors:
                if sensor.SensorType == Hardware.SensorType.Temperature:
                    temperature_data.append((sensor.Name, sensor.Value))

    handle.Close()  
    return temperature_data



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
        



    
def obtener_telemetria():
    cpu_temperatures = get_cpu_temperatures()

    cpu_info = {
        "nucleos": psutil.cpu_count(logical=False),
        "porcentaje_general": psutil.cpu_percent(),
        "porcentaje_por_nucleo": psutil.cpu_percent(percpu=True),
        "temperaturas_cpu": dict(cpu_temperatures),
    }

    try:
        gpu = GPUtil.getGPUs()[0]
        gpu_info = {
            "porcentaje_trabajo": gpu.load * 100,
            "frecuencia": getattr(gpu, 'memoryInfo', {}).get(0, "No disponible"),  # Assuming core frequency is stored at index 0
        }

    except Exception as e:
        gpu_info = {
            "porcentaje_trabajo": "No disponible",
            "frecuencia": "No disponible",
            "temperatura_gpu": "No disponible",
        }


    # Obtener información de RAM
    try:
        ram_info = {
            "uso_ram": psutil.virtual_memory().used,
            "total": psutil.virtual_memory().total
        }
    except Exception as e:
        ram_info = {
            "uso": "No disponible",
            "total": "No disponible"
        }

    try:
        almacenamiento_info = {
            "interno": {
                "uso_disco": psutil.disk_usage('/').used,  # Cambia '/' con la ruta correcta en tu sistema
                "almacenamiento_total": psutil.disk_usage('/').total
            }
        }
    except Exception as e:
        almacenamiento_info = {
            "interno": {
                "uso_disco": "No disponible",
                "almacenamiento_total": "No disponible"
            },
            "sd": {
                "usado": "No disponible",
                "total": "No disponible"
            }
        }


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

current_cpu_temperature = tk.StringVar()

current_cpu_temperature = tk.StringVar()

def mostrar_telemetria_tiempo_real():
    ventana_telemetria = tk.Toplevel(root)
    ventana_telemetria.title("Telemetría en Tiempo Real")
    ventana_telemetria.attributes('-fullscreen', True)
    ventana_telemetria.configure(bg='#2E2E2E')  # Fondo gris oscuro

    frames = []

    # Obtener la temperatura de la CPU
    temperatures = get_cpu_temperatures()
    cpu_temperature = temperatures[0][1] if temperatures else "N/A"
    current_cpu_temperature.set(cpu_temperature)

    # Crear un frame para cada conjunto de etiquetas y porcentajes
    for idx, (label_text, data_key) in enumerate([
        ("Porcentaje CPU:", "porcentaje_general"),
        ("Uso de RAM:", "uso_ram"),
        ("Temperatura CPU:", current_cpu_temperature),  # Agregado: Temperatura CPU
        ("Porcentaje GPU:", "porcentaje_trabajo"),
        ("Frecuencia GPU:", "frecuencia"),
        ("Temperatura GPU:", "temperatura_gpu"),
        ("Uso de almacenamiento interno:", "uso_disco"),
        ("Almacenamiento total del Disco:", "almacenamiento_total"),
        ("Porcentaje Batería:", "porcentaje_bateria"),
    ]):
        frame = tk.Frame(ventana_telemetria, bg='#0D2E3B')  # Fondo azul oscuro
        frame.grid(row=idx // 2, column=idx % 2, padx=10, pady=10, sticky='we')

        title_label = tk.Label(frame, text=label_text, font=('Helvetica', 18), fg='white', bg='#0D2E3B')  # Texto blanco, fondo azul oscuro
        title_label.pack(pady=(10, 5))  # Aumenté el espaciado superior

        value_label = tk.Label(frame, textvariable=data_key, font=('Helvetica', 18), fg='white', bg='#0D2E3B')  # Texto blanco, fondo azul oscuro
        value_label.pack(pady=(0, 10))  # Aumenté el espaciado inferior

        frames.append((value_label, data_key))

    # Configurar las columnas para centrar los elementos horizontalmente
    ventana_telemetria.columnconfigure(0, weight=1)
    ventana_telemetria.columnconfigure(1, weight=1)

    def actualizar_telemetria():
        telemetria = obtener_telemetria()

        for label, data_key in frames[:-1]:  # Excluir la última etiqueta ("Porcentaje Total")
            if data_key == "temperaturas_cpu":
                label.config(text=current_cpu_temperature.get())
            else:
                value = telemetria[0][data_key] if data_key in telemetria[0] else "N/A"

                if data_key == "uso_disco" or data_key == "almacenamiento_total":
                    value = f"{round(telemetria[3]['interno'][data_key] / (1024 ** 3), 2)} GB"
                elif data_key == "uso_ram":
                    value = f"{round(telemetria[2][data_key] / (1024 ** 3), 2)} GB"

                if isinstance(value, (int, float)):
                    label.config(text=f"{value:.2f}%")
                else:
                    label.config(text=str(value))

        ventana_telemetria.after(1000, actualizar_telemetria)  # Programar la próxima ejecución después de 1000 ms (1 segundo)

    actualizar_telemetria()

    ventana_telemetria.mainloop()

tiempo_real_button = CTkButton(main_toolbar, text="Telemetría en Tiempo Real", command=mostrar_telemetria_tiempo_real)
main_toolbar.add_button(tiempo_real_button)
root.mainloop()