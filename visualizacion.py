import tkinter as tk
from tkinter import messagebox
import serial
import csv
import math
import time
PUERTO_SERIAL = 'COM6'
BAUD_RATE = 115200
class AppSensorColor:
    def __init__(self, root):
        self.root = root
        self.root.title("Clasificador de Color ESP32")
        self.db_file = "datos_color.csv"
        self.conexion = None
        try:
            self.conexion = serial.Serial(PUERTO_SERIAL, BAUD_RATE, timeout=2)
            time.sleep(2)
            self.conexion.reset_input_buffer() # Limpiar la "basura" del reinicio
        except:
            messagebox.showerror("Error", f"No se pudo abrir el puerto {PUERTO_SERIAL}")
        self.setup_ui()

    def setup_ui(self):
        # Titulo
        tk.Label(self.root, text="Laboratorio de detección de color", font=("Arial", 16, "bold")).pack(pady=10)
        # Contenedor Principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(pady=10, padx=20, fill="both", expand=True)
        # --- SECCIoN IZQUIERDA: CAPTURA ACTUAL ---
        self.frame_actual = tk.LabelFrame(main_frame, text="Lectura Actual (ESP32)", padx=10, pady=10)
        self.frame_actual.grid(row=0, column=0, padx=10, sticky="nsew")
        self.canvas_actual = tk.Canvas(self.frame_actual, width=150, height=100, bg="gray")
        self.canvas_actual.pack()
        self.lbl_rgb_actual = tk.Label(self.frame_actual, text="R: -- | G: -- | B: --", font=("Courier", 10))
        self.lbl_rgb_actual.pack(pady=5)
        # --- SECCIoN DERECHA: RESULTADO BASE DE DATOS ---
        self.frame_match = tk.LabelFrame(main_frame, text="Color mas Cercano (DB)", padx=10, pady=10)
        self.frame_match.grid(row=0, column=1, padx=10, sticky="nsew")
        self.canvas_match = tk.Canvas(self.frame_match, width=150, height=100, bg="gray")
        self.canvas_match.pack()
        self.lbl_nombre_match = tk.Label(self.frame_match, text="NOMBRE: ???", font=("Arial", 11, "bold"))
        self.lbl_nombre_match.pack(pady=2)
        self.lbl_rgb_match = tk.Label(self.frame_match, text="R: -- | G: -- | B: --", font=("Courier", 10))
        self.lbl_rgb_match.pack(pady=5)
        # Boton de Captura
        self.btn_capturar = tk.Button(self.root, text="ESCANEAR COLOR", command=self.ejecutar_proceso, 
                                      bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), height=2)
        self.btn_capturar.pack(pady=20, fill="x", padx=50)

    def adc_to_hex(self, r, g, b):
        """Convierte valores ADC (0-4095) a Hexadecimal (0-255) para mostrar en pantalla."""
        r_map = int((r / 4095) * 255)
        g_map = int((g / 4095) * 255)
        b_map = int((b / 4095) * 255)
        return f'#{r_map:02x}{g_map:02x}{b_map:02x}'

    def buscar_en_db(self, r_cap, g_cap, b_cap):
        """Busca el color mas cercano en el archivo CSV."""
        mejor_match = None
        distancia_minima = float('inf')
        try:
            with open(self.db_file, mode='r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Extraer valores de la DB
                    r_db = float(row['Lectura_R'])
                    g_db = float(row['Lectura_G'])
                    b_db = float(row['Lectura_B'])
                    nombre_db = row['Color']
                    # Calculo de Distancia Euclidea
                    dist = math.sqrt((r_cap - r_db)**2 + (g_cap - g_db)**2 + (b_cap - b_db)**2)
                    if dist < distancia_minima:
                        distancia_minima = dist
                        mejor_match = {
                            "nombre": nombre_db,
                            "r": r_db, "g": g_db, "b": b_db
                        }
            return mejor_match
        except FileNotFoundError:
            messagebox.showwarning("Archivo no encontrado", "Asegurate de que 'datos_color.csv' exista.")
            return None

    def ejecutar_proceso(self):
        if not self.conexion:
            messagebox.showerror("Error", "No hay conexion con la ESP32")
            return
        # 1. Pedir captura a la ESP32
        self.conexion.write(b"CAPTURAR\n")
        linea = self.conexion.readline().decode('utf-8').strip()
        if linea:
            try:
                # 2. Procesar datos capturados
                valores = [float(x) for x in linea.split(',')]
                r_c, g_c, b_c = valores
                color_hex_actual = self.adc_to_hex(r_c, g_c, b_c)
                # Actualizar UI Izquierda
                self.canvas_actual.configure(bg=color_hex_actual)
                self.lbl_rgb_actual.config(text=f"R:{int(r_c)} | G:{int(g_c)} | B:{int(b_c)}")
                # 3. Buscar el mas parecido
                match = self.buscar_en_db(r_c, g_c, b_c)
                if match:
                    # Actualizar UI Derecha
                    color_hex_match = self.adc_to_hex(match['r'], match['g'], match['b'])
                    self.canvas_match.configure(bg=color_hex_match)
                    self.lbl_nombre_match.config(text=f"NOMBRE: {match['nombre'].upper()}")
                    self.lbl_rgb_match.config(text=f"R:{int(match['r'])} | G:{int(match['g'])} | B:{int(match['b'])}")
            except ValueError:
                print("Error procesando datos recibidos")
        else:
            messagebox.showwarning("Timeout", "La ESP32 no respondio a tiempo.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppSensorColor(root)
    root.mainloop()