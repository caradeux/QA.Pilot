"""
Modelos de Base de Datos para el Sistema de Testing Automatizado
================================================================
Este archivo contiene todas las clases modelo de SQLAlchemy que 
corresponden a las tablas de PostgreSQL definidas en db_complete_setup.sql
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4
from sqlalchemy import (
    Column, String, Text, Integer, Boolean, DateTime, 
    ForeignKey, DECIMAL, BIGINT, ARRAY, JSON, CheckConstraint,
    UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from sqlalchemy import create_engine

Base = declarative_base()

# ===============================================================
# MODELOS DE TABLAS PRINCIPALES
# ===============================================================

class Project(Base):
    """Modelo para la tabla testing.projects"""
    __tablename__ = 'projects'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    base_url = Column(String(500))
    status = Column(String(50), default='active')
    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), default=func.current_timestamp(), onupdate=func.current_timestamp())
    created_by = Column(String(100))
    metadata_json = Column('metadata', JSONB, default={})
    
    # Relationships
    test_suites = relationship("TestSuite", back_populates="project", cascade="all, delete-orphan")
    test_cases = relationship("TestCase", back_populates="project", cascade="all, delete-orphan")
    bulk_executions = relationship("BulkExecution", back_populates="project", cascade="all, delete-orphan")
    test_executions = relationship("TestExecution", back_populates="project", cascade="all, delete-orphan")
    # Comentado temporalmente hasta que se cree la tabla analytics.execution_metrics
    # execution_metrics = relationship("ExecutionMetrics", back_populates="project", cascade="all, delete-orphan")
    
    # Constraints - Combined with schema
    __table_args__ = (
        CheckConstraint("status IN ('active', 'inactive', 'archived')", name='check_project_status'),
        {'schema': 'testing'}
    )

    def __repr__(self):
        return f"<Project(id='{self.id}', name='{self.name}', status='{self.status}')>"


class TestSuite(Base):
    """Modelo para la tabla testing.test_suites"""
    __tablename__ = 'test_suites'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('testing.projects.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default='active')
    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), default=func.current_timestamp(), onupdate=func.current_timestamp())
    created_by = Column(String(100))
    metadata_json = Column('metadata', JSONB, default={})
    
    # Relationships
    project = relationship("Project", back_populates="test_suites")
    test_cases = relationship("TestCase", back_populates="test_suite", cascade="all, delete-orphan")
    bulk_executions = relationship("BulkExecution", back_populates="test_suite")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('active', 'inactive', 'archived')", name='check_suite_status'),
        UniqueConstraint('project_id', 'name', name='unique_suite_name_per_project'),
        {'schema': 'testing'}
    )

    def __repr__(self):
        return f"<TestSuite(id='{self.id}', name='{self.name}', project_id='{self.project_id}')>"


class TestCase(Base):
    """Modelo para la tabla testing.test_cases"""
    __tablename__ = 'test_cases'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    suite_id = Column(UUID(as_uuid=True), ForeignKey('testing.test_suites.id', ondelete='SET NULL'))
    project_id = Column(UUID(as_uuid=True), ForeignKey('testing.projects.id', ondelete='CASCADE'), nullable=False)
    
    # Información básica del caso
    nombre = Column(String(255), nullable=False)
    codigo = Column(String(100), unique=True)
    tipo = Column(String(50), default='funcional')
    prioridad = Column(String(20), default='media')
    
    # Contenido del caso de prueba
    historia_usuario = Column(Text)
    objetivo = Column(Text, nullable=False)
    precondicion = Column(Text)
    pasos = Column(Text, nullable=False)
    datos_prueba = Column(Text)
    resultado_esperado = Column(Text, nullable=False)
    
    # Información técnica
    url_objetivo = Column(String(500))
    selector_elementos = Column(JSONB, default={})
    tiempo_estimado = Column(Integer)  # En segundos
    
    # Metadatos y validación
    es_valido = Column(Boolean, default=True)
    problemas = Column(ARRAY(Text))
    sugerencias = Column(ARRAY(Text))
    tags = Column(ARRAY(Text))
    
    # Instrucciones generadas
    instrucciones_qa_pilot = Column(Text)
    instrucciones_browser_use = Column(Text)
    codigo_playwright = Column(Text)
    
    # Control de versiones
    version = Column(Integer, default=1)
    version_anterior = Column(UUID(as_uuid=True), ForeignKey('testing.test_cases.id'))
    
    # Auditoría
    status = Column(String(50), default='draft')
    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), default=func.current_timestamp(), onupdate=func.current_timestamp())
    created_by = Column(String(100))
    reviewed_by = Column(String(100))
    reviewed_at = Column(DateTime(timezone=True))
    
    # Metadatos adicionales
    metadata_json = Column('metadata', JSONB, default={})
    
    # Relationships
    project = relationship("Project", back_populates="test_cases")
    test_suite = relationship("TestSuite", back_populates="test_cases")
    test_executions = relationship("TestExecution", back_populates="test_case", cascade="all, delete-orphan")
    screenshots = relationship("Screenshot", back_populates="test_case", cascade="all, delete-orphan")
    # Comentado temporalmente hasta que se cree la tabla analytics.execution_metrics
    # execution_metrics = relationship("ExecutionMetrics", back_populates="test_case", cascade="all, delete-orphan")
    
    # Self-referential relationship para versiones
    previous_version = relationship("TestCase", remote_side=[id])
    
    # Constraints
    __table_args__ = (
        CheckConstraint("tipo IN ('funcional', 'integracion', 'regresion', 'smoke', 'ui', 'api')", name='check_case_tipo'),
        CheckConstraint("prioridad IN ('alta', 'media', 'baja', 'critica')", name='check_case_prioridad'),
        CheckConstraint("status IN ('draft', 'review', 'approved', 'deprecated')", name='check_case_status'),
        Index('idx_test_cases_tags', 'tags', postgresql_using='gin'),
        {'schema': 'testing'}
    )

    def __repr__(self):
        return f"<TestCase(id='{self.id}', nombre='{self.nombre}', codigo='{self.codigo}')>"


class BulkExecution(Base):
    """Modelo para la tabla testing.bulk_executions"""
    __tablename__ = 'bulk_executions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('testing.projects.id', ondelete='CASCADE'), nullable=False)
    suite_id = Column(UUID(as_uuid=True), ForeignKey('testing.test_suites.id', ondelete='SET NULL'))
    
    # Información de la ejecución
    name = Column(String(255))
    description = Column(Text)
    execution_mode = Column(String(50), default='sequential')
    
    # Configuración
    show_browser = Column(Boolean, default=False)
    headless_mode = Column(Boolean, default=True)
    browser_type = Column(String(20), default='chromium')
    capture_screenshots = Column(Boolean, default=True)
    max_timeout = Column(Integer, default=300)
    
    # Estado y progreso
    status = Column(String(50), default='queued')
    total_cases = Column(Integer, nullable=False, default=0)
    current_case_index = Column(Integer, default=0)
    completed_cases = Column(Integer, default=0)
    failed_cases = Column(Integer, default=0)
    skipped_cases = Column(Integer, default=0)
    progress_percentage = Column(DECIMAL(5, 2), default=0.00)
    
    # Tiempos
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))
    estimated_duration = Column(Integer)
    actual_duration = Column(Integer)
    
    # Resultados generales
    success_rate = Column(DECIMAL(5, 2))
    error_summary = Column(Text)
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), default=func.current_timestamp(), onupdate=func.current_timestamp())
    created_by = Column(String(100))
    
    # Metadatos adicionales
    metadata_json = Column('metadata', JSONB, default={})
    
    # Relationships
    project = relationship("Project", back_populates="bulk_executions")
    test_suite = relationship("TestSuite", back_populates="bulk_executions")
    test_executions = relationship("TestExecution", back_populates="bulk_execution", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("execution_mode IN ('sequential', 'parallel', 'background')", name='check_execution_mode'),
        CheckConstraint("browser_type IN ('chromium', 'firefox', 'webkit')", name='check_browser_type'),
        CheckConstraint("status IN ('queued', 'running', 'paused', 'completed', 'failed', 'cancelled')", name='check_bulk_status'),
        {'schema': 'testing'}
    )

    def __repr__(self):
        return f"<BulkExecution(id='{self.id}', name='{self.name}', status='{self.status}')>"


class TestExecution(Base):
    """Modelo para la tabla testing.test_executions"""
    __tablename__ = 'test_executions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    test_case_id = Column(UUID(as_uuid=True), ForeignKey('testing.test_cases.id', ondelete='CASCADE'), nullable=False)
    bulk_execution_id = Column(UUID(as_uuid=True), ForeignKey('testing.bulk_executions.id', ondelete='SET NULL'))
    project_id = Column(UUID(as_uuid=True), ForeignKey('testing.projects.id', ondelete='CASCADE'), nullable=False)
    
    # Información de la ejecución
    execution_order = Column(Integer)
    execution_type = Column(String(50), default='manual')
    
    # Configuración de la ejecución
    browser_config = Column(JSONB, default={})
    environment = Column(String(100), default='test')
    url_executed = Column(String(500))
    
    # Estado y resultado
    status = Column(String(50), default='pending')
    result_details = Column(Text)
    error_message = Column(Text)
    stack_trace = Column(Text)
    
    # Métricas de rendimiento
    start_time = Column(DateTime(timezone=True), default=func.current_timestamp())
    end_time = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    steps_executed = Column(Integer, default=0)
    steps_total = Column(Integer, default=0)
    
    # Información del script ejecutado
    script_path = Column(String(500))
    script_hash = Column(String(64))
    return_code = Column(Integer)
    stdout_log = Column(Text)
    stderr_log = Column(Text)
    
    # Validaciones automáticas
    validation_results = Column(JSONB, default={})
    assertions_passed = Column(Integer, default=0)
    assertions_failed = Column(Integer, default=0)
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), default=func.current_timestamp(), onupdate=func.current_timestamp())
    executed_by = Column(String(100))
    
    # Metadatos adicionales
    metadata_json = Column('metadata', JSONB, default={})
    
    # Relationships
    test_case = relationship("TestCase", back_populates="test_executions")
    bulk_execution = relationship("BulkExecution", back_populates="test_executions")
    project = relationship("Project", back_populates="test_executions")
    screenshots = relationship("Screenshot", back_populates="execution", cascade="all, delete-orphan")
    execution_logs = relationship("ExecutionLog", back_populates="execution", cascade="all, delete-orphan")
    # Comentado temporalmente hasta que se cree la tabla analytics.execution_metrics
    # execution_metrics = relationship("ExecutionMetrics", back_populates="execution", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("execution_type IN ('manual', 'automated', 'scheduled', 'bulk')", name='check_execution_type'),
        CheckConstraint("status IN ('pending', 'running', 'passed', 'failed', 'skipped', 'error', 'timeout')", name='check_execution_status'),
        {'schema': 'testing'}
    )

    def __repr__(self):
        return f"<TestExecution(id='{self.id}', test_case_id='{self.test_case_id}', status='{self.status}')>"


# ===============================================================
# MODELOS DE EVIDENCIAS
# ===============================================================

class Screenshot(Base):
    """Modelo para la tabla evidence.screenshots"""
    __tablename__ = 'screenshots'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey('testing.test_executions.id', ondelete='CASCADE'), nullable=False)
    test_case_id = Column(UUID(as_uuid=True), ForeignKey('testing.test_cases.id', ondelete='CASCADE'))
    
    # Información del screenshot
    name = Column(String(255), nullable=False)
    description = Column(Text)
    step_number = Column(Integer)
    screenshot_type = Column(String(50), default='step')
    
    # Archivo y ruta
    file_path = Column(String(1000), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size_bytes = Column(BIGINT)
    file_format = Column(String(10), default='png')
    file_hash = Column(String(64))
    
    # Metadatos de la imagen
    width = Column(Integer)
    height = Column(Integer)
    is_full_page = Column(Boolean, default=False)
    
    # Contexto de captura
    url_captured = Column(String(500))
    selector_captured = Column(String(500))
    timestamp_ms = Column(BIGINT)
    
    # Base64 data (opcional)
    base64_data = Column(Text)
    
    # Estado y validación
    is_valid = Column(Boolean, default=True)
    processing_status = Column(String(50), default='processed')
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Metadatos adicionales
    metadata_json = Column('metadata', JSONB, default={})
    
    # Relationships
    execution = relationship("TestExecution", back_populates="screenshots")
    test_case = relationship("TestCase", back_populates="screenshots")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("screenshot_type IN ('initial', 'step', 'final', 'error', 'validation')", name='check_screenshot_type'),
        CheckConstraint("processing_status IN ('pending', 'processing', 'processed', 'failed')", name='check_processing_status'),
        {'schema': 'evidence'}
    )

    def __repr__(self):
        return f"<Screenshot(id='{self.id}', name='{self.name}', execution_id='{self.execution_id}')>"


class ExecutionLog(Base):
    """Modelo para la tabla evidence.execution_logs"""
    __tablename__ = 'execution_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey('testing.test_executions.id', ondelete='CASCADE'), nullable=False)
    
    # Información del log
    log_level = Column(String(20), default='INFO')
    message = Column(Text, nullable=False)
    step_number = Column(Integer)
    timestamp_ms = Column(BIGINT)
    
    # Contexto del log
    source = Column(String(100))
    category = Column(String(50))
    
    # Datos estructurados adicionales
    details = Column(JSONB, default={})
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    
    # Relationships
    execution = relationship("TestExecution", back_populates="execution_logs")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')", name='check_log_level'),
        {'schema': 'evidence'}
    )

    def __repr__(self):
        return f"<ExecutionLog(id='{self.id}', log_level='{self.log_level}', execution_id='{self.execution_id}')>"


# ===============================================================
# MODELOS DE ANALYTICS
# ===============================================================

class ExecutionMetrics(Base):
    """Modelo para la tabla analytics.execution_metrics"""
    __tablename__ = 'execution_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey('testing.test_executions.id', ondelete='CASCADE'), nullable=False)
    test_case_id = Column(UUID(as_uuid=True), ForeignKey('testing.test_cases.id', ondelete='CASCADE'))
    project_id = Column(UUID(as_uuid=True), ForeignKey('testing.projects.id', ondelete='CASCADE'))
    
    # Métricas de tiempo
    page_load_time_ms = Column(Integer)
    total_execution_time_ms = Column(Integer)
    network_idle_time_ms = Column(Integer)
    dom_content_loaded_ms = Column(Integer)
    
    # Métricas de interacción
    clicks_count = Column(Integer, default=0)
    form_fills_count = Column(Integer, default=0)
    navigations_count = Column(Integer, default=0)
    waits_count = Column(Integer, default=0)
    
    # Métricas de red
    requests_count = Column(Integer, default=0)
    failed_requests_count = Column(Integer, default=0)
    total_bytes_downloaded = Column(BIGINT, default=0)
    total_bytes_uploaded = Column(BIGINT, default=0)
    
    # Métricas de rendimiento
    memory_usage_mb = Column(DECIMAL(10, 2))
    cpu_usage_percent = Column(DECIMAL(5, 2))
    
    # Métricas de errores
    javascript_errors_count = Column(Integer, default=0)
    console_errors_count = Column(Integer, default=0)
    network_errors_count = Column(Integer, default=0)
    
    # Información del navegador
    browser_version = Column(String(100))
    viewport_width = Column(Integer)
    viewport_height = Column(Integer)
    user_agent = Column(Text)
    
    # Datos adicionales
    performance_data = Column(JSONB, default={})
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    
    # Metadatos adicionales
    metadata_json = Column('metadata', JSONB, default={})
    
    # Relationships - Comentadas temporalmente hasta resolver el esquema
    # execution = relationship("TestExecution", back_populates="execution_metrics")
    # test_case = relationship("TestCase", back_populates="execution_metrics")
    # project = relationship("Project", back_populates="execution_metrics")

    # Constraints
    __table_args__ = (
        Index('idx_execution_metrics_test_case', 'test_case_id'),
        Index('idx_execution_metrics_project', 'project_id'),
        {'schema': 'analytics'}
    )

    def __repr__(self):
        return f"<ExecutionMetrics(id='{self.id}', execution_id='{self.execution_id}')>"


# ===============================================================
# MODELO DE CONFIGURACIONES
# ===============================================================

class Configuration(Base):
    """Modelo para la tabla testing.configurations"""
    __tablename__ = 'configurations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    key = Column(String(255), nullable=False, unique=True)
    value = Column(Text)
    data_type = Column(String(50), default='string')
    category = Column(String(100))
    description = Column(Text)
    is_system = Column(Boolean, default=False)
    is_encrypted = Column(Boolean, default=False)
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), default=func.current_timestamp(), onupdate=func.current_timestamp())
    updated_by = Column(String(100))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("data_type IN ('string', 'integer', 'boolean', 'json', 'array')", name='check_data_type'),
        {'schema': 'testing'}
    )

    def __repr__(self):
        return f"<Configuration(key='{self.key}', value='{self.value}', data_type='{self.data_type}')>"


# ===============================================================
# FUNCIONES AUXILIARES PARA LA BASE DE DATOS
# ===============================================================

class DatabaseManager:
    """Clase para manejar la conexión y operaciones de base de datos"""
    
    def __init__(self, database_url: str = None, host: str = None, port: int = None, 
                 database: str = None, username: str = None, password: str = None):
        if database_url:
            self.database_url = database_url
        else:
            self.database_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Crear todas las tablas en la base de datos"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Obtener una sesión de base de datos con context manager"""
        return self.SessionLocal()
    
    def get_session_context(self):
        """Context manager para sesiones de base de datos"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def init_default_data(self):
        """Inicializar datos por defecto"""
        session = self.get_session()
        try:
            # Verificar si ya existe el proyecto por defecto
            default_project = session.query(Project).filter_by(name="Default Project").first()
            if not default_project:
                # Crear proyecto por defecto
                default_project = Project(
                    name="Default Project",
                    description="Proyecto por defecto para casos de prueba",
                    base_url="https://example.com",
                    created_by="system"
                )
                session.add(default_project)
            
            # Configuraciones por defecto
            default_configs = [
                ('default_browser', 'chromium', 'string', 'execution', 'Navegador por defecto para ejecuciones'),
                ('default_timeout', '300', 'integer', 'execution', 'Timeout por defecto en segundos'),
                ('screenshot_enabled', 'true', 'boolean', 'evidence', 'Habilitar capturas de pantalla por defecto'),
                ('max_parallel_executions', '3', 'integer', 'performance', 'Máximo número de ejecuciones paralelas'),
                ('log_retention_days', '90', 'integer', 'maintenance', 'Días de retención de logs'),
                ('evidence_retention_days', '365', 'integer', 'maintenance', 'Días de retención de evidencias'),
            ]
            
            for key, value, data_type, category, description in default_configs:
                existing_config = session.query(Configuration).filter_by(key=key).first()
                if not existing_config:
                    config = Configuration(
                        key=key,
                        value=value,
                        data_type=data_type,
                        category=category,
                        description=description,
                        is_system=True
                    )
                    session.add(config)
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


# ===============================================================
# EJEMPLO DE USO
# ===============================================================

if __name__ == "__main__":
    # Ejemplo de conexión a la base de datos
    DATABASE_URL = "postgresql://buse_app:password@localhost:5432/buse_testing_db"
    
    # Inicializar el manager de base de datos
    db_manager = DatabaseManager(DATABASE_URL)
    
    # Crear tablas (solo necesario la primera vez)
    # db_manager.create_tables()
    
    # Inicializar datos por defecto
    # db_manager.init_default_data()
    
    # Ejemplo de uso de los modelos
    session = db_manager.get_session()
    
    try:
        # Obtener todos los proyectos
        projects = session.query(Project).all()
        for project in projects:
            print(f"Proyecto: {project.name} - {project.description}")
        
        # Obtener casos de prueba con estadísticas
        test_cases = session.query(TestCase).filter_by(es_valido=True).all()
        for case in test_cases:
            print(f"Caso: {case.nombre} - Tipo: {case.tipo}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()