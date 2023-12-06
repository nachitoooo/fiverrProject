import tkinter as tk
from tkinter import ttk

class ThermometerProgressBar(ttk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.temperature = tk.DoubleVar(value=0)
        self.create_widgets()

    def create_widgets(self):
        # Crea una barra de progreso horizontal
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=200, variable=self.temperature, mode="determinate")
        self.progress_bar.grid(row=0, column=0, padx=10, pady=10)

        # Crea un canvas para dibujar el termómetro
        self.canvas = tk.Canvas(self, width=30, height=150, bg="white", highlightthickness=0)
        self.canvas.grid(row=0, column=1)

        # Dibuja el termómetro
        self.draw_thermometer()

    def draw_thermometer(self):
        # Obtén la temperatura actual
        current_temperature = self.temperature.get()

        # Calcula la posición del marcador en el canvas según la temperatura
        y_position = 150 - (current_temperature / 100) * 150

        # Borra el canvas antes de redibujar
        self.canvas.delete("all")

        # Dibuja el termómetro
        self.canvas.create_rectangle(5, 0, 25, 150, fill="lightgray", outline="black")
        self.canvas.create_rectangle(5, y_position, 25, 150, fill="red", outline="black")

# Ejemplo de uso
root = tk.Tk()
thermometer_frame = ThermometerProgressBar(root)
thermometer_frame.pack(pady=20)

# Actualiza la temperatura (puedes llamar a esta función con la temperatura actual)
def update_temperature():
    temperature = 75  # Reemplaza con la temperatura actual
    thermometer_frame.temperature.set(temperature)
    thermometer_frame.draw_thermometer()

update_temperature_button = tk.Button(root, text="Actualizar Temperatura", command=update_temperature)
update_temperature_button.pack()

root.mainloop()
