# -*- coding: utf-8 -*-
import os
import re
import glob

def update_headless_config(file_path):
    """Actualiza un script para leer la variable de entorno HEADLESS"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar si ya está actualizado
        if 'os.environ.get(\'HEADLESS\'' in content:
            print(f"✅ {os.path.basename(file_path)} ya tiene configuración HEADLESS")
            return
        
        # Buscar la función main
        if 'async def main():' in content:
            # Agregar la configuración headless después de la línea async def main():
            headless_config = '''        # Leer configuración headless desde variable de entorno
        headless_str = os.environ.get('HEADLESS', 'true').lower()
        headless = headless_str in ['true', '1', 'yes', 'on']
        
        print("DEBUG: Iniciando test con Playwright directo...")
        print(f"DEBUG: Configuración headless={headless})'''
            
            # Reemplazar la línea de configuración hardcodeada
            content = re.sub(
                r'print\("DEBUG: Iniciando test con Playwright directo\.\.\."\)\s*\n\s*print\(f"DEBUG: Configuración headless=\{False\}"\)',
                headless_config,
                content
            )
            
            # Actualizar la línea de lanzamiento del navegador
            content = re.sub(
                r'browser = await p\.chromium\.launch\(headless=False\)',
                'browser = await p.chromium.launch(headless=headless)',
                content
            )
            
            # Escribir el archivo actualizado
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ {os.path.basename(file_path)} actualizado con configuración HEADLESS")
        else:
            print(f"⚠️ {os.path.basename(file_path)} no tiene función main()")
        
    except Exception as e:
        print(f"❌ Error actualizando {os.path.basename(file_path)}: {e}")

def main():
    """Actualiza todos los scripts de prueba"""
    test_scripts_dir = 'test_scripts'
    
    if not os.path.exists(test_scripts_dir):
        print(f"❌ Directorio {test_scripts_dir} no encontrado")
        return
    
    # Obtener todos los archivos .py en test_scripts
    script_files = glob.glob(os.path.join(test_scripts_dir, 'test_*.py'))
    
    print(f"🔧 Actualizando configuración HEADLESS en {len(script_files)} scripts...")
    
    for script_file in script_files:
        update_headless_config(script_file)
    
    print("🎉 Proceso de actualización completado")

if __name__ == "__main__":
    main() 