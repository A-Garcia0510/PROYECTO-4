import sqlite3
import matplotlib.pyplot as plt
from tkinter import Tk, StringVar
from tkinter.ttk import Combobox

def ejecutar_query_sqlite(database_name, query):
    """
    Ejecuta una consulta SQL en una base de datos SQLite y retorna una lista con los resultados.

    Parámetros:
    database_name (str): Nombre del archivo de la base de datos SQLite.
    query (str): Consulta SQL a ejecutar.

    Retorna:
    list: Lista con los resultados de la consulta.
    """
    # Conectar a la base de datos SQLite
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # Ejecutar la consulta SQL
    cursor.execute(query)

    # Obtener los resultados de la consulta
    resultados = cursor.fetchall()

    # Cerrar la conexión
    conn.close()

    return resultados

def obtener_estados_emocionales(database_name):
    """
    Obtiene la lista de estados emocionales disponibles en la base de datos.

    Parámetros:
    database_name (str): Nombre del archivo de la base de datos SQLite.

    Retorna:
    list: Lista de estados emocionales.
    """
    query = "SELECT DISTINCT Estado_Emocional FROM personas;"
    estados_emocionales = [resultado[0] for resultado in ejecutar_query_sqlite(database_name, query)]
    return estados_emocionales

def obtener_profesiones(database_name):
    """
    Obtiene la lista de profesiones disponibles en la base de datos.

    Parámetros:
    database_name (str): Nombre del archivo de la base de datos SQLite.

    Retorna:
    list: Lista de profesiones.
    """
    query = "SELECT DISTINCT Profesion FROM personas;"
    profesiones = [resultado[0] for resultado in ejecutar_query_sqlite(database_name, query)]
    return profesiones

def obtener_porcentaje_por_estado_emocional(database_name, profesion_seleccionada):
    """
    Obtiene el porcentaje de personas en cada estado emocional para una profesión seleccionada.

    Parámetros:
    database_name (str): Nombre del archivo de la base de datos SQLite.
    profesion_seleccionada (str): Profesión seleccionada.

    Retorna:
    dict: Diccionario donde las claves son los estados emocionales y los valores son los porcentajes.
    """
    query = f"SELECT Estado_Emocional, COUNT(*) FROM personas WHERE Profesion = '{profesion_seleccionada}' GROUP BY Estado_Emocional;"
    resultados = ejecutar_query_sqlite(database_name, query)
    total_personas = sum([resultado[1] for resultado in resultados])
    porcentajes = {resultado[0]: (resultado[1] / total_personas) * 100 for resultado in resultados}
    return porcentajes

def crear_grafico_circular(profesion_seleccionada, porcentajes):
    """
    Crea y muestra un gráfico circular con los porcentajes de personas en cada estado emocional.

    Parámetros:
    profesion_seleccionada (str): Profesión seleccionada.
    porcentajes (dict): Diccionario donde las claves son los estados emocionales y los valores son los porcentajes.
    """
    labels = list(porcentajes.keys())
    sizes = list(porcentajes.values())

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title(f'Porcentaje de Profesionales por Estado Emocional en la profesión "{profesion_seleccionada}"')

    # Mostrar el gráfico
    plt.show()

def seleccionar_profesion(event):
    profesion_seleccionada = combobox_profesion.get()
    porcentajes = obtener_porcentaje_por_estado_emocional(database_name, profesion_seleccionada)
    crear_grafico_circular(profesion_seleccionada, porcentajes)

# Nombre de tu base de datos SQLite
database_name = 'progra2024_final.db'

# Crear la ventana principal de tkinter
root = Tk()
root.title('Selección de Profesión y Estado Emocional')

# Obtener las profesiones disponibles desde la base de datos
profesiones = obtener_profesiones(database_name)

# Crear un Combobox para seleccionar la profesión
combobox_profesion = Combobox(root, values=profesiones)
combobox_profesion.current(0)  # Establecer la primera profesión como predeterminada
combobox_profesion.pack(pady=20)
combobox_profesion.bind('<<ComboboxSelected>>', seleccionar_profesion)

# Ejecutar la interfaz gráfica
root.mainloop()
