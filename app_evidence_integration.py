#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Integración Final - Evidencia con Reportes HTML Nativos de Playwright
--------------------------------------------------------------------
Este archivo contiene la función mejorada que reemplaza la generación de evidencia
en app.py para incluir reportes HTML nativos de Playwright.
"""

import os
import sys
import logging

# Configurar logging
logger = logging.getLogger(__name__)

def generate_suite_evidence_from_results_enhanced(suite_info, suite_results, execution_id, suite_id):
    """
    Función mejorada para generar evidencia que incluye reportes HTML nativos de Playwright.
    
    Esta función reemplaza la función original en app.py y proporciona:
    1. Reporte HTML nativo de Playwright (método principal)
    2. Reporte HTML estilo Playwright (fallback 1)
    3. Documento Word tradicional (fallback 2)
    
    Args:
        suite_info: Información de la suite
        suite_results: Resultados de la ejecución
        execution_id: ID único de la ejecución
        suite_id: ID de la suite
        
    Returns:
        str: Ruta al archivo de evidencia generado o None si falla
    """
    
    logger.info(f"🎭 Generando evidencia mejorada para suite {suite_id}, ejecución {execution_id}")
    
    # Método 1: Intentar generar reporte HTML nativo de Playwright
    try:
        from simple_native_evidence import generate_native_html_evidence_integration
        
        logger.info("🎯 Intentando generar reporte HTML nativo de Playwright...")
        html_native_path = generate_native_html_evidence_integration(
            suite_info, suite_results, execution_id, suite_id
        )
        
        if html_native_path and os.path.exists(html_native_path):
            logger.info(f"✅ Reporte HTML nativo generado exitosamente: {html_native_path}")
            
            # También generar documento Word mejorado
            try:
                from simple_native_evidence import create_enhanced_word_document
                word_path = create_enhanced_word_document(
                    suite_info, suite_results, execution_id, suite_id, html_native_path
                )
                if word_path:
                    logger.info(f"📄 Documento Word mejorado generado: {word_path}")
            except Exception as e:
                logger.warning(f"No se pudo generar documento Word mejorado: {e}")
            
            return html_native_path
        else:
            logger.warning("No se pudo generar reporte HTML nativo, usando fallback...")
            
    except ImportError as e:
        logger.warning(f"simple_native_evidence no disponible: {e}")
    except Exception as e:
        logger.warning(f"Error generando reporte HTML nativo: {e}")
    
    # Método 2: Fallback a reporte HTML estilo Playwright (método existente)
    try:
        # Importar función existente si app.py está disponible
        from app import generate_playwright_html_evidence
        
        logger.info("🎨 Intentando generar reporte HTML estilo Playwright...")
        html_style_path = generate_playwright_html_evidence(
            suite_info, suite_results, execution_id, suite_id
        )
        
        if html_style_path and os.path.exists(html_style_path):
            logger.info(f"✅ Reporte HTML estilo Playwright generado: {html_style_path}")
            return html_style_path
        else:
            logger.warning("No se pudo generar reporte estilo Playwright, usando fallback final...")
            
    except ImportError as e:
        logger.warning(f"generate_playwright_html_evidence no disponible: {e}")
    except Exception as e:
        logger.warning(f"Error generando reporte estilo Playwright: {e}")
    
    # Método 3: Fallback final a documento Word tradicional
    try:
        from app import generate_word_evidence_fallback
        
        logger.info("📄 Usando fallback final: documento Word tradicional...")
        word_fallback_path = generate_word_evidence_fallback(
            suite_info, suite_results, execution_id, suite_id
        )
        
        if word_fallback_path and os.path.exists(word_fallback_path):
            logger.info(f"✅ Documento Word tradicional generado: {word_fallback_path}")
            return word_fallback_path
        else:
            logger.error("No se pudo generar documento Word tradicional")
            
    except ImportError as e:
        logger.warning(f"generate_word_evidence_fallback no disponible: {e}")
    except Exception as e:
        logger.error(f"Error generando documento Word tradicional: {e}")
    
    # Si todos los métodos fallan
    logger.error("❌ Todos los métodos de generación de evidencia fallaron")
    return None

def create_evidence_summary(suite_info, suite_results, execution_id, suite_id):
    """
    Crea un resumen de la evidencia generada con información sobre todos los archivos creados.
    
    Returns:
        dict: Diccionario con información sobre todos los archivos de evidencia
    """
    
    evidence_files = {
        'html_native': None,
        'html_style': None,
        'word_enhanced': None,
        'word_traditional': None,
        'summary': {
            'total_files': 0,
            'primary_file': None,
            'file_sizes': {}
        }
    }
    
    # Buscar archivos de evidencia
    base_dirs = [
        ('html_native', 'test_evidence/html_reports'),
        ('html_style', 'test_evidence'),  # ZIP files
        ('word_enhanced', 'test_evidence/enhanced_reports'),
        ('word_traditional', 'test_evidence/word_reports')
    ]
    
    for file_type, base_dir in base_dirs:
        search_dir = os.path.join(os.getcwd(), base_dir)
        if os.path.exists(search_dir):
            for filename in os.listdir(search_dir):
                if execution_id in filename:
                    file_path = os.path.join(search_dir, filename)
                    if os.path.isfile(file_path):
                        evidence_files[file_type] = file_path
                        evidence_files['summary']['file_sizes'][file_type] = os.path.getsize(file_path)
                        evidence_files['summary']['total_files'] += 1
    
    # Determinar archivo principal
    if evidence_files['html_native']:
        evidence_files['summary']['primary_file'] = evidence_files['html_native']
    elif evidence_files['html_style']:
        evidence_files['summary']['primary_file'] = evidence_files['html_style']
    elif evidence_files['word_enhanced']:
        evidence_files['summary']['primary_file'] = evidence_files['word_enhanced']
    elif evidence_files['word_traditional']:
        evidence_files['summary']['primary_file'] = evidence_files['word_traditional']
    
    return evidence_files

# Función para mostrar información sobre la evidencia generada
def log_evidence_summary(suite_info, suite_results, execution_id, suite_id):
    """Muestra un resumen de toda la evidencia generada"""
    
    evidence_summary = create_evidence_summary(suite_info, suite_results, execution_id, suite_id)
    
    logger.info("📋 RESUMEN DE EVIDENCIA GENERADA:")
    logger.info(f"   Suite: {suite_info.get('nombre', 'N/A') if suite_info else 'N/A'}")
    logger.info(f"   Execution ID: {execution_id}")
    logger.info(f"   Total archivos: {evidence_summary['summary']['total_files']}")
    
    if evidence_summary['html_native']:
        size = evidence_summary['summary']['file_sizes'].get('html_native', 0)
        logger.info(f"   🎭 HTML Nativo: {os.path.basename(evidence_summary['html_native'])} ({size:,} bytes)")
    
    if evidence_summary['html_style']:
        size = evidence_summary['summary']['file_sizes'].get('html_style', 0)
        logger.info(f"   🎨 HTML Estilo: {os.path.basename(evidence_summary['html_style'])} ({size:,} bytes)")
    
    if evidence_summary['word_enhanced']:
        size = evidence_summary['summary']['file_sizes'].get('word_enhanced', 0)
        logger.info(f"   📄 Word Mejorado: {os.path.basename(evidence_summary['word_enhanced'])} ({size:,} bytes)")
    
    if evidence_summary['word_traditional']:
        size = evidence_summary['summary']['file_sizes'].get('word_traditional', 0)
        logger.info(f"   📝 Word Tradicional: {os.path.basename(evidence_summary['word_traditional'])} ({size:,} bytes)")
    
    primary = evidence_summary['summary']['primary_file']
    if primary:
        logger.info(f"   🎯 Archivo principal: {os.path.basename(primary)}")
    
    return evidence_summary

# Función principal para reemplazar en app.py
def generate_suite_evidence_from_results_final(suite_info, suite_results, execution_id, suite_id):
    """
    Función final que reemplaza la función original en app.py.
    
    Esta función:
    1. Genera evidencia usando el mejor método disponible
    2. Crea un resumen de todos los archivos generados
    3. Retorna la ruta del archivo principal
    """
    
    try:
        # Generar evidencia
        primary_evidence_path = generate_suite_evidence_from_results_enhanced(
            suite_info, suite_results, execution_id, suite_id
        )
        
        # Crear y mostrar resumen
        evidence_summary = log_evidence_summary(suite_info, suite_results, execution_id, suite_id)
        
        return primary_evidence_path
        
    except Exception as e:
        logger.error(f"❌ Error en generación final de evidencia: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Prueba de la integración
    print("🧪 Probando integración final de evidencia...")
    
    # Datos de ejemplo
    suite_info = {
        'nombre': 'Suite de Integración Final',
        'descripcion': 'Prueba de la integración completa'
    }
    
    suite_results = {
        'cases': [
            {
                'case_name': 'Test de Login',
                'status': 'success',
                'message': 'Login exitoso',
                'url': 'https://example.com/login',
                'task_id': 'test_001'
            },
            {
                'case_name': 'Test de Dashboard',
                'status': 'success',
                'message': 'Dashboard cargado',
                'url': 'https://example.com/dashboard',
                'task_id': 'test_002'
            },
            {
                'case_name': 'Test de Error',
                'status': 'error',
                'message': 'Error simulado para testing',
                'url': 'https://example.com/error',
                'task_id': 'test_003'
            }
        ],
        'success_count': 2,
        'failed_count': 1,
        'total_cases': 3,
        'status': 'completed'
    }
    
    import uuid
    execution_id = str(uuid.uuid4())[:8]
    suite_id = "integration_test"
    
    result_path = generate_suite_evidence_from_results_final(
        suite_info, suite_results, execution_id, suite_id
    )
    
    if result_path:
        print(f"✅ Evidencia final generada: {result_path}")
    else:
        print("❌ Error generando evidencia final") 