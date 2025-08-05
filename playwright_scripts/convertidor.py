#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Convertidor de scripts generados a casos de prueba
--------------------------------------------------
Este script convierte los scripts generados por la aplicación principal 
al formato adecuado para el sistema de casos de prueba de Playwright.
"""

import os
import sys
import re
import argparse
from datetime import datetime

def convert_script(input_path, output_name=None, description=None):
    """
    Convierte un script generado por la aplicación a un caso de prueba.
    
    Args:
        input_path: Ruta al script generado
        output_name: Nombre para el archivo de salida (opcional)
        description: Descripción del caso de prueba (opcional)
    
    Returns:
        Ruta al archivo convertido
    """
    # Verificar si el archivo existe
    if not os.path.exists(input_path):
        print(f"❌ Error: El archivo {input_path} no existe")
        return None
    
    # Leer el contenido del script
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer información relevante
    url_match = re.search(r'navigate_to\("(https?://[^"]+)"', content)
    url = url_match.group(1) if url_match else "URL desconocida"
    
    task_match = re.search(r'task="""(.+?)"""', content, re.DOTALL)
    task = task_match.group(1).strip() if task_match else "Tarea desconocida"
    
    # Generar nombre de salida si no se proporcionó
    if not output_name:
        domain = url.split('//')[1].split('/')[0].replace('www.', '')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"test_{domain}_{timestamp}.py"
    
    # Asegurar que tenga extensión .py
    if not output_name.endswith('.py'):
        output_name += '.py'
    
    # Crear docstring con descripción
    if not description:
        description = f"Test automatizado para {url}\n\nTarea: {task}"
    
    docstring = f'"""\n{description}\n"""\n\n'
    
    # Crear ruta completa para el archivo de salida
    casos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "casos")
    output_path = os.path.join(casos_dir, output_name)
    
    # Preparar código Playwright
    # Verificar si el script ya tiene imports de Playwright
    if "from playwright.async_api import async_playwright" not in content:
        # Crear un nuevo script desde cero
        script_code = f'''{docstring}import asyncio
from playwright.async_api import async_playwright
import os
import time

async def main():
    """Función principal asíncrona."""
    print("Iniciando navegación a {url}...")
    
    # Determinar modo headless desde variables de entorno
    headless = os.environ.get('PLAYWRIGHT_HEADLESS', '1') == '1'
    print(f"Modo headless: {{\'activado\' if headless else \'desactivado\'}}")
    
    async with async_playwright() as p:
        # Lanzar navegador
        browser = await p.chromium.launch(headless=headless)
        
        try:
            # Crear contexto y página
            context = await browser.new_context(
                viewport={{"width": 1920, "height": 1080}}
            )
            page = await context.new_page()
            
            # Navegar a la URL
            print("Navegando a {url}...")
            await page.goto("{url}", timeout=30000)
            
            # Esperar a que la página cargue completamente
            await page.wait_for_load_state("networkidle")
            print("Página cargada")
            
            # Tomar captura de pantalla de la página inicial
            screenshot_path = f"playwright_scripts/reports/captura_inicial_{{int(time.time())}}.png"
            await page.screenshot(path=screenshot_path)
            print(f"Captura de pantalla guardada en: {{screenshot_path}}")
            
            # Tarea principal a realizar
            print("Realizando tarea: {task[:50]}...")
            
            # Aquí se debería implementar la tarea específica
            # ...
            
            print("Tarea pendiente de implementar. Por favor completa el código manualmente.")
            return False
            
        except Exception as e:
            print(f"Error durante la prueba: {{e}}")
            return False
        
        finally:
            # Cerrar navegador
            await browser.close()
            print("Navegador cerrado")

if __name__ == "__main__":
    asyncio.run(main())
'''
    else:
        # El script ya tiene código de Playwright, sólo añadir docstring
        script_code = docstring + content
    
    # Guardar el archivo
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(script_code)
    
    print(f"✅ Script convertido guardado en: {output_path}")
    return output_path

def convert_from_directory(source_dir, description_prefix=None):
    """
    Convierte todos los scripts encontrados en un directorio.
    
    Args:
        source_dir: Directorio donde buscar scripts
        description_prefix: Prefijo para descripciones (opcional)
    
    Returns:
        Lista de rutas a los archivos convertidos
    """
    if not os.path.exists(source_dir) or not os.path.isdir(source_dir):
        print(f"❌ Error: El directorio {source_dir} no existe")
        return []
    
    converted_files = []
    
    for filename in os.listdir(source_dir):
        if filename.endswith('.py') and filename != "__init__.py":
            input_path = os.path.join(source_dir, filename)
            
            # Generar nombre de salida
            output_name = f"auto_{filename}"
            
            # Generar descripción
            description = f"{description_prefix or 'Script convertido automáticamente'}\nOrigen: {filename}"
            
            # Convertir script
            output_path = convert_script(input_path, output_name, description)
            if output_path:
                converted_files.append(output_path)
    
    print(f"\n==== Convertidos {len(converted_files)} scripts ====")
    return converted_files

def main():
    """Función principal del convertidor."""
    parser = argparse.ArgumentParser(description="Convertidor de scripts a casos de prueba Playwright")
    
    # Comandos principales
    subparsers = parser.add_subparsers(dest="command", help="Comando")
    
    # Comando 'file'
    file_parser = subparsers.add_parser("file", help="Convertir un archivo específico")
    file_parser.add_argument("input", help="Ruta al script a convertir")
    file_parser.add_argument("--output", help="Nombre para el archivo de salida")
    file_parser.add_argument("--description", help="Descripción del caso de prueba")
    
    # Comando 'dir'
    dir_parser = subparsers.add_parser("dir", help="Convertir todos los scripts en un directorio")
    dir_parser.add_argument("directory", help="Directorio donde buscar scripts")
    dir_parser.add_argument("--description", help="Prefijo para descripciones")
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Si no se especifica comando, mostrar ayuda
    if not args.command:
        parser.print_help()
        return
    
    # Ejecutar comando correspondiente
    if args.command == "file":
        convert_script(args.input, args.output, args.description)
    
    elif args.command == "dir":
        convert_from_directory(args.directory, args.description)

if __name__ == "__main__":
    main() 