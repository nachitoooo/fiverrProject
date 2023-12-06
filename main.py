import tkinter as tk
from tkinter import messagebox, ttk, Canvas
import time
import pywifi
from customtkinter import *
import threading
import psutil
import GPUtil
import platform
import subprocess
import matplotlib.pyplot as plt
import math
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
        


def get_gpu_info():
    try:
        gpu = GPUtil.getGPUs()[0]
        gpu_info = {
            "porcentaje_trabajo": gpu.load * 100,
            "frecuencia": getattr(gpu, 'memoryInfo', {}).get(0, "No disponible"),  # Assuming core frequency is stored at index 0
            "temperatura_gpu": gpu.temperature,
        }
    except Exception as e:
        gpu_info = {
            "porcentaje_trabajo": "No disponible",
            "frecuencia": "No disponible",
            "temperatura_gpu": "No disponible",
        }

    return gpu_info

def obtener_telemetria():
    cpu_temperatures = get_cpu_temperatures()
    gpu_info = get_gpu_info()

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
class Thermometer:

    def init(self, canvas, x, y, width, height, min_value, max_value, color):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_value = min_value
        self.max_value = max_value
        self.color = color

        self.needle = self.canvas.create_line(self.x, self.y + self.height // 2, self.x, self.y)
        self.needle_tip = self.canvas.create_oval(self.x - self.width // 2, self.y - self.height // 2, self.x + self.width // 2, self.y + self.height // 2)

    def set_value(self, value):
        value = min(max(self.min_value, value), self.max_value)
        percentage = (value - self.min_value) / (self.max_value - self.min_value)
        x_pos = self.x + self.width * percentage
        self.canvas.coords(self.needle, self.x, self.y + self.height // 2, x_pos, self.y)
        self.canvas.coords(self.needle_tip, x_pos - self.width // 2, self.y - self.height // 2, x_pos + self.width // 2, self.y + self.height // 2)

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

current_cpu_temperature = tk.StringVar()

import tkinter as tk

def mostrar_telemetria_tiempo_real():


    # Crear una instancia del termómetro pasando el objeto de lienzo

    label_temperatura = tk.Label(root, text="Temperatura CPU:", font=('Arial', 18), fg='white', bg='#0D2E3B')
    label_temperatura.pack()

    ventana_telemetria = tk.Toplevel(root)
    ventana_telemetria.title("Telemetría en Tiempo Real")
    ventana_telemetria.geometry("800x600")
    ventana_telemetria.configure(bg='#0A2732')  # Fondo gris oscuro

    frames = []

    # Crear un frame cuadrado para cada conjunto de etiquetas y porcentajes
    for idx, (label_text, data_key) in enumerate([
        ("Porcentaje CPU:", "porcentaje_general"),
        ("Núm. de Cores:", "num_cores"),  # Agregado: Número de cores
        ("% Trabajo CPU (general):", "porcentaje_general"),  # Actualizado: % Trabajo (general)
        ("Temperatura CPU:", "temperaturas_cpu"),
        ("% Trabajo CPU (cada core):", "porcentaje_core"),  # Agregado: % Trabajo (cada core)
        ("Porcentaje GPU:", "porcentaje_trabajo"),
        ("Frecuencia GPU:", "frecuencia"),
        ("Temperatura GPU:", "temperatura_gpu"),
        ("Uso de RAM:", "uso_ram"),
        ("Almacenamiento Interno Usado:", "uso_disco"),  # Actualizado: Usado
        ("Almacenamiento Interno Total:", "almacenamiento_total"),  # Actualizado: Total
        ("Power Consumo Total (W):", "power_consumo"),  # Agregado: Power consumo total (en W)
        ("Porcentaje Batería:", "porcentaje_bateria"),
        ("Tiempo Autonomía Batería:", "tiempo_autonomia"),  # Agregado: Tiempo autonomía de la batería
        ("Frecuencia EMC:", "frecuencia_emc"),  # Agregado: Frecuencia EMC
        ("Temperatura SOC:", "temperatura_soc"),  # Agregado: Temperatura SOC
        ("Voltaje Rail1:", "voltaje_rail1"),  # Agregado: Voltaje Rail1
        ("Voltaje Rail2:", "voltaje_rail2"),  # Agregado: Voltaje Rail2
        ("Voltaje Rail3:", "voltaje_rail3"),  # Agregado: Voltaje Rail3
    ]):
        frame = tk.Frame(ventana_telemetria, bg='#0D2E3B', highlightbackground="white", highlightthickness=2, relief="solid", width=200, height=200)  # Fondo azul oscuro, borde redondeado
        frame.grid(row=idx // 2, column=idx % 2, padx=10, pady=10, sticky='nsew')

        title_label = tk.Label(frame, text=label_text, font=('Arial', 14), fg='white', bg='#0D2E3B')  # Texto blanco, fondo azul oscuro, letra bonita
        title_label.pack()

        if data_key == "temperaturas_cpu":
            # Crear una representación gráfica de una barra de progreso circular
            canvas = tk.Canvas(frame, width=200, height=200, bg='#0D2E3B', highlightthickness=0)
            canvas.pack()

            # Definir los colores
            verde = '#00FF00'
            amarillo = '#FFFF00'
            rojo = '#FF0000'

            # Calcular los ángulos de inicio y fin de cada color
            inicio_verde = 90
            fin_verde = 0
            inicio_amarillo = 0
            fin_amarillo = -90
            inicio_rojo = -90
            fin_rojo = -180

            # Crear arcos con colores personalizados y gradiente
            for i in range(inicio_verde, fin_verde, -1):
                canvas.create_arc(10, 10, 190, 190, start=i, extent=-1, outline=verde, width=2)
            for i in range(inicio_amarillo, fin_amarillo, -1):
                canvas.create_arc(10, 10, 190, 190, start=i, extent=-1, outline=amarillo, width=2)
            for i in range(inicio_rojo, fin_rojo, -1):
                canvas.create_arc(10, 10, 190, 190, start=i, extent=-1, outline=rojo, width=2)

            # Flecha indicadora
            flecha = canvas.create_line(100, 100, 100, 20, fill='white', width=2)

            # Etiqueta para mostrar la temperatura
            temperatura_label = tk.Label(frame, text="0°C", font=('Arial', 14), fg='white', bg='#0D2E3B')
            temperatura_label.pack(side="right", anchor="e")

            def actualizar_barra_progreso():
                nonlocal flecha
                temperatures = get_cpu_temperatures()
                temperatura_actual = temperatures[0][1] if temperatures else 0

                # Calcular el ángulo correspondiente al porcentaje de temperatura
                angulo = temperatura_actual * 1.8  # 1.8 es la relación para convertir el porcentaje a grados (180 grados / 100%)

                # Actualizar la posición de la flecha
                canvas.coords(flecha, 100, 100, 100 + 70 * math.sin(math.radians(angulo)), 100 - 70 * math.cos(math.radians(angulo)))

                # Actualizar la etiqueta de temperatura
                temperatura_label.config(text=f"{temperatura_actual}°C")

                value_label.config(text=str(temperatura_actual) + "°C")
                ventana_telemetria.after(1000, actualizar_barra_progreso)

            actualizar_barra_progreso()

        else:
            value_label = tk.Label(frame, text="0%", font=('Arial', 18), fg='white', bg='#0D2E3B')
            value_label.pack()

        frames.append((value_label, data_key))

    # Configurar las columnas y filas para centrar los elementos horizontal y verticalmente
    for i in range(2):
        ventana_telemetria.columnconfigure(i, weight=1)
        ventana_telemetria.rowconfigure(i, weight=1)

    def actualizar_telemetria():
        telemetria = obtener_telemetria()
        temperatures = get_cpu_temperatures()
        label_temperatura.config(text="Temperatura CPU: " + str(temperatures[0][1]))

        cpu_temperature = temperatures[0][1] if temperatures else "N/A"
        current_cpu_temperature.set(cpu_temperature)

        for label, data_key in frames[:-1]:  # Excluir la última etiqueta ("Porcentaje Total")
            if data_key == "temperaturas_cpu":
                label.config(text=current_cpu_temperature.get())
            else:
                value = telemetria[0][data_key] if data_key in telemetria[0] else "N/A"
                if data_key == "uso_disco" or data_key == "almacenamiento_total":
                    value = f"{round(telemetria[3]['interno'][data_key] / (1024 ** 3), 2)} GB"
                elif data_key == "uso_ram":
                    value = f"{round(telemetria[2][data_key] / (1024 ** 3), 2)} GB"
                elif data_key == "porcentaje_trabajo" and "porcentaje_trabajo" in telemetria[1]:
                    value = f"{telemetria[1]['porcentaje_trabajo']:.2f}%"
                elif data_key == "frecuencia" and "frecuencia" in telemetria[1]:
                    value = telemetria[1]['frecuencia']
                elif data_key == "temperatura_gpu" and "temperatura_gpu" in telemetria[1]:
                    value = telemetria[1]['temperatura_gpu']

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