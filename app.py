import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# 1. Configuración de página
st.set_page_config(page_title="Dashboard Biomecánica & Rendimiento", layout="wide", initial_sidebar_state="expanded")

# 2. Estilo estético y Semáforos (CSS)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .metric-box { background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 10px;}
    .semaforo-verde { border-left: 5px solid #28A745; }
    .semaforo-amarillo { border-left: 5px solid #FFC107; }
    .semaforo-rojo { border-left: 5px solid #DC3545; }
    </style>
""", unsafe_allow_html=True)

# 3. Función para leer archivos de Valkyria Trainer
def extraer_datos_valkyria(file):
    try:
        # Leer como CSV o Excel según el formato
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, header=None)
        else:
            df = pd.read_excel(file, header=None)
        
        # Las métricas están en la columna 0 y los valores en la 1
        f_pico = df[df[0] == 'Fuerza Pico (N)'][1].values[0]
        rfd_250 = df[df[0] == 'RFD en 250 (N/s)'][1].values[0]
        return float(f_pico), float(rfd_250)
    except Exception as e:
        return None, None

# --- SIDEBAR: Branding y Carga de Datos ---
st.sidebar.markdown("## Laboratorio de Biomecánica")
if os.path.exists("logo_evoxx.png"):
    st.sidebar.image("logo_evoxx.png", use_container_width=True)
elif os.path.exists("logo_evoxx.jpg"):
    st.sidebar.image("logo_evoxx.jpg", use_container_width=True)
else:
    st.sidebar.info("💡 Tip: Guardá tu logo como 'logo_evoxx.png' o '.jpg' en esta carpeta.")

st.sidebar.markdown("---")
st.sidebar.markdown("### Navegación")
st.sidebar.info("Utilizá las pestañas principales para navegar entre la Base de Datos Histórica y la Calculadora Valkyria.")

# --- TITULO DE LA APP ---
st.title("📊 Análisis de Rendimiento y Biomecánica")

# --- CUADRO PRINCIPAL DE PESTAÑAS ---
tab1, tab_valkyria, tab2, tab4 = st.tabs(["🚀 Rendimiento Histórico", "⚡ Dinamometría Valkyria (NUEVO)", "🧠 Carga & Wellness", "🩹 RTP & Referencias"])


# ================= TAB: VALKYRIA TRAINER =================
with tab_valkyria:
    st.subheader("Análisis Automatizado de Dinamometría")
    st.markdown("Subí los archivos exportados del Valkyria Trainer 6 para calcular automáticamente Asimetrías y Ratios H:Q.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Cuádriceps (Cadena Anterior)")
        quad_izq = st.file_uploader("Cuádriceps IZQUIERDO", type=['xlsx', 'csv'], key="q_i")
        quad_der = st.file_uploader("Cuádriceps DERECHO", type=['xlsx', 'csv'], key="q_d")
        
    with col2:
        st.markdown("#### Isquiosurales (Cadena Posterior)")
        isq_izq = st.file_uploader("Isquiosural IZQUIERDO", type=['xlsx', 'csv'], key="i_i")
        isq_der = st.file_uploader("Isquiosural DERECHO", type=['xlsx', 'csv'], key="i_d")

    st.markdown("---")
    
    # --- LOGICA DE PROCESAMIENTO ---
    if quad_izq and quad_der and isq_izq and isq_der:
        st.success("✅ Archivos cargados correctamente. Procesando datos...")
        
        # Extraer datos
        fp_q_i, rfd_q_i = extraer_datos_valkyria(quad_izq)
        fp_q_d, rfd_q_d = extraer_datos_valkyria(quad_der)
        fp_i_i, rfd_i_i = extraer_datos_valkyria(isq_izq)
        fp_i_d, rfd_i_d = extraer_datos_valkyria(isq_der)
        
        if None not in [fp_q_i, fp_q_d, fp_i_i, fp_i_d]:
            # --- SECCIÓN 1: ASIMETRÍAS ---
            st.markdown("### 1. Asimetrías Bilaterales (Fuerza Pico)")
            c_q, c_i = st.columns(2)
            
            # Asimetría Cuádriceps
            asim_quad = round(((fp_q_i - fp_q_d) / max(fp_q_i, fp_q_d)) * 100, 1)
            with c_q:
                st.markdown("**Cuádriceps**")
                st.write(f"Izq: {fp_q_i} N | Der: {fp_q_d} N")
                if abs(asim_quad) > 15:
                    st.markdown(f"<div class='metric-box semaforo-rojo'>🔴 <b>Asimetría: {abs(asim_quad)}%</b> (Riesgo Alto)</div>", unsafe_allow_html=True)
                elif abs(asim_quad) > 10:
                    st.markdown(f"<div class='metric-box semaforo-amarillo'>🟡 <b>Asimetría: {abs(asim_quad)}%</b> (Riesgo Moderado)</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='metric-box semaforo-verde'>🟢 <b>Asimetría: {abs(asim_quad)}%</b> (Óptimo)</div>", unsafe_allow_html=True)

            # Asimetría Isquios
            asim_isq = round(((fp_i_i - fp_i_d) / max(fp_i_i, fp_i_d)) * 100, 1)
            with c_i:
                st.markdown("**Isquiosurales**")
                st.write(f"Izq: {fp_i_i} N | Der: {fp_i_d} N")
                if abs(asim_isq) > 15:
                    st.markdown(f"<div class='metric-box semaforo-rojo'>🔴 <b>Asimetría: {abs(asim_isq)}%</b> (Riesgo Alto)</div>", unsafe_allow_html=True)
                elif abs(asim_isq) > 10:
                    st.markdown(f"<div class='metric-box semaforo-amarillo'>🟡 <b>Asimetría: {abs(asim_isq)}%</b> (Riesgo Moderado)</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='metric-box semaforo-verde'>🟢 <b>Asimetría: {abs(asim_isq)}%</b> (Óptimo)</div>", unsafe_allow_html=True)

            # --- SECCIÓN 2: RATIO H:Q ---
            st.markdown("### 2. Relación Isquiosural / Cuádriceps (Ratio H:Q)")
            st.caption("Valores normativos de referencia: > 0.60 para fuerza isométrica máxima (varía según velocidad angular en isocinético, pero adaptamos a dinamometría estática).")
            
            col_hq1, col_hq2 = st.columns(2)
            
            # Pierna Izquierda
            hq_izq = round(fp_i_i / fp_q_i, 2)
            with col_hq1:
                if hq_izq >= 0.60:
                    st.markdown(f"<div class='metric-box semaforo-verde'>🟢 <b>Ratio H:Q Izquierdo: {hq_izq}</b> - Apto</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='metric-box semaforo-rojo'>🔴 <b>Ratio H:Q Izquierdo: {hq_izq}</b> - Déficit Posterior</div>", unsafe_allow_html=True)
            
            # Pierna Derecha
            hq_der = round(fp_i_d / fp_q_d, 2)
            with col_hq2:
                if hq_der >= 0.60:
                    st.markdown(f"<div class='metric-box semaforo-verde'>🟢 <b>Ratio H:Q Derecho: {hq_der}</b> - Apto</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='metric-box semaforo-rojo'>🔴 <b>Ratio H:Q Derecho: {hq_der}</b> - Déficit Posterior</div>", unsafe_allow_html=True)
                    
            # --- SECCIÓN 3: RFD ---
            st.markdown("### 3. Tasa de Desarrollo de la Fuerza (RFD en 250ms)")
            fig_rfd = px.bar(x=['Quad Izq', 'Quad Der', 'Isq Izq', 'Isq Der'], 
                             y=[rfd_q_i, rfd_q_d, rfd_i_i, rfd_i_d],
                             labels={'x':'Grupo Muscular', 'y':'RFD (N/s)'},
                             title="Capacidad Explosiva a 250ms",
                             color=['Cuádriceps', 'Cuádriceps', 'Isquios', 'Isquios'],
                             color_discrete_map={'Cuádriceps':'#007BFF', 'Isquios':'#FF8C00'})
            st.plotly_chart(fig_rfd, use_container_width=True)

        else:
            st.error("Hubo un error al leer las variables. Asegurate de que los archivos sean los originales del Valkyria Trainer.")
    else:
        st.info("⬆️ Subí los 4 archivos en los casilleros de arriba para generar el reporte de dinamometría completo.")


# ================= TAB 1: RENDIMIENTO HISTORICO =================
with tab1:
    st.subheader("Simulación de Base de Datos")
    st.write("Esta sección usará tu Excel general (cuando lo armes) para graficar históricos. Por ahora, está en modo espera de tu base de datos principal.")

# ================= TAB 2: SALUD & WELLNESS =================
with tab2:
    st.subheader("Simulación de Carga y Wellness")
    st.write("Acá irán los cuestionarios diarios y la carga aguda/crónica.")

# ================= TAB 4: RTP & REFERENCIAS =================
with tab4:
    st.subheader("Return to Play (RTP) - Control Clínico")
    # Tabla de Evidencia
    ref_data = {
        "Métrica Evaluada": ["Ratio H:Q (Isométrico/Dinamómetro)", "Asimetría Fuerza Bilateral", "ACWR (Carga Aguda/Crónica)", "RSI (Reactividad)"],
        "Rango Óptimo / RTP": ["> 0.60 (Variable s/ ángulo)", "< 10%", "0.8 - 1.3", "> 2.5 (Atletas de campo)"],
        "Riesgo / Alerta": ["< 0.50", "> 15%", "< 0.8 o > 1.5", "< 1.5"],
        "Fuente (Evidencia)": ["Aagaard et al. (1998)", "Bishop et al. (2018). Sports Med.", "Gabbett (2016). BJSM.", "Flanagan et al. (2008). JSCR."]
    }
    st.dataframe(pd.DataFrame(ref_data), hide_index=True, use_container_width=True)