import tkinter as tk
from tkinter import messagebox
import time
import pywifi
from customtkinter import *

def show_error(message):
    messagebox.showerror("Error", message)

def scan_wifi_networks():
    wifi_listbox.delete(0, tk.END)
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    
    iface.scan()
    time.sleep(2)  # Espera unos segundos para que se complete la exploración
    
    scan_result = iface.scan_results()
    
    for result in scan_result:
        wifi_listbox.insert(tk.END, result.ssid)

def connect_to_wifi():
    selected_index = wifi_listbox.curselection()
    if selected_index:
        selected_network = wifi_listbox.get(selected_index)
        password = password_entry.get()
        
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
        
        time.sleep(5)  # Espera unos segundos para que se establezca la conexión
        
        if iface.status() == pywifi.const.IFACE_CONNECTED:
            messagebox.showinfo("Conexión exitosa.", f"Conectado a {selected_network}")
        else:
            show_error(selected_network)
    else:
        show_error("Por favor seleccione una red Wi-Fi para conectar.")

root = CTk()
root.title("Wi-Fi Escáner")

root.state('zoomed')

scan_button = CTkButton(root, text="Scan Wi-Fi Networks", command=scan_wifi_networks)
scan_button.pack(pady=10)

scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL)
wifi_listbox = tk.Listbox(root, selectmode=tk.SINGLE, yscrollcommand=scrollbar.set, height=30, width=100, fg="white", bg="#171718", justify="center", font=("Helvetica", "12", "bold"))
wifi_listbox.pack(pady=10)
scrollbar.config(command=wifi_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
wifi_listbox.yview(tk.END)

password_label = CTkLabel(root, text="Contraseña:")
password_label.pack(pady=5)
password_entry = CTkEntry(root, show="*")
password_entry.pack(pady=5)

connect_button = CTkButton(root, text="Conectar a Wi-Fi", command=connect_to_wifi)
connect_button.pack(pady=10)

root.mainloop()