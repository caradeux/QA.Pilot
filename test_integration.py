#!/usr/bin/env python3
"""
Script de prueba para la integración completa de base de datos PostgreSQL
con la aplicación Flask QA-Pilot
"""

import os
import sys
import json
import time
from datetime import datetime

def test_imports():
    """Probar que todas las importaciones funcionen correctamente"""
    print("🔍 Probando importaciones...")
    
    try:
        from db_integration import DatabaseIntegration, get_db_integration
        print("✅ db_integration importado correctamente")
        
        from db_models import DatabaseManager, Project, TestCase, BulkExecution
        print("✅ db_models importado correctamente")
        
        from excel_test_analyzer import TestCase as ExcelTestCase
        print("✅ excel_test_analyzer importado correctamente")
        
        return True
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False

def test_database_connection():
    """Probar conexión a la base de datos"""
    print("\n🔗 Probando conexión a base de datos...")
    
    try:
        from db_integration import DatabaseIntegration
        
        db_integration = DatabaseIntegration()
        
        if db_integration.test_connection():
            print("✅ Conexión a PostgreSQL exitosa")
            
            # Probar obtener proyecto por defecto en una sesión separada
            try:
                with db_integration.get_session() as session:
                    project = session.query(Project).filter_by(name="Default Project").first()
                    if project:
                        print(f"✅ Proyecto por defecto: {project.name} (ID: {project.id})")
                    else:
                        print("✅ No hay proyecto por defecto aún (se creará automáticamente)")
            except Exception as e:
                print(f"⚠️  Advertencia obteniendo proyecto: {e}")
            
            return True
        else:
            print("❌ No se pudo conectar a PostgreSQL")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_save_test_case():
    """Probar guardar un caso de prueba"""
    print("\n💾 Probando guardar caso de prueba...")
    
    try:
        from db_integration import DatabaseIntegration
        from excel_test_analyzer import TestCase as ExcelTestCase
        
        db_integration = DatabaseIntegration()
        
        # Crear caso de prueba de ejemplo
        excel_case = ExcelTestCase(
            id="test-case-001",
            nombre="Test de integración",
            historia_usuario="Como usuario quiero probar la integración",
            objetivo="Probar la integración con base de datos",
            precondicion="Base de datos configurada",
            pasos="1. Conectar a DB\n2. Insertar registro\n3. Verificar inserción",
            datos_prueba="Datos de prueba para integración",
            resultado_esperado="Caso guardado exitosamente en PostgreSQL"
        )
        excel_case.codigo = "TC_INTEGRATION_001"
        excel_case.tipo = "funcional"
        excel_case.prioridad = "alta"
        excel_case.url_extraida = "https://example.com/test"
        excel_case.es_valido = True
        excel_case.problemas = []
        excel_case.sugerencias = []
        excel_case.instrucciones_qa_pilot = "Caso de prueba para integración"
        excel_case.instrucciones_browser_use = "Caso de prueba automatizado"
        
        # Guardar caso
        case_id = db_integration.save_excel_test_case(excel_case)
        print(f"✅ Caso de prueba guardado con ID: {case_id}")
        
        return case_id
        
    except Exception as e:
        print(f"❌ Error guardando caso: {e}")
        return None

def test_create_bulk_execution():
    """Probar crear ejecución masiva"""
    print("\n🚀 Probando crear ejecución masiva...")
    
    try:
        from db_integration import DatabaseIntegration
        
        db_integration = DatabaseIntegration()
        
        # Crear ejecución masiva con casos ficticios
        test_case_ids = ["test-case-1", "test-case-2", "test-case-3"]
        config = {
            'headless_mode': True,
            'browser_type': 'chromium',
            'capture_screenshots': True,
            'max_timeout': 300
        }
        
        execution_id = db_integration.create_bulk_execution(
            name="Ejecución de prueba de integración",
            test_case_ids=test_case_ids,
            config=config
        )
        
        print(f"✅ Ejecución masiva creada con ID: {execution_id}")
        
        # Probar actualizar estado
        db_integration.update_bulk_execution_status(
            execution_id, 
            'running', 
            completed_cases=1, 
            failed_cases=0
        )
        print("✅ Estado de ejecución actualizado")
        
        # Obtener estado
        status = db_integration.get_execution_status(execution_id)
        if status:
            print(f"✅ Estado obtenido: {status['status']} - {status['progress_percentage']}%")
        
        return execution_id
        
    except Exception as e:
        print(f"❌ Error en ejecución masiva: {e}")
        return None

