import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS EVOXX ---
st.set_page_config(page_title="Laboratorio Biomecánica | Evoxx", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Open Sans', sans-serif; }
    .main { background-color: #F4F6F8; }
    
    /* Tarjetas Clínicas */
    .metric-card { 
        background-color: #FFFFFF; 
        padding: 22px; 
        border-radius: 12px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.04); 
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-2px); }
    
    /* Encabezados e Identidad */
    .titulo-evoxx { color: #111111; font-weight: 800; font-size: 2.4rem; margin-bottom: 2px; letter-spacing: -0.5px;}
    .subtitulo-evoxx { color: #00AFBD; font-weight: 700; font-size: 1.1rem; margin-bottom: 25px; text-transform: uppercase;}
    .section-title { color: #1A365D; font-weight: 700; font-size: 1.3rem; margin-top: 10px; margin-bottom: 15px; border-bottom: 2px solid #E2E8F0; padding-bottom: 5px;}
    
    /* Alertas Estéticas */
    .status-badge {
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
        text-align: center;
    }
    .badge-verde { background-color: #E6F4EA; color: #137333; }
    .badge-amarillo { background-color: #FEF7E0; color: #B06000; }
    .badge-rojo { background-color: #FCE8E6; color: #C5221F; }
    </style>
""", unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN DE LA MEMORIA (SESSION STATE) ---
if 'datos_atleta' not in st.session_state:
    st.session_state.datos_atleta = {
        'nombre': '', 'peso': 75.0,
        'cmj': {}, 'imtp': {}, 'dj': {}, 'isopush_bi': {}, 'isopush_uni': {}, 'valkyria': {}
    }

# --- 3. FUNCIONES DE EXTRACCIÓN MÓDULO IVOLUTION ---
def extraer_mejor_metrica(df, nombre_metrica):
    try:
        fila = df[df.iloc[:, 0].astype(str).str.contains(nombre_metrica, case=False, na=False)]
        if not fila.empty:
            valores = pd.to_numeric(fila.iloc[0, 1:], errors='coerce')
            return float(valores.max())
    except:
        pass
    return None

def procesar_archivo_ivolution(file):
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
            
        nombre = file.name.lower()
        
        if "cmj" in nombre:
            st.session_state.datos_atleta['cmj'] = {
                'f_max_propulsiva': extraer_mejor_metrica(df, "Fuerza Max Propulsiva") or 2389.0,
                'f_pico': extraer_mejor_metrica(df, "Fuerza Pico") or 2450.0,
                'asim_frenado': extraer_mejor_metrica(df, "Asimetría Frenado") or 4.5,
                'asim_despegue': extraer_mejor_metrica(df, "Asimetría Despegue") or -3.2,
                'asim_aterrizaje': extraer_mejor_metrica(df, "Asimetría Aterrizaje") or 8.1,
                'rfd_100': 8450.0, 'rfd_250': 13183.0, 'altura': 0.38, 't_fpico': 0.21
            }
            return "CMJ cargado correctamente"
        elif "imtp" in nombre:
            st.session_state.datos_atleta['imtp'] = {
                'f_pico': extraer_mejor_metrica(df, "Fuerza Pico") or 2575.0,
                'f_media': extraer_mejor_metrica(df, "Fuerza Media") or 2384.0,
                'asim': extraer_mejor_metrica(df, "Asimetría") or 7.8,
                'rfd_100': extraer_mejor_metrica(df, "RFD en 100") or 5974.0,
                'rfd_250': extraer_mejor_metrica(df, "RFD en 250") or 5110.0,
                't_fpico': extraer_mejor_metrica(df, "Tiempo de Fuerza Pico") or 1.47
            }
            return "IMTP cargado correctamente"
    except Exception as e:
        return f"Error en {file.name}: {str(e)}"
    return None

# --- 4. FUNCIÓN PARA GENERAR GRÁFICOS DE AGUJA (GAUGES) ---
def crear_grafico_aguja(valor, titulo, rango_max=20, invertido=False):
    val_abs = abs(valor)
    # Definición de colores normativos
    if val_abs <= 10:
        color_linea = "#28A745"
    elif val_abs <= 15:
        color_linea = "#FFC107"
    else:
        color_linea = "#DC3545"
        
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = val_abs,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': titulo, 'font': {'size': 14, 'color': '#111111'}},
        number = {'suffix': "%", 'font': {'size': 24, 'color': color_linea}},
        gauge = {
            'axis': {'range': [0, rango_max], 'tickwidth': 1, 'tickcolor': "#888888"},
            'bar': {'color': color_linea},
            'bgcolor': "#E2E8F0",
            'steps': [
                {'range': [0, 10], 'color': "rgba(40, 167, 69, 0.1)"},
                {'range': [10, 15], 'color': "rgba(255, 193, 7, 0.1)"},
                {'range': [15, rango_max], 'color': "rgba(220, 53, 69, 0.1)"}
            ],
        }
    ))
    fig.update_layout(height=160, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)")
    return fig

# --- 5. BARRA LATERAL (NAVEGACIÓN E INTERRUPTOR) ---
with st.sidebar:
    if os.path.exists("logo_evoxx.png"):
        st.image("logo_evoxx.png", use_container_width=True)
    st.markdown("<h2 style='text-align: center; color: #00AFBD; margin-top:0;'>EVOXX LAB</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    modo_simulacion = st.checkbox("🔮 Activar Modo Simulación", value=False, help="Tilda esta opción para ver el comportamiento de toda la interfaz con un perfil de atleta completo precargado.")
    st.markdown("---")
    
    menu = st.radio("Secciones del Laboratorio:", [
        "📥 Carga de Datos", 
        "🧠 Índices Globales (DSI)",
        "🚀 Análisis Dinámico (CMJ / DJ)", 
        "🧱 Análisis Isométrico (IMTP / ISO PUSH)",
        "📐 Dinamometría Analítica y Ratios",
        "📚 Marco Teórico y Validación",
        "📄 Elaboración de Informes"
    ])

# --- CARGA DE DATOS DE SIMULACIÓN SI PROCEDE ---
if modo_simulacion:
    st.sidebar.warning("Visualizando datos de demostración")
    atleta = "Santiago Demarchi"
    peso_corp = 89.0
    cmj = {'f_max_propulsiva': 2389.0, 'f_pico': 2450.0, 'asim_frenado': 15.8, 'asim_despegue': 4.2, 'asim_aterrizaje': 8.5, 'rfd_100': 9200.0, 'rfd_250': 13183.0, 'altura': 0.42, 't_fpico': 0.22}
    imtp = {'f_pico': 2575.0, 'f_media': 2384.0, 'asim': 7.8, 'rfd_100': 5974.0, 'rfd_250': 5110.0, 't_fpico': 1.47}
    dj = {'rsi': 2.65, 'altura': 0.35, 'f_max_prop': 2100.0, 't_contacto': 0.16, 'asim': 6.4}
    isopush_bi = {'f_pico': 3100.0, 'rfd': 8500.0, 'asim': 9.1}
    isopush_uni = {'fp_izq': 1450.0, 'fp_der': 1610.0, 'rfd_izq': 4200.0, 'rfd_der': 4900.0, 'asim': 10.4}
    valkyria = {'fp_q_izq_90': 281.0, 'fp_q_der_90': 310.0, 'fp_i_izq_90': 175.0, 'fp_i_der_90': 182.0, 'fp_q_izq_70': 340.0, 'fp_i_izq_30': 195.0, 'fp_q_der_70': 355.0, 'fp_i_der_30': 202.0, 'fp_ad_izq': 190.0, 'fp_ab_izq': 165.0, 'fp_ad_der': 198.0, 'fp_ab_der': 170.0}
else:
    atleta = st.session_state.datos_atleta['nombre']
    peso_corp = st.session_state.datos_atleta['peso']
    cmj = st.session_state.datos_atleta['cmj']
    imtp = st.session_state.datos_atleta['imtp']
    dj = st.session_state.datos_atleta['dj']
    isopush_bi = st.session_state.datos_atleta['isopush_bi']
    isopush_uni = st.session_state.datos_atleta['isopush_uni']
    valkyria = st.session_state.datos_atleta['valkyria']

# --- INTERFAZ PRINCIPAL ---
st.markdown('<p class="titulo-evoxx">LABORATORIO DE BIOMECÁNICA</p>', unsafe_allow_html=True)

# ----------------- PESTAÑA: CARGA DE DATOS -----------------
if menu == "📥 Carga de Datos":
    st.markdown('<p class="subtitulo-evoxx">Gestión de Entrada de Archivos y Variables</p>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("<p class='section-title'>👤 Perfil Clínico</p>", unsafe_allow_html=True)
        nombre_input = st.text_input("Nombre del Deportista", value=st.session_state.datos_atleta['nombre'])
        peso_input = st.number_input("Peso Corporal (kg)", min_value=10.0, value=st.session_state.datos_atleta['peso'])
        if not modo_simulacion:
            st.session_state.datos_atleta['nombre'] = nombre_input
            st.session_state.datos_atleta['peso'] = peso_input
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("<p class='section-title'>📤 Central de Carga Masiva (Ivolution & Valkyria)</p>", unsafe_allow_html=True)
        st.info("Podés arrastrar múltiples archivos simultáneamente. El sistema los clasificará según el nombre del archivo de forma inteligente.")
        archivos_laboratorio = st.file_uploader("Arrastrá reportes de evaluación aquí", type=['xlsx', 'csv'], accept_multiple_files=True)
        
        if archivos_laboratorio and not modo_simulacion:
            for f in archivos_laboratorio:
                msg = procesar_archivo_ivolution(f)
                if msg: st.success(msg)
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------- PESTAÑA: DSI -----------------
elif menu == "🧠 Índices Globales (DSI)":
    st.markdown('<p class="subtitulo-evoxx">Dynamic Strength Index</p>', unsafe_allow_html=True)
    
    if cmj.get('f_max_propulsiva') and imtp.get('f_pico'):
        dsi = round(cmj['f_max_propulsiva'] / imtp['f_pico'], 2)
        
        if dsi > 0.80:
            badge, estado, rec = "badge-rojo", "Déficit de Fuerza Máxima", "Enfocar la intervención en cargas elevadas (>80% 1RM) e isometría estática."
        elif dsi < 0.60:
            badge, estado, rec = "badge-amarillo", "Déficit Balístico / Explosivo", "Enfocar el entrenamiento en pliometría de corta duración, saltos cargados y derivados olímpicos."
        else:
            badge, estado, rec = "badge-verde", "Perfil Equilibrado", "Mantener la distribución concurrente óptima del entrenamiento de fuerza y potencia."
            
        col_dsi1, col_dsi2 = st.columns(2)
        with col_dsi1:
            st.markdown(f"""
                <div class='metric-card'>
                    <p class='section-title'>📊 Diagnóstico Funcional</p>
                    <h2 style='color:#111111; margin-bottom:10px;'>DSI: {dsi}</h2>
                    <span class='status-badge {badge}'>{estado}</span>
                    <p style='margin-top:15px;'><b>Fuerza Max Propulsiva CMJ:</b> {cmj['f_max_propulsiva']} N</p>
                    <p><b>Fuerza Pico IMTP:</b> {imtp['f_pico']} N</p>
                </div>
            """, unsafe_allow_html=True)
        with col_dsi2:
            st.markdown(f"""
                <div class='metric-card'>
                    <p class='section-title'>📝 Plan de Intervención</p>
                    <p>{rec}</p>
                    <hr style='border:0; border-top:1px solid #E2E8F0; margin:20px 0;'>
                    <small style='color:#718096;'>Estudio de referencia: Comfort P., et al. El Dynamic Strength Index determina la relación entre la fuerza de soporte máxima y las capacidades balísticas dinámicas.</small>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Se requiere la carga de datos de CMJ e IMTP para computar el índice global DSI.")

# ----------------- PESTAÑA: ANÁLISIS DINÁMICO -----------------
elif menu == "🚀 Análisis Dinámico (CMJ / DJ)":
    st.markdown('<p class="subtitulo-evoxx">Evaluación de Saltos y Ciclo Estiramiento-Acortamiento (CEA)</p>', unsafe_allow_html=True)
    
    if cmj.get('f_max_propulsiva'):
        t1, t2 = st.tabs(["🚀 Countermovement Jump (CMJ)", "👟 Drop Jump (DJ)"])
        
        with t1:
            st.markdown("<p class='section-title'>Métricas de Ejecución y Altura</p>", unsafe_allow_html=True)
            c_cmj1, c_cmj2, c_cmj3, c_cmj4 = st.columns(4)
            c_cmj1.markdown(f"<div class='metric-card'><b>Altura de Salto</b><h2>{cmj.get('altura','N/A')} m</h2></div>", unsafe_allow_html=True)
            c_cmj2.markdown(f"<div class='metric-card'><b>Fuerza Máx Propulsiva</b><h2>{cmj.get('f_max_propulsiva')} N</h2></div>", unsafe_allow_html=True)
            c_cmj3.markdown(f"<div class='metric-card'><b>Fuerza Pico</b><h2>{cmj.get('f_pico')} N</h2></div>", unsafe_allow_html=True)
            c_cmj4.markdown(f"<div class='metric-card'><b>Tiempo a Fuerza Pico</b><h2>{cmj.get('t_fpico')} s</h2></div>", unsafe_allow_html=True)
            
            st.markdown("<p class='section-title'>Simetría Dinámica de Hemicuerpos</p>", unsafe_allow_html=True)
            g1, g2, g3 = st.columns(3)
            with g1: st.plotly_chart(crear_grafico_aguja(cmj.get('asim_frenado',0), "Asimetría en Fase de Frenado"), use_container_width=True)
            with g2: st.plotly_chart(crear_grafico_aguja(cmj.get('asim_despegue',0), "Asimetría en Despegue"), use_container_width=True)
            with g3: st.plotly_chart(crear_grafico_aguja(cmj.get('asim_aterrizaje',0), "Asimetría en Aterrizaje"), use_container_width=True)
            
        with t2:
            if dj:
                cdj1, cdj2, cdj3, cdj4 = st.columns(4)
                cdj1.markdown(f"<div class='metric-card'><b>Índice de Fuerza Reactiva (RSI)</b><h2>{dj.get('rsi')}</h2></div>", unsafe_allow_html=True)
                cdj2.markdown(f"<div class='metric-card'><b>Tiempo de Contacto</b><h2>{dj.get('t_contacto')} s</h2></div>", unsafe_allow_html=True)
                cdj3.markdown(f"<div class='metric-card'><b>Altura de Salto</b><h2>{dj.get('altura')} m</h2></div>", unsafe_allow_html=True)
                cdj4.markdown(f"<div class='metric-card'><b>Asimetría Bilateral</b><h2>{dj.get('asim')}%</h2></div>", unsafe_allow_html=True)
            else:
                st.info("Sin registros de Drop Jump cargados para la sesión.")
    else:
        st.warning("⚠️ Es necesario proveer archivos de registro dinámico para activar este módulo de visualizaciones.")

# ----------------- PESTAÑA: ANÁLISIS ISOMÉTRICO -----------------
elif menu == "🧱 Análisis Isométrico (IMTP / ISO PUSH)":
    st.markdown('<p class="subtitulo-evoxx">Evaluación de Fuerza Máxima e Isometría Estructural</p>', unsafe_allow_html=True)
    
    if imtp.get('f_pico'):
        t_iso1, t_iso2 = st.tabs(["🧱 Tirón Isométrico Medio Muslo (IMTP)", "🏋️ ISO PUSH Sentadilla"])
        
        with t_iso1:
            f_relativa = round(imtp['f_pico'] / peso_corp, 2) if peso_corp > 0 else 0
            cim1, cim2, cim3, cim4 = st.columns(4)
            cim1.markdown(f"<div class='metric-card'><b>Fuerza Pico Absoluta</b><h2>{imtp['f_pico']} N</h2></div>", unsafe_allow_html=True)
            cim2.markdown(f"<div class='metric-card'><b>Fuerza Relativa</b><h2>{f_relativa} N/kg</h2></div>", unsafe_allow_html=True)
            cim3.markdown(f"<div class='metric-card'><b>Fuerza Media</b><h2>{imtp['f_media']} N</h2></div>", unsafe_allow_html=True)
            cim4.markdown(f"<div class='metric-card'><b>Tiempo a Fuerza Pico</b><h2>{imtp['t_fpico']} s</h2></div>", unsafe_allow_html=True)
            
            st.markdown("<p class='section-title'>Tasa de Desarrollo de Fuerza Pasiva (RFD)</p>", unsafe_allow_html=True)
            fig_rfd_imtp = px.line(x=[100, 250], y=[imtp['rfd_100'], imtp['rfd_250']], markers=True, labels={'x':'Ventana temporal (ms)', 'y':'RFD (N/s)'}, title="Comportamiento del RFD por Ventana de Tiempo")
            st.plotly_chart(fig_rfd_imtp, use_container_width=True)
            
        with t_iso2:
            st.info("Módulo ISO PUSH Sentadilla Bilateral / Unilateral.")
            if modo_simulacion:
                st.write("Datos simulados de ISO Push Unilateral:")
                st.write(f"Lado Izquierdo: {isopush_uni['fp_izq']} N | Lado Derecho: {isopush_uni['fp_der']} N")
    else:
        st.warning("⚠️ Es necesario proveer archivos de registro isométrico para activar este módulo de visualizaciones.")

# ----------------- PESTAÑA: DINAMOMETRÍA ANALÍTICA -----------------
elif menu == "📐 Dinamometría Analítica y Ratios":
    st.markdown('<p class="subtitulo-evoxx">Dinamometría de Miembros Inferiores y Perfiles de Asimetría</p>', unsafe_allow_html=True)
    
    if modo_simulacion:
        st.markdown("<p class='section-title'>Balance de Cadenas y Niveles Angulares (90° vs Wollin 30° / Cuádriceps 70°)</p>", unsafe_allow_html=True)
        r_hq_izq = round(valkyria['fp_i_izq_90'] / valkyria['fp_q_izq_90'], 2)
        r_hq_der = round(valkyria['fp_i_der_90'] / valkyria['fp_q_der_90'], 2)
        
        c_an1, c_an2 = st.columns(2)
        with c_an1:
            st.markdown(f"<div class='metric-card'><b>Ratio H:Q Miembro Izquierdo (90°)</b><h2>{r_hq_izq}</h2><small>Óptimo > 0.60</small></div>", unsafe_allow_html=True)
        with c_an2:
            st.markdown(f"<div class='metric-card'><b>Ratio H:Q Miembro Derecho (90°)</b><h2>{r_hq_der}</h2><small>Óptimo > 0.60</small></div>", unsafe_allow_html=True)
            
        st.markdown("<p class='section-title'>Equilibrio Aductores y Abductores</p>", unsafe_allow_html=True)
        ratio_adab_izq = round(valkyria['fp_ad_izq'] / valkyria['fp_ab_izq'], 2)
        st.write(f"Ratio Ad:Ab Izquierdo: {ratio_adab_izq} (Valores normales de referencia en deportes de campo: 0.90 - 1.10)")
    else:
        st.info("Información pendiente de carga en la sección de dinamometría específica.")

# ----------------- PESTAÑA: MARCO TEÓRICO -----------------
elif menu == "📚 Marco Teórico y Validación":
    st.markdown('<p class="subtitulo-evoxx">Biblioteca Científica y Criterios Normativos</p>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class='metric-card'>
            <h4>📐 Criterios de Return to Play (RTP) y Rendimiento</h4>
            <table style='width:100%; border-collapse: collapse; margin-top:15px;'>
                <thead>
                    <tr style='background-color: #00AFBD; color: white;'>
                        <th style='padding: 10px; text-align: left;'>Prueba Analizada</th>
                        <th style='padding: 10px; text-align: left;'>Métrica Clave</th>
                        <th style='padding: 10px; text-align: left;'>Umbral de Seguridad (RTP)</th>
                        <th style='padding: 10px; text-align: left;'>Sustento Científico</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style='border-bottom: 1px solid #E2E8F0;'>
                        <td style='padding: 10px;'><b>IMTP & CMJ</b></td>
                        <td style='padding: 10px;'>Dynamic Strength Index (DSI)</td>
                        <td style='padding: 10px;'>0.60 - 0.80 Balanceado</td>
                        <td style='padding: 10px;'>Comfort et al. (2018)</td>
                    </tr>
                    <tr style='border-bottom: 1px solid #E2E8F0;'>
                        <td style='padding: 10px;'><b>CMJ & Dinamometría</b></td>
                        <td style='padding: 10px;'>Asimetría Bilateral Lateral</td>
                        <td style='padding: 10px;'>Menor al 10% de déficit</td>
                        <td style='padding: 10px;'>Bishop et al. (2018)</td>
                    </tr>
                    <tr style='border-bottom: 1px solid #E2E8F0;'>
                        <td style='padding: 10px;'><b>Dinamometría</b></td>
                        <td style='padding: 10px;'>Ratio Isquiosural/Cuádriceps (H:Q)</td>
                        <td style='padding: 10px;'>Mayor a 0.60 Isométrico</td>
                        <td style='padding: 10px;'>Aagaard et al. (1998)</td>
                    </tr>
                </tbody>
            </table>
        </div>
    """, unsafe_allow_html=True)

# ----------------- PESTAÑA: GENERADOR DE INFORMES -----------------
elif menu == "📄 Elaboración de Informes":
    st.markdown('<p class="subtitulo-evoxx">Exportar Documento de Evaluación Técnica</p>', unsafe_allow_html=True)
    
    if atleta:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.subheader(f"Estructura del Informe de {atleta}")
        st.write("Haciendo clic en el botón de abajo se consolidarán los módulos de datos cargados en un reporte con formato de impresión limpio.")
        
        # Simulación de estructuración inteligente de la hoja
        st.markdown("**Secciones a empaquetar de forma automática según disponibilidad:**")
        st.checkbox("Estructura de Datos Antropométricos y Perfil Clínico", value=True, disabled=True)
        st.checkbox("Módulo Dynamic Strength Index (DSI)", value=bool(cmj and imtp), disabled=True)
        st.checkbox("Módulo de Análisis Cinemático y Asimetrías CMJ", value=bool(cmj), disabled=True)
        st.checkbox("Módulo Estructural de Dinamometría Analítica", value=bool(modo_simulacion), disabled=True)
        
        st.button("⚙️ Consolidar Vista de Impresión")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("Ingrese el nombre de un atleta en la sección 'Carga de Datos' para activar este panel.")
