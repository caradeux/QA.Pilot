#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ejecutor de Suites de Pruebas para Playwright
---------------------------------------------
Este módulo permite ejecutar múltiples casos de prueba en secuencia
como parte de una suite.
"""

import os
import sys
import json
import time
import asyncio
import traceback
import subprocess
import platform
from datetime import datetime
from threading import Thread, Lock
import queue

# Importar módulo de administración de suites
from .suites_manager import get_suite, TestSuite

# Directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CASOS_DIR = os.path.join(BASE_DIR, "casos")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
SUITES_REPORTS_DIR = os.path.join(REPORTS_DIR, "suites")

# Crear directorios si no existen
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(SUITES_REPORTS_DIR, exist_ok=True)

# Variables globales para seguimiento de ejecución
suite_runs = {}
suite_runs_lock = Lock()

class SuiteExecution:
    """Representa la ejecución de una suite de pruebas."""
    
    def __init__(self, suite_id, suite_name, cases):
        """Inicializa la ejecución de una suite.
        
        Args:
            suite_id (str): ID de la suite
            suite_name (str): Nombre de la suite
            cases (list): Lista de casos a ejecutar
        """
        self.suite_id = suite_id
        self.suite_name = suite_name
        self.cases = cases.copy()  # Lista de casos a ejecutar
        self.execution_id = f"{suite_id}_{int(time.time())}"
        self.start_time = datetime.now()
        self.end_time = None
        self.status = "queued"
        self.current_case_index = -1
        self.current_case = None
        self.results = []
        self.summary = {
            "total": len(cases),
            "completed": 0,
            "success": 0,
            "failed": 0,
            "progress": 0.0
        }
        
        # Crear directorio para reportes
        self.report_dir = os.path.join(SUITES_REPORTS_DIR, self.execution_id)
        os.makedirs(self.report_dir, exist_ok=True)
    
    def to_dict(self):
        """Convierte la ejecución a un diccionario para serialización."""
        return {
            "execution_id": self.execution_id,
            "suite_id": self.suite_id,
            "suite_name": self.suite_name,
            "cases": self.cases,
            "status": self.status,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "current_case_index": self.current_case_index,
            "current_case": self.current_case,
            "results": self.results,
            "summary": self.summary,
            "report_dir": self.report_dir
        }
    
    def start(self):
        """Inicia la ejecución de la suite."""
        self.status = "running"
        return True
    
    def get_next_case(self):
        """Obtiene el siguiente caso a ejecutar.
        
        Returns:
            dict: Información del caso, o None si no hay más casos
        """
        if self.current_case_index + 1 < len(self.cases):
            self.current_case_index += 1
            case_filename = self.cases[self.current_case_index]
            case_path = os.path.join(CASOS_DIR, case_filename)
            
            self.current_case = {
                "index": self.current_case_index,
                "filename": case_filename,
                "name": os.path.splitext(case_filename)[0],
                "path": case_path
            }
            
            return self.current_case
        
        return None
    
    def add_result(self, case_result):
        """Añade el resultado de un caso ejecutado.
        
        Args:
            case_result (dict): Resultado de la ejecución del caso
        """
        self.results.append(case_result)
        self.summary["completed"] += 1
        
        if case_result.get("success"):
            self.summary["success"] += 1
        else:
            self.summary["failed"] += 1
        
        # Actualizar progreso
        self.summary["progress"] = round((self.summary["completed"] / self.summary["total"]) * 100, 1)
        
        # Si todos los casos están completos, marcar como finalizado
        if self.summary["completed"] >= self.summary["total"]:
            self.end_time = datetime.now()
            self.status = "completed"
            
            # Guardar resultado final
            self.save_report()
    
    def save_report(self):
        """Guarda el reporte completo de la ejecución."""
        report_path = os.path.join(self.report_dir, "report.json")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            # Crear informe completo
            report_data = {
                "execution_id": self.execution_id,
                "suite_id": self.suite_id,
                "suite_name": self.suite_name,
                "status": self.status,
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.end_time else None,
                "summary": self.summary,
                "cases": self.cases,
                "results": self.results
            }
            
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return report_path

def execute_suite(suite_id, headless=True):
    """Ejecuta una suite completa de casos de prueba.
    
    Args:
        suite_id (str): ID de la suite a ejecutar
        headless (bool): Si se debe ejecutar en modo headless
    
    Returns:
        str: ID de ejecución para seguimiento
    """
    # Obtener la suite
    suite = get_suite(suite_id)
    if not suite:
        raise ValueError(f"Suite no encontrada: {suite_id}")
    
    # Verificar que tenga casos
    if not suite.cases:
        raise ValueError(f"La suite {suite.name} no tiene casos configurados")
    
    # Crear objeto de ejecución
    execution = SuiteExecution(
        suite_id=suite.id,
        suite_name=suite.name,
        cases=suite.cases
    )
    
    # Registrar en el diccionario global
    with suite_runs_lock:
        suite_runs[execution.execution_id] = execution
    
    # Iniciar hilo de ejecución
    execution_thread = Thread(
        target=_run_suite_thread,
        args=(execution.execution_id, headless)
    )
    execution_thread.daemon = True
    execution_thread.start()
    
    return execution.execution_id

def _run_suite_thread(execution_id, headless=True):
    """Función que se ejecuta en un hilo para procesar todos los casos de una suite.
    
    Args:
        execution_id (str): ID de la ejecución
        headless (bool): Si se debe ejecutar en modo headless
    """
    # Obtener el objeto de ejecución
    with suite_runs_lock:
        if execution_id not in suite_runs:
            print(f"ERROR: No se encontró la ejecución {execution_id}")
            return
        
        execution = suite_runs[execution_id]
        execution.start()
    
    # Ejecutar cada caso secuencialmente
    case = execution.get_next_case()
    while case:
        print(f"Ejecutando caso {case['index'] + 1}/{len(execution.cases)}: {case['name']}")
        
        # Ejecutar el caso y obtener resultado
        result = _execute_single_case(case, execution.report_dir, headless)
        
        # Actualizar estado de ejecución
        with suite_runs_lock:
            if execution_id in suite_runs:
                execution = suite_runs[execution_id]
                execution.add_result(result)
        
        # Obtener el siguiente caso
        case = execution.get_next_case()
    
    # Finalizar ejecución
    with suite_runs_lock:
        if execution_id in suite_runs:
            execution = suite_runs[execution_id]
            if execution.status != "completed":
                execution.end_time = datetime.now()
                execution.status = "completed"
                execution.save_report()

def _execute_single_case(case, report_dir, headless=True):
    """Ejecuta un caso de prueba individual.
    
    Args:
        case (dict): Información del caso a ejecutar
        report_dir (str): Directorio para guardar el reporte
        headless (bool): Si se debe ejecutar en modo headless
    
    Returns:
        dict: Resultado de la ejecución
    """
    case_path = case['path']
    case_name = case['name']
    case_index = case['index']
    
    # Preparar resultado
    result = {
        "case_filename": case['filename'],
        "case_name": case_name,
        "case_index": case_index,
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "success": False,
        "return_code": None,
        "stdout": "",
        "stderr": "",
        "screenshots": []
    }
    
    try:
        # Verificar que el archivo existe
        if not os.path.exists(case_path):
            result["stderr"] = f"ERROR: Archivo no encontrado: {case_path}"
            return result
        
        # Preparar entorno para ejecución
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUTF8'] = '1'
        
        # Configurar headless
        if headless:
            env['PLAYWRIGHT_HEADLESS'] = '1'
        else:
            env['PLAYWRIGHT_HEADLESS'] = '0'
        
        # Configurar directorio para capturas específico del caso
        timestamp = int(time.time())
        screenshot_dir = os.path.join(report_dir, f"case_{case_index + 1}_{case_name}")
        os.makedirs(screenshot_dir, exist_ok=True)
        
        # También configurar variable de entorno para que el script pueda usarla
        env['PLAYWRIGHT_SCREENSHOT_DIR'] = screenshot_dir
        
        # Ejecutar proceso
        process = subprocess.Popen(
            [sys.executable, case_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=os.path.dirname(case_path),
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0
        )
        
        # Leer salida estándar
        stdout_data = ""
        for line in iter(process.stdout.readline, b''):
            decoded_line = line.decode('utf-8', errors='replace')
            stdout_data += decoded_line
            print(f"  {decoded_line.strip()}")
            
            # Buscar posibles screenshots mencionados en la salida
            import re
            screenshot_match = re.search(r'Captura.+guardada en: (.+\.png)', decoded_line)
            if screenshot_match and screenshot_match.group(1):
                screenshot_path = screenshot_match.group(1)
                if os.path.exists(screenshot_path):
                    screenshot_name = os.path.basename(screenshot_path)
                    result["screenshots"].append({
                        "name": screenshot_name,
                        "path": screenshot_path
                    })
        
        # Leer errores
        stderr_data = process.stderr.read().decode('utf-8', errors='replace')
        if stderr_data:
            print(f"  ERROR: {stderr_data}")
        
        # Esperar finalización
        return_code = process.wait()
        
        # Actualizar resultado
        result.update({
            "end_time": datetime.now().isoformat(),
            "return_code": return_code,
            "success": return_code == 0,
            "stdout": stdout_data,
            "stderr": stderr_data
        })
        
        # Buscar capturas de pantalla en el directorio
        for root, dirs, files in os.walk(screenshot_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    screenshot_path = os.path.join(root, file)
                    # Verificar si ya está en la lista
                    if not any(s["path"] == screenshot_path for s in result["screenshots"]):
                        result["screenshots"].append({
                            "name": file,
                            "path": screenshot_path
                        })
    
    except Exception as e:
        # Capturar cualquier excepción
        result.update({
            "end_time": datetime.now().isoformat(),
            "success": False,
            "stderr": f"ERROR: {str(e)}\n{traceback.format_exc()}"
        })
    
    return result

def get_suite_execution(execution_id):
    """Obtiene el estado actual de una ejecución de suite.
    
    Args:
        execution_id (str): ID de la ejecución
    
    Returns:
        dict: Estado actual, o None si no se encuentra
    """
    with suite_runs_lock:
        if execution_id in suite_runs:
            execution = suite_runs[execution_id]
            return execution.to_dict()
    
    # Si no está en la memoria, intentar leer del archivo
    for root, dirs, files in os.walk(SUITES_REPORTS_DIR):
        if os.path.basename(root) == execution_id and "report.json" in files:
            report_path = os.path.join(root, "report.json")
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error al cargar reporte {report_path}: {e}")
    
    return None

def list_suite_executions(limit=10):
    """Lista las ejecuciones de suites más recientes.
    
    Args:
        limit (int): Número máximo de ejecuciones a retornar
    
    Returns:
        list: Lista de ejecuciones
    """
    executions = []
    
    # Primero añadir las ejecuciones en memoria
    with suite_runs_lock:
        for exec_id, execution in suite_runs.items():
            executions.append(execution.to_dict())
    
    # Buscar archivos de reportes en el directorio
    try:
        for execution_dir in os.listdir(SUITES_REPORTS_DIR):
            dir_path = os.path.join(SUITES_REPORTS_DIR, execution_dir)
            if os.path.isdir(dir_path):
                report_path = os.path.join(dir_path, "report.json")
                if os.path.exists(report_path):
                    try:
                        with open(report_path, 'r', encoding='utf-8') as f:
                            report_data = json.load(f)
                            
                            # Evitar duplicados (si ya está en memoria)
                            if not any(e["execution_id"] == report_data["execution_id"] for e in executions):
                                executions.append(report_data)
                    except Exception as e:
                        print(f"Error al cargar reporte {report_path}: {e}")
    except Exception as e:
        print(f"Error al listar ejecuciones: {e}")
    
    # Ordenar por fecha de inicio (más reciente primero)
    executions.sort(key=lambda x: x.get("start_time", ""), reverse=True)
    
    # Limitar cantidad
    return executions[:limit]

# Prueba básica del módulo
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python suite_runner.py <suite_id> [--headless]")
        sys.exit(1)
    
    suite_id = sys.argv[1]
    headless = "--headless" in sys.argv
    
    try:
        print(f"Ejecutando suite {suite_id} {'en modo headless' if headless else 'con navegador visible'}")
        execution_id = execute_suite(suite_id, headless)
        print(f"Ejecución iniciada con ID: {execution_id}")
        
        # Esperar y mostrar progreso
        print("\nProgreso:")
        while True:
            time.sleep(2)
            execution = get_suite_execution(execution_id)
            if not execution:
                print("Error: No se pudo obtener el estado de la ejecución")
                break
            
            # Mostrar progreso
            status = execution["status"]
            progress = execution["summary"]["progress"]
            
            print(f"Estado: {status} - Progreso: {progress}% - "
                  f"Completados: {execution['summary']['completed']}/{execution['summary']['total']} - "
                  f"Éxitos: {execution['summary']['success']} - "
                  f"Fallos: {execution['summary']['failed']}")
            
            # Si terminó, salir del bucle
            if status == "completed":
                print("\nEjecución finalizada")
                
                # Mostrar resultados
                print("\nResultados:")
                for i, result in enumerate(execution["results"]):
                    status_str = "✅ ÉXITO" if result["success"] else "❌ FALLO"
                    print(f"{i+1}. {result['case_name']} - {status_str}")
                
                break
    
    except KeyboardInterrupt:
        print("\nEjecución interrumpida por el usuario")
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc() 