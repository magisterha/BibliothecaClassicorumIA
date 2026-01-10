import streamlit as st
import sys
import os

# Importar funciones de base de datos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import guardar_trabajo_usuario, leer_trabajos_usuario
from traducciones import diccionario

# Configuración
st.set_page_config(page_title="Zona de Usuario", page_icon="👤", layout="wide")

# Verificar Login (Doble seguridad por si alguien accede directo al link)
if st.session_state.get("authentication_status") is not True:
    st.warning("Acceso denegado. Por favor inicia sesión en la página principal.")
    st.stop()

# Textos
lang = st.session_state.get('lang', 'ES')
texts = diccionario[lang]
usuario = st.session_state['username']
nombre = st.session_state['name']

st.title(f"👤 Espacio de Trabajo: {nombre}")

# Pestañas
tab1, tab2 = st.tabs(["📝 Nuevo Documento", "📚 Mis Archivos"])

with tab1:
    st.subheader("Redactar o Guardar Notas")
    titulo = st.text_input("Título del documento / Referencia")
    contenido = st.text_area("Contenido (Puedes pegar respuestas de la IA aquí)", height=400)
    
    if st.button("Guardar en la Nube"):
        if titulo and contenido:
            with st.spinner("Sincronizando con Google Sheets..."):
                msg, tipo = guardar_trabajo_usuario(usuario, titulo, contenido)
                if tipo == "success":
                    st.success(msg)
                else:
                    st.error(msg)
        else:
            st.warning("Por favor completa el título y el contenido.")

with tab2:
    st.subheader("Biblioteca Personal")
    df_trabajos = leer_trabajos_usuario(usuario)
    
    if not df_trabajos.empty:
        for index, row in df_trabajos.iterrows():
            with st.expander(f"📄 {row['Titulo']} ({row['Fecha']})"):
                st.write(row['Contenido'])
                st.info("Para editar: Copia el contenido, ve a la pestaña 'Nuevo Documento', usa el MISMO título y guarda.")
    else:
        st.info("No tienes documentos guardados todavía.")
