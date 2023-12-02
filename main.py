import tkinter as tk
import subprocess
import re

def scan_wifi_networks():
    wifi_listbox.delete(0, tk.END)
    try:
        result = subprocess.run(["netsh", "wlan", "show", "network"], capture_output=True, text=True, check=True)
        networks = re.findall(r"SSID \d+ : (.+)", result.stdout)
        for network in networks:
            wifi_listbox.insert(tk.END, network)
    except subprocess.CalledProcessError as e:
        print(f"Error scanning Wi-Fi networks: {e}")

def connect_to_wifi():
    selected_index = wifi_listbox.curselection()
    if selected_index:
        selected_network = wifi_listbox.get(selected_index)
        password = password_entry.get()
        
        try:
            subprocess.run(["netsh", "wlan", "connect", "name=" + selected_network], check=True)
            print(f"Connected to {selected_network}")
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to {selected_network}: {e}")
    else:
        print("Please select a Wi-Fi network to connect.")

def check_connection_successful():
    try:
        # Intenta realizar una operación que dependa de la conexión, por ejemplo, hacer ping a un servidor
        subprocess.run(["ping", "-n", "1", "google.com"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

root = tk.Tk()
root.title("Wi-Fi Scanner")

root.state('zoomed')

scan_button = tk.Button(root, text="Scan Wi-Fi Networks", command=scan_wifi_networks)
scan_button.pack(pady=10)

scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL)
wifi_listbox = tk.Listbox(root, selectmode=tk.SINGLE, yscrollcommand=scrollbar.set, height=30, width=100)
wifi_listbox.pack(pady=10)
scrollbar.config(command=wifi_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
wifi_listbox.yview(tk.END)

password_label = tk.Label(root, text="Password:")
password_label.pack(pady=5)
password_entry = tk.Entry(root, show="*")
password_entry.pack(pady=5)

connect_button = tk.Button(root, text="Connect to Wi-Fi", command=connect_to_wifi)
connect_button.pack(pady=10)

root.mainloop()
