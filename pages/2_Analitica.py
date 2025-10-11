import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("📊 Analítica de Datos del Aeropuerto")

st.write("Sube un archivo CSV del aeropuerto (vuelos, pasajeros, aviones, etc.) para analizarlo.")

uploaded_file = st.file_uploader("Selecciona tu archivo CSV", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        st.success("✅ Archivo cargado correctamente")

        st.write("### 🧾 Información general")
        st.write(f"**Columnas:** {list(df.columns)}")
        st.write(f"**Número de filas:** {len(df)}")

        st.write("### 🗂️ Vista previa de los datos")
        st.dataframe(df.head())

        st.write("### 📈 Estadísticas descriptivas")
        st.dataframe(df.describe(include='all'))

        columnas = [col.lower() for col in df.columns]
        tipo = "Desconocido"

        if "vuelo" in columnas or "origen" in columnas or "destino" in columnas:
            tipo = "Vuelos"
        elif "pasajero" in columnas or "edad" in columnas:
            tipo = "Pasajeros"
        elif "avion" in columnas or "modelo" in columnas:
            tipo = "Aviones"

        st.info(f"📂 Tipo de archivo detectado: **{tipo}**")

        st.write("### ✈️ Visualización rápida")
        col_numericas = df.select_dtypes(include=['int64', 'float64']).columns

        if len(col_numericas) > 0:
            col_x = st.selectbox("Selecciona una columna numérica para graficar:", col_numericas)
            fig, ax = plt.subplots()
            ax.hist(df[col_x], bins=10)
            st.pyplot(fig)
        else:
            st.warning("No se encontraron columnas numéricas para graficar.")

    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {e}")
