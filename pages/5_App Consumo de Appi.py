import streamlit as st
import requests

# URL base de tu MockAPI
API_URL = "https://68dc955d7cd1948060aaba15.mockapi.io/Usuarios"

st.title("👥 Lista de Usuarios (MockAPI)")


def obtener_usuarios():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al conectar con la API: {e}")
        return []

usuarios = obtener_usuarios()

if usuarios:
    st.success("Datos cargados correctamente ✅")
    for usuario in usuarios:
        st.write(f"🧑 **{usuario['nombre']}** — Edad: {usuario['edad']}")
else:
    st.warning("No hay usuarios disponibles.")
