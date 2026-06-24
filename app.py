import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import time

# --- 1. CONFIGURACIÓN CORPORATIVA ---
st.set_page_config(
    page_title="Control Tower | PepsiCo Analytics",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS inyectados para lucir corporativo
st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; color: #002F6C; font-weight: 800; margin-bottom: 0px;}
    .sub-header {font-size: 1.2rem; color: #00A3E0; font-weight: 600; margin-top: -10px; margin-bottom: 20px;}
    .metric-card {background-color: #f8fafc; border-left: 5px solid #002F6C; padding: 15px; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);}
    </style>
""", unsafe_allow_html=True)

# --- 2. GENERACIÓN DE BASE DE DATOS MASIVA (Simulación de Data Lake) ---
@st.cache_data
def load_enterprise_data():
    # Simulamos el tiempo de conexión a la nube de PepsiCo
    time.sleep(1.5) 
    
    categorias = {
        "Botanas Saladas": [
            "Sabritas Original 110g", "Doritos Nacho 146g", "Cheetos Torciditos 150g", "Ruffles Queso 120g",
            "Tostitos Salsa Verde 240g", "Fritos Sal y Limón 110g", "Rancheritos 160g", "Crujitos 120g"
        ],
        "Bebidas": [
            "Pepsi Black 600ml", "Pepsi Regular 2.5L", "Gatorade Naranja 1L", "Gatorade Moras 500ml",
            "7Up 600ml", "Mirinda 600ml", "Epura 1L", "Lipton Ice Tea Durazno 600ml"
        ],
        "Galletas y Dulces": [
            "Emperador Chocolate 101g", "Chokis Clásica 84g", "Marias Gamesa 170g", "Arcoiris 115g",
            "Mamut Flipy 45g", "Surtido Rico 436g", "Florentinas Cajeta 83g", "Giro 114g"
        ],
        "Nutrición": [
            "Avena Quaker 400g", "Barras Stila 120g", "Granola Quaker 350g", "Avena 3 Minutos 500g"
        ]
    }
    
    datos = []
    np.random.seed(10) # Para mantener consistencia en la demo
    for cat, prods in categorias.items():
        for prod in prods:
            datos.append({
                "Categoría": cat,
                "SKU_Name": prod,
                "Demanda_Base": np.random.randint(50, 400),
                "Costo_Unitario": np.random.uniform(15.0, 65.0),
                "Margen_Venta_Multiplicador": np.random.uniform(15, 30) # Valor de penalización por quiebre
            })
    return pd.DataFrame(datos)

df_productos = load_enterprise_data()

CEDIS = {
    "CEDIS Vallejo (CDMX)": {"var": 1.25, "lead_time_base": 2},
    "CEDIS Monterrey": {"var": 1.40, "lead_time_base": 3},
    "CEDIS Guadalajara": {"var": 1.15, "lead_time_base": 2},
    "CEDIS Tijuana": {"var": 1.60, "lead_time_base": 5},
    "CEDIS Mérida": {"var": 1.10, "lead_time_base": 4},
    "CEDIS Toluca": {"var": 0.95, "lead_time_base": 1}
}

# --- 3. INTERFAZ DE USUARIO ---
st.markdown('<p class="main-header">Control Tower: Predictive Supply Chain</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Módulo de Prevención de Quiebres | Modelo Estocástico de Monte Carlo</p>', unsafe_allow_html=True)

# Simulador de carga de red
with st.spinner('Conectando con Azure Data Lake (Pepsico Central)... extrayendo telemetría de CEDIS...'):
    time.sleep(1)

# Sidebar corporativo
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/PepsiCo_logo.svg/512px-PepsiCo_logo.svg.png", width=150)
st.sidebar.markdown("---")
st.sidebar.header("🎯 Filtros de Operación")

cedis_sel = st.sidebar.selectbox("Planta / CEDIS", list(CEDIS.keys()))
cat_sel = st.sidebar.selectbox("Categoría de Negocio", df_productos['Categoría'].unique())

# Filtrar productos por categoría
df_filtrado = df_productos[df_productos['Categoría'] == cat_sel]
prod_sel = st.sidebar.selectbox("SKU a Analizar", df_filtrado['SKU_Name'].tolist())

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Parámetros de Simulación")
inv_actual = st.sidebar.number_input("Stock Físico Actual (Cajas)", min_value=0, max_value=10000, value=850, step=50)
retraso_logistico = st.sidebar.slider("Días de Retraso Extra (Tráfico/Clima)", min_value=0, max_value=5, value=0)
n_simulaciones = st.sidebar.select_slider("Resolución de Simulación (Vectores)", options=[1000, 5000, 10000], value=5000)

# --- 4. MOTOR MATEMÁTICO ---
# Extraer datos del SKU
datos_sku = df_filtrado[df_filtrado['SKU_Name'] == prod_sel].iloc[0]
demanda_lambda = int(datos_sku['Demanda_Base'] * CEDIS[cedis_sel]['var'])
costo_quiebre = datos_sku['Costo_Unitario'] * datos_sku['Margen_Venta_Multiplicador']
lead_time_total = CEDIS[cedis_sel]['lead_time_base'] + retraso_logistico
horizonte = lead_time_total + 5 # Simular días extra después del camión

# Ejecución de Monte Carlo Vectorizada (¡Mucho más rápido y profesional!)
np.random.seed(42)
# Generamos todas las demandas diarias de una vez (Matriz: Simulaciones x Días)
demandas_simuladas = np.random.poisson(lam=demanda_lambda, size=(n_simulaciones, horizonte))
# Calculamos el inventario acumulado restando la suma acumulada de las demandas
inventario_acumulado = inv_actual - np.cumsum(demandas_simuladas, axis=1)

# Evaluar quiebres exactos durante el Lead Time
# Cortamos la matriz hasta el día que llega el camión
inventario_lead_time = inventario_acumulado[:, :lead_time_total]
# Si el mínimo de la trayectoria es menor a 0, hubo quiebre
quiebres_array = np.min(inventario_lead_time, axis=1) < 0

prob_quiebre = (np.sum(quiebres_array) / n_simulaciones) * 100
# Calcular cajas faltantes promedio solo en los escenarios donde hubo quiebre
faltantes_escenarios = np.abs(np.minimum(inventario_lead_time[quiebres_array, -1], 0))
promedio_cajas_faltantes = np.mean(faltantes_escenarios) if len(faltantes_escenarios) > 0 else 0
riesgo_financiero = (prob_quiebre/100) * promedio_cajas_faltantes * costo_quiebre

# --- 5. DASHBOARD DE ALTO IMPACTO ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Demanda Diaria Esperada", f"{demanda_lambda} cajas", f"Ajuste {CEDIS[cedis_sel]['var']}x")
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Punto de Reorden (ROP)", f"{demanda_lambda * lead_time_total} cajas", "Mínimo sugerido", delta_color="off")
    st.markdown('</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Probabilidad de Desabasto", f"{prob_quiebre:.1f}%", "Riesgo Crítico" if prob_quiebre > 20 else "Controlado", delta_color="inverse")
    st.markdown('</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Valor Monetario en Riesgo", f"${riesgo_financiero:,.0f} MXN", "Pérdida esperada de sell-out", delta_color="inverse")
    st.markdown('</div>', unsafe_allow_html=True)

st.write("") # Espacio

# Pestañas de Análisis (Muestra mucha robustez de desarrollo)
tab1, tab2 = st.tabs(["📊 Visor Cuántico de Simulaciones (Monte Carlo)", "📋 Actionable Insights (Recomendaciones)"])

with tab1:
    st.markdown("##### Trayectorias Estocásticas de Inventario")
    st.write("Visualización de las distintas realidades posibles de consumo. La línea roja marca la llegada del transporte logístico.")
    
    # Gráfica Premium con Plotly
    fig = go.Figure()
    
    # Eje X
    dias_eje = np.arange(1, horizonte + 1)
    
    # Dibujar 50 trayectorias grises para contexto visual
    for i in range(50):
        fig.add_trace(go.Scatter(x=dias_eje, y=inventario_acumulado[i, :], mode='lines', line=dict(color='rgba(150, 150, 150, 0.1)'), showlegend=False, hoverinfo='skip'))
    
    # Calcular y dibujar Percentiles P50 (Mediana), P10 (Pesimista), P90 (Optimista)
    p50 = np.percentile(inventario_acumulado, 50, axis=0)
    p10 = np.percentile(inventario_acumulado, 10, axis=0)
    p90 = np.percentile(inventario_acumulado, 90, axis=0)
    
    fig.add_trace(go.Scatter(x=dias_eje, y=p90, mode='lines', line=dict(color='#00A3E0', width=2, dash='dash'), name='P90 (Demanda Lenta)'))
    fig.add_trace(go.Scatter(x=dias_eje, y=p50, mode='lines', line=dict(color='#002F6C', width=4), name='Mediana Esperada'))
    fig.add_trace(go.Scatter(x=dias_eje, y=p10, mode='lines', line=dict(color='#E31837', width=2, dash='dash'), name='P10 (Demanda Agresiva)'))
    
    # Línea de Quiebre (0)
    fig.add_trace(go.Scatter(x=[1, horizonte], y=[0, 0], mode='lines', line=dict(color='black', width=1), name='Límite de Quiebre'))
    
    # Línea vertical de llegada del camión
    fig.add_vline(x=lead_time_total, line_width=2, line_dash="dash", line_color="orange", annotation_text=f"Llegada de Camión (Día {lead_time_total})")

    fig.update_layout(
        height=450,
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor='white',
        xaxis=dict(title='Días Hacia el Futuro', showgrid=True, gridcolor='#e5e7eb'),
        yaxis=dict(title='Cajas Físicas en CEDIS', showgrid=True, gridcolor='#e5e7eb'),
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("##### Motor de Decisión Automatizado")
    
    if prob_quiebre > 15.0:
        st.error(f"🚨 **ALERTA ROJA EN {cedis_sel.upper()}:** La probabilidad de desabasto para {prod_sel} es del **{prob_quiebre:.1f}%**.")
        st.write("**Instrucciones al sistema ERP (SAP):**")
        st.code(f"""
        > GENERANDO ORDEN DE TRASLADO DE EMERGENCIA...
        > DESTINO: {cedis_sel}
        > MATERIAL: {prod_sel} (SKU ID: {np.random.randint(10000, 99999)})
        > CANTIDAD SUGERIDA: {int(promedio_cajas_faltantes + (demanda_lambda*2))} cajas (Cubre faltante + Safety Stock de 2 días)
        > PRIORIDAD: ALTA (Envío Consolidado Inmediato)
        """, language="sql")
    else:
        st.success(f"✅ **OPERACIÓN ESTABLE:** Los niveles de inventario de {prod_sel} son óptimos para absorber la volatilidad probabilística.")
        st.write(f"El Fill Rate (Nivel de Servicio) proyectado es del **{100 - prob_quiebre:.1f}%**. No se requieren movimientos logísticos no planeados.")
