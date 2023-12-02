import tkinter as tk
import subprocess
import re

def scan_wifi_networks():
    # Clear existing entries in the listbox
    wifi_listbox.delete(0, tk.END)

    try:
        # Run the netsh command to get Wi-Fi information
        result = subprocess.run(["netsh", "wlan", "show", "network"], capture_output=True, text=True, check=True)

        # Process the output to extract and display relevant information
        networks = re.findall(r"SSID \d+ : (.+)", result.stdout)
        for network in networks:
            wifi_listbox.insert(tk.END, network)

    except subprocess.CalledProcessError as e:
        # Handle the error, for example, print the error message
        print(f"Error: {e}")

# Create the main window
root = tk.Tk()
root.title("Wi-Fi Scanner")

# Maximize the window
root.state('zoomed')

# Create a button to initiate Wi-Fi scanning
scan_button = tk.Button(root, text="Scan Wi-Fi Networks", command=scan_wifi_networks)
scan_button.pack(pady=10)

# Create a vertical scrollbar
scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL)

# Create a larger listbox to display the scanned Wi-Fi networks with scrollbar
wifi_listbox = tk.Listbox(root, selectmode=tk.SINGLE, yscrollcommand=scrollbar.set, height=30, width=100)
wifi_listbox.pack(pady=10)

# Configure the scrollbar to work with the listbox
scrollbar.config(command=wifi_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Set the yscroll to the bottom to make the text start from the bottom
wifi_listbox.yview(tk.END)

# Start the Tkinter main loop
root.mainloop()