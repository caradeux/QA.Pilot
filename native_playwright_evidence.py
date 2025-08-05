#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generador de Evidencia con Reportes HTML Nativos de Playwright
------------------------------------------------------------
Este módulo proporciona endpoints Flask para generar evidencia
usando reportes HTML nativos de Playwright/pytest-html.
"""

import os
import sys
import json
import tempfile
import logging
from flask import Flask, request, jsonify, send_file
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar el generador de reportes
try:
    from pytest_html_integration import create_playwright_html_generator
    PLAYWRIGHT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"pytest_html_integration no disponible: {e}")
    PLAYWRIGHT_AVAILABLE = False

def generate_native_evidence_for_suite(suite_id, execution_id, suite_results_file=None):
    """
    Genera evidencia con reporte HTML nativo de Playwright para una suite.
    
    Args:
        suite_id: ID de la suite
        execution_id: ID de la ejecución
        suite_results_file: Ruta al archivo de resultados de la suite (opcional)
        
    Returns:
        dict: Resultado de la generación de evidencia
    """
    try:
        if not PLAYWRIGHT_AVAILABLE:
            return {
                'success': False,
                'error': 'pytest_html_integration no está disponible'
            }
        
        logger.info(f"🎭 Generando evidencia nativa para suite {suite_id}, ejecución {execution_id}")
        
        # Buscar archivo de resultados de la suite
        if not suite_results_file:
            # Buscar en directorio temporal
            temp_file = os.path.join(tempfile.gettempdir(), f"suite_results_{execution_id}.json")
            if os.path.exists(temp_file):
                suite_results_file = temp_file
            else:
                return {
                    'success': False,
                    'error': f'No se encontró archivo de resultados para ejecución {execution_id}'
                }
        
        # Leer resultados de la suite
        try:
            with open(suite_results_file, 'r', encoding='utf-8') as f:
                suite_data = json.load(f)
        except Exception as e:
            return {
                'success': False,
                'error': f'Error leyendo archivo de resultados: {e}'
            }
        
        # Extraer información de la suite
        suite_info = {
            'nombre': f'Suite {suite_id}',
            'descripcion': f'Ejecución automatizada {execution_id}'
        }
        
        suite_results = {
            'cases': suite_data.get('cases', []),
            'success_count': suite_data.get('success_count', 0),
            'failed_count': suite_data.get('failed_count', 0),
            'total_cases': suite_data.get('total_cases', 0),
            'status': suite_data.get('status', 'completed'),
            'start_time': suite_data.get('start_time', datetime.now().isoformat())
        }
        
        # Crear generador y generar evidencia
        generator = create_playwright_html_generator()
        
        try:
            # Generar evidencia híbrida (HTML nativo + Word)
            result = generator.generate_hybrid_evidence(
                suite_info, suite_results, execution_id, suite_id
            )
            
            if result.get('success'):
                logger.info(f"✅ Evidencia nativa generada exitosamente")
                return {
                    'success': True,
                    'html_report_path': result.get('html_report_path'),
                    'word_report_path': result.get('word_report_path'),
                    'execution_id': execution_id,
                    'suite_id': suite_id
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Error desconocido generando evidencia')
                }
                
        finally:
            generator.cleanup()
            
    except Exception as e:
        logger.error(f"❌ Error generando evidencia nativa: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }

def create_native_evidence_app():
    """Crea una aplicación Flask para manejar evidencia nativa"""
    app = Flask(__name__)
    
    @app.route('/api/generate_native_evidence/<suite_id>/<execution_id>', methods=['POST'])
    def api_generate_native_evidence(suite_id, execution_id):
        """Endpoint para generar evidencia con reporte HTML nativo"""
        try:
            # Obtener parámetros opcionales
            data = request.get_json() or {}
            suite_results_file = data.get('suite_results_file')
            
            # Generar evidencia
            result = generate_native_evidence_for_suite(
                suite_id, execution_id, suite_results_file
            )
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error en endpoint de evidencia nativa: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/download_native_report/<execution_id>')
    def api_download_native_report(execution_id):
        """Endpoint para descargar reporte HTML nativo"""
        try:
            # Buscar reporte HTML
            evidence_dir = os.path.join(os.getcwd(), "test_evidence", "playwright_reports")
            html_report_path = os.path.join(evidence_dir, f"native_report_{execution_id}.html")
            
            if os.path.exists(html_report_path):
                return send_file(
                    html_report_path,
                    as_attachment=True,
                    download_name=f"playwright_native_report_{execution_id}.html"
                )
            else:
                return jsonify({
                    'success': False,
                    'error': 'Reporte HTML nativo no encontrado'
                }), 404
                
        except Exception as e:
            logger.error(f"Error descargando reporte nativo: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/native_evidence_status')
    def api_native_evidence_status():
        """Endpoint para verificar el estado del sistema de evidencia nativa"""
        return jsonify({
            'playwright_available': PLAYWRIGHT_AVAILABLE,
            'pytest_html_available': PLAYWRIGHT_AVAILABLE,
            'system_ready': PLAYWRIGHT_AVAILABLE
        })
    
    return app

# Función para integrar con app.py principal
def add_native_evidence_routes(main_app):
    """
    Agrega las rutas de evidencia nativa a la aplicación principal.
    
    Args:
        main_app: Instancia de Flask de la aplicación principal
    """
    
    @main_app.route('/api/test_suites/<suite_id>/execution/<execution_id>/generate_native_evidence', methods=['POST'])
    def api_generate_suite_native_evidence(suite_id, execution_id):
        """Endpoint integrado para generar evidencia nativa desde la app principal"""
        try:
            logger.info(f"🎭 Solicitud de evidencia nativa para suite {suite_id}, ejecución {execution_id}")
            
            # Generar evidencia nativa
            result = generate_native_evidence_for_suite(suite_id, execution_id)
            
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'message': 'Evidencia nativa generada exitosamente',
                    'html_report_path': result.get('html_report_path'),
                    'word_report_path': result.get('word_report_path'),
                    'download_url': f'/api/download_native_report/{execution_id}'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Error generando evidencia nativa')
                }), 500
                
        except Exception as e:
            logger.error(f"Error en endpoint integrado de evidencia nativa: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @main_app.route('/api/download_native_report/<execution_id>')
    def api_download_native_report_integrated(execution_id):
        """Endpoint integrado para descargar reporte HTML nativo"""
        try:
            evidence_dir = os.path.join(os.getcwd(), "test_evidence", "playwright_reports")
            html_report_path = os.path.join(evidence_dir, f"native_report_{execution_id}.html")
            
            if os.path.exists(html_report_path):
                return send_file(
                    html_report_path,
                    as_attachment=True,
                    download_name=f"playwright_native_report_{execution_id}.html"
                )
            else:
                return jsonify({
                    'success': False,
                    'error': 'Reporte HTML nativo no encontrado'
                }), 404
                
        except Exception as e:
            logger.error(f"Error descargando reporte nativo: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

if __name__ == "__main__":
    # Ejecutar como aplicación independiente para testing
    app = create_native_evidence_app()
    
    print("🎭 Servidor de Evidencia Nativa de Playwright")
    print(f"Playwright disponible: {PLAYWRIGHT_AVAILABLE}")
    print("Endpoints disponibles:")
    print("  POST /api/generate_native_evidence/<suite_id>/<execution_id>")
    print("  GET  /api/download_native_report/<execution_id>")
    print("  GET  /api/native_evidence_status")
    
    app.run(debug=True, port=5001) 