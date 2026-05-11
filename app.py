return json.loads(data)
    except Exception as e:
        return None
def generar_secuencia_meduca(tema, grado, materia, api_key):
    """Genera secuencia didáctica de 40 min con formato obligatorio MEDUCA 2014"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
    prompt = f"""
    Eres un experto en el currículo de Panamá (MEDUCA 2014). Genera una secuencia didáctica para:
    Tema: {tema} | Grado: {grado} | Asignatura: {materia}.
    
    ESTRUCTURA OBLIGATORIA:
    1. Objetivos de Aprendizaje.
    2. Metas e Indicadores de Logro.
    3. Aprendizajes Fundamentales (DFA).
    4. Actividades detalladas (Día 1, Día 2, Día 3, Día 4, Día 5) separadas visualmente.
    5. Cuadro de Contenidos:
       - CONCEPTUAL
       - PROCEDIMENTAL
       - ACTITUDINAL
    Los párrafos deben ser fluidos, sin errores de símbolos y con una estética profesional para imprimir.
    """
    try:
        return model.generate_content(prompt).text
    except:
        return "Error en la conexión con la IA. Verifique su API Key."

# ==============================================================================
# 4. NAVEGACIÓN Y PERFILES
# ==============================================================================
with st.sidebar:
    st.markdown("### 🏫 ACCESO AL PORTAL")
    perfil_acceso = st.radio("Identificarse como:", ["Padre de Familia", "Personal Administrativo/Docente"])
    st.divider()

# --- VISTA: PADRE DE FAMILIA ---
if perfil_acceso == "Padre de Familia":
    st.markdown('<div class="main-header"><h1>Portal de Consulta para Padres</h1><p>Sistema Académico Visión 2026</p></div>', unsafe_allow_html=True)
    st.info("💡 Ingrese la Cédula de su acudido para visualizar sus notas y progreso actual.")
    
    ced_input = st.text_input("Cédula del Estudiante (Ej: 8-000-0000):")
    
    if ced_input:
        registros = [r for r in st.session_state.db_global if r['Cedula'] == ced_input]
        if registros:
            st.success(f"Se encontraron {len(registros)} registros para esta identificación.")
            for r in registros:
                st.markdown(f"""
                <div class="parent-card">
                    <div style="float: right;"><span class="grade-badge">{r['Final']}</span></div>
                    <h3>{r['Nombre']}</h3>
                    <p><b>Grado:</b> {r['Grado']} | <b>Materia:</b> {r['Materia']}</p>
                    <p><b>Docente:</b> {r['Docente']}</p>
                    <hr style="border-color: rgba(0,242,255,0.2)">
                    <p style="font-style: italic; color: #00f2ff;">Estatus Académico: {r.get('Obs', 'Actualización constante.')}</p>
                    <p style="font-size: 0.8em; color: #888;">Fecha de Registro: {r['Fecha']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            df_hist = pd.DataFrame(registros)
            fig_hist = px.bar(df_hist, x='Materia', y='Final', color='Final', title="Rendimiento por Asignatura")
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.warning("Cédula no encontrada en el sistema actual.")

# --- VISTA: DOCENTE / ADMINISTRATIVO (DENSIS) ---
else:
    name, status, username = auth.login(location='main')

    if status:
        st.markdown(f'<div class="main-header"><h1>Gestión Académica Visión 2026</h1><p>Bienvenida Directora {name}</p></div>', unsafe_allow_html=True)

        with st.sidebar:
            st.markdown("### ⚙️ CONFIGURACIÓN")
            api_key = st.text_input("Google AI API Key:", type="password")
            
            # Gestión de tiempos
            if username != "Densis":
                if 't_exp' not in st.session_state: st.session_state.t_exp = datetime.now() + timedelta(minutes=40)
                t_rem = st.session_state.t_exp - datetime.now()
                st.warning(f"⏳ Tiempo de Planificación: {int(max(0, t_rem.total_seconds() // 60))} min")
            else:
                st.info("👑 Densis: Acceso Administrativo Ilimitado")
            
            auth.logout('Cerrar Sesión', 'sidebar')

        if not api_key:
            st.error("📢 Ingrese su API Key para habilitar la Visión IA y Planificación.")

        tabs = st.tabs(["📸 CARGA DE LISTAS (IA)", "📝 SECUENCIA DIDÁCTICA", "📈 DASHBOARD DENSIS"])

        # TAB 1: CARGA VISUAL (PARA LA IMAGEN DE EXCEL)
        with tabs[0]:
            st.subheader("Importación Visual de Alumnos")
            st.write("Suba la captura de pantalla de su lista de Excel para procesar datos automáticamente.")
            
            c1, c2 = st.columns(2)
            with c1:
                g_sel = st.selectbox("Asignar Grado:", ["K"] + [f"{i}º" for i in range(1, 13)])
                m_sel = st.selectbox("Asignatura:", ["Matemáticas", "Español", "Ciencias", "Inglés", "Física", "Historia"])
                n_ini = st.number_input("Nota Promedio Inicial:", 1.0, 5.0, 3.0)
            with c2:
                img_up = st.file_uploader("Subir Imagen del Listado:", type=['png', 'jpg', 'jpeg'])

            if img_up and api_key:
                if st.button("🚀 Iniciar Reconocimiento IA"):
                    with st.spinner("Procesando nombres y cédulas con Visión Artificial..."):
                        datos = motor_ia_vision(img_up.getvalue(), api_key)
                        if datos:
                            for est in datos:
                                st.session_state.db_global.append({
                                    "Cedula": est["Cedula"], "Nombre": est["Nombre"],
                                    "Grado": g_sel, "Materia": m_sel, "Final": n_ini,
                                    "Docente": name, "Fecha": datetime.now().strftime('%d/%m/%Y'),
                                    "Obs": "Validación visual exitosa."
                                })
                            st.balloons()
                            st.success(f"¡Éxito! Se registraron {len(datos)} estudiantes.")
                        else:
                            st.error("Error al leer la imagen. Verifique la calidad o el formato.")

        # TAB 2: PLANIFICACIÓN (DENSIS MASTER)
        with tabs[1]:
            st.subheader("Generador de Secuencias (Formato MEDUCA)")
            tema_txt = st.text_input("Tema a Planificar:")
            if st.button("🪄 Generar Estructura Académica"):
                if api_key and tema_txt:
                    with st.spinner("Construyendo contenidos Conceptual, Procedimental y Actitudinal..."):
                        plan_meduca = generar_secuencia_meduca(tema_txt, g_sel, m_sel, api_key)
                        st.markdown(f'<div class="sequence-block">{plan_meduca}</div>', unsafe_allow_html=True)

        # TAB 3: DASHBOARD ADMINISTRATIVO (DENSIS)
        with tabs[2]:
            if username == "Densis":
                st.subheader("Analítica Institucional Visión 2026")
                if st.session_state.db_global:
                    df = pd.DataFrame(st.session_state.db_global)
                    
                    k1, k2, k3 = st.columns(3)
                    k1.metric("Promedio Institucional", round(df['Final'].mean(), 2))
                    k2.metric("Alumnos Registrados", len(df['Cedula'].unique()))
                    k3.metric("Grados Cubiertos", df['Grado'].nunique())
                    
                    st.divider()
                    
                    fig_rend = px.box(df, x='Grado', y='Final', color='Materia', title="Rendimiento Académico Global")
                    st.plotly_chart(fig_rend, use_container_width=True)
                    
                    st.markdown("#### Alerta de Rendimiento (Debajo de 3.0)")
                    st.dataframe(df[df['Final'] < 3.0], use_container_width=True)
                else:
                    st.info("Sin datos para analizar. Los docentes deben subir listas primero.")
            else:
                st.warning("⚠️ Acceso exclusivo para la Directora Densis Carvajal.")

elif status is False:
    st.error("Credenciales incorrectas.")
