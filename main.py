import tkinter as tk
from tkinter import messagebox, ttk, Canvas, Scrollbar
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
from PIL import Image, ImageTk

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
wifi_button_icon = CTkImage(Image.open("wifi.png"))
scan_button = CTkButton(root, text="Escanear redes Wi-FI", font=("Helvetica",12,"bold"), command=scan_wifi_networks, image=wifi_button_icon)
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

    def __init__(self, canvas, x, y, width, height, min_value, max_value, color):
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

monitorIcon = CTkImage(Image.open("velocimetro.png"))
monitor_button = CTkButton(main_toolbar, text="Monitor",font=("Helvetica",12,"bold"), text_color="black", image=monitorIcon)

search_deviceIcon = CTkImage(Image.open("search-engine-optimization.png"))
search_device_button = CTkButton(main_toolbar, text="Buscar dispositivos", font=("Helvetica", 12, "bold"), text_color="black", image=search_deviceIcon)

infoIcon = CTkImage(Image.open("info.png"))
infoButton = CTkButton(main_toolbar, text="Info", font=("Helvetica", 12, "bold"), text_color="black", image=infoIcon)
logsButtonIcon = CTkImage(Image.open("logs.png"))
logsButton = CTkButton(main_toolbar, text="Registros", font=("Helvetica", 12, "bold"), text_color="black", image=logsButtonIcon)

main_toolbar.add_button(monitor_button)
main_toolbar.add_button(search_device_button)
main_toolbar.add_button(infoButton)
main_toolbar.add_button(logsButton)


wifi_listbox.bind("<Double-Button-1>", on_wifi_double_click)

current_cpu_temperature = tk.StringVar()

current_cpu_temperature = tk.StringVar()

current_cpu_temperature = tk.StringVar()

