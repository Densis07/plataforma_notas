import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# Conexión BD
conn = sqlite3.connect("notas.db")
c = conn.cursor()

# Panel docente
st.sidebar.title("Panel Docente")
with st.sidebar.form("subir_notas"):
    cedula = st.text_input("Cédula del estudiante")
    materia = st.text_input("Materia")
    fecha_actividad = st.date_input("Fecha de la actividad", value=date.today())
    tema = st.text_input("Tema de la actividad")
    nota = st.slider("Nota (1–5)", 1.0, 5.0, step=0.5)
    apreciacion = st.slider("Apreciación (1–5)", 1.0, 5.0, step=0.5)
    docente = st.text_input("Nombre del docente")
    enviar = st.form_submit_button("Guardar nota")
    if enviar:
        c.execute("SELECT id FROM Materias WHERE nombre=?", (materia,))
        materia_id = c.fetchone()
        if materia_id:
            c.execute("""INSERT INTO Notas (cedula_estudiante, id_materia, fecha, tema, nota, apreciacion, docente)
                         VALUES (?, ?, ?, ?, ?, ?, ?)""",
                      (cedula, materia_id[0], str(fecha_actividad), tema, nota, apreciacion, docente))
            conn.commit()
            st.success("✅ Nota guardada correctamente")
        else:
            st.error("⚠️ La materia no existe en la base de datos")

# Panel padres
st.title("Consulta de notas")
cedula_padre = st.text_input("Ingrese la cédula del estudiante")
if cedula_padre:
    query = """SELECT fecha, tema, m.nombre AS materia, nota, apreciacion, docente 
               FROM Notas n 
               JOIN Materias m ON n.id_materia = m.id 
               WHERE cedula_estudiante=?"""
    df = pd.read_sql_query(query, conn, params=(cedula_padre,))
    if not df.empty:
        st.subheader("Historial de notas")
        st.dataframe(df)

        st.subheader("Gráfico de desempeño")
        st.line_chart(df.set_index("fecha")[["nota", "apreciacion"]])

        promedio_nota = df["nota"].mean()
        promedio_apreciacion = df["apreciacion"].mean()
        st.write(f"📊 Promedio Nota: {promedio_nota:.2f}")
        st.write(f"📊 Promedio Apreciación: {promedio_apreciacion:.2f}")

        if promedio_nota < 3.0 or promedio_apreciacion < 3.0:
            st.error("⚠️ El estudiante está en riesgo académico")
    else:
        st.warning("No se encontraron notas para esta cédula")
