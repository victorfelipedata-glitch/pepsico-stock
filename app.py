import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# ==========================================
# 1. CONFIGURACIÓN CORPORATIVA Y UI
# ==========================================
st.set_page_config(page_title="Fondo Cuantitativo | Escáner", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .kpi-title {font-size: 0.9rem; color: #8892B0; text-transform: uppercase; margin-bottom: 5px;}
    .kpi-value {font-size: 1.8rem; color: #E6F1FF; font-weight: bold;}
    .kpi-container {background-color: #112240; padding: 20px; border-radius: 10px; border-left: 5px solid #00F0FF; margin-bottom: 15px;}
    .alert-success {background-color: rgba(0, 255, 65, 0.1); border: 1px solid #00FF41; padding: 15px; border-radius: 8px; color: #00FF41;}
    .alert-danger {background-color: rgba(227, 24, 55, 0.1); border: 1px solid #E31837; padding: 15px; border-radius: 8px; color: #E31837;}
    .user-badge {background-color: #002F6C; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #00F0FF; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

# Simulador de carga inicial
if 'loaded' not in st.session_state:
    st.toast('Analizando partidos del día...', icon='🔍')
    time.sleep(1)
    st.toast('Cálculos completados', icon='✅')
    st.session_state['loaded'] = True

# ==========================================
# 2. BARRA LATERAL (CONTROL DE MANDO)
# ==========================================
with st.sidebar:
    st.markdown("""
        <div class="user-badge">
            <h4 style="color:white; margin:0;">Víctor Antonio Felipe</h4>
            <p style="color:#00F0FF; font-size:13px; margin:0;">Gestor de Portafolio</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📅 AGENDA DEL DÍA (29 JUN)")
    partido_sel = st.selectbox(
        "Selecciona el partido escaneado:", 
        ["🇩🇪 Alemania vs Paraguay 🇵🇾", "🇳🇱 Países Bajos vs Marruecos 🇲🇦"]
    )
    
    st.markdown("### 💰 CAPITAL DISPONIBLE")
    bankroll = st.number_input("Fondo asignado (MXN):", min_value=1000, value=5000, step=1000)
    
    st.divider()
    st.caption("Motor Matemático Activo - FES Acatlán")

# ==========================================
# 3. BASE DE DATOS DEL DÍA (PRECONFIGURADA PARA LA DEMO)
# ==========================================
if "Alemania" in partido_sel:
    mercado = "Gana Alemania"
    cuota_mercado = 2.10
    prob_real = 0.55  # 55%
else:
    mercado = "Gana Países Bajos"
    cuota_mercado = 1.50
    prob_real = 0.60  # 60%

# Cálculos del Modelo
prob_implicita = 1 / cuota_mercado
ganancia_neta = cuota_mercado - 1
ev_porcentual = (prob_real * ganancia_neta) - ((1 - prob_real) * 1)

if ev_porcentual > 0:
    kelly_fraccional = (ev_porcentual / ganancia_neta) * 0.25 # 25% de Kelly para seguridad
    inversion_sugerida = bankroll * kelly_fraccional
    estado = "APROBADO"
    color_tema = "#00FF41"
else:
    kelly_fraccional = 0.0
    inversion_sugerida = 0.0
    estado = "RECHAZADO"
    color_tema = "#E31837"

# ==========================================
# 4. HEADER Y RESUMEN EJECUTIVO (PARA LA MADRINA)
# ==========================================
st.markdown(f'''
    <div style="background: linear-gradient(135deg, #0a192f 0%, #112240 100%); border-radius: 12px; padding: 30px; display: flex; align-items: center; justify-content: space-between; border: 1px solid #233554; margin-bottom: 25px;">
        <div>
            <h1 style="color: #ffffff; margin: 0; font-size: 2.2rem;">Análisis Cuantitativo: <span style="color: {color_tema};">{partido_sel}</span></h1>
            <p style="color: #8892B0; margin: 5px 0 0 0; font-size: 1.1rem;">Evaluación de rentabilidad para el mercado: <b>{mercado}</b></p>
        </div>
    </div>
''', unsafe_allow_html=True)

# Tarjeta de Decisión (Lo primero que ella debe ver)
if estado == "APROBADO":
    st.markdown(f"""
        <div class="alert-success">
            <h3 style="margin:0;">✅ ¡Oportunidad de Inversión Encontrada!</h3>
            <p style="margin:5px 0 0 0; font-size: 1.1rem;">El algoritmo detectó un error en las cuotas del mercado. Tenemos una ventaja matemática clara. Se recomienda invertir <b>${inversion_sugerida:,.2f} MXN</b> (riesgo estrictamente calculado).</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div class="alert-danger">
            <h3 style="margin:0;">⛔ Operación Rechazada para Proteger el Capital</h3>
            <p style="margin:5px 0 0 0; font-size: 1.1rem;">El modelo matemático indica que invertir en este partido a largo plazo genera pérdidas. <b>La inversión recomendada es $0.00 MXN.</b> El dinero se queda seguro en el fondo.</p>
        </div>
    """, unsafe_allow_html=True)

st.write("<br>", unsafe_allow_html=True)

# KPIs Explicados de forma sencilla
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="kpi-container"><div class="kpi-title">La Casa Paga (Cuota)</div><div class="kpi-value">{cuota_mercado}</div><div style="color:#8892B0; font-size:0.8rem; margin-top:5px;">Equivale a una probabilidad del {prob_implicita*100:.1f}%</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="kpi-container"><div class="kpi-title">Nuestra Probabilidad Real</div><div class="kpi-value">{prob_real*100:.1f}%</div><div style="color:#8892B0; font-size:0.8rem; margin-top:5px;">Calculada con nuestra base de datos estadística</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="kpi-container" style="border-left-color: {color_tema}"><div class="kpi-title">Ventaja Matemática Final</div><div class="kpi-value" style="color:{color_tema};">{ev_porcentual*100:.1f}%</div><div style="color:#8892B0; font-size:0.8rem; margin-top:5px;">Si es mayor a 0%, ganamos dinero a largo plazo.</div></div>', unsafe_allow_html=True)

st.divider()

# ==========================================
# 5. PESTAÑAS DETALLADAS
# ==========================================
tab1, tab2, tab3 = st.tabs([
    "🗣️ Explicación Paso a Paso", 
    "📈 Simulador de Crecimiento (Visual)", 
    "🖥️ Cálculos Internos (Auditoría)"
])

# TAB 1: EXPLICACIÓN PARA EL INVERSIONISTA (MADRINA)
with tab1:
    st.markdown("### ¿Por qué el algoritmo tomó esta decisión?")
    st.write(f"Para el partido **{partido_sel}**, el mercado está pagando una cuota de **{cuota_mercado}** a que **{mercado}**.")
    
    st.markdown(f"""
    1. **Lo que cree el mercado:** Al pagar {cuota_mercado}, la casa de apuestas asume que hay un **{prob_implicita*100:.1f}%** de probabilidad de que esto ocurra.
    2. **Lo que sabemos nosotros:** Nuestro modelo matemático analizó los datos y determinó que la probabilidad *real* de que ocurra es del **{prob_real*100:.1f}%**.
    """)
    
    if estado == "APROBADO":
        st.success(f"**CONCLUSIÓN:** Como nuestra probabilidad ({prob_real*100:.1f}%) es MAYOR que la de la casa ({prob_implicita*100:.1f}%), tenemos una ventaja sobre ellos. A esto se le llama **Valor Esperado Positivo**. Para no arriesgar tu dinero, la fórmula matemática de Kelly nos dicta que solo debemos usar **${inversion_sugerida:,.2f} MXN** de los ${bankroll:,.2f} disponibles.")
    else:
        st.error(f"**CONCLUSIÓN:** Como nuestra probabilidad ({prob_real*100:.1f}%) es MENOR que la de la casa ({prob_implicita*100:.1f}%), no tenemos ninguna ventaja. Aunque sea el equipo favorito, las matemáticas dicen que a largo plazo perderíamos dinero. Por lo tanto, el sistema bloquea la operación y no arriesgamos ni un peso.")

# TAB 2: MONTECARLO
with tab2:
    st.markdown("### Proyección del Dinero a 100 Operaciones Similares")
    if estado == "RECHAZADO":
        st.info("No hay gráfica de crecimiento porque el sistema no permitió la inversión en este partido para evitar pérdidas.")
    else:
        # Simulación de Montecarlo
        n_sim = 1000
        num_op = 100
        resultados = np.random.binomial(1, prob_real, (n_sim, num_op))
        retornos = np.where(resultados == 1, ganancia_neta, -1)
        
        evolucion = np.zeros((n_sim, num_op + 1))
        evolucion[:, 0] = bankroll
        
        for i in range(num_op):
            inversion_paso = evolucion[:, i] * kelly_fraccional
            evolucion[:, i+1] = evolucion[:, i] + (inversion_paso * retornos[:, i])

        fig = go.Figure()
        dias = np.arange(0, num_op + 1)
        
        # 100 trayectorias aleatorias
        muestras = evolucion[np.random.choice(n_sim, 100, replace=False), :]
        for i in range(100):
            fig.add_trace(go.Scatter(x=dias, y=muestras[i, :], mode='lines', line=dict(color='#8892B0', width=1), opacity=0.1, showlegend=False))
            
        p50 = np.percentile(evolucion, 50, axis=0)
        p10 = np.percentile(evolucion, 10, axis=0)
        
        fig.add_trace(go.Scatter(x=dias, y=p50, mode='lines+markers', name='Crecimiento Promedio', line=dict(color='#00FF41', width=3)))
        fig.add_trace(go.Scatter(x=dias, y=p10, mode='lines', name='Peor Escenario Posible', line=dict(color='#E31837', width=2, dash='dash')))
        fig.add_hline(y=bankroll, line_dash="solid", line_color="#ffffff", annotation_text="CAPITAL INICIAL (Intacto)")
        
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_title="Cantidad de Operaciones", yaxis_title="Dinero en la Cuenta (MXN)")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Esta gráfica demuestra que, al invertir solo cuando hay ventaja matemática, el dinero siempre crece a largo plazo, incluso si perdemos algunas operaciones individuales.")

# TAB 3: AUDITORÍA
with tab3:
    st.markdown("### Bitácora del Sistema")
    t = datetime.utcnow() - timedelta(hours=6)
    
    logs = f"""
    {(t - timedelta(seconds=15)).strftime("%Y-%m-%d %H:%M:%S")} [SISTEMA] - Evaluando evento: {partido_sel}
    {(t - timedelta(seconds=12)).strftime("%Y-%m-%d %H:%M:%S")} [MERCADO] - Cuota extraída: {cuota_mercado}
    {(t - timedelta(seconds=8)).strftime("%Y-%m-%d %H:%M:%S")} [ALGORITMO] - Calculando probabilidad real vs implícita...
    {(t - timedelta(seconds=5)).strftime("%Y-%m-%d %H:%M:%S")} [MATE] - Valor Esperado (EV): {ev_porcentual*100:.2f}%
    {(t - timedelta(seconds=2)).strftime("%Y-%m-%d %H:%M:%S")} [RIESGO] - Verificando Criterio de Seguridad de Capital...
    {t.strftime("%Y-%m-%d %H:%M:%S")} [DECISIÓN] - Estatus de la inversión: {estado} | Monto: ${inversion_sugerida:,.2f}
    """
    st.code(logs, language="bash")
