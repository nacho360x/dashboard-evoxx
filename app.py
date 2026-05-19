import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

# --- 1. CONFIGURACIÓN Y ESTILOS EVOXX ---
st.set_page_config(page_title="Evoxx | Biomecánica Avanzada", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Open Sans', sans-serif; }
    .main { background-color: #F4F6F8; }
    
    .metric-card { 
        background-color: #FFFFFF; padding: 20px; border-radius: 10px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 20px;
        border-top: 4px solid #00AFBD; 
    }
    .titulo-evoxx { color: #111111; font-weight: 800; font-size: 2.2rem; margin-bottom: 0px; }
    .subtitulo-evoxx { color: #00AFBD; font-weight: 700; font-size: 1.1rem; margin-bottom: 20px; text-transform: uppercase;}
    .section-title { color: #1A365D; font-weight: 700; font-size: 1.2rem; margin-top: 10px; margin-bottom: 15px; border-bottom: 2px solid #E2E8F0; padding-bottom: 5px;}
    </style>
""", unsafe_allow_html=True)

# --- 2. MOTOR CENTRAL DE DATOS (SESSION STATE) ---
if 'atleta' not in st.session_state:
    st.session_state.atleta = {
        'nombre': '', 'peso': 75.0, 'email_profesional': 'ignacioalmiron02@gmail.com',
        'datos': {
            'CMJ': {'Fuerza_Max_Propulsiva': 0.0, 'Altura': 0.0, 'RFD_100': 0.0, 'RFD_250': 0.0, 'Asim_Frenado': 0.0, 'Asim_Despegue': 0.0, 'Asim_Aterrizaje': 0.0, 'Eficiencia': 0.0},
            'DJ': {'RSI': 0.0, 'Tiempo_Contacto': 0.0, 'Tiempo_Vuelo': 0.0, 'Altura': 0.0},
            'IMTP': {'Fuerza_Pico': 0.0, 'RFD_100': 0.0, 'RFD_250': 0.0, 'Tiempo_Fuerza_Pico': 0.0, 'Asimetria': 0.0},
            'ISO_UNI': {'Fpico_Izq': 0.0, 'Fpico_Der': 0.0, 'RFD250_Izq': 0.0, 'RFD250_Der': 0.0, 'Asimetria': 0.0},
            'VALKYRIA': {'Fpico_Q_Izq': 0.0, 'Fpico_Q_Der': 0.0, 'Fpico_I_Izq': 0.0, 'Fpico_I_Der': 0.0}
        }
    }

# --- 3. LÓGICA DE EXTRACCIÓN INTELIGENTE ---
def extraer_valor(df, palabra_clave, col_idx=1):
    """Busca un texto parcial o exacto en la columna 0 y devuelve el número de la columna indicada."""
    try:
        fila = df[df.iloc[:, 0].astype(str).str.contains(palabra_clave, case=False, na=False)]
        if not fila.empty:
            return float(pd.to_numeric(fila.iloc[0, col_idx], errors='coerce'))
    except:
        pass
    return 0.0

def procesar_archivo(file):
    try:
        df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
        nombre = file.name.lower()
        datos = st.session_state.atleta['datos']
        
        # Identificar qué test es según el nombre del archivo
        if "cmj" in nombre:
            datos['CMJ']['Fuerza_Max_Propulsiva'] = extraer_valor(df, "Fuerza Max Propulsiva")
            datos['CMJ']['Asim_Frenado'] = extraer_valor(df, "Asimetría Frenado")
            datos['CMJ']['Asim_Despegue'] = extraer_valor(df, "Asimetría Despegue")
            datos['CMJ']['Asim_Aterrizaje'] = extraer_valor(df, "Asimetría Aterrizaje")
            return "✅ CMJ procesado"
            
        elif "imtp" in nombre or "tirón" in nombre:
            datos['IMTP']['Fuerza_Pico'] = extraer_valor(df, "Fuerza Pico")
            datos['IMTP']['RFD_100'] = extraer_valor(df, "RFD en 100")
            datos['IMTP']['RFD_250'] = extraer_valor(df, "RFD en 250")
            datos['IMTP']['Tiempo_Fuerza_Pico'] = extraer_valor(df, "Tiempo de Fuerza Pico")
            datos['IMTP']['Asimetria'] = extraer_valor(df, "Asimetría")
            return "✅ IMTP procesado"
            
        elif "dj" in nombre or "drop" in nombre:
            datos['DJ']['RSI'] = extraer_valor(df, "RSI")
            datos['DJ']['Tiempo_Contacto'] = extraer_valor(df, "Tiempo de Contacto")
            datos['DJ']['Tiempo_Vuelo'] = extraer_valor(df, "Tiempo de Vuelo")
            return "✅ Drop Jump procesado"
            
    except Exception as e:
        return f"⚠️ Error en {file.name}: {e}"
    return None

# --- 4. FUNCIONES GRÁFICAS ---
def grafico_aguja(valor, titulo):
    val_abs = abs(valor)
    color = "#28A745" if val_abs <= 10 else "#FFC107" if val_abs <= 15 else "#DC3545"
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=val_abs, title={'text': titulo, 'font': {'size': 14}},
        number={'suffix': "%", 'font': {'color': color}},
        gauge={'axis': {'range': [0, 25]}, 'bar': {'color': color},
               'steps': [{'range': [0, 10], 'color': "rgba(40,167,69,0.1)"},
                         {'range': [10, 15], 'color': "rgba(255,193,7,0.1)"},
                         {'range': [15, 25], 'color': "rgba(220,53,69,0.1)"}]}
    ))
    fig.update_layout(height=160, margin=dict(l=10, r=10, t=30, b=10))
    return fig

# --- 5. INTERFAZ Y NAVEGACIÓN ---
with st.sidebar:
    if os.path.exists("logo_evoxx.png"): st.image("logo_evoxx.png")
    st.markdown("<h2 style='text-align:center; color:#00AFBD;'>EVOXX LAB</h2>", unsafe_allow_html=True)
    menu = st.radio("Módulo de Trabajo:", [
        "📥 1. Carga y Revisión Manual", 
        "📊 2. Dashboard de Rendimiento", 
        "📐 3. Dinamometría y Ratios",
        "📄 4. Generación de Informe PDF"
    ])

st.markdown('<p class="titulo-evoxx">LABORATORIO DE BIOMECÁNICA</p>', unsafe_allow_html=True)

# ----------------- PESTAÑA 1: CARGA Y REVISIÓN -----------------
if menu == "📥 1. Carga y Revisión Manual":
    st.markdown('<p class="subtitulo-evoxx">Gestión Integral del Deportista</p>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("<p class='section-title'>👤 Perfil Clínico</p>", unsafe_allow_html=True)
        st.session_state.atleta['nombre'] = st.text_input("Nombre del Deportista", st.session_state.atleta['nombre'])
        st.session_state.atleta['peso'] = st.number_input("Peso Corporal (kg)", value=st.session_state.atleta['peso'])
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("<p class='section-title'>📤 Carga Masiva (Archivos Crudos)</p>", unsafe_allow_html=True)
        files = st.file_uploader("Arrastrá los reportes Excel/CSV aquí", accept_multiple_files=True)
        if files: 
            for f in files:
                res = procesar_archivo(f)
                if res: st.success(res)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 🛠️ Configuración y Corrección Manual")
    st.info("Todos los valores extraídos pueden ser sobrescritos manualmente aquí.")
    
    t1, t2, t3 = st.tabs(["🚀 Saltos (CMJ / DJ)", "🧱 Isometría Máxima", "📐 Dinamometría / Unipodal"])
    with t1:
        cc1, cc2, cc3 = st.columns(3)
        cmj = st.session_state.atleta['datos']['CMJ']
        dj = st.session_state.atleta['datos']['DJ']
        cmj['Fuerza_Max_Propulsiva'] = cc1.number_input("Fuerza Max Propulsiva (CMJ)", value=float(cmj['Fuerza_Max_Propulsiva']))
        cmj['Asim_Frenado'] = cc2.number_input("Asimetría Frenado (%)", value=float(cmj['Asim_Frenado']))
        cmj['Asim_Despegue'] = cc3.number_input("Asimetría Despegue (%)", value=float(cmj['Asim_Despegue']))
        dj['RSI'] = cc1.number_input("Índice RSI (Drop Jump)", value=float(dj['RSI']))
        dj['Tiempo_Contacto'] = cc2.number_input("Tiempo de Contacto (s)", value=float(dj['Tiempo_Contacto']))
        
    with t2:
        ci1, ci2, ci3 = st.columns(3)
        imtp = st.session_state.atleta['datos']['IMTP']
        imtp['Fuerza_Pico'] = ci1.number_input("Fuerza Pico IMTP (N)", value=float(imtp['Fuerza_Pico']))
        imtp['RFD_250'] = ci2.number_input("RFD en 250ms", value=float(imtp['RFD_250']))
        imtp['Asimetria'] = ci3.number_input("Asimetría Bilateral (%)", value=float(imtp['Asimetria']))

    with t3:
        st.write("Configuración de fuerzas unipodales e índices a cargar (Ad/Ab, etc).")
        cu1, cu2 = st.columns(2)
        iso_uni = st.session_state.atleta['datos']['ISO_UNI']
        iso_uni['Fpico_Izq'] = cu1.number_input("Fuerza Pico Izquierda (N)", value=float(iso_uni['Fpico_Izq']))
        iso_uni['Fpico_Der'] = cu2.number_input("Fuerza Pico Derecha (N)", value=float(iso_uni['Fpico_Der']))

# ----------------- PESTAÑA 2: DASHBOARD -----------------
elif menu == "📊 2. Dashboard de Rendimiento":
    st.markdown('<p class="subtitulo-evoxx">Panel de Visualización Interactiva</p>', unsafe_allow_html=True)
    
    cmj = st.session_state.atleta['datos']['CMJ']
    imtp = st.session_state.atleta['datos']['IMTP']
    
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>Control Clínico de Asimetrías</p>", unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3)
    with g1: st.plotly_chart(grafico_aguja(imtp['Asimetria'], "Asimetría Estructural (IMTP)"), use_container_width=True)
    with g2: st.plotly_chart(grafico_aguja(cmj['Asim_Frenado'], "Asimetría Frenado (CMJ)"), use_container_width=True)
    with g3: st.plotly_chart(grafico_aguja(cmj['Asim_Despegue'], "Asimetría Despegue (CMJ)"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("<p class='section-title'>Fuerza y Explosividad</p>", unsafe_allow_html=True)
        st.write(f"**Fuerza Pico Isométrica:** {imtp['Fuerza_Pico']} N")
        st.write(f"**RFD (250ms):** {imtp['RFD_250']} N/s")
        if st.session_state.atleta['peso'] > 0:
            f_rel = round(imtp['Fuerza_Pico'] / st.session_state.atleta['peso'], 2)
            st.write(f"**Fuerza Relativa:** {f_rel} N/kg")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("<p class='section-title'>Métricas Dinámicas y Reactivas</p>", unsafe_allow_html=True)
        st.write(f"**Fuerza Máx Propulsiva:** {cmj['Fuerza_Max_Propulsiva']} N")
        dj = st.session_state.atleta['datos']['DJ']
        st.write(f"**RSI (Reactive Strength Index):** {dj['RSI']}")
        st.write(f"**Tiempo de Contacto:** {dj['Tiempo_Contacto']} ms")
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------- PESTAÑA 4: REPORTE PDF -----------------
elif menu == "📄 4. Generación de Informe PDF":
    st.markdown('<p class="subtitulo-evoxx">Exportar Documento Formal</p>', unsafe_allow_html=True)
    
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.write(f"### Atleta a evaluar: {st.session_state.atleta['nombre']}")
    st.write("El informe compilará los datos de plataformas de fuerza, dinamometría y los índices de simetría.")
    
    # Vista previa de lo que irá al PDF
    st.markdown("**Secciones detectadas con información lista para imprimir:**")
    cmj_val = st.session_state.atleta['datos']['CMJ']['Fuerza_Max_Propulsiva'] > 0
    imtp_val = st.session_state.atleta['datos']['IMTP']['Fuerza_Pico'] > 0
    
    st.checkbox("Datos Antropométricos (Peso, Relativas)", value=True, disabled=True)
    st.checkbox("Test Isométricos (Fuerza Pico, Asimetrías, RFD)", value=imtp_val, disabled=True)
    st.checkbox("Test Dinámicos (Fases de Salto, RSI, Eficiencia)", value=cmj_val, disabled=True)
    st.checkbox("Dinamometría Analítica y Ratios", value=True, disabled=True)
    
    st.info("Para exportar el reporte final con el motor de Python (PDF con gráficos vectoriales y el logo del laboratorio), necesitamos instalar la librería de reportes. ¿Avanzamos con ese paso?")
    st.button("⚙️ Pre-Visualizar PDF (Próximo paso)")
    st.markdown("</div>", unsafe_allow_html=True)
