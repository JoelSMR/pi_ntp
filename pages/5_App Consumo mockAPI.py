import streamlit as st
import requests

API_URL = "https://68dc955d7cd1948060aaba15.mockapi.io/Usuarios"

st.set_page_config(page_title="App Consumo mockAPI", layout="wide")

def obtener_usuarios():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error al conectar con la API: {e}")
        return []

st.markdown("<h1 class='title'>👥 Lista de Usuarios (MockAPI)</h1>", unsafe_allow_html=True)

usuarios = obtener_usuarios()

if usuarios:
    st.success("✅ Datos cargados correctamente")

    cols = st.columns(3)
    for i, usuario in enumerate(usuarios):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="user-card">
                    <p class="user-name">🧑 {usuario['nombre']}</p>
                    <p class="user-age">Edad: <b>{usuario['edad']}</b></p>
                    <p>ID: {usuario['id']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
else:
    st.warning("⚠️ No hay usuarios disponibles.")
