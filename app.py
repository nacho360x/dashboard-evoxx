import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Laboratorio Biomecánica | Evoxx", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Open Sans', sans-serif; }
    .main { background-color: #F4F6F8; }
    .metric-card { 
        background-color: #FFFFFF; padding: 22px; border-radius: 12px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.04); margin-bottom: 20px;
    }
    .titulo-evoxx { color: #111111; font-weight: 800; font-size: 2.4rem; margin-bottom: 2px; }
    .subtitulo-evoxx { color: #00AFBD; font-weight: 700; font-size: 1.1rem; margin-bottom: 25px; text-transform: uppercase;}
    .section-title { color: #1A365D; font-weight: 700; font-size: 1.3rem; margin-top: 10px; margin-bottom: 15px; border-bottom: 2px solid #E2E8F0; padding-bottom: 5px;}
    </style>
""", unsafe_allow_html=True)

# --- 2. MEMORIA DE LA APLICACIÓN ---
if 'datos_atleta' not in st.session_state:
    st.session_state.datos_atleta = {
        'nombre': '', 'peso': 75.0,
        'cmj': {'f_max_propulsiva': 0.0, 'f_pico': 0.0, 'asim_frenado': 0.0, 'asim_despegue': 0.0, 'asim_aterrizaje': 0.0, 'rfd_100': 0.0, 'rfd_250': 0.0, 'altura': 0.0, 't_fpico': 0.0},
        'imtp': {'f_pico': 0.0, 'f_media': 0.0, 'asim': 0.0, 'rfd_100': 0.0, 'rfd_250': 0.0, 't_fpico': 0.0}
    }

# --- 3. MOTOR INTELIGENTE DE EXTRACCIÓN (MEJOR REPETICIÓN Y COINCIDENCIA EXACTA) ---
def obtener_valor_exacto(df, nombre_metrica, columna_rep):
    """Busca la fila exacta y saca el valor de la columna especificada"""
    try:
        # Buscamos coincidencia EXACTA (sin espacios extra)
        fila = df[df.iloc[:, 0].astype(str).str.strip() == nombre_metrica]
        if not fila.empty:
            return float(fila.iloc[0][columna_rep])
    except:
        pass
    return 0.0

def procesar_archivo_ivolution(file):
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
            
        nombre = file.name.lower()
        
        if "cmj" in nombre:
            # 1. Buscamos cuál fue la mejor repetición basada en la Fuerza Max Propulsiva
            fila_clave = df[df.iloc[:, 0].astype(str).str.strip() == "Fuerza Max Propulsiva (N)"]
            if not fila_clave.empty:
                valores = pd.to_numeric(fila_clave.iloc[0, 1:], errors='coerce')
                mejor_rep = valores.idxmax() # Nos dice si fue Rep 1, Rep 2, etc.
                
                # 2. Extraemos todos los datos SOLO de esa mejor repetición
                st.session_state.datos_atleta['cmj']['f_max_propulsiva'] = obtener_valor_exacto(df, "Fuerza Max Propulsiva (N)", mejor_rep)
                st.session_state.datos_atleta['cmj']['asim_frenado'] = obtener_valor_exacto(df, "Asimetría Frenado (%)", mejor_rep)
                # (Se pueden sumar más métricas acá usando la misma lógica)
                return f"CMJ analizado (Se utilizó la {mejor_rep} como mejor salto)"
                
        elif "imtp" in nombre:
            fila_clave = df[df.iloc[:, 0].astype(str).str.strip() == "Fuerza Pico (N)"]
            if not fila_clave.empty:
                valores = pd.to_numeric(fila_clave.iloc[0, 1:], errors='coerce')
                mejor_rep = valores.idxmax()
                
                st.session_state.datos_atleta['imtp']['f_pico'] = obtener_valor_exacto(df, "Fuerza Pico (N)", mejor_rep)
                st.session_state.datos_atleta['imtp']['asim'] = obtener_valor_exacto(df, "Asimetría (%)", mejor_rep)
                st.session_state.datos_atleta['imtp']['rfd_100'] = obtener_valor_exacto(df, "RFD en 100 (N/s)", mejor_rep)
                st.session_state.datos_atleta['imtp']['rfd_250'] = obtener_valor_exacto(df, "RFD en 250 (N/s)", mejor_rep)
                st.session_state.datos_atleta['imtp']['t_fpico'] = obtener_valor_exacto(df, "Tiempo de Fuerza Pico (s)", mejor_rep)
                return f"IMTP analizado (Se utilizó la {mejor_rep})"
                
    except Exception as e:
        return f"Error leyendo archivo: {e}"
    return None

# --- 4. GRÁFICOS VISUALES AVANZADOS ---
def crear_grafico_aguja(valor, titulo):
    """Semáforo de Asimetrías: Verde (0-10), Amarillo (10-15), Rojo (15+)"""
    val_abs = abs(valor)
    color = "#28A745" if val_abs <= 10 else "#FFC107" if val_abs <= 15 else "#DC3545"
        
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = val_abs,
        title = {'text': titulo, 'font': {'size': 14}},
        number = {'suffix': "%", 'font': {'color': color}},
        gauge = {
            'axis': {'range': [0, 20]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 10], 'color': "rgba(40, 167, 69, 0.15)"}, # Verde
                {'range': [10, 15], 'color': "rgba(255, 193, 7, 0.15)"}, # Amarillo
                {'range': [15, 25], 'color': "rgba(220, 53, 69, 0.15)"}  # Rojo
            ]
        }
    ))
    fig.update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10))
    return fig

def crear_grafico_referencia(valor, titulo, maximo, optimo_min, optimo_max):
    """Gráfico de barra horizontal para ver dónde está el atleta respecto a la norma"""
    fig = go.Figure(go.Indicator(
        mode = "number+gauge", value = valor, title = {'text': titulo},
        gauge = {
            'shape': "bullet", 'axis': {'range': [0, maximo]},
            'bar': {'color': "#111111"},
            'steps': [
                {'range': [0, optimo_min], 'color': "#FCE8E6"}, # Rojo (Bajo)
                {'range': [optimo_min, optimo_max], 'color': "#E6F4EA"}, # Verde (Óptimo)
                {'range': [optimo_max, maximo], 'color': "#FEF7E0"} # Amarillo (Exceso/Déficit)
            ]
        }
    ))
    fig.update_layout(height=120, margin=dict(l=100, r=20, t=20, b=20))
    return fig


# --- 5. INTERFAZ Y NAVEGACIÓN ---
with st.sidebar:
    if os.path.exists("logo_evoxx.png"): st.image("logo_evoxx.png")
    menu = st.radio("Secciones:", ["📥 Carga y Edición de Datos", "🧠 Índices Globales (DSI)", "🧱 Análisis Isométrico (IMTP)"])

st.markdown('<p class="titulo-evoxx">LABORATORIO DE BIOMECÁNICA</p>', unsafe_allow_html=True)

# ----- PESTAÑA: CARGA Y EDICIÓN (CON OVERRIDE MANUAL) -----
if menu == "📥 Carga y Edición de Datos":
    st.markdown('<p class="subtitulo-evoxx">Ingreso de Archivos y Revisión Manual</p>', unsafe_allow_html=True)
    
    # Zona de Carga
    archivos = st.file_uploader("Arrastrá los archivos (CMJ, IMTP)", type=['xlsx', 'csv'], accept_multiple_files=True)
    if archivos:
        for f in archivos:
            msg = procesar_archivo_ivolution(f)
            if msg: st.success(msg)
            
    # Zona de Edición Manual (¡NUEVO!)
    with st.expander("🛠️ Corrección Manual de Datos (Clic para abrir)"):
        st.info("¿El software etiquetó mal un test o querés corregir un dato? Modificalo directamente acá y se actualizará en todos los gráficos.")
        
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            st.markdown("**Datos del Atleta**")
            st.session_state.datos_atleta['nombre'] = st.text_input("Nombre", value=st.session_state.datos_atleta['nombre'])
            st.session_state.datos_atleta['peso'] = st.number_input("Peso (kg)", value=st.session_state.datos_atleta['peso'])
            
            st.markdown("**Métricas CMJ**")
            st.session_state.datos_atleta['cmj']['f_max_propulsiva'] = st.number_input("Fuerza Max Propulsiva (N)", value=float(st.session_state.datos_atleta['cmj']['f_max_propulsiva']))
            st.session_state.datos_atleta['cmj']['asim_frenado'] = st.number_input("Asimetría Frenado (%)", value=float(st.session_state.datos_atleta['cmj']['asim_frenado']))
            
        with c_m2:
            st.markdown("**Métricas IMTP**")
            st.session_state.datos_atleta['imtp']['f_pico'] = st.number_input("Fuerza Pico (N)", value=float(st.session_state.datos_atleta['imtp']['f_pico']))
            st.session_state.datos_atleta['imtp']['asim'] = st.number_input("Asimetría IMTP (%)", value=float(st.session_state.datos_atleta['imtp']['asim']))


# ----- PESTAÑA: DSI Y GRÁFICOS DE REFERENCIA -----
elif menu == "🧠 Índices Globales (DSI)":
    cmj_f = st.session_state.datos_atleta['cmj']['f_max_propulsiva']
    imtp_f = st.session_state.datos_atleta['imtp']['f_pico']
    
    if cmj_f > 0 and imtp_f > 0:
        dsi = round(cmj_f / imtp_f, 2)
        st.markdown(f"<div class='metric-card'><h2 style='text-align:center;'>Dynamic Strength Index (DSI): {dsi}</h2></div>", unsafe_allow_html=True)
        
        # Gráfico tipo "Bullet" para ver dónde cae el DSI
        st.markdown("#### Ubicación en Referencia Clínica (DSI)")
        st.plotly_chart(crear_grafico_referencia(dsi, "DSI", 1.2, 0.60, 0.80), use_container_width=True)
    else:
        st.warning("Faltan datos de CMJ o IMTP.")

# ----- PESTAÑA: ANÁLISIS ISOMÉTRICO (CON SEMÁFOROS) -----
elif menu == "🧱 Análisis Isométrico (IMTP)":
    imtp = st.session_state.datos_atleta['imtp']
    
    if imtp['f_pico'] > 0:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='metric-card'><b>Fuerza Pico</b><h2>{imtp['f_pico']} N</h2></div>", unsafe_allow_html=True)
        with c2:
            # Semáforo Visual de Asimetría (Verde -> Amarillo -> Rojo)
            st.markdown("<div class='metric-card'><b>Control de Asimetría Bilateral</b>", unsafe_allow_html=True)
            st.plotly_chart(crear_grafico_aguja(imtp['asim'], "Asimetría IMTP"), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
