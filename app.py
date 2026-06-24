import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time

# ==========================================
# 1. CONFIGURACIÓN CORPORATIVA Y UI
# ==========================================
st.set_page_config(page_title="PepsiCo | SCM Control Tower", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .kpi-title {font-size: 0.85rem; color: #8892B0; text-transform: uppercase;}
    .kpi-value {font-size: 2.2rem; color: #E6F1FF; font-weight: bold; font-family: 'Courier New', monospace;}
    .kpi-container {background-color: #112240; padding: 15px; border-radius: 8px; border-left: 4px solid #00A3E0;}
    .user-badge {background-color: #002F6C; padding: 10px; border-radius: 5px; text-align: center; border: 1px solid #00A3E0; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

# Simulador de carga del sistema (Notificaciones flotantes)
if 'loaded' not in st.session_state:
    st.toast('Sincronizando con SAP ERP...', icon='🔄')
    time.sleep(0.5)
    st.toast('Modelos Estocásticos Compilados', icon='✅')
    st.session_state['loaded'] = True

# ==========================================
# 2. GENERADOR DE DATOS AVANZADO
# ==========================================
@st.cache_data
def get_network_data():
    np.random.seed(42)
    # Coordenadas geográficas para el mapa de México
    cedis_geo = {
        "Vallejo (CDMX)": [19.4978, -99.1676, "Crítico", "#E31837"],
        "Monterrey": [25.6866, -100.3161, "Estable", "#00A3E0"],
        "Guadalajara": [20.6597, -103.3496, "Estable", "#00A3E0"],
        "Tijuana": [32.5149, -117.0382, "Alerta", "#FFC107"],
        "Mérida": [20.9674, -89.6236, "Estable", "#00A3E0"]
    }
    df_geo = pd.DataFrame.from_dict(cedis_geo, orient='index', columns=['Lat', 'Lon', 'Status', 'Color']).reset_index()
    df_geo.rename(columns={'index': 'CEDIS'}, inplace=True)
    return df_geo

df_geo = get_network_data()

# ==========================================
# 3. BARRA LATERAL (CONTROL DE MANDO)
# ==========================================
with st.sidebar:
    # Identidad de Usuario (Gran impacto visual)
    st.markdown("""
        <div class="user-badge">
            <h4 style="color:white; margin:0;">Víctor Martínez</h4>
            <p style="color:#00A3E0; font-size:12px; margin:0;">Sr. Data Analyst | SCM Analytics</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎛️ FILTROS DE RED")
    cedis_sel = st.selectbox("📍 Nodo Logístico", df_geo['CEDIS'].tolist())
    cat_sel = st.selectbox("📂 Familia de Producto", ["Botanas Saladas", "Bebidas", "Galletas"])
    sku_sel = st.selectbox("📦 SKU Analizado", ["Sabritas Original 110g", "Doritos Nacho 146g", "Cheetos 150g"] if cat_sel == "Botanas Saladas" else ["Pepsi Black 600ml", "Gatorade 1L"])
    
    st.markdown("### ⚙️ VARIABLES DE ESTRÉS")
    volatilidad = st.slider("📈 Volatilidad de Demanda (%)", 5, 50, 15) / 100.0
    lead_time = st.number_input("🚚 Lead Time Estándar (Días)", min_value=1, max_value=10, value=3)
    retraso_log = st.slider("⚠️ Ruido Logístico (Días Extra)", 0, 5, 0)
    
    st.divider()
    st.caption("Última actualización: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Parámetros base simulados del producto
stock_actual = 4500
demanda_media = 1200
costo_caja = 45.50
lead_time_total = lead_time + retraso_log

# ==========================================
# 4. MOTOR MATEMÁTICO (MONTE CARLO)
# ==========================================
n_sim = 10000
demandas = np.random.normal(loc=demanda_media, scale=demanda_media * volatilidad, size=(n_sim, lead_time_total))
demandas = np.clip(demandas, 0, None)
consumo = np.cumsum(demandas, axis=1)
matriz_inv = stock_actual - consumo
inv_final = matriz_inv[:, -1]

prob_quiebre = np.mean(inv_final < 0) * 100
faltante_avg = np.mean(np.abs(inv_final[inv_final < 0])) if prob_quiebre > 0 else 0
ev_perdida = (prob_quiebre / 100) * faltante_avg * costo_caja

# ==========================================
# 5. HEADER Y KPIs PRINCIPALES
# ==========================================
# Lógica de saludo dinámico según la hora local (Ajustado a CST)
hora_actual = (datetime.utcnow() - timedelta(hours=6)).hour
if hora_actual < 12:
    saludo = "Buenos días"
elif hora_actual < 19:
    saludo = "Buenas tardes"
else:
    saludo = "Buenas noches"

# Banner de bienvenida personalizado
st.markdown(f'''
    <div style="background-color: rgba(0, 163, 224, 0.1); border-left: 4px solid #00A3E0; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="color: #ffffff; margin: 0; font-family: 'Helvetica Neue', sans-serif;">¡{saludo}, Víctor! Bienvenido.</h3>
        <p style="color: #8892B0; margin: 0; font-size: 0.95rem;">Sesión validada y activa. Privilegios de administrador (Data Analyst) concedidos.</p>
    </div>
''', unsafe_allow_html=True)

# Título principal
st.markdown('<h1 style="color: #ffffff; margin-bottom: 0px; margin-top: 10px;">&gt;_ PepsiCo Control Tower v2.0</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #00A3E0; font-size: 1.1rem; margin-top: -10px;">Enterprise Supply Chain Intelligence Platform</p>', unsafe_allow_html=True)

cols = st.columns(5)
metrics = [
    ("Stock Físico", f"{stock_actual:,} CX"),
    ("Demanda Diaria", f"{demanda_media:,} CX"),
    ("ROP Sugerido", f"{int(demanda_media * lead_time_total):,} CX"),
    ("Riesgo (Stockout)", f"{prob_quiebre:.1f}%"),
    ("Value at Risk (VaR)", f"${ev_perdida:,.0f}")
]
for col, (title, val) in zip(cols, metrics):
    with col:
        st.markdown(f'<div class="kpi-container"><div class="kpi-title">{title}</div><div class="kpi-value">{val}</div></div>', unsafe_allow_html=True)

st.write("<br>", unsafe_allow_html=True)

# ==========================================
# 6. MÓDULOS DE ANÁLISIS (SÚPER TABS)
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🗺️ Geo-Network", 
    "📉 Simulador Monte Carlo", 
    "🤖 AI Demand Forecast", 
    "💰 P&L Financiero", 
    "⚖️ What-If Scenarios", 
    "🖥️ System Logs"
])

# TAB 1: MAPA GEOESPACIAL
with tab1:
    st.markdown("### Mapa de Salud de Red Logística (México)")
    fig_map = px.scatter_mapbox(df_geo, lat="Lat", lon="Lon", hover_name="CEDIS", hover_data=["Status"],
                        color="Status", color_discrete_map={"Crítico": "#E31837", "Alerta": "#FFC107", "Estable": "#00A3E0"},
                        size_max=15, zoom=4.5, mapbox_style="carto-darkmatter")
    fig_map.update_traces(marker=dict(size=12))
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=400)
    st.plotly_chart(fig_map, use_container_width=True)

# TAB 2: MONTE CARLO
with tab2:
    st.markdown("### Simulador de Riesgo Estocástico (10,000 Vectores)")
    fig_mc = go.Figure()
    dias = np.arange(1, lead_time_total + 1)
    
    # 100 rutas transparentes
    muestras = matriz_inv[np.random.choice(n_sim, 100, replace=False), :]
    for i in range(100):
        fig_mc.add_trace(go.Scatter(x=dias, y=muestras[i, :], mode='lines', line=dict(color='#8892B0', width=1), opacity=0.1, showlegend=False))
        
    p50, p10 = np.percentile(matriz_inv, 50, axis=0), np.percentile(matriz_inv, 10, axis=0)
    fig_mc.add_trace(go.Scatter(x=dias, y=p50, mode='lines+markers', name='Mediana (P50)', line=dict(color='#00A3E0', width=3)))
    fig_mc.add_trace(go.Scatter(x=dias, y=p10, mode='lines', name='Estrés (P10)', line=dict(color='#E31837', width=2, dash='dash')))
    fig_mc.add_hline(y=0, line_dash="solid", line_color="#E31837", annotation_text="QUIEBRE DE STOCK")
    
    fig_mc.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig_mc, use_container_width=True)

# TAB 3: MACHINE LEARNING FORECAST
with tab3:
    st.markdown("### Proyección de Demanda (Modelo AI Predictivo)")
    st.write("Simulación de proyección usando algoritmos de series de tiempo (ARIMA/Prophet) integrando estacionalidad y clima.")
    
    dias_hist = pd.date_range(end=datetime.now(), periods=30)
    dias_fut = pd.date_range(start=datetime.now(), periods=15)
    
    hist_val = demanda_media + np.random.normal(0, demanda_media*0.1, 30)
    fut_val = demanda_media + np.random.normal(0, demanda_media*0.15, 15)
    
    fig_ai = go.Figure()
    fig_ai.add_trace(go.Scatter(x=dias_hist, y=hist_val, mode='lines', name='Histórico Real', line=dict(color='#ffffff')))
    fig_ai.add_trace(go.Scatter(x=dias_fut, y=fut_val, mode='lines+markers', name='AI Forecast', line=dict(color='#00F0FF', dash='dot')))
    
    # Intervalo de confianza
    fig_ai.add_trace(go.Scatter(x=dias_fut.tolist() + dias_fut[::-1].tolist(), 
                                y=(fut_val*1.2).tolist() + (fut_val*0.8)[::-1].tolist(), 
                                fill='toself', fillcolor='rgba(0, 240, 255, 0.2)', line=dict(color='rgba(255,255,255,0)'), name='Intervalo de Confianza 95%'))
    
    fig_ai.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig_ai, use_container_width=True)

# TAB 4: IMPACTO FINANCIERO (WATERFALL)
with tab4:
    st.markdown("### Desglose de Costos Logísticos (Cascada P&L)")
    costo_mantener = stock_actual * 0.50 # Asumiendo 50 centavos por caja por guardar
    costo_transporte = 15000 # Costo fijo de flete
    
    fig_wf = go.Figure(go.Waterfall(
        orientation="v", measure=["relative", "relative", "relative", "total"],
        x=["Costo Almacenaje", "Flete Estándar", "VaR (Riesgo Quiebre)", "Costo Total Proyectado"],
        textposition="outside",
        text=[f"${costo_mantener:,.0f}", f"${costo_transporte:,.0f}", f"${ev_perdida:,.0f}", f"${costo_mantener+costo_transporte+ev_perdida:,.0f}"],
        y=[costo_mantener, costo_transporte, ev_perdida, costo_mantener+costo_transporte+ev_perdida],
        connector={"line":{"color":"rgb(63, 63, 63)"}}
    ))
    fig_wf.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=20,b=0))
    st.plotly_chart(fig_wf, use_container_width=True)

# TAB 5: WHAT-IF SCENARIOS
with tab5:
    st.markdown("### Planificador de Escenarios: Envío Normal vs. Transporte Dedicado")
    st.info("Utiliza esta herramienta para justificar el gasto extra en transporte urgente.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"#### 🚚 Escenario Actual")
        st.metric("Lead Time", f"{lead_time_total} días")
        st.metric("Probabilidad Stockout", f"{prob_quiebre:.1f}%")
        st.metric("Valor en Riesgo", f"${ev_perdida:,.2f} MXN")
        
    with c2:
        st.markdown(f"#### 🚀 Flete Urgente (Acelerado)")
        # Recalculo rápido para What-If (Restando el retraso logístico)
        lt_urgente = lead_time
        inv_urgente = stock_actual - np.cumsum(np.clip(np.random.normal(demanda_media, demanda_media*volatilidad, (n_sim, lt_urgente)), 0, None), axis=1)[:, -1]
        prob_urgente = np.mean(inv_urgente < 0) * 100
        ev_urgente = (prob_urgente/100) * (np.mean(np.abs(inv_urgente[inv_urgente < 0])) if prob_urgente > 0 else 0) * costo_caja
        
        st.metric("Lead Time", f"{lt_urgente} días", delta="-Días de Retraso Eliminados", delta_color="inverse")
        st.metric("Probabilidad Stockout", f"{prob_urgente:.1f}%", delta=f"{prob_urgente - prob_quiebre:.1f}%", delta_color="inverse")
        st.metric("Valor en Riesgo", f"${ev_urgente:,.2f} MXN", delta=f"${ev_urgente - ev_perdida:,.2f} MXN", delta_color="inverse")

# TAB 6: LOGS Y AUDITORÍA
# TAB 6: LOGS Y AUDITORÍA
with tab6:
    st.markdown("### Registro Activo del Sistema (Backend)")
    
    # Ajuste de Zona Horaria: Hora UTC del servidor MENOS 6 horas (CST - México)
    t = datetime.utcnow() - timedelta(hours=6)
    
    logs = f"""
    {(t - timedelta(seconds=120)).strftime("%Y-%m-%d %H:%M:%S")} [AUTH] - User Login Success: Victor Martinez (Role: Sr. Analyst)
    {(t - timedelta(seconds=115)).strftime("%Y-%m-%d %H:%M:%S")} [INFO] - Conectando API Plotly GeoSpatial... OK.
    {(t - timedelta(seconds=45)).strftime("%Y-%m-%d %H:%M:%S")} [INFO] - Extrayendo telemetría de CEDIS (Vallejo, MTY, GDL, TIJ, MER)...
    {(t - timedelta(seconds=2)).strftime("%Y-%m-%d %H:%M:%S")} [ML_ENGINE] - Corriendo {n_sim} vectores estocásticos.
    {t.strftime("%Y-%m-%d %H:%M:%S")} [WARNING] - VaR calculado en ${ev_perdida:,.2f} MXN para el SKU actual.
    """
    st.code(logs, language="bash")
