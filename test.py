import wmi

def obtener_temperatura_cpu():
    try:
        # Conectar con el servicio WMI
        w = wmi.WMI()

        # Obtener información sobre la temperatura de la CPU
        temperaturas_cpu = w.Win32_TemperatureProbe()

        # Mostrar la información
        for temperatura in temperaturas_cpu:
            print(f"Nombre: {temperatura.Name}")
            print(f"Temperatura: {temperatura.CurrentReading} °C\n")
            print("hola")

    except Exception as e:
        print(f"Error al obtener la temperatura de la CPU: {e}")

if __name__ == "__main__":
    obtener_temperatura_cpu()