#!/usr/bin/env python3
"""
Módulo de integración de base de datos PostgreSQL con la aplicación Flask existente.
Proporciona funciones para migrar datos existentes y mantener sincronización.
"""

import os
import sys
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

# Importar modelos de base de datos
from db_models import (
    DatabaseManager, Project, TestSuite, TestCase, BulkExecution, 
    TestExecution, Screenshot, ExecutionLog, ExecutionMetrics, Configuration
)

# Importar clases existentes del sistema
from excel_test_analyzer import TestCase as ExcelTestCase

class DatabaseIntegration:
    """Clase principal para integrar la base de datos con la aplicación Flask"""
    
    def __init__(self, config_file='config_db.env'):
        """Inicializar la integración de base de datos"""
        self.config = self._load_config(config_file)
        self.db_manager = DatabaseManager(**self.config)
        self._default_project = None
    
    def _load_config(self, config_file):
        """Cargar configuración desde archivo .env"""
        from dotenv import load_dotenv
        
        if os.path.exists(config_file):
            load_dotenv(config_file)
        elif os.path.exists('.env'):
            load_dotenv('.env')
        
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'buse_testing_db'),
            'username': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
        }
    
    @contextmanager
    def get_session(self):
        """Context manager para sesiones de base de datos"""
        session = self.db_manager.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def test_connection(self):
        """Probar conexión a la base de datos"""
        try:
            with self.get_session() as session:
                from sqlalchemy import text
                session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            print(f"Error de conexión: {e}")
            return False
    
    def get_default_project(self):
        """Obtener o crear el proyecto por defecto"""
        with self.get_session() as session:
            # Buscar proyecto por defecto existente
            project = session.query(Project).filter_by(name="Default Project").first()
            
            if not project:
                # Crear proyecto por defecto
                project = Project(
                    name="Default Project",
                    description="Proyecto por defecto para casos de prueba migrados",
                    base_url="https://example.com",
                    status="active",
                    created_by="system"
                )
                session.add(project)
                session.commit()
                session.refresh(project)  # Asegurar que el objeto esté vinculado
            
            return project
    
    def save_excel_test_case(self, excel_case: ExcelTestCase, project_id: str = None) -> str:
        """
        Guardar un caso de prueba desde Excel en la base de datos
        
        Args:
            excel_case: Caso de prueba extraído de Excel
            project_id: ID del proyecto (opcional, usa el por defecto si no se especifica)
        
        Returns:
            str: ID del caso de prueba guardado
        """
        with self.get_session() as session:
            if not project_id:
                # Buscar proyecto por defecto en esta sesión
                project = session.query(Project).filter_by(name="Default Project").first()
                if not project:
                    # Crear proyecto por defecto en esta sesión
                    project = Project(
                        name="Default Project",
                        description="Proyecto por defecto para casos de prueba migrados",
                        base_url="https://example.com",
                        status="active",
                        created_by="system"
                    )
                    session.add(project)
                    session.commit()
                    session.refresh(project)
                project_id = project.id
            
            # Crear caso de prueba en la base de datos
            test_case = TestCase(
                project_id=project_id,
                nombre=excel_case.nombre,
                codigo=excel_case.codigo,
                tipo=excel_case.tipo or 'funcional',
                prioridad=excel_case.prioridad or 'media',
                historia_usuario=excel_case.historia_usuario,
                objetivo=excel_case.objetivo,
                precondicion=excel_case.precondicion,
                pasos=excel_case.pasos,
                datos_prueba=excel_case.datos_prueba,
                resultado_esperado=excel_case.resultado_esperado,
                url_objetivo=excel_case.url_extraida,
                es_valido=excel_case.es_valido,
                problemas=excel_case.problemas or [],
                sugerencias=excel_case.sugerencias or [],
                tags=getattr(excel_case, 'tags', []),
                instrucciones_qa_pilot=excel_case.instrucciones_qa_pilot,
                instrucciones_browser_use=excel_case.instrucciones_browser_use,
                codigo_playwright=getattr(excel_case, 'codigo_playwright', None),
                status='draft',
                created_by='excel_import',
                metadata_json={
                    'source': 'excel_import',
                    'import_timestamp': datetime.now(timezone.utc).isoformat(),
                    'excel_row': getattr(excel_case, 'row_number', None)
                }
            )
            
            session.add(test_case)
            session.commit()
            
            return str(test_case.id)
    
    def create_bulk_execution(self, name: str, test_case_ids: List[str], 
                            config: Dict[str, Any] = None) -> str:
        """
        Crear una nueva ejecución masiva
        
        Args:
            name: Nombre de la ejecución
            test_case_ids: Lista de IDs de casos de prueba
            config: Configuración de ejecución
        
        Returns:
            str: ID de la ejecución masiva
        """
        with self.get_session() as session:
            # Buscar proyecto por defecto en esta sesión
            project = session.query(Project).filter_by(name="Default Project").first()
            if not project:
                # Crear proyecto por defecto en esta sesión
                project = Project(
                    name="Default Project",
                    description="Proyecto por defecto para casos de prueba migrados",
                    base_url="https://example.com",
                    status="active",
                    created_by="system"
                )
                session.add(project)
                session.commit()
                session.refresh(project)
            
            # Configuración por defecto
            default_config = {
                'headless_mode': True,
                'browser_type': 'chromium',
                'capture_screenshots': True,
                'max_timeout': 300,
                'execution_mode': 'sequential'
            }
            
            if config:
                default_config.update(config)
            
            bulk_execution = BulkExecution(
                project_id=project.id,
                name=name,
                description=f"Ejecución masiva de {len(test_case_ids)} casos",
                execution_mode=default_config['execution_mode'],
                headless_mode=default_config['headless_mode'],
                browser_type=default_config['browser_type'],
                capture_screenshots=default_config['capture_screenshots'],
                max_timeout=default_config['max_timeout'],
                total_cases=len(test_case_ids),
                status='queued',
                created_by='system',
                metadata_json={
                    'test_case_ids': test_case_ids,
                    'config': default_config
                }
            )
            
            session.add(bulk_execution)
            session.commit()
            
            return str(bulk_execution.id)
    
    def create_bulk_execution(self, bulk_data: Dict[str, Any]) -> str:
        """
        Crear una nueva ejecución masiva (versión actualizada)
        
        Args:
            bulk_data: Diccionario con datos de la ejecución masiva
        
        Returns:
            str: ID de la ejecución masiva
        """
        with self.get_session() as session:
            # Obtener proyecto
            project_id = bulk_data.get('project_id')
            if not project_id:
                project = session.query(Project).filter_by(name="Default Project").first()
                if not project:
                    project = Project(
                        name="Default Project",
                        description="Proyecto por defecto para casos de prueba",
                        base_url="https://example.com",
                        status="active",
                        created_by="system"
                    )
                    session.add(project)
                    session.commit()
                    session.refresh(project)
                project_id = project.id
            
            bulk_execution = BulkExecution(
                project_id=project_id,
                suite_id=bulk_data.get('suite_id'),
                name=bulk_data.get('name', 'Ejecución Masiva'),
                description=bulk_data.get('description', ''),
                execution_mode=bulk_data.get('execution_mode', 'sequential'),
                headless_mode=bulk_data.get('headless_mode', True),
                browser_type=bulk_data.get('browser_type', 'chromium'),
                capture_screenshots=bulk_data.get('capture_screenshots', True),
                max_timeout=bulk_data.get('max_timeout', 300),
                show_browser=bulk_data.get('show_browser', False),
                total_cases=bulk_data.get('total_cases', 0),
                status=bulk_data.get('status', 'queued'),
                created_by=bulk_data.get('created_by', 'system'),
                metadata_json=bulk_data.get('metadata_json', {})
            )
            
            session.add(bulk_execution)
            session.commit()
            
            return str(bulk_execution.id)
    
    def save_test_execution(self, test_case_id: str, execution_data: Dict[str, Any], 
                          bulk_execution_id: str = None) -> str:
        """
        Guardar resultado de ejecución de un caso de prueba
        
        Args:
            test_case_id: ID del caso de prueba
            execution_data: Datos de la ejecución
            bulk_execution_id: ID de ejecución masiva (opcional)
        
        Returns:
            str: ID de la ejecución guardada
        """
        with self.get_session() as session:
            # Buscar proyecto por defecto en esta sesión
            project = session.query(Project).filter_by(name="Default Project").first()
            if not project:
                # Crear proyecto por defecto en esta sesión
                project = Project(
                    name="Default Project",
                    description="Proyecto por defecto para casos de prueba migrados",
                    base_url="https://example.com",
                    status="active",
                    created_by="system"
                )
                session.add(project)
                session.commit()
                session.refresh(project)
            
            execution = TestExecution(
                test_case_id=test_case_id,
                project_id=project.id,
                bulk_execution_id=bulk_execution_id,
                execution_type=execution_data.get('execution_type', 'automated'),
                status=execution_data.get('status', 'pending'),
                result_details=execution_data.get('result_details'),
                error_message=execution_data.get('error_message'),
                stack_trace=execution_data.get('stack_trace'),
                start_time=execution_data.get('start_time', datetime.now(timezone.utc)),
                end_time=execution_data.get('end_time'),
                duration_seconds=execution_data.get('duration_seconds'),
                steps_executed=execution_data.get('steps_executed', 0),
                steps_total=execution_data.get('steps_total', 0),
                script_path=execution_data.get('script_path'),
                script_hash=execution_data.get('script_hash'),
                return_code=execution_data.get('return_code'),
                stdout_log=execution_data.get('stdout_log'),
                stderr_log=execution_data.get('stderr_log'),
                url_executed=execution_data.get('url_executed'),
                browser_config=execution_data.get('browser_config', {}),
                environment=execution_data.get('environment', 'test'),
                executed_by=execution_data.get('executed_by', 'system'),
                metadata_json=execution_data.get('metadata', {})
            )
            
            session.add(execution)
            session.commit()
            
            return str(execution.id)
    
    def save_screenshot(self, execution_id: str, screenshot_data: Dict[str, Any]) -> str:
        """
        Guardar información de una captura de pantalla
        
        Args:
            execution_id: ID de la ejecución
            screenshot_data: Datos de la captura
        
        Returns:
            str: ID de la captura guardada
        """
        with self.get_session() as session:
            screenshot = Screenshot(
                execution_id=execution_id,
                test_case_id=screenshot_data.get('test_case_id'),
                name=screenshot_data.get('name', 'screenshot'),
                description=screenshot_data.get('description'),
                step_number=screenshot_data.get('step_number'),
                screenshot_type=screenshot_data.get('screenshot_type', 'step'),
                file_path=screenshot_data.get('file_path'),
                file_name=screenshot_data.get('file_name'),
                file_size_bytes=screenshot_data.get('file_size_bytes'),
                file_format=screenshot_data.get('file_format', 'png'),
                file_hash=screenshot_data.get('file_hash'),
                width=screenshot_data.get('width'),
                height=screenshot_data.get('height'),
                is_full_page=screenshot_data.get('is_full_page', False),
                url_captured=screenshot_data.get('url_captured'),
                selector_captured=screenshot_data.get('selector_captured'),
                timestamp_ms=screenshot_data.get('timestamp_ms'),
                base64_data=screenshot_data.get('base64_data'),
                is_valid=screenshot_data.get('is_valid', True),
                processing_status=screenshot_data.get('processing_status', 'processed'),
                metadata_json=screenshot_data.get('metadata', {})
            )
            
            session.add(screenshot)
            session.commit()
            
            return str(screenshot.id)
    
    def get_test_cases(self, project_id: str = None, status: str = None, 
                      limit: int = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Obtener casos de prueba de la base de datos
        
        Args:
            project_id: Filtrar por proyecto
            status: Filtrar por estado
            limit: Límite de resultados
            offset: Offset para paginación
        
        Returns:
            Lista de casos de prueba
        """
        with self.get_session() as session:
            query = session.query(TestCase)
            
            if project_id:
                query = query.filter(TestCase.project_id == project_id)
            
            if status:
                query = query.filter(TestCase.status == status)
            
            if offset:
                query = query.offset(offset)
            
            if limit:
                query = query.limit(limit)
            
            cases = query.all()
            
            return [
                {
                    'id': str(case.id),
                    'nombre': case.nombre,
                    'codigo': case.codigo,
                    'tipo': case.tipo,
                    'prioridad': case.prioridad,
                    'objetivo': case.objetivo,
                    'pasos': case.pasos,
                    'resultado_esperado': case.resultado_esperado,
                    'url_objetivo': case.url_objetivo,
                    'status': case.status,
                    'es_valido': case.es_valido,
                    'created_at': case.created_at.isoformat() if case.created_at else None,
                    'instrucciones_browser_use': case.instrucciones_browser_use,
                    'instrucciones_qa_pilot': case.instrucciones_qa_pilot
                }
                for case in cases
            ]
    
    def update_bulk_execution(self, bulk_execution_id: str, updates: Dict[str, Any]):
        """
        Actualizar una ejecución masiva
        
        Args:
            bulk_execution_id: ID de la ejecución masiva
            updates: Diccionario con actualizaciones
        """
        with self.get_session() as session:
            bulk_execution = session.query(BulkExecution).filter_by(id=bulk_execution_id).first()
            
            if bulk_execution:
                for field, value in updates.items():
                    if hasattr(bulk_execution, field):
                        setattr(bulk_execution, field, value)
                
                # Calcular progreso si es necesario
                if bulk_execution.total_cases > 0 and 'completed_cases' in updates:
                    bulk_execution.progress_percentage = (
                        bulk_execution.completed_cases / bulk_execution.total_cases * 100
                    )
                
                # Actualizar tiempos automáticamente
                if updates.get('status') == 'running' and not bulk_execution.started_at:
                    bulk_execution.started_at = datetime.now(timezone.utc)
                elif updates.get('status') in ['completed', 'failed'] and not bulk_execution.finished_at:
                    bulk_execution.finished_at = datetime.now(timezone.utc)
                    
                    if bulk_execution.started_at:
                        duration = bulk_execution.finished_at - bulk_execution.started_at
                        bulk_execution.actual_duration = int(duration.total_seconds())
                
                session.commit()
    
    def update_bulk_execution_status(self, bulk_execution_id: str, 
                                   status: str, completed_cases: int = None,
                                   failed_cases: int = None, error_summary: str = None):
        """
        Actualizar el estado de una ejecución masiva
        
        Args:
            bulk_execution_id: ID de la ejecución masiva
            status: Nuevo estado
            completed_cases: Número de casos completados
            failed_cases: Número de casos fallidos
            error_summary: Resumen de errores
        """
        with self.get_session() as session:
            bulk_execution = session.query(BulkExecution).filter_by(id=bulk_execution_id).first()
            
            if bulk_execution:
                bulk_execution.status = status
                
                if completed_cases is not None:
                    bulk_execution.completed_cases = completed_cases
                
                if failed_cases is not None:
                    bulk_execution.failed_cases = failed_cases
                
                if error_summary:
                    bulk_execution.error_summary = error_summary
                
                # Calcular progreso
                if bulk_execution.total_cases > 0:
                    bulk_execution.progress_percentage = (
                        bulk_execution.completed_cases / bulk_execution.total_cases * 100
                    )
                
                # Actualizar tiempos
                if status == 'running' and not bulk_execution.started_at:
                    bulk_execution.started_at = datetime.now(timezone.utc)
                elif status in ['completed', 'failed'] and not bulk_execution.finished_at:
                    bulk_execution.finished_at = datetime.now(timezone.utc)
                    
                    if bulk_execution.started_at:
                        duration = bulk_execution.finished_at - bulk_execution.started_at
                        bulk_execution.actual_duration = int(duration.total_seconds())
                
                session.commit()
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener estado de una ejecución masiva
        
        Args:
            execution_id: ID de la ejecución
        
        Returns:
            Datos de la ejecución o None si no existe
        """
        with self.get_session() as session:
            execution = session.query(BulkExecution).filter_by(id=execution_id).first()
            
            if not execution:
                return None
            
            return {
                'id': str(execution.id),
                'name': execution.name,
                'status': execution.status,
                'total_cases': execution.total_cases,
                'completed_cases': execution.completed_cases,
                'failed_cases': execution.failed_cases,
                'skipped_cases': execution.skipped_cases,
                'progress_percentage': float(execution.progress_percentage or 0),
                'started_at': execution.started_at.isoformat() if execution.started_at else None,
                'finished_at': execution.finished_at.isoformat() if execution.finished_at else None,
                'actual_duration': execution.actual_duration,
                'error_summary': execution.error_summary,
                'metadata': execution.metadata_json or {}
            }
    
    # ===============================================================
    # MÉTODOS PARA GESTIÓN DE TEST SUITES
    # ===============================================================
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Obtener todos los proyectos"""
        with self.get_session() as session:
            projects = session.query(Project).filter_by(status='active').all()
            
            result = []
            for project in projects:
                result.append({
                    'id': str(project.id),
                    'name': project.name,
                    'description': project.description,
                    'base_url': project.base_url,
                    'status': project.status,
                    'created_at': project.created_at,
                    'created_by': project.created_by
                })
            
            return result
    
    def create_project(self, project_data: Dict[str, Any]) -> str:
        """Crear un nuevo proyecto"""
        with self.get_session() as session:
            project = Project(
                name=project_data['name'],
                description=project_data.get('description', ''),
                base_url=project_data.get('base_url', ''),
                status=project_data.get('status', 'active'),
                created_by=project_data.get('created_by', 'system'),
                metadata_json=project_data.get('metadata_json', {})
            )
            
            session.add(project)
            session.commit()
            
            return str(project.id)
    
    def get_test_suites(self, project_id: str = None) -> List[Dict[str, Any]]:
        """Obtener suites de prueba con información de casos"""
        with self.get_session() as session:
            from sqlalchemy import func
            
            # Query base para suites con conteo de casos
            query = session.query(
                TestSuite,
                Project.name.label('project_name'),
                func.count(TestCase.id).label('test_cases_count')
            ).join(
                Project, TestSuite.project_id == Project.id
            ).outerjoin(
                TestCase, TestSuite.id == TestCase.suite_id
            ).group_by(TestSuite.id, Project.name)
            
            if project_id:
                query = query.filter(TestSuite.project_id == project_id)
            
            results = query.all()
            
            suites = []
            for suite, project_name, test_cases_count in results:
                suites.append({
                    'id': str(suite.id),
                    'name': suite.name,
                    'description': suite.description,
                    'project_id': str(suite.project_id),
                    'project_name': project_name,
                    'status': suite.status,
                    'created_at': suite.created_at,
                    'updated_at': suite.updated_at,
                    'created_by': suite.created_by,
                    'test_cases_count': test_cases_count or 0,
                    'metadata': suite.metadata_json
                })
            
            return suites
    
    def get_test_suite_details(self, suite_id: str) -> Dict[str, Any]:
        """Obtener detalles completos de una suite específica"""
        with self.get_session() as session:
            from sqlalchemy import func
            
            # Obtener la suite con información del proyecto
            suite_query = session.query(
                TestSuite,
                Project.name.label('project_name')
            ).join(
                Project, TestSuite.project_id == Project.id
            ).filter(TestSuite.id == suite_id).first()
            
            if not suite_query:
                return None
            
            suite, project_name = suite_query
            
            # Obtener casos de prueba asociados
            test_cases = session.query(TestCase).filter_by(suite_id=suite_id).all()
            
            # Formatear casos de prueba
            cases_data = []
            for case in test_cases:
                cases_data.append({
                    'id': str(case.id),
                    'nombre': case.nombre,
                    'codigo': case.codigo,
                    'tipo': case.tipo,
                    'prioridad': case.prioridad,
                    'objetivo': case.objetivo,
                    'pasos': case.pasos,
                    'resultado_esperado': case.resultado_esperado,
                    'url_objetivo': case.url_objetivo,
                    'status': case.status,
                    'es_valido': case.es_valido,
                    'created_at': case.created_at.isoformat() if case.created_at else None,
                    'metadata': case.metadata_json
                })
            
            # Obtener estadísticas de ejecución recientes
            recent_executions = session.query(TestExecution).filter(
                TestExecution.test_case_id.in_([case.id for case in test_cases])
            ).order_by(TestExecution.start_time.desc()).limit(10).all()
            
            executions_data = []
            for execution in recent_executions:
                executions_data.append({
                    'id': str(execution.id),
                    'test_case_id': str(execution.test_case_id),
                    'status': execution.status,
                    'start_time': execution.start_time.isoformat() if execution.start_time else None,
                    'end_time': execution.end_time.isoformat() if execution.end_time else None,
                    'duration_seconds': execution.duration_seconds,
                    'result_details': execution.result_details,
                    'error_message': execution.error_message
                })
            
            return {
                'id': str(suite.id),
                'name': suite.name,
                'description': suite.description,
                'project_id': str(suite.project_id),
                'project_name': project_name,
                'status': suite.status,
                'created_at': suite.created_at.isoformat() if suite.created_at else None,
                'updated_at': suite.updated_at.isoformat() if suite.updated_at else None,
                'created_by': suite.created_by,
                'metadata': suite.metadata_json,
                'test_cases': cases_data,
                'recent_executions': executions_data,
                'stats': {
                    'total_cases': len(cases_data),
                    'valid_cases': len([c for c in cases_data if c.get('es_valido', True)]),
                    'recent_executions_count': len(executions_data)
                }
            }
    
    def create_test_suite(self, suite_data: Dict[str, Any]) -> str:
        """Crear una nueva suite de prueba"""
        with self.get_session() as session:
            test_suite = TestSuite(
                project_id=suite_data['project_id'],
                name=suite_data['name'],
                description=suite_data.get('description', ''),
                status=suite_data.get('status', 'active'),
                created_by=suite_data.get('created_by', 'system'),
                metadata_json=suite_data.get('metadata_json', {})
            )
            
            session.add(test_suite)
            session.commit()
            
            return str(test_suite.id)
    
    def update_test_suite(self, suite_id: str, updates: Dict[str, Any]) -> bool:
        """Actualizar una suite de prueba"""
        with self.get_session() as session:
            test_suite = session.query(TestSuite).filter_by(id=suite_id).first()
            
            if not test_suite:
                return False
            
            # Actualizar campos permitidos
            allowed_fields = ['name', 'description', 'status', 'metadata_json']
            for field, value in updates.items():
                if field in allowed_fields and hasattr(test_suite, field):
                    setattr(test_suite, field, value)
            
            # Procesar casos seleccionados (si se proporcionan)
            if 'cases' in updates and isinstance(updates['cases'], list):
                # Primero, desasociar todos los casos actuales de esta suite
                session.query(TestCase).filter_by(suite_id=suite_id).update({'suite_id': None})
                
                # Luego, asociar los casos seleccionados a esta suite
                for case_filename in updates['cases']:
                    # Buscar el caso por código (filename)
                    test_case = session.query(TestCase).filter_by(codigo=case_filename).first()
                    if test_case:
                        test_case.suite_id = suite_id
                        print(f"Asociando caso {test_case.nombre} ({test_case.codigo}) a suite {suite_id}")
                    else:
                        print(f"Advertencia: No se encontró caso con código {case_filename}")
            
            test_suite.updated_at = datetime.now(timezone.utc)
            session.commit()
            
            return True
    
    def delete_test_suite(self, suite_id: str) -> bool:
        """Eliminar una suite de prueba"""
        with self.get_session() as session:
            test_suite = session.query(TestSuite).filter_by(id=suite_id).first()
            
            if not test_suite:
                return False
            
            session.delete(test_suite)
            session.commit()
            
            return True
    
    def update_test_case(self, case_id: str, updates: Dict[str, Any]) -> bool:
        """Actualizar un caso de prueba"""
        with self.get_session() as session:
            test_case = session.query(TestCase).filter_by(id=case_id).first()
            
            if not test_case:
                return False
            
            # Actualizar campos permitidos
            allowed_fields = [
                'suite_id', 'nombre', 'codigo', 'tipo', 'prioridad', 
                'historia_usuario', 'objetivo', 'precondicion', 'pasos',
                'datos_prueba', 'resultado_esperado', 'url_objetivo',
                'es_valido', 'problemas', 'sugerencias', 'tags',
                'instrucciones_qa_pilot', 'instrucciones_browser_use',
                'codigo_playwright', 'status', 'reviewed_by', 'metadata_json'
            ]
            
            for field, value in updates.items():
                if field in allowed_fields and hasattr(test_case, field):
                    setattr(test_case, field, value)
            
            test_case.updated_at = datetime.now(timezone.utc)
            session.commit()
            
            return True
    
    def save_test_case(self, test_case_data: Dict[str, Any]) -> str:
        """Guardar un caso de prueba genérico"""
        with self.get_session() as session:
            # Obtener proyecto por defecto si no se especifica
            project_id = test_case_data.get('project_id')
            if not project_id:
                project = session.query(Project).filter_by(name="Default Project").first()
                if not project:
                    project = Project(
                        name="Default Project",
                        description="Proyecto por defecto para casos de prueba",
                        base_url="https://example.com",
                        status="active",
                        created_by="system"
                    )
                    session.add(project)
                    session.commit()
                    session.refresh(project)
                project_id = project.id
            
            test_case = TestCase(
                project_id=project_id,
                suite_id=test_case_data.get('suite_id'),
                nombre=test_case_data['nombre'],
                codigo=test_case_data.get('codigo'),
                tipo=test_case_data.get('tipo', 'funcional'),
                prioridad=test_case_data.get('prioridad', 'media'),
                historia_usuario=test_case_data.get('historia_usuario'),
                objetivo=test_case_data['objetivo'],
                precondicion=test_case_data.get('precondicion'),
                pasos=test_case_data['pasos'],
                datos_prueba=test_case_data.get('datos_prueba'),
                resultado_esperado=test_case_data['resultado_esperado'],
                url_objetivo=test_case_data.get('url_objetivo'),
                es_valido=test_case_data.get('es_valido', True),
                problemas=test_case_data.get('problemas', []),
                sugerencias=test_case_data.get('sugerencias', []),
                tags=test_case_data.get('tags', []),
                instrucciones_qa_pilot=test_case_data.get('instrucciones_qa_pilot'),
                instrucciones_browser_use=test_case_data.get('instrucciones_browser_use'),
                codigo_playwright=test_case_data.get('codigo_playwright'),
                status=test_case_data.get('status', 'draft'),
                created_by=test_case_data.get('created_by', 'system'),
                reviewed_by=test_case_data.get('reviewed_by'),
                metadata_json=test_case_data.get('metadata_json', {})
            )
            
            session.add(test_case)
            session.commit()
            
            return str(test_case.id)
    
    def create_test_execution(self, execution_data: Dict[str, Any]) -> str:
        """Crear una nueva ejecución de prueba"""
        with self.get_session() as session:
            # Obtener información del caso de prueba
            test_case = session.query(TestCase).filter_by(id=execution_data['test_case_id']).first()
            if not test_case:
                raise ValueError(f"Test case {execution_data['test_case_id']} not found")
            
            execution = TestExecution(
                test_case_id=execution_data['test_case_id'],
                bulk_execution_id=execution_data.get('bulk_execution_id'),
                project_id=test_case.project_id,
                execution_type=execution_data.get('execution_type', 'manual'),
                status=execution_data.get('status', 'pending'),
                result_details=execution_data.get('result_details'),
                error_message=execution_data.get('error_message'),
                url_executed=execution_data.get('url_executed'),
                script_path=execution_data.get('script_path'),
                return_code=execution_data.get('return_code'),
                stdout_log=execution_data.get('stdout_log'),
                stderr_log=execution_data.get('stderr_log'),
                duration_seconds=execution_data.get('duration_seconds'),
                browser_config=execution_data.get('browser_config', {}),
                executed_by=execution_data.get('executed_by', 'system'),
                metadata_json=execution_data.get('metadata_json', {})
            )
            
            session.add(execution)
            session.commit()
            
            return str(execution.id)
    
    def get_test_cases(self, project_id: str = None, suite_id: str = None, 
                      status: str = None, limit: int = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Obtener casos de prueba de la base de datos (método actualizado)
        
        Args:
            project_id: Filtrar por proyecto
            suite_id: Filtrar por suite
            status: Filtrar por estado
            limit: Límite de resultados
            offset: Offset para paginación
        
        Returns:
            Lista de casos de prueba
        """
        with self.get_session() as session:
            query = session.query(TestCase)
            
            if project_id:
                query = query.filter(TestCase.project_id == project_id)
            
            if suite_id:
                query = query.filter(TestCase.suite_id == suite_id)
            
            if status:
                query = query.filter(TestCase.status == status)
            
            if offset:
                query = query.offset(offset)
            
            if limit:
                query = query.limit(limit)
            
            cases = query.all()
            
            return [
                {
                    'id': str(case.id),
                    'suite_id': str(case.suite_id) if case.suite_id else None,
                    'project_id': str(case.project_id),
                    'nombre': case.nombre,
                    'codigo': case.codigo,
                    'tipo': case.tipo,
                    'prioridad': case.prioridad,
                    'objetivo': case.objetivo,
                    'pasos': case.pasos,
                    'resultado_esperado': case.resultado_esperado,
                    'url_objetivo': case.url_objetivo,
                    'status': case.status,
                    'es_valido': case.es_valido,
                    'created_at': case.created_at,
                    'instrucciones_browser_use': case.instrucciones_browser_use,
                    'instrucciones_qa_pilot': case.instrucciones_qa_pilot
                }
                for case in cases
            ]
    
    def is_connected(self) -> bool:
        """Verificar si la conexión a la base de datos está activa"""
        return self.test_connection()
    
    def get_orphaned_test_cases(self) -> List[Dict[str, Any]]:
        """Obtener casos de prueba sin suite asociada que fueron guardados desde historial"""
        with self.get_session() as session:
            from db_models import TestCase
            import json
            
            # Buscar casos donde suite_id es NULL y fueron creados desde historial
            orphaned_cases = session.query(TestCase).filter(TestCase.suite_id.is_(None)).all()
            
            # Filtrar solo casos guardados desde historial
            filtered_cases = []
            for case in orphaned_cases:
                # Verificar si el caso fue creado desde historial
                is_saved_case = False
                
                # Opción 1: Verificar metadatos JSON
                if case.metadata_json:
                    try:
                        metadata = json.loads(case.metadata_json) if isinstance(case.metadata_json, str) else case.metadata_json
                        if metadata.get('created_from_history', False):
                            is_saved_case = True
                    except (json.JSONDecodeError, TypeError):
                        pass
                
                # Opción 2: Verificar created_by específico
                if case.created_by in ['qa_pilot_web', 'history_save']:
                    is_saved_case = True
                
                # Opción 3: Verificar si tiene instrucciones de QA Pilot (indicativo de caso guardado)
                if case.instrucciones_qa_pilot and case.instrucciones_qa_pilot.strip():
                    is_saved_case = True
                
                if is_saved_case:
                    filtered_cases.append(case)
            
            return [
                {
                    'id': str(case.id),
                    'nombre': case.nombre,
                    'codigo': case.codigo,
                    'tipo': case.tipo,
                    'prioridad': case.prioridad,
                    'objetivo': case.objetivo,
                    'pasos': case.pasos,
                    'url_objetivo': case.url_objetivo,
                    'status': case.status,
                    'es_valido': case.es_valido,
                    'created_at': case.created_at.isoformat() if case.created_at else None,
                    'created_by': case.created_by,
                    'instrucciones_qa_pilot': case.instrucciones_qa_pilot
                }
                for case in filtered_cases
            ]
    
    def delete_test_case(self, case_id: str) -> bool:
        """Eliminar un caso de prueba por ID"""
        with self.get_session() as session:
            from sqlalchemy import text
            
            # Usar SQL directo para evitar cargar relaciones que pueden referenciar tablas inexistentes
            
            # 1. Verificar que el caso existe
            result = session.execute(
                text("SELECT id FROM testing.test_cases WHERE id = :case_id"),
                {"case_id": case_id}
            ).fetchone()
            
            if not result:
                return False
            
            # 2. Eliminar registros relacionados con SQL directo
            
            # Eliminar screenshots si la tabla existe
            try:
                session.execute(
                    text("DELETE FROM evidence.screenshots WHERE test_case_id = :case_id"),
                    {"case_id": case_id}
                )
            except Exception as e:
                print(f"Warning: No se pudieron eliminar screenshots: {e}")
            
            # Eliminar ejecuciones si la tabla existe
            try:
                session.execute(
                    text("DELETE FROM testing.test_executions WHERE test_case_id = :case_id"),
                    {"case_id": case_id}
                )
            except Exception as e:
                print(f"Warning: No se pudieron eliminar ejecuciones: {e}")
            
            # Eliminar execution metrics si la tabla existe
            try:
                session.execute(
                    text("DELETE FROM analytics.execution_metrics WHERE test_case_id = :case_id"),
                    {"case_id": case_id}
                )
            except Exception as e:
                print(f"Warning: No se pudieron eliminar metrics: {e}")
            
            # 3. Finalmente eliminar el caso de prueba
            session.execute(
                text("DELETE FROM testing.test_cases WHERE id = :case_id"),
                {"case_id": case_id}
            )
            
            session.commit()
            return True
    
    def bulk_delete_test_cases(self, case_ids: List[str]) -> int:
        """Eliminar múltiples casos de prueba"""
        with self.get_session() as session:
            from sqlalchemy import text
            from uuid import UUID
            
            # Convertir case_ids a UUIDs válidos
            valid_case_ids = []
            for case_id in case_ids:
                try:
                    UUID(case_id)  # Validar formato UUID
                    valid_case_ids.append(case_id)
                except ValueError:
                    print(f"WARNING: ID inválido ignorado: {case_id}")
                    continue
            
            if not valid_case_ids:
                return 0
            
            # Construir lista de parámetros para SQL
            case_ids_str = "','".join(valid_case_ids)
            case_ids_list = f"'{case_ids_str}'"
            
            # Eliminar registros relacionados con SQL directo
            
            # 1. Eliminar screenshots relacionados
            try:
                session.execute(
                    text(f"DELETE FROM evidence.screenshots WHERE test_case_id IN ({case_ids_list})")
                )
            except Exception as e:
                print(f"Warning: No se pudieron eliminar screenshots: {e}")
            
            # 2. Eliminar ejecuciones relacionadas
            try:
                session.execute(
                    text(f"DELETE FROM testing.test_executions WHERE test_case_id IN ({case_ids_list})")
                )
            except Exception as e:
                print(f"Warning: No se pudieron eliminar ejecuciones: {e}")
            
            # 3. Eliminar execution metrics relacionados
            try:
                session.execute(
                    text(f"DELETE FROM analytics.execution_metrics WHERE test_case_id IN ({case_ids_list})")
                )
            except Exception as e:
                print(f"Warning: No se pudieron eliminar metrics: {e}")
            
            # 4. Finalmente eliminar los casos de prueba y obtener el conteo
            result = session.execute(
                text(f"DELETE FROM testing.test_cases WHERE id IN ({case_ids_list})")
            )
            
            session.commit()
            return result.rowcount

    def get_executions_by_date(self, date) -> List[Dict[str, Any]]:
        """Obtener ejecuciones de prueba por fecha específica"""
        with self.get_session() as session:
            from db_models import TestExecution
            from sqlalchemy import func, cast, Date
            
            executions = session.query(TestExecution).filter(
                cast(TestExecution.start_time, Date) == date
            ).all()
            
            return [
                {
                    'id': str(execution.id),
                    'test_case_id': str(execution.test_case_id),
                    'status': execution.status,
                    'start_time': execution.start_time.isoformat() if execution.start_time else None,
                    'end_time': execution.end_time.isoformat() if execution.end_time else None,
                    'duration_seconds': execution.duration_seconds,
                    'result_details': execution.result_details,
                    'error_message': execution.error_message
                }
                for execution in executions
            ]
    
    def get_recent_executions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Obtener ejecuciones recientes"""
        with self.get_session() as session:
            from db_models import TestExecution
            
            executions = session.query(TestExecution).order_by(
                TestExecution.start_time.desc()
            ).limit(limit).all()
            
            return [
                {
                    'id': str(execution.id),
                    'test_case_id': str(execution.test_case_id),
                    'status': execution.status,
                    'start_time': execution.start_time.isoformat() if execution.start_time else None,
                    'end_time': execution.end_time.isoformat() if execution.end_time else None,
                    'duration_seconds': execution.duration_seconds,
                    'result_details': execution.result_details,
                    'error_message': execution.error_message,
                    'execution_type': execution.execution_type,
                    'executed_by': execution.executed_by
                }
                for execution in executions
            ]
    
    def get_execution_stats_by_hour(self, days: int = 1) -> Dict[str, Any]:
        """Obtener estadísticas de ejecución por hora para el gráfico"""
        with self.get_session() as session:
            from db_models import TestExecution
            from sqlalchemy import func, text
            from datetime import datetime, timedelta
            
            # Calcular fecha de inicio
            start_date = datetime.now() - timedelta(days=days)
            
            # Obtener estadísticas por hora
            hourly_stats = session.execute(text("""
                SELECT 
                    EXTRACT(hour FROM start_time) as hour,
                    COUNT(*) as executions_count
                FROM testing.test_executions 
                WHERE start_time >= :start_date
                GROUP BY EXTRACT(hour FROM start_time)
                ORDER BY hour
            """), {"start_date": start_date}).fetchall()
            
            # Preparar datos para el gráfico
            labels = [f"{i:02d}:00" for i in range(0, 24, 4)]  # Cada 4 horas
            data_points = [0] * 6  # 6 intervalos de 4 horas
            
            for hour, count in hourly_stats:
                interval_index = int(hour) // 4
                if interval_index < 6:
                    data_points[interval_index] += count
            
            return {
                'labels': labels,
                'openai': [0] * 6,  # Sin datos específicos de IA por ahora
                'anthropic': [0] * 6,  # Sin datos específicos de IA por ahora
                'gemini': [0] * 6,  # Sin datos específicos de IA por ahora
                'system_executions': data_points  # Ejecuciones del sistema
            }

# Instancia global de integración de base de datos
db_integration = None

def get_db_integration():
    """Obtener instancia de integración de base de datos"""
    global db_integration
    if db_integration is None:
        db_integration = DatabaseIntegration()
    return db_integration

def init_db_integration(app=None):
    """Inicializar integración de base de datos para Flask"""
    global db_integration
    db_integration = DatabaseIntegration()
    
    if app:
        # Agregar instancia a la configuración de Flask
        app.config['DB_INTEGRATION'] = db_integration
        
        # Probar conexión al inicializar
        if db_integration.test_connection():
            print("✅ Conexión a base de datos PostgreSQL establecida")
        else:
            print("❌ Error al conectar con base de datos PostgreSQL")
    
    return db_integration 