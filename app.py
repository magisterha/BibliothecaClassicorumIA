import streamlit as st
import streamlit_authenticator as stauth
import yaml
import copy  # <--- CRÍTICO: Necesario para copiar los secretos
from yaml.loader import SafeLoader
from traducciones import diccionario

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Bibliotheca Classicarum IA",
    page_icon="🏛️",
    layout="wide"
)

# 2. SISTEMA DE LOGIN / AUTENTICACIÓN
try:
    # --- CORRECCIÓN DE SEGURIDAD ---
    # Usamos copy.deepcopy() para crear una copia editable y evitar el error
    # "Secrets does not support item assignment".
    credentials = copy.deepcopy(dict(st.secrets['credentials']))
    cookie = copy.deepcopy(dict(st.secrets['cookie']))
except FileNotFoundError:
    st.error("Error crítico: No se han configurado los Secrets de credenciales.")
    st.stop()
except KeyError as e:
    st.error(f"Error en la estructura de Secrets: Falta la clave {e}")
    st.stop()

# Crear el objeto autenticador con los datos copiados
authenticator = stauth.Authenticate(
    credentials,
    cookie['name'],
    cookie['key'],
    cookie['expiry_days']
)

# Renderizamos widget de Login
authenticator.login()

# Verificar estado de autenticación
if st.session_state["authentication_status"] is False:
    st.error('Usuario o contraseña incorrectos')
    st.stop()
elif st.session_state["authentication_status"] is None:
    st.warning('Por favor, inicie sesión para acceder a la Bibliotheca.')
    st.stop()

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

st.info("Sistema conectado a Google Sheets y Gemini 2.0 Flash Lite.")
