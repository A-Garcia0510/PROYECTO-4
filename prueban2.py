import math
import customtkinter as ctk
import os
import tkinter
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

def haversine(lat1, lon1, lat2, lon2):
    # Calcular la distancia entre dos puntos en la superficie de la Tierra usando la fórmula de Haversine
    R = 6371.0  # Radio de la Tierra en kilómetros

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance

def ejecutar_query_sqlite(database_name, table_name, columns='*', where_column=None, where_value=None):
    """
    Ejecuta una consulta SQL en una base de datos SQLite y retorna una lista con los resultados.
    """
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    query = f'SELECT {columns} FROM {table_name}'
    if where_column and where_value is not None:
        query += f' WHERE {where_column} = ?'
    cursor.execute(query, (where_value,) if where_column and where_value is not None else ())
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def agregar_df_a_sqlite(df, database_name, table_name):
    """
    Agrega un DataFrame a una tabla SQLite.
    """
    conn = sqlite3.connect(database_name)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

def get_country_city(lat, long):
    country = tkintermapview.convert_coordinates_to_country(lat, long)
    print(country)
    city = tkintermapview.convert_coordinates_to_city(lat, long)
    return country, city

def utm_to_latlong(easting, northing, zone_number, zone_letter):
    utm_proj = pyproj.Proj(proj='utm', zone=zone_number, datum='WGS84')
    longitude, latitude = utm_proj(easting, northing, inverse=True)
    return round(latitude, 2), round(longitude, 2)

def combo_event2(value):
    global marker_2
    try:
        marker_2.delete()
    except NameError:
        pass
    result = ejecutar_query_sqlite('progra2024_final.db', 'personas_coordenadas', columns='Latitude,Longitude,Nombre,Apellido', where_column='RUT', where_value=value)
    if result:
        nombre_apellido = str(result[0][2]) + ' ' + str(result[0][3])
        marker_2 = map_widget.set_marker(result[0][0], result[0][1], text=nombre_apellido)

def combo_event(value):
    global marker_1
    try:
        marker_1.delete()
    except NameError:
        pass
    result = ejecutar_query_sqlite('progra2024_final.db', 'personas_coordenadas', columns='Latitude,Longitude,Nombre,Apellido', where_column='RUT', where_value=value)
    if result:
        nombre_apellido = str(result[0][2]) + ' ' + str(result[0][3])
        marker_1 = map_widget.set_marker(result[0][0], result[0][1], text=nombre_apellido)
        
        # Populate the second dropdown with RUTs
        ruts = [row[0] for row in ejecutar_query_sqlite('progra2024_final.db', 'personas_coordenadas', columns='RUT')]
        ruts.remove(value)  # Remove the selected RUT from the first dropdown
        optionmenu_2.configure(values=ruts)
        optionmenu_2.set("Select RUT")

