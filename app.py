import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

# --- 1. CONFIGURACIÓN Y ESTILOS AVANZADOS EVOXX ---
st.set_page_config(page_title="Evoxx | Biomecánica Avanzada", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #F8FAFC; } /* Fondo más claro y moderno */
    
    .metric-card { 
        background-color: #FFFFFF; padding: 24px; border-radius: 12px; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); 
        margin-bottom: 24px; border-top: 4px solid #00AFBD; 
    }
    
    .titulo-evoxx { color: #0F172A; font-weight: 800; font-size: 2.2rem; margin-bottom: 0px; letter-spacing: -0.02em;}
    .subtitulo-evoxx { color: #00AFBD; font-weight: 700; font-size: 1rem; margin-bottom: 24px; text-transform: uppercase; letter-spacing: 0.05em;}
    .section-title { color: #1E293B; font-weight: 700; font-size: 1.25rem; margin-top: 8px; margin-bottom: 16px; border-bottom: 2px solid #E2E8F0; padding-bottom: 8px;}
    
    /* Mejoras visuales para st.metric */
    div[data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 700; color: #0F172A; }
    div[data-testid="stMetricLabel"] { font-size: 0.9rem; font-weight: 600; color: #64748B; }
    </style>
""", unsafe_allow_html=True)

# --- 2. MOTOR CENTRAL DE DATOS ---
if 'atleta' not in st.session_state:
    st.session_state.atleta = {
        'nombre': '', 'peso': 75.0,
        'datos': {
            'CMJ': {'Fuerza_Max_Propulsiva': 0.0, 'Fuerza_Pico': 0.0, 'Altura': 0.0, 'RFD_Frenado': 0.0, 'Asim_Frenado': 0.0, 'Asim_Despegue': 0.0, 'Asim_Aterrizaje': 0.0, 'Eficiencia': 0.0, 'Rep_Elegida': ''},
            'DJ': {'RSI': 0.0, 'Tiempo_Contacto': 0.0, 'Tiempo_Vuelo': 0.0, 'Altura': 0.0, 'Fuerza_Max_Prop': 0.0, 'Asimetria': 0.0, 'Rep_Elegida': ''},
            'IMTP': {'Fuerza_Pico': 0.0, 'RFD_100': 0.0, 'RFD_250': 0.0, 'Tiempo_Fuerza_Pico': 0.0, 'Asimetria': 0.0, 'Rep_Elegida': ''},
            'ISO_UNI': {'Fpico_Izq': 0.0, 'Fpico_Der': 0.0, 'RFD250_Izq': 0.0, 'RFD250_Der': 0.0, 'Asimetria': 0.0},
            'AD_AB': {'Ad_Izq': 0.0, 'Ad_Der': 0.0, 'Ab_Izq': 0.0, 'Ab_Der': 0.0} # NUEVO MÓDULO AD/AB
        }
    }

# --- 3. LÓGICA DE EXTRACCIÓN AVANZADA (PYTHON EXPERT MODE) ---
def obtener_mejor_columna(df, metrica_clave):
    """Busca la fila exacta y determina qué repetición (columna) tiene el valor máximo."""
    try:
        fila = df[df.iloc[:, 0].astype(str).str.strip() == metrica_clave]
        if not fila.empty:
            valores = pd.to_numeric(fila.iloc[0, 1:], errors='coerce')
            return valores.idxmax() # Devuelve el nombre de la columna (ej: 'Rep 2')
    except:
        pass
    return None

def extraer_valor_exacto(df, nombre_exacto, columna_objetivo):
    """Extrae el valor cruzando el nombre exacto de la fila y la columna ganadora."""
    try:
        fila = df[df.iloc[:, 0].astype(str).str.strip() == nombre_exacto]
        if not fila.empty and columna_objetivo in df.columns:
            return float(fila.iloc[0][columna_objetivo])
    except:
        pass
    return 0.0

def procesar_archivo(file):
    try:
        df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
        nombre = file.name.lower()
        datos = st.session_state.atleta['datos']
        
        # --- PROCESAMIENTO CMJ ---
        if "cmj" in nombre:
            mejor_rep = obtener_mejor_columna(df, "Fuerza Max Propulsiva (N)")
            if mejor_rep:
                datos['CMJ']['Rep_Elegida'] = mejor_rep
                datos['CMJ']['Fuerza_Max_Propulsiva'] = extraer_valor_exacto(df, "Fuerza Max Propulsiva (N)", mejor_rep)
                datos['CMJ']['RFD_Frenado'] = extraer_valor_exacto(df, "RFD Frenado", mejor_rep) # Según tu Excel
                datos['CMJ']['Asim_Frenado'] = extraer_valor_exacto(df, "Asimetría Frenado (%)", mejor_rep)
                # Agrega más extracciones exactas aquí leyendo tu Excel
                return f"✅ CMJ: {mejor_rep} procesada."
            return "⚠️ CMJ: No se encontró 'Fuerza Max Propulsiva (N)'"
            
        # --- PROCESAMIENTO IMTP ---
        elif "imtp" in nombre or "tirón" in nombre:
            mejor_rep = obtener_mejor_columna(df, "Fuerza Pico (N)")
            if mejor_rep:
                datos['IMTP']['Rep_Elegida'] = mejor_rep
                datos['IMTP']['Fuerza_Pico'] = extraer_valor_exacto(df, "Fuerza Pico (N)", mejor_rep)
                datos['IMTP']['RFD_100'] = extraer_valor_exacto(df, "RFD en 100 (N/s)", mejor_rep)
                datos['IMTP']['RFD_250'] = extraer_valor_exacto(df, "RFD en 250 (N/s)", mejor_rep)
                datos['IMTP']['Tiempo_Fuerza_Pico'] = extraer_valor_exacto(df, "Tiempo de Fuerza Pico (s)", mejor_rep)
                datos['IMTP']['Asimetria'] = extraer_valor_exacto(df, "Asimetría (%)", mejor_rep)
                return f"✅ IMTP: {mejor_rep} procesada."
            return "⚠️ IMTP: No se encontró 'Fuerza Pico (N)'"
            
    except Exception as e:
        return f"⚠️ Error procesando {file.name}: {e}"
    return None

# --- 4. COMPONENTES VISUALES ---
def grafico_aguja(valor, titulo):
    val_abs = abs(valor)
    color = "#10B981" if val_abs <= 10 else "#F59E0B" if val_abs <= 15 else "#EF4444"
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=val_abs, title={'text': titulo, 'font': {'size': 14, 'color': '#475569'}},
        number={'suffix': "%", 'font': {'color': color, 'size': 28, 'weight': 'bold'}},
        gauge={
            'axis': {'range': [0, 25], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': "#F1F5F9",
            'steps': [
                {'range': [0, 10], 'color': "rgba(16, 185, 129, 0.1)"},
                {'range': [10, 15], 'color': "rgba(245, 158, 11, 0.1)"},
                {'range': [15, 25], 'color': "rgba(239, 68, 68, 0.1)"}]
        }
    ))
    fig.update_layout(height=180, margin=dict(l=20, r=20, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)")
    return fig

# --- 5. INTERFAZ Y NAVEGACIÓN ---
with st.sidebar:
    if os.path.exists("logo_evoxx.png"): st.image("logo_evoxx.png")
    st.markdown("<h3 style='text-align:center; color:#00AFBD; font-weight: 800;'>EVOXX LAB</h3>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("Menú Principal", [
        "📥 1. Carga y Revisión Manual", 
        "📊 2. Dashboard de Rendimiento", 
        "📄 3. Generación de Informe PDF"
    ])

st.markdown('<p class="titulo-evoxx">LABORATORIO DE BIOMECÁNICA</p>', unsafe_allow_html=True)

# ==========================================
# PESTAÑA 1: CARGA Y REVISIÓN (ESQUELETO INTACTO + MEJORAS)
# ==========================================
if menu == "📥 1. Carga y Revisión Manual":
    st.markdown('<p class="subtitulo-evoxx">Gestión Integral del Deportista</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("<p class='section-title'>👤 Perfil Clínico</p>", unsafe_allow_html=True)
        st.session_state.atleta['nombre'] = st.text_input("Nombre del Deportista", st.session_state.atleta['nombre'])
        st.session_state.atleta['peso'] = st.number_input("Peso Corporal (kg)", value=st.session_state.atleta['peso'])
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("<p class='section-title'>📤 Motor de Extracción (Archivos Crudos)</p>", unsafe_allow_html=True)
        files = st.file_uploader("Arrastrá los reportes Excel/CSV aquí", accept_multiple_files=True)
        if files: 
            for f in files:
                res = procesar_archivo(f)
                if res: st.success(res)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- PANEL DE CORRECCIÓN (Agradable y en Pestañas nativas) ---
    st.markdown("### 🛠️ Configuración y Corrección Manual")
    t1, t2, t3 = st.tabs(["🚀 Saltos (CMJ / DJ)", "🧱 Isometría Máxima", "📐 Aductores / Abductores"])
    
    with t1:
        st.write("Verificá o editá los valores extraídos para los saltos.")
        cc1, cc2, cc3, cc4 = st.columns(4)
        cmj = st.session_state.atleta['datos']['CMJ']
        dj = st.session_state.atleta['datos']['DJ']
        cmj['Fuerza_Max_Propulsiva'] = cc1.number_input("Fuerza Max Propulsiva (N)", value=float(cmj['Fuerza_Max_Propulsiva']))
        cmj['RFD_Frenado'] = cc2.number_input("RFD Frenado (N/s)", value=float(cmj['RFD_Frenado']))
        cmj['Asim_Frenado'] = cc3.number_input("Asim. Frenado (%)", value=float(cmj['Asim_Frenado']))
        dj['RSI'] = cc4.number_input("Índice RSI (DJ)", value=float(dj['RSI']))
        
    with t2:
        ci1, ci2, ci3, ci4 = st.columns(4)
        imtp = st.session_state.atleta['datos']['IMTP']
        imtp['Fuerza_Pico'] = ci1.number_input("Fuerza Pico IMTP (N)", value=float(imtp['Fuerza_Pico']))
        imtp['RFD_100'] = ci2.number_input("RFD en 100ms", value=float(imtp['RFD_100']))
        imtp['RFD_250'] = ci3.number_input("RFD en 250ms", value=float(imtp['RFD_250']))
        imtp['Asimetria'] = ci4.number_input("Asimetría Bilateral (%)", value=float(imtp['Asimetria']))

    with t3: # EL NUEVO MÓDULO QUE PEDISTE
        st.write("Carga manual de Dinamometría de Cadera (N).")
        cad1, cad2, cad3, cad4 = st.columns(4)
        adab = st.session_state.atleta['datos']['AD_AB']
        adab['Ad_Izq'] = cad1.number_input("Aductor Izquierdo (N)", value=float(adab['Ad_Izq']))
        adab['Ad_Der'] = cad2.number_input("Aductor Derecho (N)", value=float(adab['Ad_Der']))
        adab['Ab_Izq'] = cad3.number_input("Abductor Izquierdo (N)", value=float(adab['Ab_Izq']))
        adab['Ab_Der'] = cad4.number_input("Abductor Derecho (N)", value=float(adab['Ab_Der']))

# ==========================================
# PESTAÑA 2: DASHBOARD (UI/UX MEJORADA)
# ==========================================
elif menu == "📊 2. Dashboard de Rendimiento":
    st.markdown('<p class="subtitulo-evoxx">Visualización Profesional de Resultados</p>', unsafe_allow_html=True)
    
    cmj = st.session_state.atleta['datos']['CMJ']
    imtp = st.session_state.atleta['datos']['IMTP']
    adab = st.session_state.atleta['datos']['AD_AB']
    
    # 1. TARJETAS DE MÉTRICAS PRINCIPALES
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>⚡ Resumen de Aplicación de Fuerza</p>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Fuerza Máx. Propulsiva (CMJ)", f"{cmj['Fuerza_Max_Propulsiva']} N")
    m2.metric("Fuerza Pico (IMTP)", f"{imtp['Fuerza_Pico']} N")
    m3.metric("RFD 250ms (IMTP)", f"{imtp['RFD_250']} N/s")
    
    peso = st.session_state.atleta['peso']
    f_relativa = round(imtp['Fuerza_Pico'] / peso, 2) if peso > 0 else 0
    m4.metric("Fuerza Relativa (IMTP)", f"{f_relativa} N/kg")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 2. CONTROL DE ASIMETRÍAS (Semáforos)
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>⚖️ Control Clínico de Asimetrías</p>", unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3)
    with g1: st.plotly_chart(grafico_aguja(imtp['Asimetria'], "Asimetría Estructural (IMTP)"), use_container_width=True)
    with g2: st.plotly_chart(grafico_aguja(cmj['Asim_Frenado'], "Asimetría Frenado (CMJ)"), use_container_width=True)
    
    # Ratios de Cadera (Si están cargados)
    with g3:
        if adab['Ab_Izq'] > 0 and adab['Ab_Der'] > 0:
            ratio_izq = round(adab['Ad_Izq'] / adab['Ab_Izq'], 2)
            ratio_der = round(adab['Ad_Der'] / adab['Ab_Der'], 2)
            st.markdown(f"**Ratios Aductor/Abductor**")
            st.write(f"🟢 **Izquierdo:** {ratio_izq} *(Óptimo ~0.90 - 1.10)*")
            st.write(f"🟢 **Derecho:** {ratio_der} *(Óptimo ~0.90 - 1.10)*")
        else:
            st.info("Carga datos de Ad/Ab para ver los ratios de cadera.")
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# PESTAÑA 3: PDF (ESQUELETO LISTO)
# ==========================================
elif menu == "📄 3. Generación de Informe PDF":
    st.markdown('<p class="subtitulo-evoxx">Exportar Documento Formal</p>', unsafe_allow_html=True)
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.write(f"### Atleta a evaluar: {st.session_state.atleta['nombre']}")
    st.write("El sistema detectó los siguientes módulos listos para exportar:")
    
    st.checkbox("Test Isométricos (Fuerza Pico, Asimetrías, RFD)", value=bool(st.session_state.atleta['datos']['IMTP']['Fuerza_Pico']), disabled=True)
    st.checkbox("Test Dinámicos (Fuerza Propulsiva, Frenado)", value=bool(st.session_state.atleta['datos']['CMJ']['Fuerza_Max_Propulsiva']), disabled=True)
    st.checkbox("Test de Cadera (Aductores / Abductores)", value=bool(st.session_state.atleta['datos']['AD_AB']['Ad_Izq']), disabled=True)
    
    st.button("⚙️ Generar PDF (Configuración final pendiente)")
    st.markdown("</div>", unsafe_allow_html=True)
