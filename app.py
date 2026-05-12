import streamlit as st
import streamlit_authenticator as stauth
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# 1. Configuración de Seguridad 🔐
credentials = {
    "usernames": {
        "Marquelis": {"name": "MARQUELIS CARVAJAL", "password": "marqueliscarvajal9@gmail.com"},
        "Docente1": {"name": "DOCENTE MULTI-GRADO", "password": "densis07"}
    }
}

auth = stauth.Authenticate(credentials, "vision_cookie", "vision_key", 30)

# 2. Base de datos temporal en la sesión 📊
if 'db_notas' not in st.session_state:
    st.session_state.db_notas = []

# 3. Interfaz de Inicio de Sesión
auth.login(location='main')

if st.session_state["authentication_status"]:
    st.sidebar.write(f"Bienvenido, {st.session_state['name']} 👋")
    auth.logout('Cerrar Sesión', 'sidebar')
    
    # Aquí es donde el docente puede registrar notas o ver el dashboard
    st.title("Gestión Académica Visión 2026")
    
    # Ejemplo de formulario manual
    with st.form("registro_notas"):
        nombre = st.text_input("Nombre del Estudiante")
        nota = st.number_input("Calificación", 1.0, 5.0, 3.0)
        if st.form_submit_button("Guardar Nota"):
            st.session_state.db_notas.append({"Nombre": nombre, "Nota": nota, "Fecha": datetime.now()})
            st.success("Nota registrada con éxito")

elif st.session_state["authentication_status"] is False:
    st.error("Usuario o contraseña incorrectos")