def center_window(window, width, height):
    root.update_idletasks()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    x = root_x + (root_width // 2) - (width // 2)
    y = root_y + (root_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def setup_toplevel(window):
    window.geometry("400x300")
    window.title("Modificar datos")
    center_window(window, 400, 300)
    window.lift()
    window.focus_force()
    window.grab_set()

    label = ctk.CTkLabel(window, text="ToplevelWindow")
    label.pack(padx=20, pady=20)

def calcular_distancia():
    rut1 = optionmenu_1.get()
    rut2 = optionmenu_2.get()
    
    if rut1 == "Select RUT" or rut2 == "Select RUT":
        CTkMessagebox.show_info(title="Error", message="Please select two valid RUTs")
        return
    
    result1 = ejecutar_query_sqlite('progra2024_final.db', 'personas_coordenadas', columns='Latitude,Longitude', where_column='RUT', where_value=rut1)
    result2 = ejecutar_query_sqlite('progra2024_final.db', 'personas_coordenadas', columns='Latitude,Longitude', where_column='RUT', where_value=rut2)
    
    if result1 and result2:
        lat1, lon1 = result1[0]
        lat2, lon2 = result2[0]
        
        distancia = haversine(lat1, lon1, lat2, lon2)
        distance_label.configure(text=f"Distancia: {distancia:.2f} km")
        
        # Draw line between the two markers
        map_widget.set_path([(lat1, lon1), (lat2, lon2)], color="red")

def guardar_data(row_selector):
    print(row_selector.get())
    print(row_selector.table.values)

def editar_panel(root):
    global toplevel_window
    if toplevel_window is None or not toplevel_window.winfo_exists():
        toplevel_window = ctk.CTkToplevel(root)
        setup_toplevel(toplevel_window)
    else:
        toplevel_window.focus()

def seleccionar_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")])
    if archivo:
        print(f"Archivo seleccionado: {archivo}")
        leer_archivo_csv(archivo)

def on_scrollbar_move(*args):
    canvas.yview(*args)
    canvas.bbox("all")

def leer_archivo_csv(ruta_archivo):
    try:
        datos = pd.read_csv(ruta_archivo)
        datos['Latitude'], datos['Longitude'] = zip(*datos.apply(lambda row: utm_to_latlong(row['UTM_Easting'], row['UTM_Northing'], row['UTM_Zone_Number'], row['UTM_Zone_Letter']), axis=1))
        agregar_df_a_sqlite(datos, 'progra2024_final.db', 'personas_coordenadas')
        print("Datos agregados a la base de datos")
        
        # Update the dropdown menus
        ruts = [row[0] for row in ejecutar_query_sqlite('progra2024_final.db', 'personas_coordenadas', columns='RUT')]
        print(f"RUTs disponibles: {ruts}")  # Verificación de los RUTs
        optionmenu_1.configure(values=ruts)
        optionmenu_2.configure(values=ruts)
        
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")

def mostrar_datos(datos):
    boton_imprimir = ctk.CTkButton(
        master=home_frame, text="guardar informacion", command=lambda: guardar_data())
    boton_imprimir.grid(row=2, column=0, pady=(0, 20))
    
    boton_imprimir = ctk.CTkButton(
        master=data_panel_superior, text="modificar dato", command=lambda: editar_panel(root))
    boton_imprimir.grid(row=0, column=2, pady=(0, 0))
    
    # Boton para graficar
    boton_imprimir = ctk.CTkButton(
        master=home_frame, text="graficar datos", command=lambda: graficar_datos(datos))
    boton_imprimir.grid(row=2, column=3, pady=(10, 0))

def graficar_datos(datos):
    print(datos)

def select_frame_by_name(name):
    home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
    frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
    frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")

    if name == "home":
        home_frame.grid(row=0, column=1, sticky="nsew")
    else:
        home_frame.grid_forget()
    if name == "frame_2":
        second_frame.grid(row=0, column=1, sticky="nsew")
    else:
        second_frame.grid_forget()
    if name == "frame_3":
        third_frame.grid(row=0, column=1, sticky="nsew")
    else:
        third_frame.grid_forget()

def home_button_event():
    select_frame_by_name("home")

def frame_2_button_event():
    select_frame_by_name("frame_2")

def frame_3_button_event():
    select_frame_by_name("frame_3")

def change_appearance_mode_event(new_appearance_mode: str):
    ctk.set_appearance_mode(new_appearance_mode)

def mapas(panel):
    map_widget = tkintermapview.TkinterMapView(panel, width=800, height=800, corner_radius=0)
    map_widget.pack(padx=20, pady=10)
    map_widget.set_position(-33.4691, -70.641)
    map_widget.set_zoom(15)
    return map_widget

root = ctk.CTk()
root.geometry("950x450")
root.title("Proyecto final progra I 2024")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
toplevel_window = None

navigation_frame = ctk.CTkFrame(root, corner_radius=0)
navigation_frame.grid(row=0, column=0, sticky="nsew")
navigation_frame.grid_rowconfigure(4, weight=1)

navigation_frame_label = ctk.CTkLabel(navigation_frame, text="Proyecto final progra I 2024", font=ctk.CTkFont(size=15, weight="bold"))
navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

home_button = ctk.CTkButton(navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Home", fg_color="transparent", anchor="w", command=home_button_event)
home_button.grid(row=1, column=0, sticky="ew")

frame_2_button = ctk.CTkButton(navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Frame 2", fg_color="transparent", anchor="w", command=frame_2_button_event)
frame_2_button.grid(row=2, column=0, sticky="ew")

frame_3_button = ctk.CTkButton(navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Frame 3", fg_color="transparent", anchor="w", command=frame_3_button_event)
frame_3_button.grid(row=3, column=0, sticky="ew")

appearance_mode_menu = ctk.CTkOptionMenu(navigation_frame, values=["Light", "Dark", "System"], command=change_appearance_mode_event)
appearance_mode_menu.grid(row=5, column=0, padx=20, pady=20)

home_frame = ctk.CTkFrame(root, corner_radius=0, fg_color="transparent")
home_frame.grid_columnconfigure(0, weight=1)
home_frame.grid_rowconfigure(0, weight=1)
home_frame.grid_rowconfigure(1, weight=10)

label_1 = ctk.CTkLabel(home_frame, text="Home", font=ctk.CTkFont(size=20, weight="bold"))
label_1.grid(row=0, column=0, padx=30, pady=30)

data_panel_superior = ctk.CTkFrame(home_frame, corner_radius=0)
data_panel_superior.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

boton_imprimir = ctk.CTkButton(master=data_panel_superior, text="Seleccionar archivo", command=seleccionar_archivo)
boton_imprimir.grid(row=0, column=1, pady=(0, 0))

second_frame = ctk.CTkFrame(root, corner_radius=0, fg_color="transparent")
second_frame.grid_rowconfigure(0, weight=1)
second_frame.grid_columnconfigure(0, weight=1)
second_frame.grid_rowconfigure(1, weight=1)
second_frame.grid_columnconfigure(1, weight=1)

# Crear el frame superior para los comboboxes
top_frame = ctk.CTkFrame(second_frame)
top_frame.pack(side=ctk.TOP, fill=ctk.X)

# Crear el frame inferior para los dos gráficos
bottom_frame = ctk.CTkFrame(second_frame)
bottom_frame.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

# Crear los paneles izquierdo y derecho para los gráficos
left_panel = ctk.CTkFrame(bottom_frame)
left_panel.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

right_panel = ctk.CTkFrame(bottom_frame)
right_panel.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)

# Crear los paneles superior izquierdo y derecho para los comboboxes
top_left_panel = ctk.CTkFrame(top_frame)
top_left_panel.pack(side=ctk.LEFT, fill=ctk.X, expand=True)

top_right_panel = ctk.CTkFrame(top_frame)
top_right_panel.pack(side=ctk.RIGHT, fill=ctk.X, expand=True)

# Agregar un Combobox al panel superior izquierdo
combobox_left = ctk.CTkComboBox(top_left_panel, values=["Opción 1", "Opción 2", "Opción 3"])
combobox_left.pack(pady=20, padx=20)

# Agregar un Combobox al panel superior derecho
combobox_right = ctk.CTkComboBox(top_right_panel, values=["Opción 1", "Opción 2", "Opción 3"])
combobox_right.pack(pady=20, padx=20)
# Crear el gráfico de barras en el panel izquierdo
fig1, ax1 = plt.subplots()
profesiones = ["Profesion A", "Profesion B", "Profesion C", "Profesion D", "Profesion E"]
paises = ["País 1", "País 2", "País 3", "País 4", "País 5"]
x = np.arange(len(profesiones))
y = np.random.rand(len(profesiones))
ax1.bar(x, y)
ax1.set_xticks(x)
ax1.set_xticklabels(profesiones)
ax1.set_xlabel("Profesiones")
ax1.set_ylabel("Numero de profesionales")
ax1.set_title("Profesiones vs Paises")

# Integrar el gráfico en el panel izquierdo
canvas1 = FigureCanvasTkAgg(fig1, master=left_panel)
canvas1.draw()
canvas1.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

# Crear el gráfico de torta en el panel derecho
fig2, ax2 = plt.subplots()
labels = 'A', 'B', 'C', 'D'
sizes = [15, 30, 45, 10]
colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
explode = (0.1, 0, 0, 0)  # explotar la porción 1

ax2.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
ax2.axis('equal')  # para que el gráfico sea un círculo
ax2.set_title("Estado emocional vs profesion")

# Integrar el gráfico de torta en el panel derecho
canvas2 = FigureCanvasTkAgg(fig2, master=right_panel)
canvas2.draw()
canvas2.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

third_frame = ctk.CTkFrame(root, corner_radius=0, fg_color="transparent")
third_frame.grid_rowconfigure(0, weight=1)
third_frame.grid_columnconfigure(0, weight=1)
third_frame.grid_rowconfigure(1, weight=3)  # Panel inferior 3/4 más grande
# Crear dos bloques dentro del frame principal
third_frame_top =  ctk.CTkFrame(third_frame, fg_color="gray")
third_frame_top.grid(row=0, column=0,  sticky="nsew", padx=5, pady=5)
third_frame = ctk.CTkFrame(root, corner_radius=0, fg_color="transparent")
label_3 = ctk.CTkLabel(third_frame, text="Seleccionar datos", font=ctk.CTkFont(size=20, weight="bold"))
label_3.grid(row=0, column=0, padx=30, pady=30)

optionmenu_1 = ctk.CTkOptionMenu(third_frame, values=["Select RUT"], command=combo_event)
optionmenu_1.grid(row=1, column=0, padx=20, pady=10)

optionmenu_2 = ctk.CTkOptionMenu(third_frame, values=["Select RUT"], command=combo_event2)
optionmenu_2.grid(row=2, column=0, padx=20, pady=10)

calcular_button = ctk.CTkButton(third_frame, text="Calcular distancia", command=calcular_distancia)
calcular_button.grid(row=3, column=0, padx=20, pady=10)

distance_label = ctk.CTkLabel(third_frame, text="Distancia: ")
distance_label.grid(row=4, column=0, padx=20, pady=10)

map_frame = ctk.CTkFrame(third_frame, width=800, height=800)
map_frame.grid(row=5, column=0, padx=20, pady=10)

map_widget = mapas(map_frame)

root.mainloop()
select_frame_by_name("home")
toplevel_window = None
root.protocol("WM_DELETE_WINDOW", root.quit)
# Ejecutar el bucle principal de la interfaz
root.mainloop()