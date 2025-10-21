import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime


API_BASE_URL = "http://localhost:8080/api/v1/products" 

st.set_page_config(
    page_title="Dashboard de Análisis de Productos (Pandas/Streamlit)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. FUNCIÓN DE CONEXIÓN A LA API Y CACHÉ ---

# st.cache_data almacena el resultado de la función. Si los argumentos no cambian,
# no vuelve a llamar a la API.
@st.cache_data(ttl=600) # ttl=600 significa que refrescará los datos cada 10 minutos
def fetch_data_from_api(endpoint):
    """Obtiene datos de la API de Spring Boot y los convierte a un DataFrame de Pandas."""
    try:
        # Petición GET a un endpoint específico
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        response.raise_for_status()
        data = response.json()
        
        # Convertir la lista de objetos JSON a DataFrame de Pandas
        df = pd.DataFrame(data)
        
        # Procesamiento de datos: Asegurar que 'ingresos' es numérico y 'fecha' es datetime
        if 'ingresos' in df.columns:
            df['ingresos'] = pd.to_numeric(df['ingresos'], errors='coerce')
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce') 
            df['mes_nombre'] = df['fecha'].dt.strftime('%B') # Nombre del mes
            df['año'] = df['fecha'].dt.year

        return df
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error al conectar con la API ({API_BASE_URL}/{endpoint}): {e}")
        return pd.DataFrame() # Retorna un DataFrame vacío en caso de error

# --- 3. SIMULACIÓN DE DATOS  ---
# Esta función es para que puedas ejecutar la app si la API no está lista
def get_simulated_data():
    data = {
        'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'producto': ['Leche Entera', 'Queso Fresco', 'Avena', 'Arroz', 'Yogur', 
                     'Mantequilla', 'Lentejas', 'Frijoles', 'Crema', 'Cebada'],
        'categoria': ['Lácteos', 'Lácteos', 'Granos', 'Granos', 'Lácteos', 
                      'Lácteos', 'Granos', 'Granos', 'Lácteos', 'Granos'],
        'ingresos': [1200, 850, 400, 300, 750, 500, 250, 150, 600, 100],
        # Fechas simuladas para análisis mensual
        'fecha': [
            datetime(2025, 9, 15), datetime(2025, 10, 5), datetime(2025, 10, 10), 
            datetime(2025, 9, 20), datetime(2025, 10, 1), datetime(2025, 9, 25), 
            datetime(2025, 10, 12), datetime(2025, 9, 28), datetime(2025, 10, 3), 
            datetime(2025, 10, 11)
        ]
    }
    df = pd.DataFrame(data)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['mes_nombre'] = df['fecha'].dt.strftime('%B')
    df['año'] = df['fecha'].dt.year
    return df
# --- FIN DE LA SIMULACIÓN ---


# --- CÓDIGO PRINCIPAL DE LA APLICACIÓN ---

# 1. Carga de datos (Usa la API o la simulación si la API falla)
df_ventas = fetch_data_from_api(API_BASE_URL) 

if df_ventas.empty:
    st.warning(" Usando datos simulados: Fallo al conectar con la API de Spring Boot.")
    df_ventas = get_simulated_data()
    # Si la data simulada también es vacía, no se puede continuar
    if df_ventas.empty:
        st.error("No se pudo cargar la información. Revisa la API o la simulación.")
        st.stop()


# 2. Sidebar con el Acordeón (st.expander) y Filtros
st.sidebar.title(" Filtros de Análisis")

with st.sidebar.expander("Filtros de Datos (Acordeón)", expanded=True):
    # Filtro 1: Mes
    meses_disponibles = sorted(df_ventas['mes_nombre'].unique(), key=lambda m: datetime.strptime(m, '%B'))
    selected_mes = st.selectbox(
        "Seleccionar Mes", 
        options=meses_disponibles, 
        index=len(meses_disponibles) - 1 
    )

    # Filtro 2: Categoría de Productos
    categorias_disponibles = sorted(df_ventas['categoria'].unique())
    selected_categories = st.multiselect(
        "Selecciona Categorías",
        options=categorias_disponibles,
        default=categorias_disponibles 
    )

# 3. Aplicar Filtros
df_filtrado = df_ventas[
    (df_ventas['mes_nombre'] == selected_mes) & 
    (df_ventas['categoria'].isin(selected_categories))
].copy() 


# 4. HOME PAGE LAYOUT
st.title(" Dashboard de Ingresos de Productos")
st.markdown(f"**Datos basados en la conexión con Spring Boot API** | Mes de análisis: **{selected_mes}**")

st.divider() # Línea divisoria


# --- 5. VISUALIZACIONES DINÁMICAS Y KPIs ---

if df_filtrado.empty:
    st.warning("No hay datos para mostrar con los filtros aplicados. Ajusta tus selecciones.")
else:
    # KPI 1: Ingresos Totales
    total_ingresos = df_filtrado['ingresos'].sum()
    st.metric(
        label="Ingresos Totales del Mes", 
        value=f"${total_ingresos:,.2f}",
        delta="Datos Reales de la API"
    )

    # Contenedor para los Gráficos de Análisis (uso de st.columns)
    col1, col2 = st.columns(2)

    # GRÁFICO 1: Ingresos por Categoría (para la comparativa Lácteos vs Granos)
    with col1:
        st.subheader("Ingresos Totales por Categoría")
        
        # Agrupar y preparar datos para el gráfico
        df_comparativa = df_filtrado.groupby('categoria')['ingresos'].sum().reset_index()
        
        # Creación del Gráfico de Barras con Plotly
        fig_bar = px.bar(
            df_comparativa,
            x='categoria',
            y='ingresos',
            color='categoria', # Colorear por categoría para distinguirlas
            title='Comparativa de Ingresos',
            labels={'ingresos': 'Ingresos ($)', 'categoria': 'Categoría'},
            template='streamlit'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # GRÁFICO 2: Tendencia de Ingresos Diarios
    with col2:
        st.subheader("Tendencia de Ingresos Diarios")
        
        df_tendencia = df_filtrado.groupby('fecha')['ingresos'].sum().reset_index()
        
        fig_line = px.line(
            df_tendencia,
            x='fecha',
            y='ingresos',
            title='Ingresos Acumulados Diarios',
            labels={'ingresos': 'Ingresos ($)', 'fecha': 'Fecha'},
            template='streamlit'
        )
        st.plotly_chart(fig_line, use_container_width=True)


    st.divider()

    # --- 6. REPORTE DE TEXTO DINÁMICO (Análisis de Mayor Ingreso) ---
    st.subheader("🔎 Conclusión del Análisis Mensual")

    # Lógica para determinar el mayor ingreso 
    if not df_comparativa.empty:
        max_ingreso = df_comparativa['ingresos'].max()
        categoria_max = df_comparativa[df_comparativa['ingresos'] == max_ingreso]['categoria'].iloc[0]
        
        st.success(
            f"**¡Análisis Clave!** En **{selected_mes}**, la categoría con mayor reporte de ingresos fue **{categoria_max}** "
            f"con un total de **${max_ingreso:,.2f}**. "
            "Esto indica un foco importante de negocio en esta área."
        )

        # Opcional: Mostrar la tabla completa
        with st.expander("Ver Datos Crudos Filtrados"):
            st.dataframe(df_filtrado, use_container_width=True)