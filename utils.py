import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ==============================================================================
#  CONFIGURACIÓN MANUAL DEL ENLACE
#  Pega aquí abajo el enlace completo de tu Google Sheet (dentro de las comillas)
# ==============================================================================
URL_HOJA = "https://docs.google.com/spreadsheets/d/1ggKrCykbta1ef8JiTJsi_BLqkqcGRIDfYtV_DnoNojY/edit?usp=edit" 


def guardar_interaccion(query, respuesta, modulo, idioma, tipo="Chat"):
    """
    Guarda la interacción del usuario en Google Sheets.
    Usa la URL directa para evitar errores de configuración en Secrets.
    """
    try:
        # 1. Obtener datos básicos
        usuario = st.session_state.get('usuario_activo', 'Invitado')
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 2. Preparar la nueva fila
        nueva_fila = pd.DataFrame([{
            "Fecha": fecha_actual,
            "Usuario": usuario,
            "Modulo": modulo,
            "Idioma": idioma,
            "Tipo": tipo,
            "Query": query,
            "Respuesta": respuesta
        }])

        # 3. Establecer conexión
        # Usamos el nombre estándar "gsheets". Si en secrets tienes [connections.gsheets] perfecto,
        # si no, no importa tanto porque le vamos a forzar la URL en el siguiente paso.
        conn = st.connection("gsheets", type=GSheetsConnection)

        # 4. Leer datos (Forzando la URL específica)
        nombre_pestaña = "Logs" # Asegúrate de que tu pestaña se llama así
        
        try:
            # AQUÍ ESTÁ EL CAMBIO CLAVE: Pasamos spreadsheet=URL_HOJA explícitamente
            datos_existentes = conn.read(spreadsheet=URL_HOJA, worksheet=nombre_pestaña, ttl=0)
            
            if datos_existentes.empty:
                df_final = nueva_fila
            else:
                df_final = pd.concat([datos_existentes, nueva_fila], ignore_index=True)
                
        except Exception:
            # Si falla la lectura (hoja nueva o vacía), creamos el DF inicial
            df_final = nueva_fila

        # 5. Guardar datos (Forzando la URL específica)
        conn.update(spreadsheet=URL_HOJA, worksheet=nombre_pestaña, data=df_final)
        
        # Debug en consola (solo visible para el desarrollador)
        print(f"✅ Guardado exitoso para: {usuario}")

    except Exception as e:
        print(f"❌ Error crítico guardando en Sheets: {e}")
        # Opcional: Descomentar si quieres ver el error en la web
        # st.toast(f"Error guardando historial: {e}")
