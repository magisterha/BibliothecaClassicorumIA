# --- CÓDIGO DE DIAGNÓSTICO (BORRAR DESPUÉS) ---
st.write("--- MODO DEBUG ---")
try:
    # Verificamos qué usuarios ha cargado el sistema
    usuarios_cargados = list(credentials['usernames'].keys())
    st.write(f"✅ Usuarios detectados en el sistema: {usuarios_cargados}")
    
    # Verificamos (sin mostrarla) si la contraseña tiene formato correcto
    for user in usuarios_cargados:
        pwd = credentials['usernames'][user]['password']
        es_hash = pwd.startswith('$2b$')
        st.write(f"👤 Usuario: '{user}' -> ¿Contraseña encriptada bien?: {'✅ SÍ' if es_hash else '❌ NO (Debe empezar por $2b$)'}")
        
except Exception as e:
    st.error(f"❌ Error leyendo credenciales: {e}")
st.stop()
# ---------------------------------------------
