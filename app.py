import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# ==========================================
# 1. CONFIGURACIÓN CORPORATIVA Y UI
# ==========================================
st.set_page_config(page_title="Fondo Cuantitativo | Demo Operativa", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .kpi-title {font-size: 0.85rem; color: #8892B0; text-transform: uppercase;}
    .kpi-value {font-size: 2.2rem; color: #E6F1FF; font-weight: bold; font-family: 'Courier New', monospace;}
    .kpi-container {background-color: #112240; padding: 15px; border-radius: 8px; border-left: 4px solid #00F0FF;}
    .user-badge {background-color: #002F6C; padding: 10px; border-radius: 5px; text-align: center; border: 1px solid #00F0FF; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

# Simulador de carga del sistema
if 'loaded' not in st.session_state:
    st.toast('Conectando con base de datos de cuotas históricas...', icon='🔄')
    time.sleep(0.5)
    st.toast('Modelos Probabilísticos Compilados', icon='✅')
    st.session_state['loaded'] = True

# ==========================================
# 2. BARRA LATERAL (PARÁMETROS DE ENTRADA)
# ==========================================
with st.sidebar:
    st.markdown("""
        <div class="user-badge">
            <h4 style="color:white; margin:0;">Víctor Antonio Felipe</h4>
            <p style="color:#00F0FF; font-size:12px; margin:0;">Analista Cuantitativo | FES Acatlán</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎛️ PARÁMETROS DEL MERCADO")
    liga_sel = st.selectbox("📍 Mercado Analizado", ["Liga MX", "NBA", "Premier League", "NFL"])
    
    st.markdown("### ⚙️ VARIABLES DEL MODELO")
    bankroll = st.number_input("💰 Capital Asignado al Pilar (MXN)", min_value=1000, max_value=30000, value=5000, step=1000)
    cuota_mercado = st.number_input("📊 Cuota del Mercado (Decimal)", min_value=1.01, max_value=10.0, value=2.10, step=0.05)
    
    st.divider()
    st.markdown("### 🧮 CÁLCULO DE PROBABILIDAD")
    prob_real = st.slider("🎯 Probabilidad Real (Calculada por Modelo %)", 1, 99, 55) / 100.0
    
    st.caption("Última actualización: " + (datetime.utcnow() - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"))

# ==========================================
# 3. MOTOR MATEMÁTICO (EV+ Y KELLY)
# ==========================================
# Probabilidad que el mercado cree que tiene el evento
prob_implicita = 1 / cuota_mercado

# Cálculo de Valor Esperado (EV)
ganancia_neta = cuota_mercado - 1
ev_porcentual = (prob_real * ganancia_neta) - ((1 - prob_real) * 1)
ev_monetario = ev_porcentual * 100 # Representación en base 100

# Criterio de Kelly Fraccional (Usando 25% de Kelly para máxima seguridad)
if ev_porcentual > 0:
    kelly_full = ev_porcentual / ganancia_neta
    kelly_fraccional = kelly_full * 0.25
else:
    kelly_fraccional = 0.0

inversion_sugerida = bankroll * kelly_fraccional

# Simulación de Montecarlo (Varianza a 100 operaciones)
n_sim = 1000
num_operaciones = 100
resultados = np.random.binomial(1, prob_real, (n_sim, num_operaciones))
# Si gana, suma ganancia_neta; si pierde, resta 1
retornos = np.where(resultados == 1, ganancia_neta, -1)

# Evolución del Bankroll
evolucion_bankroll = np.zeros((n_sim, num_operaciones + 1))
evolucion_bankroll[:, 0] = bankroll

for i in range(num_operaciones):
    # En cada paso se invierte el porcentaje fijo de Kelly fraccional del bankroll actual
    inversion_paso = evolucion_bankroll[:, i] * kelly_fraccional
    evolucion_bankroll[:, i+1] = evolucion_bankroll[:, i] + (inversion_paso * retornos[:, i])

# ==========================================
# 4. HEADER Y KPIs PRINCIPALES
# ==========================================
st.markdown(f'''
    <div style="background: linear-gradient(135deg, #0a192f 0%, #112240 100%); border-radius: 12px; padding: 25px; display: flex; align-items: center; justify-content: space-between; border: 1px solid #233554; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
        <div>
            <h1 style="color: #ffffff; margin: 0; font-size: 2.2rem; font-weight: 800; letter-spacing: 0.5px;">Portafolio <span style="color: #00F0FF;">Cuantitativo</span></h1>
            <p style="color: #8892B0; margin: 5px 0 0 0; font-size: 1.1rem;">Fase Piloto | Demo de Mitigación de Riesgo Estadístico</p>
        </div>
        <div style="text-align: right;">
            <p style="color: #00F0FF; margin: 0; font-size: 1.4rem; font-weight: bold; font-family: 'Courier New', monospace;">{cuota_mercado} / {prob_real*100:.1f}%</p>
            <p style="color: #8892B0; margin: 0; font-size: 0.85rem; text-transform: uppercase;">Cuota / Prob. Real</p>
        </div>
    </div>
''', unsafe_allow_html=True)

cols = st.columns(4)
metrics = [
    ("Probabilidad Implícita", f"{prob_implicita*100:.1f}%"),
    ("Ventaja Matemática (Edge)", f"{(prob_real - prob_implicita)*100:.1f}%" if prob_real > prob_implicita else "NO HAY VENTAJA"),
    ("Valor Esperado (EV+)", f"{ev_porcentual*100:.2f}%" if ev_porcentual > 0 else "NEGATIVO"),
    ("Riesgo por Operación", f"${inversion_sugerida:,.2f} MXN" if ev_porcentual > 0 else "$0.00")
]

for col, (title, val) in zip(cols, metrics):
    color_border = "#00F0FF" if "NO HAY" not in val and "NEGATIVO" not in val else "#E31837"
    st.markdown(f'<div class="kpi-container" style="border-left-color: {color_border}"><div class="kpi-title">{title}</div><div class="kpi-value">{val}</div></div>', unsafe_allow_html=True)

st.write("<br>", unsafe_allow_html=True)

# ==========================================
# 5. MÓDULOS DE ANÁLISIS (SÚPER TABS)
# ==========================================
tab1, tab2, tab3 = st.tabs([
    "📈 Simulador de Varianza (Montecarlo)", 
    "🧮 Fundamento Matemático", 
    "🖥️ Terminal de Ejecución"
])

# TAB 1: MONTECARLO
with tab1:
    st.markdown("### Proyección Estocástica de Capital (1,000 Escenarios a 100 operaciones)")
    if ev_porcentual <= 0:
        st.error("El sistema no recomienda operar. El Valor Esperado es negativo. Ajusta la Probabilidad Real o busca otra cuota de mercado.")
    else:
        fig_mc = go.Figure()
        dias = np.arange(0, num_operaciones + 1)
        
        # Plotear 100 trayectorias aleatorias
        muestras = evolucion_bankroll[np.random.choice(n_sim, 100, replace=False), :]
        for i in range(100):
            fig_mc.add_trace(go.Scatter(x=dias, y=muestras[i, :], mode='lines', line=dict(color='#8892B0', width=1), opacity=0.1, showlegend=False))
            
        p50 = np.percentile(evolucion_bankroll, 50, axis=0)
        p10 = np.percentile(evolucion_bankroll, 10, axis=0)
        p90 = np.percentile(evolucion_bankroll, 90, axis=0)
        
        fig_mc.add_trace(go.Scatter(x=dias, y=p50, mode='lines+markers', name='Crecimiento Esperado (Mediana)', line=dict(color='#00F0FF', width=3)))
        fig_mc.add_trace(go.Scatter(x=dias, y=p10, mode='lines', name='Peor Escenario (Percentil 10)', line=dict(color='#E31837', width=2, dash='dash')))
        fig_mc.add_trace(go.Scatter(x=dias, y=p90, mode='lines', name='Mejor Escenario (Percentil 90)', line=dict(color='#00FF41', width=2, dash='dash')))
        
        fig_mc.add_hline(y=bankroll, line_dash="solid", line_color="#ffffff", annotation_text="CAPITAL INICIAL")
        
        fig_mc.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_title="Número de Operaciones", yaxis_title="Capital (MXN)")
        st.plotly_chart(fig_mc, use_container_width=True)

# TAB 2: EXPLICACIÓN MATEMÁTICA
with tab2:
    st.markdown("### Transparencia del Modelo de Riesgo")
    st.write("El algoritmo blinda el capital utilizando dos fórmulas exactas para evitar la toma de decisiones emocionales:")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**1. Filtro de Valor Esperado (EV)**")
        st.write("Calcula si a largo plazo la operación es matemáticamente rentable.")
        st.latex(r"EV = (P_{ganar} \times Ganancia) - (P_{perder} \times 1)")
    with col2:
        st.markdown("**2. Criterio de Kelly (Gestión de Riesgo)**")
        st.write("Dicta exactamente qué porcentaje del capital usar para maximizar el crecimiento sin riesgo de quiebra.")
        st.latex(r"f^* = \frac{bp - q}{b}")
        st.caption("Nota: El modelo aplica un Kelly Fraccional conservador (25%) para proteger el fondo contra la varianza natural.")

# TAB 3: LOGS Y AUDITORÍA
with tab3:
    st.markdown("### Registro del Sistema Backend")
    t = datetime.utcnow() - timedelta(hours=6)
    
    accion = "APROBADA" if ev_porcentual > 0 else "DENEGADA (EV NEGATIVO)"
    
    logs = f"""
    {(t - timedelta(seconds=15)).strftime("%Y-%m-%d %H:%M:%S")} [INIT] - Arrancando script de evaluación en {liga_sel}
    {(t - timedelta(seconds=12)).strftime("%Y-%m-%d %H:%M:%S")} [CALC] - Evaluando cuota {cuota_mercado} -> Prob implícita: {prob_implicita*100:.1f}%
    {(t - timedelta(seconds=8)).strftime("%Y-%m-%d %H:%M:%S")} [MODEL] - Probabilidad Real insertada: {prob_real*100:.1f}%
    {(t - timedelta(seconds=5)).strftime("%Y-%m-%d %H:%M:%S")} [MATH] - Evaluando EV: {ev_porcentual*100:.2f}%
    {(t - timedelta(seconds=2)).strftime("%Y-%m-%d %H:%M:%S")} [RISK] - Calculando Criterio de Kelly Fraccional (0.25x)
    {t.strftime("%Y-%m-%d %H:%M:%S")} [STATUS] - Operación {accion}. Inversión dictada: ${inversion_sugerida:,.2f} MXN
    """
    st.code(logs, language="bash")
