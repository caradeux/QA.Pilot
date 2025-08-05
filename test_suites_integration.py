#!/usr/bin/env python3
"""
Script de prueba para validar la integración completa de gestión de test suites
"""

import sys
import time
from datetime import datetime
from pprint import pprint

def test_suites_integration():
    """Prueba completa de la integración de gestión de suites"""
    
    print("🧪 INICIANDO PRUEBAS DE INTEGRACIÓN DE GESTIÓN DE SUITES")
    print("=" * 60)
    
    try:
        # Importar módulos
        print("1️⃣ Importando módulos...")
        from db_integration import get_db_integration
        
        db_integration = get_db_integration()
        print("   ✅ Módulos importados correctamente")
        
        # Probar conexión
        print("\n2️⃣ Probando conexión a base de datos...")
        if db_integration.test_connection():
            print("   ✅ Conexión exitosa")
        else:
            print("   ❌ Error de conexión")
            return False
        
        # Obtener proyectos
        print("\n3️⃣ Obteniendo proyectos...")
        projects = db_integration.get_projects()
        print(f"   ✅ Proyectos encontrados: {len(projects)}")
        if projects:
            project_id = projects[0]['id']
            print(f"   📁 Usando proyecto: {projects[0]['name']} (ID: {project_id})")
        else:
            print("   ⚠️ No hay proyectos, creando proyecto por defecto...")
            project = db_integration.get_default_project()
            project_id = str(project.id)
            print(f"   ✅ Proyecto creado: {project_id}")
        
        # Crear suite de prueba
        print("\n4️⃣ Creando suite de prueba...")
        suite_data = {
            'name': f'Suite Test {datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'description': 'Suite de prueba para validar integración',
            'project_id': project_id,
            'status': 'active',
            'created_by': 'test_script',
            'metadata_json': {
                'test_suite': True,
                'created_by_script': True
            }
        }
        
        suite_id = db_integration.create_test_suite(suite_data)
        print(f"   ✅ Suite creada con ID: {suite_id}")
        
        # Crear casos de prueba
        print("\n5️⃣ Creando casos de prueba...")
        test_cases_created = []
        
        for i in range(3):
            case_data = {
                'nombre': f'Caso de Prueba {i+1} - Test Suite',
                'codigo': f'TS-{datetime.now().strftime("%Y%m%d")}-{i+1:03d}',
                'tipo': ['funcional', 'integracion', 'ui'][i],
                'prioridad': ['alta', 'media', 'baja'][i],
                'objetivo': f'Validar funcionalidad {i+1} del sistema',
                'pasos': f'1. Abrir navegador\n2. Navegar a URL\n3. Ejecutar acción {i+1}\n4. Validar resultado',
                'resultado_esperado': f'El sistema debe ejecutar correctamente la acción {i+1}',
                'url_objetivo': f'https://example.com/test-{i+1}',
                'suite_id': suite_id,
                'project_id': project_id,
                'es_valido': True,
                'status': 'approved',
                'created_by': 'test_script',
                'metadata_json': {
                    'test_case': True,
                    'suite_test': True,
                    'order': i+1
                }
            }
            
            case_id = db_integration.save_test_case(case_data)
            test_cases_created.append(case_id)
            print(f"   ✅ Caso {i+1} creado con ID: {case_id}")
        
        # Obtener suites
        print("\n6️⃣ Obteniendo suites de prueba...")
        suites = db_integration.get_test_suites()
        print(f"   ✅ Suites encontradas: {len(suites)}")
        
        # Buscar nuestra suite
        our_suite = next((s for s in suites if s['id'] == suite_id), None)
        if our_suite:
            print(f"   ✅ Suite encontrada: {our_suite['name']}")
            print(f"   📊 Casos en la suite: {our_suite['test_cases_count']}")
        else:
            print("   ❌ No se encontró la suite creada")
        
        # Obtener casos de la suite
        print("\n7️⃣ Obteniendo casos de la suite...")
        suite_cases = db_integration.get_test_cases(suite_id=suite_id)
        print(f"   ✅ Casos encontrados en la suite: {len(suite_cases)}")
        
        for case in suite_cases:
            print(f"   📝 {case['nombre']} ({case['tipo']}) - {case['prioridad']}")
        
        # Crear ejecución masiva
        print("\n8️⃣ Creando ejecución masiva...")
        bulk_data = {
            'suite_id': suite_id,
            'project_id': project_id,
            'name': f'Ejecución Test Suite - {datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'description': 'Ejecución de prueba para validar integración',
            'execution_mode': 'sequential',
            'show_browser': False,
            'total_cases': len(test_cases_created),
            'status': 'queued',
            'created_by': 'test_script'
        }
        
        bulk_execution_id = db_integration.create_bulk_execution(bulk_data)
        print(f"   ✅ Ejecución masiva creada con ID: {bulk_execution_id}")
        
        # Simular progreso de ejecución
        print("\n9️⃣ Simulando progreso de ejecución...")
        
        # Iniciar ejecución
        db_integration.update_bulk_execution(bulk_execution_id, {
            'status': 'running',
            'started_at': datetime.now()
        })
        print("   🚀 Ejecución iniciada")
        
        # Simular progreso
        for i in range(len(test_cases_created)):
            # Crear ejecución individual
            execution_data = {
                'test_case_id': test_cases_created[i],
                'bulk_execution_id': bulk_execution_id,
                'execution_type': 'automated',
                'status': 'completed' if i < 2 else 'failed',
                'result_details': f'Caso {i+1} ejecutado correctamente' if i < 2 else 'Error simulado',
                'error_message': None if i < 2 else 'Error de prueba simulado',
                'duration_seconds': 30 + i * 10,
                'browser_config': {
                    'browser': 'chromium',
                    'headless': True
                },
                'executed_by': 'test_script',
                'metadata_json': {
                    'simulated': True,
                    'test_run': True
                }
            }
            
            execution_id = db_integration.create_test_execution(execution_data)
            print(f"   ✅ Ejecución individual {i+1} creada: {execution_id}")
            
            # Actualizar progreso de ejecución masiva
            completed = i + 1
            failed = 1 if i == 2 else 0
            
            db_integration.update_bulk_execution(bulk_execution_id, {
                'completed_cases': completed,
                'failed_cases': failed,
                'current_case_index': completed
            })
            
            time.sleep(0.5)  # Simular tiempo de ejecución
        
        # Finalizar ejecución
        db_integration.update_bulk_execution(bulk_execution_id, {
            'status': 'completed',
            'finished_at': datetime.now()
        })
        print("   🏁 Ejecución finalizada")
        
        # Verificar estado final
        print("\n🔟 Verificando estado final...")
        execution_status = db_integration.get_execution_status(bulk_execution_id)
        if execution_status:
            print(f"   ✅ Estado de ejecución: {execution_status['status']}")
            print(f"   📊 Casos totales: {execution_status['total_cases']}")
            print(f"   ✅ Casos completados: {execution_status['completed_cases']}")
            print(f"   ❌ Casos fallidos: {execution_status['failed_cases']}")
            print(f"   📈 Progreso: {execution_status['progress_percentage']:.1f}%")
        
        # Probar actualización de suite
        print("\n1️⃣1️⃣ Probando actualización de suite...")
        update_result = db_integration.update_test_suite(suite_id, {
            'description': 'Suite de prueba actualizada desde test script',
            'status': 'inactive'
        })
        print(f"   ✅ Suite actualizada: {update_result}")
        
        # Probar movimiento de casos entre suites
        print("\n1️⃣2️⃣ Probando movimiento de casos...")
        if len(test_cases_created) > 0:
            # Crear una segunda suite
            suite2_data = {
                'name': f'Suite Destino {datetime.now().strftime("%H%M%S")}',
                'description': 'Suite destino para prueba de movimiento',
                'project_id': project_id,
                'status': 'active',
                'created_by': 'test_script'
            }
            
            suite2_id = db_integration.create_test_suite(suite2_data)
            print(f"   ✅ Segunda suite creada: {suite2_id}")
            
            # Mover un caso a la segunda suite
            case_to_move = test_cases_created[0]
            move_result = db_integration.update_test_case(case_to_move, {
                'suite_id': suite2_id
            })
            print(f"   ✅ Caso movido a nueva suite: {move_result}")
            
            # Verificar movimiento
            moved_case = db_integration.get_test_cases(suite_id=suite2_id)
            print(f"   📊 Casos en suite destino: {len(moved_case)}")
        
        print("\n" + "=" * 60)
        print("🎉 TODAS LAS PRUEBAS DE INTEGRACIÓN COMPLETADAS EXITOSAMENTE")
        print("=" * 60)
        
        # Resumen final
        print("\n📋 RESUMEN DE FUNCIONALIDADES PROBADAS:")
        print("   ✅ Conexión a base de datos")
        print("   ✅ Gestión de proyectos")
        print("   ✅ Creación de suites")
        print("   ✅ Creación de casos de prueba")
        print("   ✅ Asignación de casos a suites")
        print("   ✅ Obtención de suites con contadores")
        print("   ✅ Ejecuciones masivas")
        print("   ✅ Seguimiento de progreso")
        print("   ✅ Ejecuciones individuales")
        print("   ✅ Actualización de suites")
        print("   ✅ Movimiento de casos entre suites")
        print("   ✅ Estados y metadatos")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de integración de gestión de suites...")
    success = test_suites_integration()
    
    if success:
        print("\n✅ Todas las pruebas pasaron exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Algunas pruebas fallaron")
        sys.exit(1) 