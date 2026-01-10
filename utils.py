import streamlit as st
# Importamos la función de guardado en la nube
from database import guardar_chat_log

def guardar_interaccion(usuario_input, ia_raw_output, modulo, idioma="ES", origen="General"):
    """
    Wrapper que llama a la base de datos en la nube.
    """
    # Obtenemos el usuario actual de la sesión, o 'anonimo' si fallase algo
    usuario = st.session_state.get('username', 'anonimo')
    
    # Llamamos a la función de database.py
    guardar_chat_log(usuario, modulo, usuario_input, ia_raw_output)
    
    return True
