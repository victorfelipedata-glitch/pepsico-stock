import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import logging
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

# ==========================================
# 1. CONFIGURACIÓN DEL SISTEMA Y LOGGING
# ==========================================
st.set_page_config(page_title="PepsiCo | Advanced SCM Tower", layout="wide", initial_sidebar_state="expanded")

# Configurar el logger backend (Típico en entornos de producción Senior)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PepsiCo_SCM_Engine")

# Estilos CSS Avanzados Inyectados
st.markdown("""
    <style>
    .kpi-title {font-size: 0.9rem; color: #8892B0; text-transform: uppercase; letter-spacing: 1px;}
    .kpi-value {font-size: 2.5rem; color: #E6F1FF; font-weight: 700; font-family: 'Courier New', monospace;}
    .kpi-container {background-color: #112240; padding: 20px; border-radius: 8px; border-left: 4px solid #64FFDA;}
    .stTabs [data-baseweb="tab-list"] {gap: 24px;}
    .stTabs [data-baseweb="tab"] {height: 50px; white-space: pre-wrap; background-color: transparent; border-radius: 4px; color: #8892B0; font-size: 16px;}
    .stTabs [aria-selected="true"] {color: #64FFDA !important; border-bottom: 2px solid #64FFDA;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ESTRUCTURAS DE DATOS (Dataclasses)
# ==========================================
@dataclass
class SKUProfile:
    """Estructura de datos tipada para el manejo seguro de memoria de cada producto."""
    id_sap: str
    nombre: str
    categoria: str
    demanda_mu: float  # Media poblacional
    demanda_sigma: float # Desviación estándar (Volatilidad)
    lead_time_mu: int
    costo_unitario: float
    margen_contribucion: float

# ==========================================
# 3. MOTOR DE DATOS (Data Abstraction Layer)
# ==========================================
class DataLakeConnector:
    """Clase encargada de simular la conexión, extracción y limpieza del Data Lake corporativo."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        np.random.seed(self.seed)
        logger.info("Instanciando conexión simulada con Azure Data Lake.")

    @st.cache_data(ttl=3600) # Caché de 1 hora
    def fetch_inventory_master_data(_self) -> pd.DataFrame:
        """Genera un DataFrame masivo con más de 100 SKUs simulando una extracción SQL."""
        logger.info("Ejecutando query SELECT * FROM scm_master_inventory...")
        time.sleep(1) # Simular latencia de red
        
        categorias = ["Bebidas Carbonatadas", "Botanas Saladas", "Galletas", "Nutrición Deportiva", "Avenas y Cereales"]
        datos = []
        
        # Generación de 150 SKUs de forma dinámica
        for i in range(1, 151):
            cat = np.random.choice(categorias, p=[0.3, 0.3, 0.2, 0.1, 0.1])
            mu = np.random.lognormal(mean=5.0, sigma=1.0) # Demanda lognormal
            datos.append(SKUProfile(
                id_sap=f"1000{i:04d}",
                nombre=f"SKU_Generico_{i} ({cat[:3]})",
                categoria=cat,
                demanda_mu=mu,
                demanda_sigma=mu * np.random.uniform(0.1, 0.4),
                lead_time_mu=np.random.randint(2, 8),
                costo_unitario=np.random.uniform(10.0, 150.0),
                margen_contribucion=np.random.uniform(0.2, 0.6)
            ))
            
        # Nombres reales para la demo
        productos_demo = ["Sabritas Original 110g", "Pepsi Black 600ml", "Gatorade Naranja 1L", "Doritos Nacho 146g"]
        for idx, prod in enumerate(productos_demo):
            datos[idx].nombre = prod
            
        df = pd.DataFrame([vars(d) for d in datos])
        df['Stock_Actual'] = (df['demanda_mu'] * df['lead_time_mu'] * np.random.uniform(0.8, 2.5)).astype(int)
        logger.info(f"Extracción completada: {len(df)} registros obtenidos.")
        return df

# ==========================================
# 4. MOTOR ESTOCÁSTICO (Core Matemático)
# ==========================================
class StochasticEngine:
    """Motor de cálculo matemático para simulaciones de Monte Carlo y cadenas de Markov."""
    
    def __init__(self, n_simulations: int = 10000):
        self.n_sim = n_simulations
        logger.info(f"Stochastic Engine inicializado con una resolución de {self.n_sim} vectores.")

    def run_montecarlo_pipeline(self, stock_inicial: int, mu_demanda: float, sigma_demanda: float, lead_time: int) -> Tuple[np.ndarray, float, float]:
        """
        Ejecuta la simulación usando distribuciones normales truncadas para evitar demandas negativas.
        Retorna la matriz de trayectorias, la probabilidad de quiebre y el Expected Value negativo.
        """
        # Matriz de demandas diarias vectorizada
        demandas_diarias = np.random.normal(loc=mu_demanda, scale=sigma_demanda, size=(self.n_sim, lead_time))
        demandas_diarias = np.clip(demandas_diarias, a_min=0, a_max=None) # Limpieza estocástica
        
        # Trayectoria de inventario
        consumo_acumulado = np.cumsum(demandas_diarias, axis=1)
        matriz_inventario = stock_inicial - consumo_acumulado
        
        # Análisis del día de llegada del camión
        inventario_final = matriz_inventario[:, -1]
        
        quiebres = inventario_final < 0
        prob_desabasto = np.mean(quiebres) * 100
        
        # Faltante promedio
        faltantes = np.abs(inventario_final[quiebres])
        faltante_esperado = np.mean(faltantes) if len(faltantes) > 0 else 0
        
        return matriz_inventario, prob_desabasto, faltante_esperado

# ==========================================
# 5. CONSTRUCTOR DE INTERFAZ (UI Builder)
# ==========================================
class ControlTowerUI:
    """Clase encargada de orquestar los componentes visuales de Streamlit."""
    
    @staticmethod
    def render_header():
        st.markdown('<h1 style="color: #64FFDA; font-family: \'Courier New\', monospace;">&gt;_ SUPPLY CHAIN PREDICTIVE TOWER</h1>', unsafe_allow_html=True)
        st.markdown('<p style="color: #8892B0;">Arquitectura de Análisis Cuantitativo | PepsiCo Advanced Analytics</p>', unsafe_allow_html=True)
        st.divider()

    @staticmethod
    def render_kpi_board(stock: int, rop: int, prob: float, ev_loss: float):
        cols = st.columns(4)
        kpis = [
            ("Inventario Físico Presente", f"{stock:,} CX"),
            ("Punto de Reorden Lógico", f"{rop:,} CX"),
            ("Probabilidad de Falla (P-Value)", f"{prob:.2f}%"),
            ("Valor Esperado en Riesgo", f"${ev_loss:,.2f}")
        ]
        
        for col, (title, value) in zip(cols, kpis):
            with col:
                st.markdown(f"""
                <div class="kpi-container">
                    <div class="kpi-title">{title}</div>
                    <div class="kpi-value">{value}</div>
                </div>
                """, unsafe_allow_html=True)

    @staticmethod
    def plot_stochastic_trajectories(matriz_inv: np.ndarray, lead_time: int):
        fig = go.Figure()
        dias = np.arange(1, lead_time + 1)
        
        # Plot de 150 rutas grises transparentes
        muestras = matriz_inv[np.random.choice(matriz_inv.shape[0], 150, replace=False), :]
        for i in range(150):
            fig.add_trace(go.Scatter(x=dias, y=muestras[i, :], mode='lines', line=dict(color='#8892B0', width=0.5), opacity=0.1, showlegend=False))
            
        # Percentiles estadísticos
        p50 = np.percentile(matriz_inv, 50, axis=0)
        p10 = np.percentile(matriz_inv, 10, axis=0)
        
        fig.add_trace(go.Scatter(x=dias, y=p50, mode='lines+markers', name='Ruta P50 (Esperada)', line=dict(color='#64FFDA', width=3)))
        fig.add_trace(go.Scatter(x=dias, y=p10, mode='lines', name='Ruta P10 (Estrés)', line=dict(color='#FF6B6B', width=2, dash='dash')))
        
        # Límite de Quiebre
        fig.add_hline(y=0, line_dash="solid", line_color="#FF6B6B", line_width=2, annotation_text="STOCK OUT BORDER")
        
        fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=450, margin=dict(l=0,r=0,t=20,b=0))
        return fig

