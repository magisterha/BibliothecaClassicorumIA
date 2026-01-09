import streamlit as st
import json
import os
import google.generativeai as genai
import sys

# Truco para importar módulos de la carpeta superior (padre)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import guardar_interaccion
from traducciones import diccionario

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Xunzi - Zhengming", page_icon="📜", layout="wide")

# Gestión de Idioma (Sincronizado con app.py mediante session_state)
if 'lang' not in st.session_state:
    st.session_state.lang = 'ES'
    
lang_code = st.session_state.lang
texts = diccionario[lang_code]

# --- 2. CONEXIÓN SEGURA A GEMINI (Secrets) ---
try:
    # Intenta obtener la clave de los Secrets de Streamlit (Nube)
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    # Fallback para local si usas .env (opcional)
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
    except:
        api_key = None

if not api_key:
    st.error("⚠️ API Key no encontrada. Configura 'GOOGLE_API_KEY' en Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# --- 3. CARGA DE DATOS (El JSON de Xunzi) ---
# Ajusta 'chinese' si tu carpeta dentro de data se llama diferente
ruta_actual = os.path.dirname(__file__)
ruta_json = os.path.join(ruta_actual, '..', 'data', 'chinese', 'xunzi_zhengming.json')

try:
    with open(ruta_json, 'r', encoding='utf-8') as f:
        data_xunzi = json.load(f)
except FileNotFoundError:
    st.error(f"Error crítico: No se encuentra el archivo en {ruta_json}")
    st.stop()

# --- 4. INTERFAZ DE USUARIO ---
st.title(texts["xunzi_titulo"])

# Visualizador del Texto Original (Colapsable)
with st.expander(texts["expander_texto"]):
    for segmento in data_xunzi['corpus']:
        st.markdown(f"**[{segmento['id']}]** {segmento['texto_original']}")

# Área de Chat
st.divider()
query = st.chat_input(texts["chat_placeholder"])

if query:
    # Mostrar mensaje usuario
    with st.chat_message("user"):
        st.write(query)

    # --- 5. LÓGICA RAG (Retrieval Augmented Generation) ---
    # Convertimos el JSON a texto para dárselo a Gemini
    contexto_str = json.dumps(data_xunzi, ensure_ascii=False)
    
    prompt = f"""
    {texts['prompt_sistema']}
    
    CONTEXTO (FUENTE DE VERDAD):
    El siguiente JSON contiene el texto completo de 'Zhengming' (正名):
    '''
    {contexto_str}
    '''
    
    INSTRUCCIONES:
    1. Responde a la pregunta basándote PRINCIPALMENTE en el contexto provisto.
    2. Si citas el texto, indica el ID del párrafo.
    3. Si la pregunta es sobre traducción, analiza filológicamente los términos clave.
    
    PREGUNTA DEL USUARIO:
    {query}
    """
    
    with st.spinner(texts["analizando"]):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            respuesta_texto = response.text
            
            with st.chat_message("assistant"):
                st.markdown(respuesta_texto)
                
            # Guardar log
            guardar_interaccion(query, respuesta_texto, "Xunzi", lang_code, "Chat Libre")
            st.toast(texts["log_guardado"])
            
        except Exception as e:
            st.error(f"{texts['error_api']}: {e}")
