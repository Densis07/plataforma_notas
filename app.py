import streamlit as st
import streamlit_authenticator as stauth
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import json
from datetime import datetime
from PIL import Image
import io

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SISTEMA DE NOTAS VISIÓN 2026", layout="wide")

# --- 2. ESTILO VISUAL (NEÓN / DARK MODE) ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top right, #05162a, #000000); color: #e6f1ff; }
    .main-header { 
        background: linear-gradient(135deg, rgba(0, 242, 255, 0.1) 0%, rgba(10, 25, 47, 0.9) 100%);
        backdrop-filter: blur(15px); border: 1px solid rgba(0, 242, 255, 0.4); 
        padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 30px;
    }
    .data-card {
        background: rgba(255, 255, 255, 0.05); border-radius: 12px;
        padding: 20px; border-left: 5px solid #00f2ff; margin-bottom: 20px;
    }
    .stNumberInput input { background-color: #0a192f !important; color: #00f2ff !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SEGURIDAD Y USUARIOS ---
# Admin: Marquelis | Docente: Docente1
usuarios = {
    "usernames": {
        "Marquelis": {"name": "MARQUELIS CARVAJAL", "password": "marqueliscarvajal9@gmail.com"},
        "Docente1": {"name": "DOCENTE MULTI-GRADO", "password": "densis07"}
    }
}

# Configuración del autenticador
auth = stauth.Authenticate(usuarios, "vision_2026_auth", "secret_key_123", cookie_expiry_days=30)

# Base de datos persistente en la sesión
if 'db_notas' not in st.session_state:
    st.session_state.db_notas = []

# --- 4. MOTOR DE IA (MODELS[0]) ---
MODELO_TARGET = 'gemini-2.5-flash-preview-09-2025'

def leer_lista_estudiantes(img_bytes, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODELO_TARGET)
        img = Image.open(io.BytesIO(img_bytes))
        prompt = "Analiza esta lista. Extrae Cédula y Nombre Completo. Responde solo con JSON: [{'Cedula': '...', 'Nombre': '...'}]"
        response = model.generate_content([prompt, img])
        # Limpieza de la respuesta para asegurar JSON puro
        clean_json = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(clean_json)
    except Exception as e:
        st.error(f"Error de IA: {str(e)}")
        return None

# --- 5. INTERFAZ Y NAVEGACIÓN ---
with st.sidebar:
    st.title("VISIÓN 2026")
    rol = st.radio("Módulo de acceso:", ["Padre de Familia", "Acceso Docente/Admin"])
    st.divider()

if rol == "Padre de Familia":
    st.markdown('<div class="main-header"><h1>Portal de Padres de Familia</h1></div>', unsafe_allow_html=True)
    ced_buscar = st.text_input("Ingrese la Cédula del Estudiante para consultar:")
    
    if ced_buscar:
        registros = [n for n in st.session_state.db_notas if n['Cedula'] == ced_buscar]
        if registros:
            for n in registros:
                st.markdown(f"""
                <div class="data-card">
                    <h3 style="color:#00f2ff;">{n['Nombre']}</h3>
                    <p><b>Asignatura:</b> {n['Materia']} | <b>Grado:</b> {n['Grado']}</p>
                    <p style="font-size: 2rem; color: #00f2ff; text-align: right;"><b>NOTA: {n['Nota']}</b></p>
                    <p style="font-size: 0.8rem; text-align: right;">Registrado el {n['Fecha']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No se encontró información para la cédula indicada.")

else:
    # Autenticación para Personal Docente y Administrativo
    name, authentication_status, username = auth.login("Login", "main")
    
    if authentication_status:
        st.markdown(f'<div class="main-header"><h1>Gestión Académica - {name}</h1></div>', unsafe_allow_html=True)
        
        with st.sidebar:
            key_ai = st.text_input("Configurar Google AI API Key:", type="password")
            if username == "Marquelis":
                st.success("Acceso Total: Administradora")
            auth.logout('Cerrar Sesión', 'sidebar')

        if not key_ai:
            st.warning("⚠️ Ingrese su API Key en el menú lateral para activar el escaneo por IA.")

        tab_carga, tab_notas, tab_admin = st.tabs(["📥 Registro Estudiantes", "📝 Calificar", "📊 Dashboard Admin"])

        with tab_carga:
            st.subheader("Carga de Datos")
            c1, c2 = st.columns(2)
            with c1:
                grado = st.selectbox("Grado:", ["K"] + [f"{i}º" for i in range(1, 13)])
                materia = st.selectbox("Asignatura:", ["Español", "Matemáticas", "Ciencias", "Inglés", "Sociales", "Física", "Química"])
            with c2:
                tipo_carga = st.radio("Método:", ["Escaneo IA (Foto)", "Manual"])

            if tipo_carga == "Escaneo IA (Foto)":
                foto = st.file_uploader("Subir foto de la lista escolar:", type=['png', 'jpg', 'jpeg'])
                if foto and key_ai and st.button("🚀 Iniciar Escaneo"):
                    with st.spinner("La IA está procesando la imagen..."):
                        alumnos = leer_lista_estudiantes(foto.getvalue(), key_ai)
                        if alumnos:
                            for a in alumnos:
                                st.session_state.db_notas.append({
                                    "Cedula": a["Cedula"], "Nombre": a["Nombre"],
                                    "Grado": grado, "Materia": materia, "Nota": 3.0,
                                    "Docente": name, "Fecha": datetime.now().strftime("%d/%m/%Y")
                                })
                            st.success(f"Cargados {len(alumnos)} alumnos correctamente.")
            else:
                with st.form("manual_form", clear_on_submit=True):
                    ced_m = st.text_input("Cédula:")
                    nom_m = st.text_input("Nombre Completo:")
                    not_m = st.number_input("Nota Inicial:", 1.0, 5.0, 3.0, 0.1)
                    if st.form_submit_button("Guardar en Sistema"):
                        st.session_state.db_notas.append({
                            "Cedula": ced_m, "Nombre": nom_m, "Grado": grado,
                            "Materia": materia, "Nota": not_m, "Docente": name,
                            "Fecha": datetime.now().strftime("%d/%m/%Y")
                        })
                        st.success("Alumno registrado.")

        with tab_notas:
            st.subheader("Control de Calificaciones")
            if st.session_state.db_notas:
                for i, row in enumerate(st.session_state.db_notas):
                    with st.expander(f"👤 {row['Nombre']} ({row['Materia']})"):
                        nueva_n = st.slider("Asignar Calificación:", 1.0, 5.0, float(row['Nota']), 0.1, key=f"edit_{i}")
                        if st.button("Actualizar", key=f"btn_{i}"):
                            st.session_state.db_notas[i]['Nota'] = nueva_n
                            st.rerun()
            else:
                st.info("No hay alumnos registrados aún.")

        with tab_admin:
            if username == "Marquelis":
                st.subheader("Reporte General del Centro")
                if st.session_state.db_notas:
                    df = pd.DataFrame(st.session_state.db_notas)
                    st.metric("Población Estudiantil", len(df))
                    st.plotly_chart(px.bar(df, x="Nombre", y="Nota", color="Materia", barmode="group", title="Rendimiento por Estudiante"), use_container_width=True)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Esperando registros para generar estadísticas.")
            else:
                st.error("🔒 Área exclusiva para la Dirección (Marquelis).")

    elif authentication_status == False:
        st.error("Usuario o contraseña incorrectos.")
    elif authentication_status == None:
        st.info("Por favor, inicie sesión.")