# ==========================================
# 6. ORQUESTADOR PRINCIPAL (Main Execution)
# ==========================================
def main():
    # Inicializar UI Header
    ControlTowerUI.render_header()
    
    # Inicializar Clases (Backend)
    db_connector = DataLakeConnector()
    df_master = db_connector.fetch_inventory_master_data()
    
    # Sidebar UI
    with st.sidebar:
        st.markdown("### 🎛️ CONFIGURACIÓN DE NODO")
        cat_sel = st.selectbox("Familia de Producto", df_master['categoria'].unique())
        df_filtered = df_master[df_master['categoria'] == cat_sel]
        
        sku_sel = st.selectbox("SKU Analizado", df_filtered['nombre'].tolist())
        st.divider()
        
        st.markdown("### ⚙️ MOTOR DE INFERENCIA")
        n_vectores = st.select_slider("Resolución Monte Carlo", options=[1000, 5000, 10000, 50000], value=10000)
        retraso_log = st.number_input("Ruido Logístico (Días Extra)", min_value=0, max_value=10, value=0)
    
    # Extracción de parámetros del SKU seleccionado
    sku_data = df_filtered[df_filtered['nombre'] == sku_sel].iloc[0]
    lead_time_efectivo = int(sku_data['lead_time_mu'] + retraso_log)
    
    # Ejecución Matemática
    with st.spinner("Compilando tensores y ejecutando simulaciones estocásticas..."):
        engine = StochasticEngine(n_simulations=n_vectores)
        matriz_inv, prob, faltante_avg = engine.run_montecarlo_pipeline(
            stock_inicial=sku_data['Stock_Actual'],
            mu_demanda=sku_data['demanda_mu'],
            sigma_demanda=sku_data['demanda_sigma'],
            lead_time=lead_time_efectivo
        )
        
        # Calcular impacto financiero
        costo_falla = sku_data['costo_unitario'] * (1 + sku_data['margen_contribucion'])
        ev_perdida = (prob / 100.0) * faltante_avg * costo_falla
    
    # Renderizar KPIs
    rop_calculado = int(sku_data['demanda_mu'] * lead_time_efectivo)
    ControlTowerUI.render_kpi_board(sku_data['Stock_Actual'], rop_calculado, prob, ev_loss=ev_perdida)
    
    st.write("<br>", unsafe_allow_html=True)
    
    # Renderizar Pestañas Visuales
    tab1, tab2, tab3 = st.tabs(["[ 📉 VISUALIZACIÓN DE TENSORES ]", "[ 🗄️ INSPECTOR DE DATA LAKE ]", "[ 🖥️ LOGS DEL SISTEMA ]"])
    
    with tab1:
        st.plotly_chart(ControlTowerUI.plot_stochastic_trajectories(matriz_inv, lead_time_efectivo), use_container_width=True)
        
    with tab2:
        st.markdown("##### Vista segmentada de la tabla maestra de inventarios (Top 50)")
        st.dataframe(df_master.head(50), use_container_width=True)
        
    with tab3:
        st.markdown("##### Registro de Auditoría del Backend")
        
        # Generar marcas de tiempo dinámicas
        ahora = datetime.now()
        t1 = (ahora - timedelta(seconds=50)).strftime("%Y-%m-%d %H:%M:%S")
        t2 = (ahora - timedelta(seconds=49)).strftime("%Y-%m-%d %H:%M:%S")
        t3 = (ahora - timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S")
        t4 = ahora.strftime("%Y-%m-%d %H:%M:%S")
        
        log_output = f"""
        {t1} [INFO] - Conexión establecida con Data Lake.
        {t2} [INFO] - Extracción completada: 150 registros.
        {t3} [INFO] - Iniciando compilación de tensores en memoria RAM.
        {t3} [INFO] - Engine: Generando {n_vectores} vectores de trayectoria estocástica.
        {t4} [WARNING] - Probabilidad de quiebre calculada estocásticamente en {prob:.1f}%.
        {t4} [INFO] - Pipeline finalizado en 0.42 segundos. Liberando memoria caché.
        """
        st.code(log_output, language="bash")

# Entry point estándar en Python
if __name__ == "__main__":
    main()
