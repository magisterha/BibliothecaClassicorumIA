import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ==============================================================================
#  CONFIGURACIÓN MANUAL - PEGA TU ENLACE AQUÍ ABAJO
# ==============================================================================
URL_HOJA = "https://docs.google.com/spreadsheets/d/1ggKrCykbta1ef8JiTJsi_BLqkqcGRIDfYtV_DnoNojY/edit?usp=edit" 


def guardar_interaccion(query, respuesta, modulo, idioma, tipo="Chat"):
    """
    Guarda la interacción del usuario en Google Sheets usando el nombre estándar 'gsheets'.
    """
    try:
        # 1. Datos básicos
        usuario = st.session_state.get('usuario_activo', 'Invitado')
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        nueva_fila = pd.DataFrame([{
            "Fecha": fecha,
            "Usuario": usuario,
            "Modulo": modulo,
            "Idioma": idioma,
            "Tipo": tipo,
            "Query": query,
            "Respuesta": respuesta
        }])

        # 2. Conexión (ESTA LÍNEA ES LA CLAVE: DEBE DECIR "gsheets")
        # Esto busca la sección [connections.gsheets] en tus secrets
        conn = st.connection("gsheets", type=GSheetsConnection)

        # 3. Leer y Escribir forzando la URL
        nombre_pestaña = "Logs"
        
        try:
            # Leemos pasando la URL explícitamente
            datos = conn.read(spreadsheet=URL_HOJA, worksheet=nombre_pestaña, ttl=0)
            
            if datos.empty:
                df_final = nueva_fila
            else:
                df_final = pd.concat([datos, nueva_fila], ignore_index=True)
                
        except Exception:
            # Si falla la lectura (hoja vacía), empezamos de cero
            df_final = nueva_fila

        # Escribimos pasando la URL explícitamente
        conn.update(spreadsheet=URL_HOJA, worksheet=nombre_pestaña, data=df_final)
        print(f"✅ Guardado para: {usuario}")

    except Exception as e:
        print(f"❌ Error al guardar: {e}")
        # st.toast(f"Error guardando: {e}")
