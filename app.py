import streamlit as st
from traducciones import diccionario

# --- SELECTOR DE IDIOMA EN LA BARRA LATERAL ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'ES' # Idioma por defecto

with st.sidebar:
    idioma_elegido = st.selectbox(
        "Language / 語言 / Idioma",
        options=["Español", "繁體中文", "English"],
        index=0
    )
    
    # Mapeo de la selección al código del diccionario
    mapping = {"Español": "ES", "繁體中文": "ZH", "English": "EN"}
    st.session_state.lang = mapping[idioma_elegido]

# --- USO DE LAS TRADUCCIONES EN LA UI ---
lang_code = st.session_state.lang
texts = diccionario[lang_code]

st.title(texts["titulo"])
st.write(texts["bienvenida"])

# Ejemplo en el área de chat
categoria = st.selectbox(texts["preguntas_frecuentes"], ["", "Análisis 1", "Análisis 2"])
pregunta_libre = st.chat_input(texts["consulta_libre"])
