#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ejecutor de scripts de Playwright
---------------------------------
Este script permite listar y ejecutar los scripts de Playwright generados.
"""

import os
import sys
import importlib.util
import inspect
import argparse
import time
import platform
import subprocess
from datetime import datetime

# Directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CASOS_DIR = os.path.join(BASE_DIR, "casos")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# Crear directorio de reportes si no existe
os.makedirs(REPORTS_DIR, exist_ok=True)

class CasoTest:
    """Representa un caso de prueba de Playwright."""
    def __init__(self, filename, module_path):
        self.filename = filename
        self.module_path = module_path
        self.name = os.path.splitext(filename)[0]
        self.description = ""
        self.module = None
        self._load_module()
    
    def _load_module(self):
        """Carga el módulo Python."""
        try:
            spec = importlib.util.spec_from_file_location(self.name, self.module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.module = module
            
            # Intenta extraer descripción del docstring
            if module.__doc__:
                self.description = module.__doc__.strip().split("\n")[0]
            else:
                self.description = f"Script de prueba: {self.name}"
        except Exception as e:
            print(f"⚠️ Error al cargar {self.name}: {e}")
    
    def execute(self, headless=True):
        """Ejecuta el caso de prueba."""
        if not self.module:
            print(f"❌ No se pudo ejecutar {self.name}: módulo no cargado")
            return False
        
        print(f"\n==== Ejecutando caso: {self.name} ====")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(REPORTS_DIR, f"{self.name}_{timestamp}.log")
        
        try:
            # Verificar si el módulo tiene una función main asíncrona
            if hasattr(self.module, 'main') and inspect.iscoroutinefunction(self.module.main):
                # Ejecutar el script como subproceso para capturar su salida completa
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                env['PYTHONUTF8'] = '1'
                
                # Configurar opciones para headless si es necesario
                if headless:
                    env['PLAYWRIGHT_HEADLESS'] = '1'
                else:
                    env['PLAYWRIGHT_HEADLESS'] = '0'
                
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== Ejecución de {self.name} ===\n")
                    f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Headless: {'Sí' if headless else 'No'}\n\n")
                
                cmd = [sys.executable, self.module_path]
                print(f"🚀 Iniciando {' '.join(cmd)}")
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    env=env
                )
                
                # Capturar la salida en tiempo real y escribirla en el archivo de log
                with open(log_file, 'a', encoding='utf-8') as f:
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            print(f"  {output.strip()}")
                            f.write(output)
                
                # Capturar cualquier salida de error restante
                stderr = process.stderr.read()
                if stderr:
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write("\n=== ERRORES ===\n")
                        f.write(stderr)
                    print(f"⚠️ Errores: {stderr}")
                
                returncode = process.wait()
                
                # Registrar resultado
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n=== Finalizado con código: {returncode} ===\n")
                
                if returncode == 0:
                    print(f"✅ Caso {self.name} ejecutado correctamente")
                    return True
                else:
                    print(f"❌ Caso {self.name} falló con código {returncode}")
                    return False
            else:
                print(f"❌ El script {self.name} no tiene una función main asíncrona")
                return False
        except Exception as e:
            print(f"❌ Error al ejecutar {self.name}: {e}")
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n=== ERROR DE EJECUCIÓN ===\n{str(e)}\n")
            return False

def list_test_cases():
    """Lista todos los casos de prueba disponibles."""
    casos = []
    
    # Buscar archivos .py en el directorio de casos
    for filename in os.listdir(CASOS_DIR):
        if filename.endswith('.py') and not filename.startswith('__'):
            filepath = os.path.join(CASOS_DIR, filename)
            casos.append(CasoTest(filename, filepath))
    
    return casos

def save_test_case(name, code, description=""):
    """Guarda un nuevo caso de prueba."""
    # Sanitizar el nombre del archivo
    safe_name = "".join(c for c in name if c.isalnum() or c in "._- ").replace(" ", "_").lower()
    
    # Asegurar que tenga extensión .py
    if not safe_name.endswith('.py'):
        safe_name += '.py'
    
    # Crear la ruta completa
    filepath = os.path.join(CASOS_DIR, safe_name)
    
    # Agregar docstring si hay descripción
    if description:
        docstring = f'"""\n{description}\n"""\n\n'
        code = docstring + code
    
    # Escribir el código al archivo
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(code)
    
    print(f"✅ Caso de prueba guardado en: {filepath}")
    return filepath

def print_cases(casos):
    """Imprime la lista de casos disponibles en formato tabular."""
    if not casos:
        print("No hay casos de prueba disponibles.")
        return
    
    print("\n=== CASOS DE PRUEBA DISPONIBLES ===")
    print(f"{'#':<3} {'NOMBRE':<30} {'DESCRIPCIÓN':<50}")
    print("-" * 83)
    
    for i, caso in enumerate(casos, 1):
        print(f"{i:<3} {caso.name:<30} {caso.description[:50]:<50}")

def main():
    """Función principal del ejecutor."""
    parser = argparse.ArgumentParser(description="Ejecutor de scripts de Playwright")
    
    # Comandos principales
    subparsers = parser.add_subparsers(dest="command", help="Comando")
    
    # Comando 'list'
    list_parser = subparsers.add_parser("list", help="Listar casos disponibles")
    
    # Comando 'run'
    run_parser = subparsers.add_parser("run", help="Ejecutar un caso específico")
    run_parser.add_argument("caso", help="Nombre o número del caso a ejecutar")
    run_parser.add_argument("--no-headless", action="store_true", help="Ejecutar con navegador visible")
    
    # Comando 'run-all'
    run_all_parser = subparsers.add_parser("run-all", help="Ejecutar todos los casos")
    run_all_parser.add_argument("--no-headless", action="store_true", help="Ejecutar con navegador visible")
    
    # Comando 'save'
    save_parser = subparsers.add_parser("save", help="Guardar un nuevo caso")
    save_parser.add_argument("nombre", help="Nombre del nuevo caso")
    save_parser.add_argument("archivo", help="Archivo con el código a guardar")
    save_parser.add_argument("--descripcion", help="Descripción del caso", default="")
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Si no se especifica comando, mostrar ayuda
    if not args.command:
        parser.print_help()
        return
    
    # Obtener lista de casos
    casos = list_test_cases()
    
    # Ejecutar comando correspondiente
    if args.command == "list":
        print_cases(casos)
    
    elif args.command == "run":
        # Convertir a índice si se proporciona un número
        try:
            if args.caso.isdigit():
                idx = int(args.caso) - 1
                if 0 <= idx < len(casos):
                    caso = casos[idx]
                else:
                    print(f"❌ Índice fuera de rango: {args.caso}")
                    return
            else:
                # Buscar por nombre
                caso_encontrado = False
                for c in casos:
                    if c.name == args.caso or c.filename == args.caso:
                        caso = c
                        caso_encontrado = True
                        break
                
                if not caso_encontrado:
                    print(f"❌ Caso no encontrado: {args.caso}")
                    return
            
            # Ejecutar el caso
            caso.execute(headless=not args.no_headless)
        
        except Exception as e:
            print(f"❌ Error al ejecutar el caso: {e}")
    
    elif args.command == "run-all":
        print(f"\n=== EJECUTANDO {len(casos)} CASOS DE PRUEBA ===")
        resultados = []
        
        for caso in casos:
            resultado = caso.execute(headless=not args.no_headless)
            resultados.append((caso.name, resultado))
        
        # Mostrar resumen
        print("\n=== RESUMEN DE EJECUCIÓN ===")
        print(f"{'CASO':<30} {'RESULTADO':<10}")
        print("-" * 42)
        
        exitosos = 0
        for nombre, resultado in resultados:
            estado = "✅ EXITOSO" if resultado else "❌ FALLIDO"
            if resultado:
                exitosos += 1
            print(f"{nombre:<30} {estado:<10}")
        
        print(f"\nResultado final: {exitosos}/{len(casos)} casos exitosos")
    
    elif args.command == "save":
        # Leer el archivo de código
        try:
            with open(args.archivo, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Guardar el caso
            save_test_case(args.nombre, code, args.descripcion)
        except Exception as e:
            print(f"❌ Error al guardar el caso: {e}")

if __name__ == "__main__":
    # Configurar codificación para Windows
    if platform.system() == 'Windows':
        # Intentar configurar la codificación de la consola
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleOutputCP(65001)  # UTF-8
        except:
            pass
        
        # Configurar variables de entorno
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    main() 