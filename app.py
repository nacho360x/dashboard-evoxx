import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURACIÓN Y ESTILOS EVOXX ---
st.set_page_config(page_title="Laboratorio Biomecánica | Evoxx", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Open Sans', sans-serif; }
    .main { background-color: #F8F9FA; }
    .metric-card { 
        background-color: #FFFFFF; padding: 20px; border-radius: 8px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 20px;
        border-top: 4px solid #00AFBD; 
    }
    .titulo-evoxx { color: #1E1E1E; font-weight: 800; font-size: 2.5rem; margin-bottom: 0px;}
    .subtitulo-evoxx { color: #00AFBD; font-weight: 700; margin-bottom: 20px;}
    .alerta-verde { border-top: 4px solid #28A745; }
    .alerta-amarilla { border-top: 4px solid #FFC107; }
    .alerta-roja { border-top: 4px solid #DC3545; }
    </style>
""", unsafe_allow_html=True)

# --- 2. MEMORIA DE LA APLICACIÓN ---
if 'datos_atleta' not in st.session_state:
    st.session_state.datos_atleta = {'nombre': '', 'peso': 75.0, 'cmj': {}, 'imtp': {}}

# --- 3. MOTOR DE LECTURA DE IVOLUTION ---
def extraer_mejor_metrica(df, nombre_metrica):
    """Busca la métrica en la columna 0 y devuelve el valor máximo entre las repeticiones"""
    try:
        fila = df[df.iloc[:, 0].astype(str).str.contains(nombre_metrica, case=False, na=False)]
        if not fila.empty:
            valores = pd.to_numeric(fila.iloc[0, 1:], errors='coerce')
            return valores.max()
    except:
        pass
    return None

def procesar_archivo_ivolution(file):
    try:
        # Lee CSV o Excel
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
            
        nombre = file.name.lower()
        
        # --- LÓGICA PARA CMJ ---
        if "cmj" in nombre:
            st.session_state.datos_atleta['cmj'] = {
                'f_max_propulsiva': extraer_mejor_metrica(df, "Fuerza Max Propulsiva \\(N\\)"),
                'asim_frenado': extraer_mejor_metrica(df, "Asimetría Frenado"),
                'rfd_frenado': extraer_mejor_metrica(df, "RFD Frenado"),
                'altura': extraer_mejor_metrica(df, "Altura") # Se ajustará según exporte real
            }
            return "CMJ procesado con éxito"
            
        # --- LÓGICA PARA IMTP ---
        elif "imtp" in nombre:
            st.session_state.datos_atleta['imtp'] = {
                'f_pico': extraer_mejor_metrica(df, "Fuerza Pico \\(N\\)"),
                'f_media': extraer_mejor_metrica(df, "Fuerza Media \\(N\\)"),
                'asim': extraer_mejor_metrica(df, "Asimetría"),
                'rfd_100': extraer_mejor_metrica(df, "RFD en 100"),
                'rfd_250': extraer_mejor_metrica(df, "RFD en 250"),
                't_fpico': extraer_mejor_metrica(df, "Tiempo de Fuerza Pico")
            }
            return "IMTP procesado con éxito"
            
    except Exception as e:
        return f"Error leyendo {file.name}: {e}"
    return None

# --- 4. BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo_evoxx.png"):
        st.image("logo_evoxx.png", use_container_width=True)
    
    st.markdown("### Navegación")
    menu = st.radio("Seleccioná un módulo:", [
        "📥 Carga de Datos", 
        "🧠 Índices Globales (DSI)",
        "🚀 Análisis Dinámico (CMJ / DJ)", 
        "🧱 Análisis Isométrico (IMTP / ISO PUSH)",
        "📚 Marco Teórico y RTP",
        "📄 Generador de Reporte PDF"
    ])

# --- 5. PANTALLAS ---
st.markdown('<p class="titulo-evoxx">LABORATORIO DE BIOMECÁNICA</p>', unsafe_allow_html=True)

# PANTALLA 1: CARGA DE DATOS
if menu == "📥 Carga de Datos":
    st.markdown('<p class="subtitulo-evoxx">Ingreso de Evaluación del Deportista</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("#### 1. Datos Clínicos")
        st.session_state.datos_atleta['nombre'] = st.text_input("Deportista", value=st.session_state.datos_atleta['nombre'])
        st.session_state.datos_atleta['peso'] = st.number_input("Peso Corporal (kg)", min_value=30.0, value=st.session_state.datos_atleta['peso'])
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("#### 2. Importar Archivos Ivolution")
        archivos = st.file_uploader("Arrastrá los archivos (CMJ, IMTP, etc.)", type=['xlsx', 'csv'], accept_multiple_files=True)
        
        if archivos:
            for arch in archivos:
                resultado = procesar_archivo_ivolution(arch)
                if resultado:
                    st.success(f"✅ {resultado}")
        st.markdown("</div>", unsafe_allow_html=True)

# PANTALLA 2: ÍNDICES GLOBALES (DSI)
elif menu == "🧠 Índices Globales (DSI)":
    st.markdown('<p class="subtitulo-evoxx">Dynamic Strength Index (DSI)</p>', unsafe_allow_html=True)
    
    cmj_data = st.session_state.datos_atleta['cmj']
    imtp_data = st.session_state.datos_atleta['imtp']
    
    if cmj_data.get('f_max_propulsiva') and imtp_data.get('f_pico'):
        f_cmj = cmj_data['f_max_propulsiva']
        f_imtp = imtp_data['f_pico']
        dsi = round(f_cmj / f_imtp, 2)
        
        # Clasificación del DSI
        if dsi > 0.80:
            estado = "Déficit de Fuerza Máxima"
            clase_css = "alerta-roja"
            recomendacion = "Priorizar entrenamiento de fuerza máxima pesada (>80% 1RM) e isometría máxima."
        elif dsi < 0.60:
            estado = "Déficit Balístico / Explosivo"
            clase_css = "alerta-amarilla"
            recomendacion = "Priorizar entrenamiento pliométrico, balístico y levantamientos olímpicos derivados."
        else:
            estado = "Óptimo / Equilibrado"
            clase_css = "alerta-verde"
            recomendacion = "Mantener entrenamiento concurrente equilibrado."
            
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"""
            <div class='metric-card {clase_css}'>
                <h3 style='text-align:center; color:#1E1E1E;'>Índice DSI: {dsi}</h3>
                <h4 style='text-align:center;'>{estado}</h4>
                <hr>
                <p><b>Fuerza Pico CMJ:</b> {f_cmj} N</p>
                <p><b>Fuerza Pico IMTP:</b> {f_imtp} N</p>
            </div>
            """, unsafe_allow_html=True)
        
        with c2:
            st.markdown(f"""
            <div class='metric-card'>
                <h4>📝 Intervención Sugerida</h4>
                <p>{recomendacion}</p>
                <hr>
                <small><i>Valores de referencia: DSI > 0.80 (Énfasis en Fuerza), DSI < 0.60 (Énfasis Balístico).</i></small>
            </div>
            """, unsafe_allow_html=True)
            
    else:
        st.warning("⚠️ Faltan datos. Asegurate de haber cargado el archivo del CMJ y del IMTP en la pestaña de 'Carga de Datos'.")

# PANTALLA 3: ANÁLISIS ISOMÉTRICO (IMTP)
elif menu == "🧱 Análisis Isométrico (IMTP / ISO PUSH)":
    st.markdown('<p class="subtitulo-evoxx">Fuerza Máxima Estructural</p>', unsafe_allow_html=True)
    
    imtp = st.session_state.datos_atleta['imtp']
    peso = st.session_state.datos_atleta['peso']
    
    if imtp.get('f_pico'):
        fuerza_relativa = round(imtp['f_pico'] / peso, 2) if peso > 0 else 0
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='metric-card'><b>Fuerza Pico</b><br><h2>{imtp['f_pico']} N</h2></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-card'><b>Fuerza Relativa</b><br><h2>{fuerza_relativa} N/kg</h2></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='metric-card'><b>Asimetría IMTP</b><br><h2>{imtp.get('asim', 'N/A')}%</h2></div>", unsafe_allow_html=True)
    else:
        st.info("No hay datos de IMTP cargados.")

elif menu == "🚀 Análisis Dinámico (CMJ / DJ)":
    st.markdown('<p class="subtitulo-evoxx">Métricas de Salto (CMJ)</p>', unsafe_allow_html=True)
    cmj = st.session_state.datos_atleta['cmj']
    if cmj.get('f_max_propulsiva'):
        st.write(cmj) # Aquí después armamos las tarjetas visuales como en el IMTP
    else:
        st.info("No hay datos de CMJ cargados.")
