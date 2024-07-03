import sqlite3
import matplotlib.pyplot as plt
from tkinter import Tk, Label, StringVar, ttk
from tkinter.ttk import Combobox, Separator

# Función para obtener países desde la base de datos
def obtener_paises_desde_db(db_file):
    try:
        conexion = sqlite3.connect(db_file)
        cursor = conexion.cursor()

        consulta = """
        SELECT DISTINCT Pais
        FROM personas;
        """
        cursor.execute(consulta)
        resultados = cursor.fetchall()

        paises = [resultado[0] for resultado in resultados]

        return paises

    except sqlite3.Error as error:
        print("Error al conectar a la base de datos SQLite:", error)
        return []

    finally:
        if conexion:
            conexion.close()

# Función para obtener profesiones desde la base de datos
def obtener_profesiones_desde_db(db_file):
    try:
        conexion = sqlite3.connect(db_file)
        cursor = conexion.cursor()

        consulta = """
        SELECT DISTINCT Profesion
        FROM personas;
        """
        cursor.execute(consulta)
        resultados = cursor.fetchall()

        profesiones = [resultado[0] for resultado in resultados]

        return profesiones

    except sqlite3.Error as error:
        print("Error al conectar a la base de datos SQLite:", error)
        return []

    finally:
        if conexion:
            conexion.close()

# Función para graficar personas por profesión en un país específico
def grafico_personas_por_profesion_en_pais(db_file, pais):
    try:
        conexion = sqlite3.connect(db_file)
        cursor = conexion.cursor()

        # Obtener todas las profesiones
        profesiones = obtener_profesiones_desde_db(db_file)

        # Crear lista para almacenar cantidad de personas por profesión en el país específico
        datos_profesiones = []

        # Obtener datos de cantidad de personas por profesión en el país especificado
        for profesion in profesiones:
            consulta = f"""
            SELECT COUNT(*) AS Cantidad
            FROM personas
            WHERE Profesion = '{profesion}' AND Pais = '{pais}';
            """
            cursor.execute(consulta)
            resultado = cursor.fetchone()
            cantidad_personas = resultado[0] if resultado else 0
            datos_profesiones.append(cantidad_personas)

        # Gráfico de barras por cantidad de personas por profesión en el país específico
        fig, ax = plt.subplots(figsize=(10, 6))
        x = range(len(profesiones))

        ax.bar(x, datos_profesiones, color='blue')
        ax.set_xlabel('Profesión')
        ax.set_ylabel('Cantidad de Personas')
        ax.set_title(f'Cantidad de Personas por Profesión en {pais}')
        ax.set_xticks(x)
        ax.set_xticklabels(profesiones, rotation=45, ha='right')

        plt.tight_layout()
        plt.show()

    except sqlite3.Error as error:
        print("Error al conectar a la base de datos SQLite:", error)

    finally:
        if conexion:
            conexion.close()

# Función para manejar el evento de selección de país desde la interfaz gráfica
def seleccionar_pais(event):
    pais_seleccionado = cmb_paises.get()
    grafico_personas_por_profesion_en_pais('progra2024_final.db', pais_seleccionado)

# Configuración básica de la interfaz gráfica de Tkinter
root = Tk()
root.title("Visualización de Datos")

# Obtener la lista de países desde la base de datos
paises = obtener_paises_desde_db('progra2024_final.db')

# Crear etiqueta y combobox para seleccionar el país
lbl_pais = Label(root, text="Seleccione un País:")
lbl_pais.pack(pady=10)

cmb_paises = Combobox(root, values=paises)
cmb_paises.pack()

# Manejar el evento de selección de país
cmb_paises.bind("<<ComboboxSelected>>", seleccionar_pais)

root.mainloop()

