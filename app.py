import streamlit as st  # <--- ESTO SIEMPRE VA PRIMERO
import streamlit_authenticator as stauth
from traducciones import diccionario

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Bibliotheca Classicarum IA", page_icon="🏛️", layout="wide")

# --- FUNCIÓN DE LIMPIEZA DE SECRETOS ---
def parse_secrets(obj):
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
    
    # --- CHIVATO DE DIAGNÓSTICO (Te dirá el usuario correcto) ---
    usuarios_validos = list(credentials['usernames'].keys())
    st.toast(f"ℹ️ Usuarios válidos detectados: {usuarios_validos}", icon="🕵️")
    # ------------------------------------------------------------

except Exception as e:
    st.error(f"Error leyendo Secrets: {e}")
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
    st.error('Usuario o contraseña incorrectos')
    # Pista visual por si fallas
    st.caption(f"Asegúrate de usar uno de estos usuarios: {', '.join(usuarios_validos)}")
    
elif st.session_state["authentication_status"] is None:
    st.warning('Introduce tus credenciales.')
    
    # MODO INVITADO
    if 'guest_credits' not in st.session_state:
        st.session_state.guest_credits = 20
        
    if st.session_state.guest_credits > 0:
        with st.sidebar:
            st.info(f"Modo Invitado: {st.session_state.guest_credits} usos")
            
elif st.session_state["authentication_status"] is True:
    # SI ENTRAS AQUÍ, TODO HA FUNCIONADO
    usuario = st.session_state['name']
    st.session_state['es_premium'] = True
    
    with st.sidebar:
        st.success(f"Bienvenido, {usuario}")
        authenticator.logout('Salir', 'sidebar')
        
    # --- RESTO DE TU APP ---
    if 'lang' not in st.session_state:
        st.session_state.lang = 'ES'
    
    lang_code = st.session_state.lang
    texts = diccionario[lang_code]
    st.title(texts["titulo_app"])
    st.write(texts["bienvenida"])
