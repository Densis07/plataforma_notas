import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# Conexión BD
conn = sqlite3.connect("notas.db")
c = conn.cursor()

# Crear tablas si no existen
c.execute("""CREATE TABLE IF NOT EXISTS Estudiantes (
    cedula TEXT PRIMARY KEY,
    nombre TEXT,
    grado TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS Materias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS Notas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cedula_estudiante TEXT,
    id_materia INTEGER,
    fecha TEXT,
    nota REAL,
    apreciacion TEXT,
    docente TEXT
)""")

conn.commit()

# Panel docente
st.sidebar.title("Panel Docente")
with st.sidebar.form("subir_notas"):
    cedula = st.text_input("Cédula del estudiante")
    materia = st.text_input("Materia")
    nota = st.number_input("Nota", 0.0, 5.0, step=0.1)
    apreciacion = st.text_area("Apreciación")
    docente = st.text_input("Nombre del docente")
    enviar = st.form_submit_button("Guardar nota")
    if enviar:
        c.execute("INSERT INTO Notas (cedula_estudiante, id_materia, fecha, nota, apreciacion, docente) VALUES (?, ?, ?, ?, ?, ?)",
                  (cedula, 1, str(date.today()), nota, apreciacion, docente))
        conn.commit()
        st.success("Nota guardada correctamente")

# Panel padres
st.title("Consulta de notas")
cedula_padre = st.text_input("Ingrese la cédula del estudiante")
if cedula_padre:
    df = pd.read_sql_query("SELECT fecha, materia, nota, apreciacion FROM Notas JOIN Materias ON Notas.id_materia = Materias.id WHERE cedula_estudiante=?", conn, params=(cedula_padre,))
    if not df.empty:
        st.dataframe(df)
        st.bar_chart(df.set_index("fecha")["nota"])
        promedio = df["nota"].mean()
        if promedio < 3.0:
            st.error("⚠️ El estudiante está en riesgo académico")
    else:
        st.warning("No se encontraron notas para esta cédula")
