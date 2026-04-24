import serial
import csv
import time
arduino_port = 'COM6' 
baud_rate = 115200
file_name = "datos_color.csv"
try:
    # Inicializar puerto serie
    ser = serial.Serial(arduino_port, baud_rate, timeout=2)
    time.sleep(2) # Esperar a que la conexion se estabilice
    ser.reset_input_buffer() # Limpiar la "basura" del reinicio
    print(f"Conectado a la ESP32 en {arduino_port}\n")
    # Abrir (o crear) el archivo CSV
    with open(file_name, "a", newline="") as f:
        writer = csv.writer(f)
        # Si el archivo esta vacio, escribir encabezados.
        if f.tell() == 0:
            writer.writerow(["Lectura_R", "Lectura_G", "Lectura_B", "Color"])
        while True:
            # 1. Pedir el nombre del color al usuario
            color_input = input("Ingresa el color a escanear (o escribe 'salir' para terminar): ").strip()
            # Salir del bucle si el usuario lo desea
            if color_input.lower() == 'salir':
                print("Finalizando recoleccion de datos...")
                break
            # Evitar entradas vacias
            if not color_input:
                print("Por favor, ingresa un nombre valido.\n")
                continue
            # 2. Enviar el comando "CAPTURAR" a la ESP32
            ser.write(b"CAPTURAR\n")
            # 3. Esperar y leer la respuesta de la ESP32
            line = ser.readline().decode('utf-8').strip()
            if line:
                # Validar que los datos tengan el formato esperado (3 valores separados por coma)
                datos = line.split(',')
                print(datos)
                if len(datos) == 3:
                    # Crear la fila agregando el color al final
                    row = [datos[0], datos[1], datos[2], color_input]
                    # Guardar en CSV
                    writer.writerow(row)
                    f.flush() # Forzar la escritura en el disco inmediatamente
                    print(f"Muestra guardada -> R:{datos[0]} G:{datos[1]} B:{datos[2]} | Color: {color_input}\n")
                else:
                    print(f"Error: Formato de datos inesperado de la ESP32: {line}\n")
            else:
                print("Error: No se recibio respuesta de la ESP32. Revisa la conexion o si la placa se reinicio.\n")
except KeyboardInterrupt:
    print("\nDeteniendo la captura de datos (Interrupcion por teclado)...")
except Exception as e:
    print(f"Error de conexion: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
    print("Puerto cerrado.")