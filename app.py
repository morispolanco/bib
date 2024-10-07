import streamlit as st
import requests
import json
import logging

# Configurar el nivel de logging
logging.basicConfig(level=logging.DEBUG)

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
    url = "https://api.together.com/v1/bibliography/search"  # Reemplaza con la URL real de Together
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    params = {
        "query": tema,
        "num": num_fuentes
    }
    logging.debug(f"Together API URL: {url}")
    logging.debug(f"Together API Params: {params}")
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred en Together API: {http_err}")
        logging.error(f"HTTP error occurred en Together API: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        st.error(f"Error de conexión en Together API: {conn_err}")
        logging.error(f"Error de conexión en Together API: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        st.error(f"Timeout en Together API: {timeout_err}")
        logging.error(f"Timeout en Together API: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"Error inesperado en Together API: {req_err}")
        logging.error(f"Error inesperado en Together API: {req_err}")
    return []

def obtener_fuentes_serper(tema, api_key, num_fuentes=25):
    url = "https://api.serper.com/v1/search"  # Reemplaza con la URL real de Serper
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "q": tema,
        "num": num_fuentes
    }
    logging.debug(f"Serper API URL: {url}")
    logging.debug(f"Serper API Data: {data}")
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred en Serper API: {http_err}")
        logging.error(f"HTTP error occurred en Serper API: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        st.error(f"Error de conexión en Serper API: {conn_err}")
        logging.error(f"Error de conexión en Serper API: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        st.error(f"Timeout en Serper API: {timeout_err}")
        logging.error(f"Timeout en Serper API: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"Error inesperado en Serper API: {req_err}")
        logging.error(f"Error inesperado en Serper API: {req_err}")
    return []

def obtener_fuentes_crossref(tema, num_fuentes=25):
    url = "https://api.crossref.org/works"
    params = {
        "query": tema,
        "rows": num_fuentes
    }
    logging.debug(f"CrossRef API URL: {url}")
    logging.debug(f"CrossRef API Params: {params}")
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get("message", {}).get("items", [])
        fuentes = []
        for item in results:
            titulo = item.get("title", ["Sin título"])[0]
            enlace = item.get("URL", "#")
            descripcion = item.get("abstract", "No hay descripción disponible.")
            fuentes.append({
                "title": titulo,
                "link": enlace,
                "description": descripcion
            })
        return fuentes
    except requests.exceptions.RequestException as e:
        st.error(f"Error al acceder a la API de CrossRef: {e}")
        logging.error(f"Error al acceder a la API de CrossRef: {e}")
    return []

def generar_bibliografia(tema):
    together_api_key = st.secrets["TOGETHER_API_KEY"]
    serper_api_key = st.secrets["SERPER_API_KEY"]

    st.info("Buscando fuentes con Together API...")
    fuentes_together = obtener_fuentes_together(tema, together_api_key, num_fuentes=25)

    st.info("Buscando fuentes con Serper API...")
    fuentes_serper = obtener_fuentes_serper(tema, serper_api_key, num_fuentes=25)

    st.info("Buscando fuentes con CrossRef API...")
    fuentes_crossref = obtener_fuentes_crossref(tema, num_fuentes=25)

    # Combinar y eliminar duplicados
    fuentes = fuentes_together + fuentes_serper + fuentes_crossref
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
