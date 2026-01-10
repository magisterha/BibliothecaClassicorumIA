
import streamlit as st
import streamlit_authenticator as stauth

# --- BORRAR ESTO DESPUÉS DE OBTENER EL CÓDIGO ---
# 1. Escribe aquí ABAJO la contraseña que quieres mantener (la tuya)
tu_password_actual = "$adad(JKJKU)oooo111OOb44.4441Ju8" 

# 2. Generamos el código secreto
hash_generado = stauth.Hasher([$adad(JKJKU)oooo111OOb44.4441Ju8]).generate()[0]

# 3. Te lo mostramos en pantalla para que lo copies
st.write(f"Para mantener tu contraseña '{$adad(JKJKU)oooo111OOb44.4441Ju8}', copia este código:")
st.code(hash_generado, language="text")
st.stop()
# ------------------------------------------------



# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Bibliotheca Classicarum IA",
    page_icon="🏛️",
    layout="wide"
)

# --- FUNCIÓN CRÍTICA DE CONVERSIÓN ---
def parse_secrets(obj):
    """
    Convierte recursivamente el objeto st.secrets (inmutable) 
    en un diccionario estándar de Python (mutable).
    Esto soluciona el error 'Secrets does not support item assignment'.
    """
    if hasattr(obj, 'items'):
        return {k: parse_secrets(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [parse_secrets(i) for i in obj]
    else:
        return obj

# 2. INICIALIZACIÓN DEL MODO INVITADO
if 'guest_credits' not in st.session_state:
    st.session_state.guest_credits = 20

# 3. SISTEMA DE LOGIN / AUTENTICACIÓN
try:
    # CARGAMOS LOS SECRETOS USANDO LA FUNCIÓN DE LIMPIEZA
    # Esto crea una copia limpia en memoria que la librería sí puede editar
    secrets_dict = parse_secrets(st.secrets)
    
    credentials = secrets_dict['credentials']
    cookie = secrets_dict['cookie']
    
except Exception as e:
    st.error(f"Error cargando secretos: {e}")
    st.stop()

# Crear el objeto autenticador con los datos ya convertidos
authenticator = stauth.Authenticate(
    credentials,
    cookie['name'],
    cookie['key'],
    cookie['expiry_days']
)

# Renderizamos widget de Login
authenticator.login()

# --- 4. LÓGICA DE CONTROL DE ACCESO (HÍBRIDO) ---

usuario_activo = "Invitado"
es_premium = False

# CASO A: LOGUEADO CORRECTAMENTE
if st.session_state["authentication_status"] is True:
    usuario_activo = st.session_state['name']
    es_premium = True
    
    with st.sidebar:
        st.success(f"Investigador: **{usuario_activo}**")
        authenticator.logout('Cerrar Sesión', 'sidebar')

# CASO B: CONTRASEÑA INCORRECTA
elif st.session_state["authentication_status"] is False:
    st.error('Usuario o contraseña incorrectos / Username or password incorrect')

# CASO C: NO LOGUEADO (MODO INVITADO)
elif st.session_state["authentication_status"] is None:
    # Verificamos si le quedan créditos
    if st.session_state.guest_credits > 0:
        with st.sidebar:
            st.info(f"👤 Modo Invitado")
            st.warning(f"Créditos restantes: {st.session_state.guest_credits}")
            st.markdown("---")
            st.caption("Inicia sesión para acceso ilimitado.")
    else:
        # Si no hay créditos y no está logueado -> BLOQUEO TOTAL
        st.error("⛔ Se han agotado tus 20 interacciones gratuitas.")
        st.info("Por favor, inicia sesión con una cuenta de investigador.")
        st.stop()

# Guardar estado en sesión para las páginas satélite
st.session_state['usuario_activo'] = usuario_activo
st.session_state['es_premium'] = es_premium

# ==============================================================================
#  INTERFAZ PRINCIPAL
# ==============================================================================

# Selector de Idioma (Seguro)
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

lang_code = st.session_state.lang
texts = diccionario[lang_code]

# Contenido
st.title(texts["titulo_app"])
st.markdown(f"""
### {texts['bienvenida']}

**Estado de la Sesión:**
* Usuario: **{usuario_activo}**
* Tipo de acceso: **{'🛡️ Ilimitado (Premium)' if es_premium else '⏳ Limitado (Invitado)'}**
""")

st.info("Sistema operativo: Google Sheets Backend + Gemini 2.0 Flash Lite")
