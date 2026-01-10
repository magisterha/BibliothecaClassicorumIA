import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Conexión Singleton (se mantiene viva)
conn = st.connection("gsheets", type=GSheetsConnection)

def guardar_chat_log(usuario, modulo, pregunta, respuesta):
    """Guarda la interacción del chat en la pestaña 'chat_logs'"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nuevo_dato = pd.DataFrame([{
            "Fecha": timestamp,
            "Usuario": usuario,
            "Modulo": modulo,
            "Pregunta": pregunta,
            "Respuesta": respuesta
        }])
        
        # Leemos la hoja actual (con caché mínima para ver cambios recientes)
        data = conn.read(worksheet="chat_logs", usecols=list(range(5)), ttl=5)
        updated_data = pd.concat([data, nuevo_dato], ignore_index=True)
        
        # Actualizamos la hoja
        conn.update(worksheet="chat_logs", data=updated_data)
        return True
    except Exception as e:
        print(f"Error guardando log: {e}")
        return False

def guardar_trabajo_usuario(usuario, titulo, contenido):
    """Guarda o actualiza un trabajo en la pestaña 'user_works'"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Leemos las columnas necesarias
        df = conn.read(worksheet="user_works", usecols=list(range(4)), ttl=5)
        
        # Buscamos si ya existe ese título para ese usuario
        filtro = (df['Usuario'] == usuario) & (df['Titulo'] == titulo)
        
        if not df[filtro].empty:
            # ACTUALIZAR
            df.loc[filtro, 'Contenido'] = contenido
            df.loc[filtro, 'Fecha'] = timestamp
            mensaje = "Trabajo actualizado correctamente."
        else:
            # CREAR NUEVO
            nuevo = pd.DataFrame([{
                "Usuario": usuario,
                "Titulo": titulo,
                "Contenido": contenido,
                "Fecha": timestamp
            }])
            df = pd.concat([df, nuevo], ignore_index=True)
            mensaje = "Nuevo trabajo guardado."
            
        conn.update(worksheet="user_works", data=df)
        return mensaje, "success"
        
    except Exception as e:
        return f"Error al guardar: {e}", "error"

def leer_trabajos_usuario(usuario):
    """Recupera los trabajos del usuario activo"""
    try:
        df = conn.read(worksheet="user_works", usecols=list(range(4)), ttl=5)
        # Filtramos para que solo vea SUS trabajos
        return df[df['Usuario'] == usuario]
    except Exception:
        return pd.DataFrame()
