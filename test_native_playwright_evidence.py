#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Prueba - Evidencia con Reportes HTML Nativos de Playwright
------------------------------------------------------------------
Este script demuestra cómo generar evidencia usando reportes HTML
nativos de Playwright/pytest-html.
"""

import os
import sys
import json
import uuid
import tempfile
from datetime import datetime

# Agregar directorios al path
sys.path.append(os.getcwd())

def create_sample_suite_results():
    """Crea datos de ejemplo para una suite de pruebas"""
    
    execution_id = str(uuid.uuid4())[:8]
    suite_id = "demo_suite_001"
    
    # Datos de ejemplo de una suite ejecutada
    suite_results = {
        'execution_id': execution_id,
        'suite_id': suite_id,
        'total_cases': 3,
        'completed_cases': 3,
        'success_count': 2,
        'failed_count': 1,
        'status': 'completed',
        'start_time': datetime.now().isoformat(),
        'end_time': datetime.now().isoformat(),
        'cases': [
            {
                'case_name': 'Test Login Funcional',
                'status': 'success',
                'message': 'Login ejecutado correctamente',
                'task_id': f'{execution_id}_case_1',
                'url': 'https://example.com/login',
                'duration': '2.5s',
                'screenshots': ['inicio_test.png', 'login_form.png', 'dashboard.png']
            },
            {
                'case_name': 'Test Navegación Dashboard',
                'status': 'success',
                'message': 'Navegación exitosa por el dashboard',
                'task_id': f'{execution_id}_case_2',
                'url': 'https://example.com/dashboard',
                'duration': '1.8s',
                'screenshots': ['dashboard_inicio.png', 'menu_navegacion.png']
            },
            {
                'case_name': 'Test Formulario Contacto',
                'status': 'error',
                'message': 'Error al enviar formulario - timeout',
                'task_id': f'{execution_id}_case_3',
                'url': 'https://example.com/contact',
                'duration': '30.0s',
                'screenshots': ['contacto_form.png', 'error_timeout.png']
            }
        ]
    }
    
    return suite_results, execution_id, suite_id

def save_suite_results_to_temp(suite_results, execution_id):
    """Guarda los resultados de la suite en un archivo temporal"""
    
    temp_file = os.path.join(tempfile.gettempdir(), f"suite_results_{execution_id}.json")
    
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(suite_results, f, indent=2, ensure_ascii=False)
    
    print(f"📁 Resultados guardados en: {temp_file}")
    return temp_file

def test_native_playwright_evidence():
    """Prueba la generación de evidencia con reportes HTML nativos"""
    
    print("🎭 DEMO: Generación de Evidencia con Reportes HTML Nativos de Playwright")
    print("=" * 80)
    
    # Crear datos de ejemplo
    print("\n1. 📋 Creando datos de ejemplo de suite...")
    suite_results, execution_id, suite_id = create_sample_suite_results()
    
    print(f"   Suite ID: {suite_id}")
    print(f"   Execution ID: {execution_id}")
    print(f"   Total casos: {suite_results['total_cases']}")
    print(f"   Casos exitosos: {suite_results['success_count']}")
    print(f"   Casos fallidos: {suite_results['failed_count']}")
    
    # Guardar resultados en archivo temporal
    print("\n2. 💾 Guardando resultados en archivo temporal...")
    temp_file = save_suite_results_to_temp(suite_results, execution_id)
    
    # Probar generación de evidencia nativa
    print("\n3. 🎭 Generando evidencia con reporte HTML nativo...")
    
    try:
        from native_playwright_evidence import generate_native_evidence_for_suite
        
        result = generate_native_evidence_for_suite(
            suite_id=suite_id,
            execution_id=execution_id,
            suite_results_file=temp_file
        )
        
        if result.get('success'):
            print("   ✅ Evidencia generada exitosamente!")
            
            if result.get('html_report_path'):
                print(f"   📄 Reporte HTML nativo: {result['html_report_path']}")
                
                # Verificar que el archivo existe
                if os.path.exists(result['html_report_path']):
                    file_size = os.path.getsize(result['html_report_path'])
                    print(f"   📊 Tamaño del reporte: {file_size:,} bytes")
                else:
                    print("   ⚠️  Archivo de reporte no encontrado")
            
            if result.get('word_report_path'):
                print(f"   📝 Documento Word: {result['word_report_path']}")
                
                # Verificar que el archivo existe
                if os.path.exists(result['word_report_path']):
                    file_size = os.path.getsize(result['word_report_path'])
                    print(f"   📊 Tamaño del documento: {file_size:,} bytes")
                else:
                    print("   ⚠️  Archivo Word no encontrado")
        else:
            print(f"   ❌ Error generando evidencia: {result.get('error')}")
            
    except ImportError as e:
        print(f"   ❌ Error de importación: {e}")
        print("   💡 Asegúrate de que todos los módulos estén disponibles")
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    
    # Probar también el método de fallback
    print("\n4. 🔄 Probando método de fallback (reporte estilo Playwright)...")
    
    try:
        # Importar función de app.py (si está disponible)
        sys.path.append(os.getcwd())
        
        # Simular datos de suite_info
        suite_info = {
            'nombre': 'Suite Demo de Playwright',
            'descripcion': 'Suite de demostración para testing de evidencia'
        }
        
        # Intentar importar función de fallback
        try:
            from app import generate_playwright_html_evidence
            
            fallback_result = generate_playwright_html_evidence(
                suite_info, suite_results, execution_id, suite_id
            )
            
            if fallback_result:
                print(f"   ✅ Reporte de fallback generado: {fallback_result}")
                
                if os.path.exists(fallback_result):
                    file_size = os.path.getsize(fallback_result)
                    print(f"   📊 Tamaño del reporte de fallback: {file_size:,} bytes")
            else:
                print("   ❌ Error generando reporte de fallback")
                
        except ImportError as e:
            print(f"   ⚠️  No se pudo importar función de fallback: {e}")
        except Exception as e:
            print(f"   ❌ Error en fallback: {e}")
            
    except Exception as e:
        print(f"   ❌ Error probando fallback: {e}")
    
    print("\n" + "=" * 80)
    print("🎭 Demo completado!")
    
    # Mostrar estructura de directorios de evidencia
    print("\n5. 📂 Estructura de directorios de evidencia:")
    
    evidence_dirs = [
        "test_evidence/playwright_reports",
        "test_evidence/word_reports"
    ]
    
    for evidence_dir in evidence_dirs:
        full_path = os.path.join(os.getcwd(), evidence_dir)
        if os.path.exists(full_path):
            files = os.listdir(full_path)
            print(f"   📁 {evidence_dir}:")
            for file in files:
                file_path = os.path.join(full_path, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"      📄 {file} ({size:,} bytes)")
        else:
            print(f"   📁 {evidence_dir}: (no existe)")

def test_pytest_runner_directly():
    """Prueba el runner de pytest directamente"""
    
    print("\n🧪 DEMO: Probando pytest runner directamente")
    print("-" * 50)
    
    try:
        from playwright_scripts.pytest_runner import create_pytest_runner
        
        # Crear un script de prueba simple
        test_script = '''
import pytest
import asyncio

class TestDemo:
    @pytest.mark.asyncio
    async def test_example_success(self):
        """Test que debe pasar"""
        print("Ejecutando test exitoso...")
        await asyncio.sleep(0.1)
        assert True, "Test passed successfully"
    
    @pytest.mark.asyncio
    async def test_example_failure(self):
        """Test que debe fallar"""
        print("Ejecutando test que falla...")
        await asyncio.sleep(0.1)
        pytest.fail("Test failed intentionally for demo")
'''
        
        # Guardar script temporal
        temp_script = os.path.join(tempfile.gettempdir(), "demo_test.py")
        with open(temp_script, 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        print(f"📝 Script de demo creado: {temp_script}")
        
        # Crear runner y ejecutar
        runner = create_pytest_runner()
        
        result = runner.run_single_test_with_html_report(
            temp_script,
            test_name="demo_test",
            execution_id="demo_001"
        )
        
        print(f"Resultado de pytest:")
        print(f"  Exitoso: {result.get('success')}")
        print(f"  Código de retorno: {result.get('returncode')}")
        
        if result.get('html_report_path'):
            print(f"  Reporte HTML: {result['html_report_path']}")
            if os.path.exists(result['html_report_path']):
                size = os.path.getsize(result['html_report_path'])
                print(f"  Tamaño: {size:,} bytes")
        
        # Limpiar
        runner.cleanup()
        
        if os.path.exists(temp_script):
            os.remove(temp_script)
            
    except ImportError as e:
        print(f"❌ Error importando pytest_runner: {e}")
    except Exception as e:
        print(f"❌ Error en prueba directa: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Ejecutar demos
    test_native_playwright_evidence()
    test_pytest_runner_directly()
    
    print("\n🎉 Todas las pruebas completadas!")
    print("\n💡 Para usar en producción:")
    print("   1. Ejecuta una suite de pruebas normal")
    print("   2. Usa el botón 'Generar Evidencia' en la interfaz web")
    print("   3. El sistema intentará generar reporte HTML nativo de Playwright")
    print("   4. Si falla, usará el método de fallback existente") 