import streamlit as st
import requests

API_URL = "https://68dc955d7cd1948060aaba15.mockapi.io/Usuarios"

st.set_page_config(page_title="Usuarios MockAPI", page_icon="👥", layout="wide")

st.markdown("""
    <style>
        body {
            background-color: #0e1117;
        }
        .user-card {
            background-color: #1e1e1e;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            color: white;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.3);
            transition: transform 0.2s;
        }
        .user-card:hover {
            transform: scale(1.02);
        }
        .user-name {
            font-size: 1.2rem;
            font-weight: 600;
            color: #00b4d8;
        }
        .user-age {
            font-size: 1rem;
            color: #adb5bd;
        }
        .title {
            color: #f8f9fa;
            font-weight: 700;
        }
    </style>
""", unsafe_allow_html=True)

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
