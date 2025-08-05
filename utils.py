import os
import traceback
from dotenv import load_dotenv, find_dotenv, set_key

API_KEYS_TO_MANAGE = [
    'GEMINI_API_KEY',
    'OPENAI_API_KEY',
    'ANTHROPIC_API_KEY',
    'AZURE_OPENAI_API_KEY', # Revisa si este nombre es correcto
    'DEEPSEEK_API_KEY'
]

def load_env_vars():
    """Carga las variables de entorno desde .env."""
    try:
        dotenv_path = find_dotenv()
        print(f"DEBUG - Buscando archivo .env...")
        print(f"DEBUG - Ruta del archivo .env encontrado: {dotenv_path}")
        
        if dotenv_path:
            print(f"DEBUG - Cargando variables desde: {dotenv_path}")
            load_dotenv(dotenv_path=dotenv_path, override=True)
            print("DEBUG - Variables cargadas correctamente")
        else:
            print("DEBUG - No se encontró archivo .env, creando uno nuevo...")
            try:
                with open(".env", "w") as f:
                    f.write("# Archivo .env creado automáticamente\n")
                dotenv_path = find_dotenv()
                if dotenv_path:
                    print(f"DEBUG - Nuevo archivo .env creado en: {dotenv_path}")
                    load_dotenv(dotenv_path=dotenv_path, override=True)
                else:
                    print("ERROR - No se pudo crear el archivo .env")
            except Exception as e:
                print(f"ERROR - Error al crear .env: {e}")
                print(traceback.format_exc())
        
        # Cargar las claves gestionadas en un diccionario
        managed_keys = {}
        print("\nDEBUG - Cargando claves gestionadas:")
        for key in API_KEYS_TO_MANAGE:
            value = os.getenv(key, '')
            managed_keys[key] = value
            print(f"DEBUG - {key}: {'*' * len(value) if value else 'no configurada'}")
        
        return managed_keys

    except Exception as e:
        print(f"ERROR - Error en load_env_vars: {e}")
        print(traceback.format_exc())
        # Retornar un diccionario vacío en caso de error
        return {key: '' for key in API_KEYS_TO_MANAGE}

def save_api_keys_to_env(keys_to_save):
    """Guarda un diccionario de claves en el archivo .env."""
    dotenv_path = find_dotenv()
    if not dotenv_path:
        try:
            with open(".env", "w") as f:
                f.write("# Archivo .env creado por Inovabiz QA Pilot\n")
            dotenv_path = find_dotenv()
            if not dotenv_path:
                return False, "No se encontró el archivo .env y no se pudo crear."
        except Exception as create_e:
            return False, f"Error al crear .env: {create_e}"

    print(f"Utils - Guardando claves en: {dotenv_path}")
    try:
        something_changed = False
        for key_name, new_value in keys_to_save.items():
            if key_name in API_KEYS_TO_MANAGE:
                current_value = os.getenv(key_name, '')
                if new_value != current_value:
                    set_key(dotenv_path, key_name, new_value, quote_mode="never")
                    print(f"Utils - Guardado {key_name}={'*' * len(new_value) if new_value else ''}")
                    something_changed = True

        if something_changed:
            # Recargar variables para la sesión actual de la app
            load_dotenv(dotenv_path=dotenv_path, override=True)
            for key_name, new_value in keys_to_save.items():
                 if key_name in API_KEYS_TO_MANAGE:
                     os.environ[key_name] = new_value
            return True, "Claves API guardadas correctamente."
        else:
            return True, "No se detectaron cambios en las claves API."

    except Exception as e:
        print(f"Error detallado al guardar .env: {traceback.format_exc()}")
        return False, f"Error al guardar claves en .env: {e}"

# --- Aquí podríamos mover también generar_script_test si se vuelve compleja ---
# Por ahora la dejamos en app.py o la importamos de la versión anterior

# Ejemplo de uso:
if __name__ == '__main__':
    # Cargar al inicio
    current_keys = load_env_vars()
    print("Claves cargadas:", current_keys)

    # Simular cambio
    # current_keys['GEMINI_API_KEY'] = 'nueva-clave-gemini'
    # success, message = save_api_keys_to_env(current_keys)
    # print(f"Guardado: {success}, Mensaje: {message}") 