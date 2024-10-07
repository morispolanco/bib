import streamlit as st
import requests
import logging

# Configurar el nivel de logging
logging.basicConfig(level=logging.DEBUG)

# Configuración de la página
st.set_page_config(
    page_title="📚 Generador de Bibliografía en APA",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Generador de Bibliografía en Formato APA")
st.write("Introduce un tema o problema y genera una lista de fuentes relevantes en formato APA.")

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
    except requests.exceptions.RequestException as e:
        st.error(f"Error al acceder a la API de Together: {e}")
        logging.error(f"Error al acceder a la API de Together: {e}")
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
    except requests.exceptions.RequestException as e:
        st.error(f"Error al acceder a la API de Serper: {e}")
        logging.error(f"Error al acceder a la API de Serper: {e}")
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
            # Obtener autores
            autores = item.get("author", [])
            autores_formateados = []
            for autor in autores:
                nombre = autor.get("given", "")
                apellido = autor.get("family", "")
                if nombre and apellido:
                    autores_formateados.append(f"{apellido}, {nombre[0]}.")
                elif apellido:
                    autores_formateados.append(f"{apellido}.")
            autores_str = ", ".join(autores_formateados)
            if len(autores_formateados) > 1:
                autores_str = autores_str.replace(", " , ", ", len(autores_formateados)-1)

            # Año de publicación
            año = item.get("published-print", {}).get("date-parts", [[]])[0]
            if not año:
                año = item.get("published-online", {}).get("date-parts", [[]])[0]
            año = año[0] if año else "s.f."

            # Título
            titulo = item.get("title", ["Sin título"])[0]

            # Fuente (Revista o editorial)
            fuente = item.get("container-title", [""])[0]

            # DOI o URL
            doi = item.get("DOI", "")
            url_item = item.get("URL", doi if doi else "#")

            # Formato APA
            referencia = f"{autores_str} ({año}). {titulo}. {fuente}. {url_item}"
            fuentes.append(referencia)
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

    # Combinar todas las fuentes
    fuentes = fuentes_together + fuentes_serper + fuentes_crossref

    # Dado que las fuentes de CrossRef ya están formateadas en APA, necesitamos manejar las de Together y Serper
    # Suponiendo que estas APIs devuelven datos estructurados similares a CrossRef, se puede formatear también
    # Aquí omitiremos la formateación específica de estas APIs y solo usaremos CrossRef para APA
    # Para una implementación completa, deberías formatear las fuentes de Together y Serper en APA similar a CrossRef

    # Filtrar solo las referencias de CrossRef (asumiendo que las de CrossRef son strings en APA)
    referencias_apa = [fuente for fuente in fuentes_crossref if isinstance(fuente, str)]

    # Limitar a 50 fuentes
    bibliografia = referencias_apa[:50]

    return bibliografia

if st.button("Generar Bibliografía"):
    if tema.strip() == "":
        st.error("Por favor, introduce un tema o problema válido.")
    else:
        with st.spinner("Generando bibliografía..."):
            bibliografia = generar_bibliografia(tema)
        
        if bibliografia:
            st.success(f"Se encontraron {len(bibliografia)} fuentes en formato APA:")
            for idx, referencia in enumerate(bibliografia, 1):
                st.markdown(f"{idx}. {referencia}")
        else:
            st.warning("No se encontraron fuentes para el tema proporcionado.")
