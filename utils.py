import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

def guardar_interaccion(query, respuesta, modulo, idioma, tipo="Chat"):
    """
    Guarda la interacción del usuario en Google Sheets.
    Argumentos:
        query (str): La pregunta del usuario.
        respuesta (str): La respuesta generada por la IA.
        modulo (str): El nombre de la página o módulo (ej: "Xunzi").
        idioma (str): El idioma actual (ES, EN, ZH).
        tipo (str): Etiqueta opcional (ej: "Chat RAG", "Traducción").
    """
    try:
        # 1. Obtener usuario actual de la sesión
        # Si no hay usuario logueado, se marca como 'Invitado' o 'Anónimo'
        usuario = st.session_state.get('usuario_activo', 'Invitado')
        
        # 2. Crear el DataFrame con la nueva fila de datos
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        nueva_fila = pd.DataFrame([{
            "Fecha": fecha_actual,
            "Usuario": usuario,
            "Modulo": modulo,
            "Idioma": idioma,
            "Tipo": tipo,
            "Query": query,
            "Respuesta": respuesta
        }])

        # 3. Establecer la conexión
        # IMPORTANTE: Usamos "gsheets" para que coincida con [connections.gsheets] en secrets.toml
        conn = st.connection("gsheets", type=GSheetsConnection)

        # 4. Leer datos existentes y añadir los nuevos
        nombre_hoja = "Logs"  # El nombre de la pestaña en tu Google Sheet
        
        try:
            # ttl=0 evita que Streamlit lea datos viejos de la caché
            datos_existentes = conn.read(worksheet=nombre_hoja, ttl=0)
            
            # Si la hoja existe pero está vacía, pandas a veces devuelve un DF vacío
            if datos_existentes.empty:
                df_final = nueva_fila
            else:
                # Concatenamos lo antiguo con lo nuevo
                df_final = pd.concat([datos_existentes, nueva_fila], ignore_index=True)
                
        except Exception:
            # Si falla la lectura (ej: la hoja no tiene datos aún), iniciamos el archivo
            df_final = nueva_fila

        # 5. Escribir los datos actualizados en Google Sheets
        conn.update(worksheet=nombre_hoja, data=df_final)
        
        # Opcional: Imprimir en consola del servidor para debug
        print(f"Log guardado correctamente para: {usuario}")

    except Exception as e:
        # Capturamos cualquier error para que la App NO se rompa frente al usuario
        print(f"⚠️ Error al guardar en Google Sheets: {e}")
        # No mostramos error en pantalla grande para no interrumpir la experiencia, 
        # pero podrías descomentar la siguiente línea si quieres verlo:
        # st.toast(f"Error de guardado: {e}")
