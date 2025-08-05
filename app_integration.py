#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Integración entre la aplicación principal y el sistema de casos de Playwright
-----------------------------------------------------------------------------
Este script proporciona funciones para integrar la aplicación Flask con 
el sistema de gestión de casos de prueba de Playwright.
"""

import os
import sys
import re
import argparse
from datetime import datetime
import subprocess
import shutil

# Directorios
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_SCRIPTS_DIR = os.path.join(BASE_DIR, "test_scripts")
PLAYWRIGHT_DIR = os.path.join(BASE_DIR, "playwright_scripts")
CASOS_DIR = os.path.join(PLAYWRIGHT_DIR, "casos")

def copy_test_to_cases(test_script_path, new_name=None, description=None, delete_original=True):
    """
    Copia un script de test generado al directorio de casos de Playwright.
    
    Args:
        test_script_path: Ruta al script de test
        new_name: Nombre nuevo para el archivo (opcional)
        description: Descripción para el caso de prueba (opcional)
        delete_original: Si se debe eliminar el archivo original después de copiarlo (por defecto True)
    
    Returns:
        Ruta al archivo copiado
    """
    # Verificar si el archivo existe
    if not os.path.exists(test_script_path):
        print(f"Error: El archivo {test_script_path} no existe")
        return None
    
    # Generar nombre de destino si no se proporcionó
    if not new_name:
        basename = os.path.basename(test_script_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"test_imported_{timestamp}_{basename}"
    
    # Asegurar que tenga extensión .py
    if not new_name.endswith('.py'):
        new_name += '.py'
    
    # Crear ruta completa para el archivo de destino
    dest_path = os.path.join(CASOS_DIR, new_name)
    
    # Copiar el archivo
    shutil.copy2(test_script_path, dest_path)
    
    # Si se proporcionó una descripción, añadirla como docstring
    if description:
        with open(dest_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        docstring = f'"""\n{description}\n"""\n\n'
        
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(docstring + content)
    
    print(f"Script copiado a: {dest_path}")
    
    # Eliminar el archivo original si se solicitó
    if delete_original:
        try:
            os.remove(test_script_path)
            print(f"Archivo original eliminado: {test_script_path}")
        except Exception as e:
            print(f"Error al eliminar el archivo original: {e}")
    
    return dest_path

def convert_test_script(test_script_path, output_name=None, description=None):
    """
    Convierte un script de test usando el convertidor de Playwright.
    
    Args:
        test_script_path: Ruta al script de test
        output_name: Nombre para el archivo de salida (opcional)
        description: Descripción del caso de prueba (opcional)
    
    Returns:
        Ruta al archivo convertido
    """
    # Verificar si el archivo existe
    if not os.path.exists(test_script_path):
        print(f"Error: El archivo {test_script_path} no existe")
        return None
    
    # Verificar si el convertidor existe
    convertidor_path = os.path.join(PLAYWRIGHT_DIR, "convertidor.py")
    if not os.path.exists(convertidor_path):
        print(f"Error: El convertidor {convertidor_path} no existe")
        return None
    
    # Preparar comando
    cmd = [sys.executable, convertidor_path, "file", test_script_path]
    
    if output_name:
        cmd.extend(["--output", output_name])
    
    if description:
        cmd.extend(["--description", description])
    
    # Ejecutar comando
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        
        # Buscar la ruta del archivo generado en la salida
        match = re.search(r'guardado en: (.+\.py)', result.stdout)
        if match:
            return match.group(1)
        
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el convertidor: {e}")
        print(e.stderr)
        return None

def list_recent_test_scripts(limit=10):
    """
    Lista los scripts de test más recientes.
    
    Args:
        limit: Número máximo de scripts a listar
    
    Returns:
        Lista de tuplas (ruta, fecha de modificación)
    """
    if not os.path.exists(TEST_SCRIPTS_DIR) or not os.path.isdir(TEST_SCRIPTS_DIR):
        print(f"Error: El directorio {TEST_SCRIPTS_DIR} no existe")
        return []
    
    # Buscar archivos .py
    scripts = []
    for filename in os.listdir(TEST_SCRIPTS_DIR):
        if filename.endswith('.py') and not filename.startswith('__'):
            path = os.path.join(TEST_SCRIPTS_DIR, filename)
            mtime = os.path.getmtime(path)
            scripts.append((path, mtime))
    
    # Ordenar por fecha de modificación (más reciente primero)
    scripts.sort(key=lambda x: x[1], reverse=True)
    
    # Limitar la cantidad
    return scripts[:limit]

def run_playwright_case(case_name, headless=True):
    """
    Ejecuta un caso de prueba de Playwright.
    
    Args:
        case_name: Nombre del caso a ejecutar
        headless: Si se debe ejecutar en modo headless
    
    Returns:
        Código de salida del comando
    """
    # Verificar si el ejecutor existe
    ejecutor_path = os.path.join(PLAYWRIGHT_DIR, "ejecutor.py")
    if not os.path.exists(ejecutor_path):
        print(f"Error: El ejecutor {ejecutor_path} no existe")
        return None
    
    # Preparar comando
    cmd = [sys.executable, ejecutor_path, "run", case_name]
    
    if not headless:
        cmd.append("--no-headless")
    
    # Ejecutar comando
    try:
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode
    except Exception as e:
        print(f"Error al ejecutar el caso: {e}")
        return -1

def list_playwright_cases():
    """
    Lista los casos de prueba de Playwright disponibles.
    
    Returns:
        Lista de tuplas (nombre, ruta)
    """
    # Verificar si el ejecutor existe
    ejecutor_path = os.path.join(PLAYWRIGHT_DIR, "ejecutor.py")
    if not os.path.exists(ejecutor_path):
        print(f"Error: El ejecutor {ejecutor_path} no existe")
        return []
    
    # Ejecutar comando list
    try:
        result = subprocess.run(
            [sys.executable, ejecutor_path, "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parsear la salida para obtener los casos
        cases = []
        lines = result.stdout.split('\n')
        parsing = False
        
        for line in lines:
            if "===" in line and "CASOS" in line:
                parsing = True
                continue
                
            if parsing and line.strip() and "-" * 10 not in line:
                # Formato esperado: "1   nombre_caso              descripción"
                parts = line.strip().split(None, 2)
                if len(parts) >= 2 and parts[0].isdigit():
                    idx = int(parts[0])
                    name = parts[1]
                    cases.append((name, os.path.join(CASOS_DIR, f"{name}.py")))
        
        return cases
    except subprocess.CalledProcessError as e:
        print(f"Error al listar casos: {e}")
        return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Integración con sistema de casos de Playwright")
    
    # Comandos principales
    subparsers = parser.add_subparsers(dest="command", help="Comando")
    
    # Comando 'list-tests'
    list_tests_parser = subparsers.add_parser("list-tests", help="Listar scripts de test recientes")
    list_tests_parser.add_argument("--limit", type=int, default=10, help="Número máximo de scripts a listar")
    
    # Comando 'list-cases'
    list_cases_parser = subparsers.add_parser("list-cases", help="Listar casos de Playwright")
    
    # Comando 'convert'
    convert_parser = subparsers.add_parser("convert", help="Convertir un script de test")
    convert_parser.add_argument("script", help="Ruta al script de test")
    convert_parser.add_argument("--output", help="Nombre para el archivo de salida")
    convert_parser.add_argument("--description", help="Descripción del caso de prueba")
    
    # Comando 'run'
    run_parser = subparsers.add_parser("run", help="Ejecutar un caso de Playwright")
    run_parser.add_argument("case", help="Nombre del caso a ejecutar")
    run_parser.add_argument("--no-headless", action="store_true", help="Ejecutar con navegador visible")
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Si no se especifica comando, mostrar ayuda
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Ejecutar comando correspondiente
    if args.command == "list-tests":
        scripts = list_recent_test_scripts(args.limit)
        
        print(f"\n=== SCRIPTS DE TEST RECIENTES ({len(scripts)}) ===")
        for i, (path, mtime) in enumerate(scripts, 1):
            timestamp = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{i:2d}. {os.path.basename(path):<30} [{timestamp}]")
            print(f"    {path}")
        
        if not scripts:
            print("No se encontraron scripts de test.")
    
    elif args.command == "list-cases":
        cases = list_playwright_cases()
        
        print(f"\n=== CASOS DE PLAYWRIGHT ({len(cases)}) ===")
        for i, (name, path) in enumerate(cases, 1):
            print(f"{i:2d}. {name:<30}")
            print(f"    {path}")
        
        if not cases:
            print("No se encontraron casos de Playwright.")
    
    elif args.command == "convert":
        convert_test_script(args.script, args.output, args.description)
    
    elif args.command == "run":
        exitcode = run_playwright_case(args.case, not args.no_headless)
        sys.exit(exitcode or 0) 