square_size = 200
num_columns = 2
def mostrar_telemetria_tiempo_real():
    label_temperatura = tk.Label(root, text="Temperatura CPU:", font=('Arial', 18), fg='white', bg='#0D2E3B')
    label_temperatura.pack()

    ventana_telemetria = tk.Toplevel(root)
    ventana_telemetria.title("Telemetría en Tiempo Real")
    ventana_telemetria.geometry("800x600")
    ventana_telemetria.configure(bg='#0A2732')
    ventana_telemetria.columnconfigure(0, weight=1)


    frame_scroll = tk.Frame(ventana_telemetria, bg='#0A2732')
    frame_scroll.pack(fill=tk.BOTH, expand=True)
    
    canvas_scroll = Canvas(frame_scroll, bg='#0A2732')
    canvas_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    

    frame_telemetria = tk.Frame(canvas_scroll, bg='#111')
    frame_telemetria.pack(expand=True, padx=10, pady=10)
    
    frame_telemetria.place(in_=canvas_scroll, anchor="center", relx=.5, rely=.5)
    scrollbar = Scrollbar(frame_scroll, orient=tk.VERTICAL, command=canvas_scroll.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas_scroll.configure(yscrollcommand=scrollbar.set)
    frame_telemetria.bind("<Configure>", lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))

    frames = []

    for idx, (label_text, data_key) in enumerate([
        ("Porcentaje CPU:", "porcentaje_general"),
        ("Núm. de Cores:", "num_cores"),
        ("% Trabajo CPU (general):", "porcentaje_general"),
        ("Temperatura CPU:", "temperaturas_cpu"),
        ("% Trabajo CPU (cada core):", "porcentaje_core"),
        ("Porcentaje GPU:", "porcentaje_trabajo"),
        ("Frecuencia GPU:", "frecuencia"),
        ("Temperatura GPU:", "temperatura_gpu"),
        ("Uso de RAM:", "uso_ram"),
        ("Almacenamiento Interno Usado:", "uso_disco"),
        ("Almacenamiento Interno Total:", "almacenamiento_total"),
        ("Power Consumo Total (W):", "power_consumo"),
        ("Porcentaje Batería:", "porcentaje_bateria"),
        ("Tiempo Autonomía Batería:", "tiempo_autonomia"),
        ("Frecuencia EMC:", "frecuencia_emc"),
        ("Temperatura SOC:", "temperatura_soc"),
        ("Voltaje Rail1:", "voltaje_rail1"),
        ("Voltaje Rail2:", "voltaje_rail2"),
        ("Voltaje Rail3:", "voltaje_rail3"),
    ]):
        frame = tk.Frame(
            frame_telemetria,
            bg='#0D2E3B',
            highlightbackground="white",
            highlightthickness=2,
            relief="solid",
            width=square_size,
            height=square_size
        )
        frame.grid(row=idx // num_columns, column=idx % num_columns, padx=10, pady=10, sticky='nsew')
        title_label = tk.Label(frame, text=label_text, font=('Arial', 14), fg='white', bg='#0D2E3B')
        title_label.pack()
        
        # -----------Iconos------------
        if data_key == "porcentaje_bateria":
            battery_image = Image.open("bateria.png")  
            battery_image = battery_image.resize((51, 34))  
            battery_icon = ImageTk.PhotoImage(battery_image)
            battery_label = tk.Label(frame, image=battery_icon, bg='#0D2E3B')
            battery_label.image = battery_icon  
            battery_label.pack()

        if data_key == "uso_ram":
            ram_image = Image.open("ram.png")
            ram_image = ram_image.resize((50, 50))
            ram_icon = ImageTk.PhotoImage(ram_image)
            ram_label = tk.Label(frame, image=ram_icon, bg='#0D2E3B')
            ram_label.image = ram_icon
            ram_label.pack()
        
        if data_key == "porcentaje_general":
            cpu_image = Image.open("cpu.png")  
            cpu_image = cpu_image.resize((50, 50))  
            cpu_icon = ImageTk.PhotoImage(cpu_image)
            cpu_label = tk.Label(frame, image=cpu_icon, bg='#0D2E3B')
            cpu_label.image = cpu_icon  
            cpu_label.pack()

        if data_key == "frecuencia":
            gpu_image = Image.open("gpu.png")  
            gpu_image = gpu_image.resize((50, 50))  
            gpu_icon = ImageTk.PhotoImage(gpu_image)
            gpu_label = tk.Label(frame, image=gpu_icon, bg='#0D2E3B')
            gpu_label.image = gpu_icon  
            gpu_label.pack()
        
        if (data_key == "voltaje_rail1" or data_key == "voltaje_rail2" or data_key == "voltaje_rail3"):
            voltaje_image = Image.open("voltaje.png")  
            voltaje_image = voltaje_image.resize((30, 30))  
            voltaje_icon = ImageTk.PhotoImage(voltaje_image)
            voltaje_label = tk.Label(frame, image=voltaje_icon, bg='#0D2E3B')
            voltaje_label.image = voltaje_icon  
            voltaje_label.pack()
        # -----------Iconos------------

        if data_key == "temperaturas_cpu":
            canvas = tk.Canvas(frame, width=square_size, height=square_size, bg='#0D2E3B', highlightthickness=0)
            
            # canvas.pack()

            # verde = '#00FF00'
            # amarillo = '#FFFF00'
            # rojo = '#FF0000'

            # inicio_verde = 90
            # fin_verde = 0
            # inicio_amarillo = 0
            # fin_amarillo = -90
            # inicio_rojo = -90
            # fin_rojo = -180

            # for i in range(inicio_verde, fin_verde, -1):
            #     canvas.create_arc(10, 10, square_size - 10, square_size - 10, start=i, extent=-1, outline=verde, width=2)
            # for i in range(inicio_amarillo, fin_amarillo, -1):
            #     canvas.create_arc(10, 10, square_size - 10, square_size - 10, start=i, extent=-1, outline=amarillo, width=2)
            # for i in range(inicio_rojo, fin_rojo, -1):
            #     canvas.create_arc(10, 10, square_size - 10, square_size - 10, start=i, extent=-1, outline=rojo, width=2)

            # flecha = canvas.create_line(square_size // 2, square_size // 2, square_size // 2, square_size // 4, fill='white', width=2)

            # temperatura_label = tk.Label(frame, text="0°C", font=('Arial', 14), fg='white', bg='#0D2E3B')
            # temperatura_label.pack(side="right", anchor="e")

            # def actualizar_barra_progreso():
            #     nonlocal flecha
            #     temperatures = get_cpu_temperatures()
            #     temperatura_actual = temperatures[0][1] if temperatures else 0

            #     angulo = temperatura_actual * 1.8

            #     canvas.coords(flecha, square_size // 2, square_size // 2, square_size // 2 + square_size // 4 * math.sin(math.radians(angulo)), square_size // 2 - square_size // 4 * math.cos(math.radians(angulo)))

            #     temperatura_label.config(text=f"{temperatura_actual}°C")

            #     value_label.config(text=str(temperatura_actual) + "°C")
            #     ventana_telemetria.after(1000, actualizar_barra_progreso)

            # actualizar_barra_progreso()

        else:
            value_label = tk.Label(frame, text="0%", font=('Arial', 18), fg='white', bg='#0D2E3B')
            value_label.pack()

        frames.append((value_label, data_key))

    for i in range(2):
        ventana_telemetria.columnconfigure(i, weight=1)
        ventana_telemetria.rowconfigure(i, weight=1)

    def actualizar_telemetria():
        telemetria = obtener_telemetria()
        temperatures = get_cpu_temperatures()
        label_temperatura.config(text="Temperatura CPU: " + str(temperatures[0][1]))

        cpu_temperature = temperatures[0][1] if temperatures else "N/A"
        current_cpu_temperature.set(cpu_temperature)

        for label, data_key in frames[:-1]:
            if data_key == "temperaturas_cpu":
                label.config(text=current_cpu_temperature.get())
            else:
                value = telemetria[0][data_key] if data_key in telemetria[0] else ""
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

        ventana_telemetria.after(1000, actualizar_telemetria)

    # comentado para testear
    # actualizar_telemetria()

    ventana_telemetria.mainloop()

tiempo_real_button = CTkButton(main_toolbar, text="Telemetría en Tiempo Real", command=mostrar_telemetria_tiempo_real)
main_toolbar.add_button(tiempo_real_button)
root.mainloop()