import math
import customtkinter as ctk
import os
import tkinter as tk
from PIL import Image
from tkinter import filedialog
import pandas as pd
from CTkTable import CTkTable
from CTkTableRowSelector import CTkTableRowSelector
import tkintermapview
import pandas as pd
import sqlite3
import pyproj
from CTkMessagebox import CTkMessagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

#Aqui algunas modificaciones/funciones que he hecho para completar la tareas del MODULO-1

selected_data=[]

def seleccionar_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")])
    if archivo:
        print(f"Archivo seleccionado: {archivo}")
        
        leer_archivo_csv(archivo)
    
def leer_archivo_csv(ruta_archivo):
    try:
        datos = pd.read_csv(ruta_archivo,sep=',')
        agregar_df_a_sqlite(datos,'progra2024_final.db','TABLAS')
        mostrar_datos(datos)
    except Exception as e:
            print(f"Error al leer el archivo CSV: {e}")

def mostrar_datos(datos): #esta funcion itera los datos de dataframe y los pone en una tabla 
    global selected_data
    selected_rows = set()

    # Eliminar cualquier tabla existente
    for widget in scrollable_frame.winfo_children():
        widget.destroy()


    def show(cell):
        global selected_data
        row_index = cell["row"]
        if row_index == 0:
            return
        if row_index in selected_rows:
            table.deselect_row(row_index)
            selected_rows.remove(row_index)
        else:
            table.select_row(row_index)
            selected_rows.add(row_index)
        selected_data.clear()
        selected_data.extend([datos.iloc[idx - 1].tolist() for idx in selected_rows])
        print("Filas seleccionadas:", selected_data)

    value = [list(datos.columns)] + datos.values.tolist()
    table = CTkTable(master=scrollable_frame, row=len(value), column=len(value[0]), values=value, command=show, header_color="green")
    table.pack(expand=True, fill="both", padx=20, pady=20)
    
    #Creacion de Botones que no van a ayudar mas adelante
    boton_imprimir = ctk.CTkButton(
        master=home_frame, text="Guardar información", command=lambda: guardar_data(datos))
    boton_imprimir.grid(row=2, column=0, pady=(0, 20))

    boton_modificar = ctk.CTkButton(
        master=data_panel_superior, text="Modificar dato", command=lambda: editar_panel())
    boton_modificar.grid(row=0, column=2, pady=(0, 0))

    boton_eliminar = ctk.CTkButton(
        master=data_panel_superior, text="Eliminar dato", command=lambda: eliminar_panel(root, selected_data, datos),fg_color='purple',hover_color='red')
    boton_eliminar.grid(row=0, column=3, padx=4, pady=4)
    

#Boton que crea una ventana en base a nuestra desicion borrara los datos seleccionados
def eliminar_panel(root, selected_data, datos):
    if selected_data:
        mensaje = f"Peligro vas a eliminar: {selected_data}"
        toplevel_window = ctk.CTkToplevel(root)
        setup_toplevel(toplevel_window)
        label = ctk.CTkLabel(toplevel_window, text=mensaje)
        label.pack(padx=20, pady=20)

        def confirmar_eliminacion():
            eliminar_datos(selected_data, datos)
            toplevel_window.destroy()

        def cancelar_eliminacion():
            toplevel_window.destroy()

        boton_aceptar = ctk.CTkButton(toplevel_window, text="ACEPTAR", command=confirmar_eliminacion)
        boton_aceptar.pack(padx=20, pady=10)
        boton_cancelar = ctk.CTkButton(toplevel_window, text="CANCELAR", command=cancelar_eliminacion)
        boton_cancelar.pack(padx=20, pady=10)

def eliminar_datos(selected_data, datos):
    global updated_data
    for row in selected_data:
        datos = datos[~(datos == row).all(axis=1)]
    updated_data = datos
    mostrar_datos(updated_data)


#Esta funcion se activa si se aprieta el boton guardar informacion 
def guardar_data(datos):
    # Convertir coordenadas UTM a latitud y longitud y actualizar el DataFrame
    for idx, data in datos.iterrows():
        lat, long = utm_to_latlong(data['UTM_Easting'], data['UTM_Northing'], data['UTM_Zone_Number'], data['UTM_Zone_Letter'])  # Ajustar zona y letra según tus datos
        datos.at[idx, 'Latitud'] = lat
        datos.at[idx, 'Longitud'] = long

    # Actualizar la tabla con los nuevos datos
    mostrar_datos(datos)
    agregar_df_a_sqlite(datos,'base_de_datos_MOD.db','TABLAS')
    def show_info():
    # Default messagebox for showing some information
        CTkMessagebox(title="Info", message="Datos Actualizados!")
    show_info()
    

# Función para convertir UTM a latitud y longitud
def utm_to_latlong(easting, northing, zone_number, zone_letter):
    # Crear el proyector UTM con el sistema de coordenadas WGS84
    utm_proj = pyproj.Proj(proj='utm', zone=zone_number, datum='WGS84')

    # Convertir las coordenadas UTM a latitud y longitud
    longitude, latitude = utm_proj(easting, northing, inverse=True)

    # Redondear las coordenadas a 2 decimales
    return round(latitude, 2), round(longitude, 2)


def setup_toplevel(window):
    window.geometry("400x300")
    window.title("Eliminar Datos")
    center_window(window, 400, 300)  # Centrar la ventana secundaria
    window.lift()  # Levanta la ventana secundaria
    window.focus_force()  # Forzar el enfoque en la ventana secundaria
    window.grab_set()  # Evita la interacción con la ventana principal

    label = ctk.CTkLabel(window, text="¿Estas seguro que quieres eliminar la siguiente informacion?")
    label.pack(padx=20, pady=20)