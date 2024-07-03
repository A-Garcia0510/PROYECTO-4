

# Función para obtener países desde la base de datos
def obtener_paises_desde_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT Pais FROM Personas")
    paises = [row[0] for row in cursor.fetchall()]
    conn.close()
    return paises

paises = obtener_paises_desde_db('progra2024_final.db')
paises.insert(0, 'Seleccione país')  # Agregar una opción predeterminada
combobox_left = ctk.CTkComboBox(top_left_panel, values=paises)
combobox_left.pack(pady=20, padx=20)
combobox_left.bind("<<ComboboxSelected>>",'seleccionar_pais')


# Función para obtener estados emocionales desde la base de datos
def obtener_estados_emocionales_desde_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT Estado_Emocional FROM Personas")
    estados_emocionales = [row[0] for row in cursor.fetchall()]
    conn.close()
    return estados_emocionales

estados_emocionales = obtener_estados_emocionales_desde_db('progra2024_final.db')
estados_emocionales.insert(0, 'Seleccione Estado Emocional')
# Agregar un Combobox al panel superior derecho
combobox_right = ctk.CTkComboBox(top_right_panel, values=estados_emocionales)
combobox_right.pack(pady=20, padx=20)