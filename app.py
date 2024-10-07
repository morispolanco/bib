import streamlit as st
import requests
import json

# Configuración de la página
st.set_page_config(
    page_title="Generador de Bibliografía",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Generador de Bibliografía Automático")
st.write("Introduce un tema o problema y genera una lista de fuentes relevantes.")

# Input del usuario
tema = st.text_input("Introduce el tema o problema:", "")

def obtener_fuentes_together(tema, api_key, num_fuentes=25):
    url = "https://api.together.com/v1/search"  # Reemplaza con la URL real de la API de Together
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    params = {
        "query": tema,
        "num": num_fuentes
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        st.error(f"Error al acceder a la API de Together: {response.status_code}")
        return []

def obtener_fuentes_serper(tema, api_key, num_fuentes=25):
    url = "https://serper-api.com/search"  # Reemplaza con la URL real de la API de Serper
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "q": tema,
        "num": num_fuentes
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        st.error(f"Error al acceder a la API de Serper: {response.status_code}")
        return []

def generar_bibliografia(tema):
    together_api_key = st.secrets["TOGETHER_API_KEY"]
    serper_api_key = st.secrets["SERPER_API_KEY"]

    st.info("Buscando fuentes con Together API...")
    fuentes_together = obtener_fuentes_together(tema, together_api_key, num_fuentes=25)

    st.info("Buscando fuentes con Serper API...")
    fuentes_serper = obtener_fuentes_serper(tema, serper_api_key, num_fuentes=25)

    # Combinar y eliminar duplicados
    fuentes = fuentes_together + fuentes_serper
    fuentes_unicas = {fuente['title']: fuente for fuente in fuentes if 'title' in fuente}.values()

    # Limitar a 50 fuentes
    bibliografia = list(fuentes_unicas)[:50]

    return bibliografia

if st.button("Generar Bibliografía"):
    if tema.strip() == "":
        st.error("Por favor, introduce un tema o problema válido.")
    else:
        with st.spinner("Generando bibliografía..."):
            bibliografia = generar_bibliografia(tema)
        
        if bibliografia:
            st.success(f"Se encontraron {len(bibliografia)} fuentes:")
            for idx, fuente in enumerate(bibliografia, 1):
                titulo = fuente.get('title', 'Sin título')
                enlace = fuente.get('link', '#')
                descripcion = fuente.get('description', '')
                st.markdown(f"**{idx}. [{titulo}]({enlace})**\n> {descripcion}")
        else:
            st.warning("No se encontraron fuentes para el tema proporcionado.")

