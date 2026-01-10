import streamlit as st
import json
import os
import google.generativeai as genai
import sys

# --- 1. IMPORTACIÓN DE MÓDULOS DE LA RAÍZ ---
# Truco para importar módulos de la carpeta superior (padre)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import guardar_interaccion
from traducciones import diccionario

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Xunzi - Zhengming", page_icon="📜", layout="wide")

# --- 3. CONTROL DE ACCESO (HÍBRIDO: PREMIUM vs INVITADO) ---
# Recuperamos variables de estado (definidas en app.py)
es_premium = st.session_state.get('es_premium', False)
guest_credits = st.session_state.get('guest_credits', 0)

# Lógica de bloqueo
if not es_premium:
    # Si es invitado, verificamos si le quedan créditos
    if guest_credits <= 0:
        st.error("⛔ Has agotado tus 20 consultas gratuitas.")
        st.info("Por favor, regresa a la página principal e inicia sesión con credenciales de investigador.")
        st.stop() # DETIENE LA EJECUCIÓN AQUÍ
    else:
        # Mostramos aviso de créditos restantes
        st.sidebar.warning(f"Modo Invitado: {guest_credits} consultas restantes.")

# --- 4. GESTIÓN DE IDIOMA ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'ES'

lang_code = st.session_state.lang
texts = diccionario[lang_code]

# --- 5. CONEXIÓN SEGURA A GEMINI ---
try:
    # Intentamos obtener la clave de los Secrets
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("⚠️ Error Crítico: API Key no encontrada en Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# --- 6. CARGA DE DATOS (El JSON de Xunzi) ---
ruta_actual = os.path.dirname(__file__)
# Ruta relativa hacia la carpeta data en la raíz
ruta_json = os.path.join(ruta_actual, '..', 'data', 'chinese', 'xunzi_zhengming.json')

try:
    with open(ruta_json, 'r', encoding='utf-8') as f:
        data_xunzi = json.load(f)
except FileNotFoundError:
    st.error(f"Error: No se encuentra el archivo de datos en {ruta_json}")
    st.stop()

# --- 7. INTERFAZ DE USUARIO ---
st.title(texts["xunzi_titulo"])

# Visualizador del Texto Original (Colapsable)
with st.expander(texts["expander_texto"]):
    for segmento in data_xunzi['corpus']:
        # Usamos .get() para evitar errores si falta algún campo
        id_seg = segmento.get('id', '?')
        texto = segmento.get('texto_original', '')
        st.markdown(f"**[{id_seg}]** {texto}")

# Área de Chat
st.divider()
query = st.chat_input(texts["chat_placeholder"])

if query:
    # A. Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.write(query)

    # B. Preparar el Prompt (Ingeniería de RAG)
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
    2. Si citas el texto, indica el ID del párrafo (ej: [3]).
    3. Si la pregunta es sobre traducción, analiza filológicamente los términos clave (Ming vs Shi).
    
    PREGUNTA DEL USUARIO:
    {query}
    """
    
    # C. Llamada a la IA
    with st.spinner(texts["analizando"]):
        try:
            # --- MODELO ACTUALIZADO (2026) ---
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            
            response = model.generate_content(prompt)
            respuesta_texto = response.text
            
            with st.chat_message("assistant"):
                st.markdown(respuesta_texto)
            
            # --- D. CONSUMO DE CRÉDITOS ---
            if not es_premium:
                st.session_state.guest_credits -= 1
                st.caption(f"📉 Crédito consumido. Te quedan: {st.session_state.guest_credits}")
                
                # Aviso visual si se queda a cero justo ahora
                if st.session_state.guest_credits == 0:
                    st.warning("⚠️ ¡Esta ha sido tu última consulta gratuita!")

            # --- E. GUARDADO DE LOGS (GOOGLE SHEETS) ---
            # Guardamos la interacción para mejora continua
            guardar_interaccion(query, respuesta_texto, "Xunzi", lang_code, "Chat RAG")
            st.toast(texts["log_guardado"])
            
        except Exception as e:
            st.error(f"{texts['error_api']}: {e}")