def test_get_test_cases():
    """Probar obtener casos de prueba"""
    print("\n📋 Probando obtener casos de prueba...")
    
    try:
        from db_integration import DatabaseIntegration
        
        db_integration = DatabaseIntegration()
        
        # Obtener casos de prueba
        cases = db_integration.get_test_cases(limit=10)
        print(f"✅ Obtenidos {len(cases)} casos de prueba")
        
        if cases:
            case = cases[0]
            print(f"   - Primer caso: {case['nombre']} (ID: {case['id']})")
            print(f"   - Código: {case['codigo']}")
            print(f"   - Válido: {case['es_valido']}")
        
        return len(cases)
        
    except Exception as e:
        print(f"❌ Error obteniendo casos: {e}")
        return 0

def test_flask_routes():
    """Probar que las rutas de Flask se puedan importar"""
    print("\n🌐 Probando rutas de Flask...")
    
    try:
        # Importar app para verificar que las rutas estén registradas
        import app
        
        # Verificar que las rutas existan
        routes = []
        for rule in app.app.url_map.iter_rules():
            routes.append(rule.rule)
        
        expected_routes = [
            '/database_status',
            '/database',
            '/api/test_cases',
            '/api/save_test_to_db'
        ]
        
        missing_routes = []
        for route in expected_routes:
            if route not in routes:
                missing_routes.append(route)
        
        if not missing_routes:
            print("✅ Todas las rutas de integración están registradas")
            return True
        else:
            print(f"❌ Rutas faltantes: {missing_routes}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando rutas: {e}")
        return False

def test_excel_integration():
    """Probar integración con análisis de Excel"""
    print("\n📊 Probando integración con Excel...")
    
    try:
        from excel_api_routes import DB_INTEGRATION_AVAILABLE
        
        if DB_INTEGRATION_AVAILABLE:
            print("✅ Integración de base de datos disponible en Excel API")
            return True
        else:
            print("❌ Integración de base de datos NO disponible en Excel API")
            return False
            
    except Exception as e:
        print(f"❌ Error probando Excel integration: {e}")
        return False

def print_database_stats():
    """Mostrar estadísticas de la base de datos"""
    print("\n📊 Estadísticas de Base de Datos:")
    
    try:
        from db_integration import DatabaseIntegration
        from sqlalchemy import func, text
        from db_models import Project, TestCase, TestExecution, BulkExecution
        
        db_integration = DatabaseIntegration()
        
        with db_integration.get_session() as session:
            # Contar registros en cada tabla
            projects_count = session.query(func.count(Project.id)).scalar()
            cases_count = session.query(func.count(TestCase.id)).scalar()
            executions_count = session.query(func.count(TestExecution.id)).scalar()
            bulk_executions_count = session.query(func.count(BulkExecution.id)).scalar()
            
            print(f"   📁 Proyectos: {projects_count}")
            print(f"   📋 Casos de Prueba: {cases_count}")
            print(f"   ▶️  Ejecuciones: {executions_count}")
            print(f"   🚀 Ejecuciones Masivas: {bulk_executions_count}")
            
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")

def main():
    """Función principal de pruebas"""
    print("🔬 Iniciando pruebas de integración de base de datos PostgreSQL\n")
    
    tests_results = {}
    
    # Ejecutar pruebas
    tests_results['imports'] = test_imports()
    tests_results['connection'] = test_database_connection()
    tests_results['save_case'] = test_save_test_case() is not None
    tests_results['bulk_execution'] = test_create_bulk_execution() is not None
    tests_results['get_cases'] = test_get_test_cases() > 0
    tests_results['flask_routes'] = test_flask_routes()
    tests_results['excel_integration'] = test_excel_integration()
    
    # Mostrar estadísticas
    print_database_stats()
    
    # Resumen de resultados
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    
    passed = 0
    total = len(tests_results)
    
    for test_name, result in tests_results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name.upper():20} | {status}")
        if result:
            passed += 1
    
    print("="*60)
    print(f"RESULTADO FINAL: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! La integración está funcionando correctamente.")
        return True
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 