import pandas as pd
import os
from datetime import datetime

LOG_FILE = "logs/interacciones.csv"

def guardar_interaccion(usuario_input, ia_raw_output, modulo, idioma="ES", origen="General"):
    """
    Guarda la interacción en un CSV para posterior refinamiento (RLHF).
    """
    # 1. Crear la carpeta logs si no existe
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # 2. Preparar los datos
    nueva_fila = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Modulo": modulo,
        "Idioma_UI": idioma,
        "Origen": origen, # Si vino del menú o texto libre
        "Pregunta_Usuario": usuario_input,
        "Respuesta_IA": ia_raw_output,
        "Refinada_Humana": "" # Espacio para tu corrección manual
    }
    
    # 3. Guardar o Añadir (Append)
    try:
        if os.path.exists(LOG_FILE):
            df = pd.read_csv(LOG_FILE)
            new_df = pd.DataFrame([nueva_fila])
            df = pd.concat([df, new_df], ignore_index=True)
        else:
            df = pd.DataFrame([nueva_fila])
            
        df.to_csv(LOG_FILE, index=False)
        return True
    except Exception as e:
        print(f"Error guardando log: {e}")
        return False

def obtener_logs():
    """Devuelve el dataframe para visualizarlo o descargarlo"""
    if os.path.exists(LOG_FILE):
        return pd.read_csv(LOG_FILE)
    return pd.DataFrame()
