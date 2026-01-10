import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from traducciones import diccionario

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser la primera línea ejecutable de Streamlit)
st.set_page_config(
    page_title="Bibliotheca Classicarum IA",
    page_icon="🏛️",
    layout="wide"
)

# 2. SISTEMA DE LOGIN / AUTENTICACIÓN
# Intentamos cargar credenciales de los Secrets
try:
    credentials = dict(st.secrets['credentials'])
    cookie = dict(st.secrets['cookie'])
except FileNotFoundError:
    st.error("Error crítico: No se han configurado los Secrets de credenciales.")
    st.stop()

authenticator = stauth.Authenticate(
    credentials,
    cookie['name'],
    cookie['key'],
    cookie['expiry_days']
)

# Renderizamos widget de Login
# El parámetro 'main' lo pone en el centro, 'sidebar' en la barra lateral
authenticator.login()

if st.session_state["authentication_status"] is False:
    st.error('Usuario o contraseña incorrectos')
    st.stop() # DETIENE LA EJECUCIÓN AQUÍ
elif st.session_state["authentication_status"] is None:
    st.warning('Por favor, inicie sesión para acceder a la Bibliotheca.')
    st.stop() # DETIENE LA EJECUCIÓN AQUÍ

# ==============================================================================
#  ZONA SEGURA: EL CÓDIGO DE ABAJO SOLO SE EJECUTA SI ESTÁS LOGUEADO
# ==============================================================================

# Barra lateral con información de usuario y Logout
with st.sidebar:
    st.write(f"Investigador: **{st.session_state['name']}**")
    authenticator.logout('Cerrar Sesión', 'sidebar')
    st.divider()
    
    # Selector de Idioma Global
    if 'lang' not in st.session_state:
        st.session_state.lang = 'ES'
    
    idioma_elegido = st.selectbox(
        diccionario[st.session_state.lang]["sidebar_lang"],
        options=["Español", "繁體中文", "English"],
        index=0
    )
    mapping = {"Español": "ES", "繁體中文": "ZH", "English": "EN"}
    st.session_state.lang = mapping[idioma_elegido]

# Cargar textos según idioma seleccionado
lang_code = st.session_state.lang
texts = diccionario[lang_code]

# Interfaz Principal
st.title(texts["titulo_app"])
st.markdown(f"""
### {texts['bienvenida']}

Selecciona un módulo en la barra lateral (izquierda) para comenzar:
* **Módulos de Texto:** Análisis de obras clásicas.
* **Zona de Usuario:** Para guardar tus notas y ver tu historial.
""")

st.info("Sistema conectado a Google Sheets y Gemini 1.5 Flash.")
