import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time

# --- 1. CONFIGURACIÓN CORPORATIVA (DARK MODE FORZADO) ---
st.set_page_config(
    page_title="PepsiCo Control Tower",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos para un Dark Mode vibrante y profesional
st.markdown("""
    <style>
    .big-title {font-size: 2.8rem; color: #FFFFFF; font-weight: 900; margin-bottom: 0px; text-transform: uppercase; letter-spacing: 2px;}
    .sub-title {font-size: 1.2rem; color: #00A3E0; font-weight: 400; margin-top: -10px; margin-bottom: 30px; letter-spacing: 1px;}
    .highlight-red {color: #E31837; font-weight: bold;}
    .highlight-blue {color: #00A3E0; font-weight: bold;}
    div[data-testid="stMetricValue"] {font-size: 2rem; color: #FFFFFF;}
    </style>
""", unsafe_allow_html=True)

# --- 2. MOTOR DE DATOS MASIVO ---
@st.cache_data
def load_enterprise_data():
    np.random.seed(42)
    categorias = {
        "Botanas Saladas": ["Sabritas Original 110g", "Doritos Nacho 146g", "Cheetos Torciditos 150g", "Ruffles Queso 120g", "Tostitos Salsa Verde 240g", "Fritos Sal y Limón", "Rancheritos", "Crujitos"],
        "Bebidas": ["Pepsi Black 600ml", "Pepsi Regular 2.5L", "Gatorade Naranja 1L", "Gatorade Moras 500ml", "7Up 600ml", "Mirinda 600ml"],
        "Galletas": ["Emperador Chocolate 101g", "Chokis Clásica 84g", "Marias Gamesa 170g", "Arcoiris 115g", "Mamut Flipy 45g"]
    }
    
    datos = []
    for cat, prods in categorias.items():
        for prod in prods:
            demanda = np.random.randint(100, 800)
            datos.append({
                "SKU_ID": f"MX-{np.random.randint(10000, 99999)}",
                "Categoría": cat,
                "Producto": prod,
                "Demanda_Media_Diaria": demanda,
                "Inventario_Actual": int(demanda * np.random.uniform(1.5, 4.5)),
                "Valor_Unitario_MXN": np.random.uniform(18.0, 75.0),
                "Lead_Time_Dias": np.random.randint(2, 6)
            })
    return pd.DataFrame(datos)

df_db = load_enterprise_data()

# --- 3. SIDEBAR (PANEL DE CONTROL) ---
with st.sidebar:
    st.markdown("### 🎛️ PARÁMETROS DE RED")
    cedis_sel = st.selectbox("📍 Nodo Logístico", ["CEDIS Vallejo (CDMX)", "CEDIS Monterrey", "CEDIS Guadalajara", "CEDIS Tijuana"])
    
    st.markdown("---")
    cat_sel = st.selectbox("📂 Categoría de Negocio", df_db['Categoría'].unique())
    df_cat = df_db[df_db['Categoría'] == cat_sel]
    prod_sel = st.selectbox("📦 SKU Específico", df_cat['Producto'].tolist())
    
    st.markdown("---")
    st.markdown("### ⚙️ ESTRÉS ESTOCÁSTICO")
    retraso_simulado = st.slider("⚠️ Retraso Logístico (Días Extra)", 0, 7, 0)
    volatilidad = st.slider("📈 Volatilidad de Demanda (%)", 0, 100, 20) / 100.0
    n_sim = 10000 # Simulaciones pesadas fijas

# --- 4. CÁLCULO CUANTITATIVO (EV+ y Riesgo) ---
sku_data = df_cat[df_cat['Producto'] == prod_sel].iloc[0]
demanda_lambda = sku_data['Demanda_Media_Diaria'] * (1 + volatilidad)
lead_time_real = sku_data['Lead_Time_Dias'] + retraso_simulado
inventario_inicio = sku_data['Inventario_Actual']
valor_caja = sku_data['Valor_Unitario_MXN']

# Simulaciones vectorizadas
demandas_matriz = np.random.poisson(lam=demanda_lambda, size=(n_sim, lead_time_real))
consumo_total_ruta = np.sum(demandas_matriz, axis=1)
inventario_final_sim = inventario_inicio - consumo_total_ruta

# Métricas de riesgo
quiebres_bool = inventario_final_sim < 0
prob_quiebre = np.mean(quiebres_bool) * 100
cajas_perdidas = np.where(quiebres_bool, np.abs(inventario_final_sim), 0)
ev_perdida = np.mean(cajas_perdidas) * valor_caja
fill_rate = 100 - prob_quiebre

# --- 5. RENDERIZADO DEL DASHBOARD VIBRANTE ---
st.markdown('<p class="big-title">Torre de Control Analítica</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-title">Monitoreo Predictivo Activo | {cedis_sel} | {time.strftime("%H:%M:%S")} CST</p>', unsafe_allow_html=True)

# KPIs Principales
col1, col2, col3, col4 = st.columns(4)
col1.metric("Stock Físico (Cajas)", f"{inventario_inicio:,}", f"Lead Time: {lead_time_real} días")
col2.metric("Punto de Reorden Sugerido", f"{int(demanda_lambda * lead_time_real):,}", "Basado en Volatilidad")
col3.metric("Riesgo de Quiebre", f"{prob_quiebre:.1f}%", "-Crítico" if prob_quiebre > 15 else "Estable", delta_color="inverse")
col4.metric("Valor Esperado Negativo (EV-)", f"- ${ev_perdida:,.2f} MXN", "Riesgo Financiero", delta_color="inverse")

st.markdown("---")

# Pestañas de Análisis Profundo
tab1, tab2, tab3 = st.tabs(["🔭 Análisis Estocástico Avanzado", "📊 Salud Logística de la Categoría", "💻 Terminal de Operaciones"])

# COLORES VIBRANTES PARA GRÁFICOS
color_pepsi_blue = '#005BB5'
color_red_alert = '#E31837'
color_neon_cyan = '#00F0FF'

with tab1:
    c1, c2 = st.columns([2, 1])
    
    with c1:
        # Gráfico 1: Trayectorias de Monte Carlo con Plotly
        st.markdown("##### 📉 Simulación de Consumo vs Tiempo")
        matriz_trayectorias = inventario_inicio - np.cumsum(demandas_matriz, axis=1)
        fig_mc = go.Figure()
        
        # Dibujar 100 trayectorias aleatorias con color cyan transparente
        dias_x = np.arange(1, lead_time_real + 1)
        for i in range(100):
            fig_mc.add_trace(go.Scatter(x=dias_x, y=matriz_trayectorias[i, :], mode='lines', line=dict(color=color_neon_cyan, width=1), opacity=0.05, hoverinfo='skip'))
        
        # Línea Mediana
        p50 = np.percentile(matriz_trayectorias, 50, axis=0)
        fig_mc.add_trace(go.Scatter(x=dias_x, y=p50, mode='lines+markers', name='Consumo Esperado (P50)', line=dict(color='#FFFFFF', width=3)))
        
        # Zona de Quiebre
        fig_mc.add_hline(y=0, line_dash="dash", line_color=color_red_alert, annotation_text="ZONA DE QUIEBRE (STOCK OUT)", annotation_position="bottom right")
        
        fig_mc.update_layout(template="plotly_dark", height=400, margin=dict(l=0, r=0, t=30, b=0), showlegend=False, xaxis_title="Días hasta Resurtido", yaxis_title="Inventario Restante")
        st.plotly_chart(fig_mc, use_container_width=True)

    with c2:
        # Gráfico 2: Distribución del Riesgo (Campana)
        st.markdown("##### 🔔 Distribución de Inventario Final")
        fig_dist = px.histogram(x=inventario_final_sim, nbins=50, color_discrete_sequence=[color_pepsi_blue])
        fig_dist.add_vline(x=0, line_dash="solid", line_color=color_red_alert, line_width=3)
        fig_dist.update_layout(template="plotly_dark", height=400, margin=dict(l=0, r=0, t=30, b=0), showlegend=False, xaxis_title="Cajas al llegar camión", yaxis_title="Frecuencia (Escenarios)")
        st.plotly_chart(fig_dist, use_container_width=True)

with tab2:
    st.markdown(f"##### 📋 Análisis de la categoría entera: {cat_sel}")
    st.write("Visión integral de todos los SKUs para detectar vulnerabilidades cruzadas.")
    
    # Calcular riesgo dinámico para toda la tabla
    df_cat['Stock_Seguridad'] = df_cat['Demanda_Media_Diaria'] * df_cat['Lead_Time_Dias']
    df_cat['Status'] = np.where(df_cat['Inventario_Actual'] < df_cat['Stock_Seguridad'], '🚨 Riesgo Alto', '✅ Saludable')
    
    # Tabla avanzada interactiva
    st.dataframe(
        df_cat[['SKU_ID', 'Producto', 'Inventario_Actual', 'Stock_Seguridad', 'Status']],
        column_config={
            "Inventario_Actual": st.column_config.ProgressColumn("Stock Físico", format="%d", min_value=0, max_value=3000),
            "Stock_Seguridad": st.column_config.NumberColumn("ROP (Punto Reorden)"),
        },
        use_container_width=True,
        hide_index=True
    )

with tab3:
    st.markdown("##### 📟 Consola de Comandos y Exportación")
    st.info(f"El modelo predictivo sugiere un Fill Rate del {fill_rate:.2f}% bajo las condiciones actuales de volatilidad.")
    
    # Simulador de exportación de datos
    csv = df_cat.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Reporte de Categoría (CSV)",
        data=csv,
        file_name=f'analisis_{cat_sel}.csv',
        mime='text/csv',
    )
    
    if prob_quiebre > 10:
        st.error("Protocolo de emergencia logístico recomendado. Aprobar traslado entre CEDIS.")
        if st.button("⚡ Ejecutar Orden de Reabastecimiento Automático en SAP"):
            st.success("✅ Orden enviada exitosamente a la cola de procesamiento ERP.")
