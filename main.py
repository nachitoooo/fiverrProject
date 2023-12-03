import tkinter as tk
from tkinter import messagebox
import time
import pywifi
from customtkinter import *
import threading

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
        wifi_status_label.config(text="Conectado", bg="green")
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
    password_dialog = tk.Toplevel(root)
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

dashboard_button = CTkButton(main_toolbar, text="Dashboard")
monitor_button = CTkButton(main_toolbar, text="Monitor")
storage_button = CTkButton(main_toolbar, text="Almacenamiento")
settings_button = CTkButton(main_toolbar, text="Configuración")

main_toolbar.add_button(dashboard_button)
main_toolbar.add_button(monitor_button)
main_toolbar.add_button(storage_button)
main_toolbar.add_button(settings_button)

wifi_listbox.bind("<Double-Button-1>", on_wifi_double_click)

root.mainloop()
