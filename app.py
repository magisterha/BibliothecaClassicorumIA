import streamlit as st
import streamlit_authenticator as stauth
from traducciones import diccionario

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Bibliotheca Classicarum IA",
    page_icon="🏛️",
    layout="wide"
)

# --- FUNCIÓN DE LIMPIEZA DE SECRETOS ---
def parse_secrets(obj):
    """Convierte st.secrets en un diccionario estándar para evitar errores de solo lectura."""
    if hasattr(obj, 'items'):
        return {k: parse_secrets(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [parse_secrets(i) for i in obj]
    else:
        return obj

# 2. CARGA DE SECRETOS Y LOGIN
try:
    secrets_dict = parse_secrets(st.secrets)
    credentials = secrets_dict['credentials']
    cookie = secrets_dict['cookie']
except Exception as e:
    st.error(f"Error cargando configuración de seguridad: {e}")
    st.stop()

authenticator = stauth.Authenticate(
    credentials,
    cookie['name'],
    cookie['key'],
    cookie['expiry_days']
)

authenticator.login()

# 3. LÓGICA DE ACCESO
if st.session_state["authentication_status"] is False:
    st.error('Usuario o contraseña incorrectos / Username or password incorrect')
    
elif st.session_state["authentication_status"] is None:
    # MODO INVITADO
    if 'guest_credits' not in st.session_state:
        st.session_state.guest_credits = 20
        
    if st.session_state.guest_credits > 0:
        with st.sidebar:
            st.info(f"👤 Modo Invitado: {st.session_state.guest_credits} consultas disponibles")
            st.warning("Inicia sesión para acceso ilimitado.")
    else:
        st.error("⛔ Se han agotado las consultas gratuitas.")
        st.stop()
            
elif st.session_state["authentication_status"] is True:
    # USUARIO REGISTRADO
    usuario = st.session_state['name']
    st.session_state['es_premium'] = True
    
    with st.sidebar:
        st.success(f"Investigador: **{usuario}**")
        authenticator.logout('Cerrar Sesión', 'sidebar')

# ==============================================================================
#  INTERFAZ PRINCIPAL
# ==============================================================================

# Guardamos el estado del usuario para las otras páginas
if st.session_state.get("authentication_status"):
    st.session_state['usuario_activo'] = st.session_state['name']
else:
    st.session_state['usuario_activo'] = "Invitado"

# Selector de Idioma Global
if 'lang' not in st.session_state:
    st.session_state.lang = 'ES'

with st.sidebar:
    st.divider()
    idioma_elegido = st.selectbox(
        "Idioma / Language",
        options=["Español", "繁體中文", "English"],
        index=0
    )
    mapping = {"Español": "ES", "繁體中文": "ZH", "English": "EN"}
    st.session_state.lang = mapping[idioma_elegido]

# Cargar textos
lang_code = st.session_state.lang
texts = diccionario[lang_code]

# Contenido Principal
st.title(texts["titulo_app"])
st.markdown(f"""
### {texts['bienvenida']}

Bienvenido a la **Bibliotheca Classicarum IA**.

Esta plataforma utiliza modelos de lenguaje de última generación (**Gemini 2.0**) conectados a bases de datos filológicas para asistir en la investigación de textos clásicos chinos y latinos.

Selecciona un módulo en la barra lateral para comenzar.
""")

st.info("Estado del Sistema: ✅ Online | Modelo: Gemini 2.0 Flash Lite")
