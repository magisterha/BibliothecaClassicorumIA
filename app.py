import streamlit as st
import streamlit_authenticator as stauth
from traducciones import diccionario

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Bibliotheca Classicarum IA",
    page_icon="🏛️",
    layout="wide"
)

# --- FUNCIÓN PARA CORREGIR EL RECURSION ERROR ---
def convert_secrets_to_dict(secrets_section):
    """
    Convierte el objeto 'Secrets' de Streamlit en un diccionario puro de Python.
    Esto evita el RecursionError al intentar modificar credenciales.
    """
    try:
        # Convertimos recursivamente a diccionario estándar
        return {k: v for k, v in secrets_section.items()}
    except Exception:
        return {}

# 2. INICIALIZACIÓN DEL MODO INVITADO
if 'guest_credits' not in st.session_state:
    st.session_state.guest_credits = 20  # Damos 20 interacciones gratis

# 3. SISTEMA DE LOGIN / AUTENTICACIÓN
try:
    # USAMOS LA FUNCIÓN SEGURA EN LUGAR DE DEEPCOPY
    credentials = convert_secrets_to_dict(st.secrets['credentials'])
    cookie = convert_secrets_to_dict(st.secrets['cookie'])
except Exception as e:
    st.error(f"Error cargando secretos: {e}")
    st.stop()

# Crear el objeto autenticador
authenticator = stauth.Authenticate(
    credentials,
    cookie['name'],
    cookie['key'],
    cookie['expiry_days']
)

# Renderizamos widget de Login
authenticator.login()

# --- LÓGICA HÍBRIDA (LOGIN vs INVITADO) ---

# Definimos variables de estado para el resto de la app
usuario_activo = "Invitado"
es_premium = False

# CASO 1: USUARIO REGISTRADO
if st.session_state["authentication_status"] is True:
    usuario_activo = st.session_state['name']
    es_premium = True
    
    # Barra lateral para usuarios registrados
    with st.sidebar:
        st.success(f"Sesión iniciada: **{usuario_activo}**")
        authenticator.logout('Cerrar Sesión', 'sidebar')

# CASO 2: CONTRASEÑA INCORRECTA
elif st.session_state["authentication_status"] is False:
    st.error('Usuario o contraseña incorrectos.')
    # No detenemos la app, dejamos que fluya al modo invitado si quieren,
    # o pueden reintentar.

# CASO 3: MODO INVITADO (No logueado o login fallido)
else:
    if st.session_state.guest_credits > 0:
        with st.sidebar:
            st.warning("Modo Invitado")
            st.metric("Créditos Gratuitos", st.session_state.guest_credits)
            st.info("Inicia sesión para acceso ilimitado.")
    else:
        st.error("⛔ Se han agotado tus 20 interacciones gratuitas.")
        st.info("Por favor, contacta con el administrador para obtener credenciales.")
        st.stop() # AQUÍ SÍ PARAMOS SI NO HAY CRÉDITOS

# Guardamos el estado en la sesión para que las otras páginas lo sepan
st.session_state['usuario_activo'] = usuario_activo
st.session_state['es_premium'] = es_premium

# ==============================================================================
#  INTERFAZ PRINCIPAL (VISIBLE PARA TODOS LOS QUE TENGAN CRÉDITOS)
# ==============================================================================

with st.sidebar:
    st.divider()
    # Selector de Idioma Global
    if 'lang' not in st.session_state:
        st.session_state.lang = 'ES'
    
    idioma_elegido = st.selectbox(
        "Idioma / Language", # Simplificado para evitar error de diccionario antes de tiempo
        options=["Español", "繁體中文", "English"],
        index=0
    )
    mapping = {"Español": "ES", "繁體中文": "ZH", "English": "EN"}
    st.session_state.lang = mapping[idioma_elegido]

# Cargar textos
lang_code = st.session_state.lang
texts = diccionario[lang_code]

st.title(texts["titulo_app"])
st.markdown(f"""
### {texts['bienvenida']}

Bienvenido, **{usuario_activo}**.

* **Estado:** {'✅ Acceso Ilimitado' if es_premium else f'⏳ Invitado ({st.session_state.guest_credits} restantes)'}
""")

st.info("Sistema conectado a Google Sheets y Gemini 2.0 Flash Lite.")
