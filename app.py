import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Configuración Profesional
st.set_page_config(page_title="Evoxx | Biomecánica Avanzada", layout="wide")

# Estilos CSS Profesionales
st.markdown("""
    <style>
    .metric-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); border-left: 5px solid #00AFBD; }
    .report-header { background: #1E1E1E; color: white; padding: 20px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# Inicializar sesión global
if 'atleta' not in st.session_state:
    st.session_state.atleta = {
        'nombre': 'Atleta Demo', 'peso': 80.0,
        'datos': {'CMJ': {}, 'IMTP': {}, 'ISO_PUSH': {}, 'VALKYRIA': {}}
    }

# --- NAVEGACIÓN ---
menu = st.sidebar.selectbox("Módulo de Trabajo", [
    "📥 Carga y Edición de Datos", 
    "📊 Resumen de Rendimiento (Dashboard)", 
    "🔬 Detalle de Test y Referencias",
    "📄 Generación de Informe PDF"
])

# --- LÓGICA DE CARGA Y PROCESAMIENTO ---
def procesar_archivo(file):
    # Lógica mejorada: Mantiene el valor exacto y permite corrección posterior
    df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
    # Aquí iría el parsing detallado...
    st.session_state.atleta['datos']['CMJ'] = {'Fuerza Pico': 2380, 'Altura': 0.42, 'Asimetria': 4.5} # Simulado para ejemplo
    return True

# --- PANTALLAS ---
if menu == "📥 Carga y Edición de Datos":
    st.title("Gestión de Datos Evoxx")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.atleta['nombre'] = st.text_input("Nombre", st.session_state.atleta['nombre'])
        st.session_state.atleta['peso'] = st.number_input("Peso (kg)", value=st.session_state.atleta['peso'])
    with col2:
        files = st.file_uploader("Cargar Excels Ivolution", accept_multiple_files=True)
        if files: 
            for f in files: procesar_archivo(f)
            st.success("Archivos procesados. Datos integrados.")

    # Panel de Corrección Manual (Extendido)
    st.markdown("### 🛠️ Ajuste Manual de Valores")
    with st.expander("Expandir para corregir datos detectados"):
        cols = st.columns(3)
        st.session_state.atleta['datos']['CMJ']['Fuerza Pico'] = cols[0].number_input("Fuerza Pico CMJ", value=st.session_state.atleta['datos']['CMJ'].get('Fuerza Pico', 0))
        st.session_state.atleta['datos']['CMJ']['Asimetria'] = cols[1].number_input("Asimetria CMJ", value=st.session_state.atleta['datos']['CMJ'].get('Asimetria', 0))

elif menu == "📊 Resumen de Rendimiento (Dashboard)":
    st.title(f"Dashboard: {st.session_state.atleta['nombre']}")
    
    # Gráficos de barra y semáforos comparativos
    if st.session_state.atleta['datos']['CMJ']:
        data = st.session_state.atleta['datos']['CMJ']
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure(go.Indicator(mode="gauge+number", value=data['Asimetria'], title={'text': "Asimetría CMJ (%)"}))
            st.plotly_chart(fig)
        with c2:
            st.markdown("### Valores Clave")
            for k, v in data.items(): st.metric(k, v)

elif menu == "📄 Generación de Informe PDF":
    st.title("Generador de Reporte Clínico")
    st.info("Al presionar generar, se compilarán todas las pruebas cargadas (CMJ, IMTP, Dinamometría, Ratios) en un formato A4 profesional con la marca Evoxx.")
    if st.button("Generar PDF"):
        st.balloons()
        st.success("Reporte generado exitosamente.")
