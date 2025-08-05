#!/usr/bin/env python3
import os
import sys
import re
import shutil
import traceback

def patch_app_py():
    print("=== Aplicando parche a app.py para solucionar el error de Pydantic ===")
    
    # Verificar si existe app.py
    if not os.path.exists("app.py"):
        print("ERROR: No se encontró app.py en el directorio actual")
        return False
    
    # Crear backup
    backup_file = "app.py.bak_original"
    if not os.path.exists(backup_file):
        print(f"Creando backup en {backup_file}")
        shutil.copy2("app.py", backup_file)
    
    # Leer el contenido del archivo
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"ERROR al leer app.py: {e}")
        return False
    
    # 1. Modificar la importación de SecretStr
    print("1. Eliminando importación de SecretStr...")
    content = re.sub(r'from\s+pydantic\s+import\s+SecretStr\s*(#[^\n]*)?(\n|$)', '', content)
    
    # 2. Buscar todos los usos de SecretStr y reemplazarlos
    print("2. Reemplazando usos de SecretStr...")
    content = re.sub(r'SecretStr\((.*?)\)', r'\1', content)
    
    # 3. Añadir configuración extra de Pydantic al inicio
    print("3. Añadiendo configuración adicional de Pydantic...")
    pydantic_config = """
# Configuración adicional para Pydantic
os.environ['PYDANTIC_V2'] = '1'  
os.environ['PYDANTIC_STRICT_MODE'] = 'false'
os.environ['PYDANTIC_COLORS'] = 'false'
"""
    # Verificar si ya tiene la configuración básica
    if "os.environ['PYDANTIC_V2'] = '1'" in content:
        # Si ya tiene configuración, asegurarse de que tenga todas las variables
        if "os.environ['PYDANTIC_COLORS'] = 'false'" not in content:
            # Encontrar dónde está la configuración existente y añadir la faltante
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "os.environ['PYDANTIC_V2'] = '1'" in line or "os.environ['PYDANTIC_STRICT_MODE'] = 'false'" in line:
                    lines.insert(i+1, "os.environ['PYDANTIC_COLORS'] = 'false'")
                    break
            content = '\n'.join(lines)
    else:
        # Si no tiene ninguna configuración, añadirla después de las importaciones iniciales
        import_section_end = re.search(r'import\s+.*?\n\n', content, re.DOTALL)
        if import_section_end:
            pos = import_section_end.end()
            content = content[:pos] + pydantic_config + content[pos:]
        else:
            # Si no podemos encontrar el final de las importaciones, añadirlo al inicio
            content = pydantic_config + content
    
    # 4. Añadir manejo específico para el constructor de ChatAnthropic
    print("4. Corrigiendo inicialización de ChatAnthropic...")
    content = re.sub(
        r'(llm\s*=\s*ChatAnthropic\([^)]*?)api_key=SecretStr\((.*?)\)([^)]*?\))',
        r'\1api_key=\2\3',
        content
    )
    
    # 5. Añadir manejo específico para agent.run() sin parámetro task
    print("5. Corrigiendo llamadas a agent.run()...")
    content = re.sub(
        r'(agent\.run\s*\(\s*)task\s*=\s*[^,)]+(\s*[,)])',
        r'\1\2',
        content
    )
    
    # 6. Guardar el archivo modificado
    try:
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Parche aplicado correctamente a app.py")
        return True
    except Exception as e:
        print(f"ERROR al guardar app.py: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = patch_app_py()
    if success:
        print("\n=== Parche completado con éxito ===")
        print("Ahora puede ejecutar la aplicación con:")
        print("  python app.py")
        print("O usando el script corregido:")
        print("  iniciar_qa_pilot_corregido.bat")
    else:
        print("\n=== El parche no se pudo aplicar correctamente ===")
        print("Por favor, revise los errores anteriores.")
        sys.exit(1) 