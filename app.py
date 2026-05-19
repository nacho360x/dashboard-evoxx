import streamlit as st
import os

# Configuración principal de la página (Debe ir siempre primero)
st.set_page_config(page_title="Laboratorio Biomecánica | Evoxx", layout="wide", initial_sidebar_state="expanded")

# --- ESTILOS VISUALES EVOXX (CSS) ---
# Usamos el Cian de la marca (#00AFBD aprox) y tipografía estilo Open Sans
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Open Sans', sans-serif;
    }
    .main { background-color: #F8F9FA; }
    
    /* Diseño de Tarjetas Blancas */
    .metric-card { 
        background-color: #FFFFFF; 
        padding: 20px; 
        border-radius: 8px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); 
        margin-bottom: 20px;
        border-top: 4px solid #00AFBD; /* Cian Evoxx */
    }
    
    .titulo-evoxx { color: #1E1E1E; font-weight: 800; font-size: 2.5rem; margin-bottom: 0px;}
    .subtitulo-evoxx { color: #00AFBD; font-weight: 700; margin-bottom: 20px;}
    
    /* Semáforos */
    .alerta-verde { border-top: 4px solid #28A745; }
    .alerta-amarilla { border-top: 4px solid #FFC107; }
    .alerta-roja { border-top: 4px solid #DC3545; }
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (NAVEGACIÓN) ---
with st.sidebar:
    if os.path.exists("logo_evoxx.png"):
        st.image("logo_evoxx.png", use_container_width=True)
    
    st.markdown("### Navegación")
    menu = st.radio("Seleccioná un módulo:", [
        "📥 Carga de Datos", 
        "🚀 Análisis Dinámico (CMJ / DJ)", 
        "🧱 Análisis Isométrico (IMTP / ISO PUSH)",
        "📐 Dinamometría Analítica y Ratios",
        "🧠 Índices Globales (DSI)",
        "📚 Marco Teórico y RTP",
        "📄 Generador de Reporte PDF"
    ])
    st.markdown("---")
    st.info("Desarrollado para el Laboratorio de Biomecánica Evoxx.")

# --- PANTALLAS SEGÚN EL MENÚ ---
st.markdown('<p class="titulo-evoxx">LABORATORIO DE BIOMECÁNICA</p>', unsafe_allow_html=True)

if menu == "📥 Carga de Datos":
    st.markdown('<p class="subtitulo-evoxx">Ingreso de Evaluación del Deportista</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("#### 1. Datos del Deportista")
        nombre = st.text_input("Nombre y Apellido")
        peso = st.number_input("Peso Corporal (kg)", min_value=30.0, max_value=150.0, value=75.0, step=0.1)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("#### 2. Carga Masiva de Archivos")
        st.info("Arrastrá aquí los archivos de las plataformas (CMJ, IMTP, Dinamometría). El sistema detectará los test automáticamente.")
        archivos = st.file_uploader("Formatos soportados: Excel (.xlsx), CSV", type=['xlsx', 'csv'], accept_multiple_files=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif menu == "🚀 Análisis Dinámico (CMJ / DJ)":
    st.markdown('<p class="subtitulo-evoxx">Saltos Verticales y Reactividad</p>', unsafe_allow_html=True)
    st.write("Acá irán las métricas del CMJ (Fuerza propulsiva, asimetrías de aterrizaje) y Drop Jump (RSI).")

elif menu == "🧱 Análisis Isométrico (IMTP / ISO PUSH)":
    st.markdown('<p class="subtitulo-evoxx">Fuerza Máxima Estructural</p>', unsafe_allow_html=True)
    st.write("Acá cruzaremos la Fuerza Pico del IMTP con el Peso Corporal para la Fuerza Relativa.")

elif menu == "🧠 Índices Globales (DSI)":
    st.markdown('<p class="subtitulo-evoxx">Dynamic Strength Index</p>', unsafe_allow_html=True)
    st.write("Cruce automático entre CMJ y IMTP para determinar Déficit de Fuerza o Déficit Balístico.")

elif menu == "📚 Marco Teórico y RTP":
    st.markdown('<p class="subtitulo-evoxx">Referencias Científicas</p>', unsafe_allow_html=True)
    st.write("Explicación de cada test y tablas de valores normativos (ej: DSI > 0.80 = Déficit de Fuerza).")

elif menu == "📄 Generador de Reporte PDF":
    st.markdown('<p class="subtitulo-evoxx">Exportar Informe Clínico</p>', unsafe_allow_html=True)
    st.write("Botonera para ensamblar el reporte formal del atleta.")
