#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pytest Runner para Browser-Use
------------------------------
Este módulo ejecuta scripts de browser-use como tests pytest para generar
reportes HTML nativos de Playwright.
"""

import os
import sys
import tempfile
import shutil
import subprocess
import json
import uuid
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PytestBrowserUseRunner:
    """Runner que ejecuta scripts browser-use con pytest para generar reportes HTML nativos"""
    
    def __init__(self, temp_dir=None):
        self.temp_dir = temp_dir or tempfile.mkdtemp(prefix="pytest_browser_use_")
        self.reports_dir = os.path.join(self.temp_dir, "reports")
        os.makedirs(self.reports_dir, exist_ok=True)
        
    def create_pytest_test_from_script(self, script_path, test_name=None):
        """Convierte un script browser-use en un test pytest compatible"""
        
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script no encontrado: {script_path}")
        
        # Leer el script original
        with open(script_path, 'r', encoding='utf-8') as f:
            original_code = f.read()
        
        # Generar nombre del test
        if not test_name:
            test_name = f"test_{Path(script_path).stem}"
        
        # Crear wrapper pytest
        pytest_wrapper = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test pytest generado automáticamente desde: {script_path}
Generado el: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path

# Agregar el directorio del script original al path
script_dir = r"{os.path.dirname(os.path.abspath(script_path))}"
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Importar el módulo original
import importlib.util
spec = importlib.util.spec_from_file_location("original_script", r"{script_path}")
original_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original_module)

class TestBrowserUse:
    """Clase de test pytest para browser-use"""
    
    @pytest.mark.asyncio
    async def {test_name}(self):
        """Test generado desde script browser-use"""
        try:
            # Ejecutar la función main del script original
            if hasattr(original_module, 'main'):
                if asyncio.iscoroutinefunction(original_module.main):
                    result = await original_module.main()
                else:
                    result = original_module.main()
                
                # Si el resultado es None o True, considerarlo exitoso
                if result is None or result is True:
                    assert True, "Test ejecutado exitosamente"
                elif result is False:
                    assert False, "Test falló según el script"
                else:
                    assert True, f"Test completado con resultado: {{result}}"
            else:
                # Si no hay función main, ejecutar todo el código
                exec(compile(open(r"{script_path}", "rb").read(), r"{script_path}", 'exec'))
                assert True, "Script ejecutado exitosamente"
                
        except Exception as e:
            pytest.fail(f"Error en la ejecución del test: {{str(e)}}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
'''
        
        # Crear archivo de test temporal
        test_file = os.path.join(self.temp_dir, f"{test_name}.py")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(pytest_wrapper)
        
        return test_file
    
    def run_single_test_with_html_report(self, script_path, test_name=None, execution_id=None):
        """Ejecuta un solo test y genera reporte HTML nativo"""
        
        if not execution_id:
            execution_id = str(uuid.uuid4())[:8]
        
        # Crear test pytest
        test_file = self.create_pytest_test_from_script(script_path, test_name)
        
        # Configurar paths de reporte
        html_report_path = os.path.join(self.reports_dir, f"report_{execution_id}.html")
        json_report_path = os.path.join(self.reports_dir, f"report_{execution_id}.json")
        
        # Comando pytest con generación de reporte HTML
        pytest_cmd = [
            sys.executable, "-m", "pytest",
            test_file,
            f"--html={html_report_path}",
            "--self-contained-html",  # Incluir CSS/JS en el HTML
            f"--json-report={json_report_path}",
            "--json-report-file",
            "--tb=short",
            "-v",
            "--capture=no"  # Para ver output en tiempo real
        ]
        
        logger.info(f"🧪 Ejecutando pytest: {' '.join(pytest_cmd)}")
        
        try:
            # Ejecutar pytest
            result = subprocess.run(
                pytest_cmd,
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # Analizar resultado
            success = result.returncode == 0
            
            # Leer reporte JSON si existe
            test_details = {}
            if os.path.exists(json_report_path):
                try:
                    with open(json_report_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                        test_details = {
                            'duration': json_data.get('duration', 0),
                            'tests_collected': json_data.get('summary', {}).get('collected', 0),
                            'tests_passed': json_data.get('summary', {}).get('passed', 0),
                            'tests_failed': json_data.get('summary', {}).get('failed', 0),
                            'tests_error': json_data.get('summary', {}).get('error', 0)
                        }
                except Exception as e:
                    logger.warning(f"No se pudo leer reporte JSON: {e}")
            
            return {
                'success': success,
                'html_report_path': html_report_path if os.path.exists(html_report_path) else None,
                'json_report_path': json_report_path if os.path.exists(json_report_path) else None,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'test_details': test_details,
                'execution_id': execution_id
            }
            
        except Exception as e:
            logger.error(f"Error ejecutando pytest: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_id': execution_id
            }
    
    def run_suite_with_html_report(self, script_paths, suite_name="Test Suite", execution_id=None):
        """Ejecuta una suite de tests y genera reporte HTML consolidado"""
        
        if not execution_id:
            execution_id = str(uuid.uuid4())[:8]
        
        # Crear tests pytest para todos los scripts
        test_files = []
        for i, script_path in enumerate(script_paths):
            test_name = f"test_case_{i+1}_{Path(script_path).stem}"
            test_file = self.create_pytest_test_from_script(script_path, test_name)
            test_files.append(test_file)
        
        # Configurar paths de reporte
        html_report_path = os.path.join(self.reports_dir, f"suite_report_{execution_id}.html")
        json_report_path = os.path.join(self.reports_dir, f"suite_report_{execution_id}.json")
        
        # Comando pytest para toda la suite
        pytest_cmd = [
            sys.executable, "-m", "pytest"
        ] + test_files + [
            f"--html={html_report_path}",
            "--self-contained-html",
            f"--json-report={json_report_path}",
            "--json-report-file",
            "--tb=short",
            "-v"
        ]
        
        logger.info(f"🧪 Ejecutando suite pytest: {len(test_files)} tests")
        
        try:
            # Ejecutar pytest
            result = subprocess.run(
                pytest_cmd,
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # Analizar resultado
            success = result.returncode == 0
            
            # Leer reporte JSON para detalles
            suite_details = {}
            if os.path.exists(json_report_path):
                try:
                    with open(json_report_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                        suite_details = {
                            'duration': json_data.get('duration', 0),
                            'tests_collected': json_data.get('summary', {}).get('collected', 0),
                            'tests_passed': json_data.get('summary', {}).get('passed', 0),
                            'tests_failed': json_data.get('summary', {}).get('failed', 0),
                            'tests_error': json_data.get('summary', {}).get('error', 0),
                            'individual_tests': []
                        }
                        
                        # Extraer detalles de tests individuales
                        for test in json_data.get('tests', []):
                            suite_details['individual_tests'].append({
                                'name': test.get('nodeid', ''),
                                'outcome': test.get('outcome', 'unknown'),
                                'duration': test.get('duration', 0),
                                'setup_duration': test.get('setup', {}).get('duration', 0),
                                'call_duration': test.get('call', {}).get('duration', 0),
                                'teardown_duration': test.get('teardown', {}).get('duration', 0)
                            })
                            
                except Exception as e:
                    logger.warning(f"No se pudo leer reporte JSON de suite: {e}")
            
            return {
                'success': success,
                'html_report_path': html_report_path if os.path.exists(html_report_path) else None,
                'json_report_path': json_report_path if os.path.exists(json_report_path) else None,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'suite_details': suite_details,
                'execution_id': execution_id,
                'total_tests': len(test_files)
            }
            
        except Exception as e:
            logger.error(f"Error ejecutando suite pytest: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_id': execution_id,
                'total_tests': len(test_files)
            }
    
    def cleanup(self):
        """Limpia archivos temporales"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"🧹 Directorio temporal limpiado: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"No se pudo limpiar directorio temporal: {e}")
    
    def copy_html_report_to_destination(self, html_report_path, destination_dir):
        """Copia el reporte HTML a un directorio de destino"""
        try:
            if not os.path.exists(html_report_path):
                return None
            
            os.makedirs(destination_dir, exist_ok=True)
            filename = os.path.basename(html_report_path)
            destination_path = os.path.join(destination_dir, filename)
            
            shutil.copy2(html_report_path, destination_path)
            logger.info(f"📋 Reporte HTML copiado a: {destination_path}")
            return destination_path
            
        except Exception as e:
            logger.error(f"Error copiando reporte HTML: {e}")
            return None

def create_pytest_runner(temp_dir=None):
    """Factory function para crear un runner pytest"""
    return PytestBrowserUseRunner(temp_dir)

if __name__ == "__main__":
    # Ejemplo de uso
    runner = create_pytest_runner()
    
    # Ejemplo con un script
    script_path = "casos/busqueda_google.py"
    if os.path.exists(script_path):
        result = runner.run_single_test_with_html_report(script_path)
        print(f"Resultado: {result}")
        
        if result.get('html_report_path'):
            print(f"Reporte HTML generado: {result['html_report_path']}")
    
    runner.cleanup() 