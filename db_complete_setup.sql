-- ===============================================================
-- SCRIPT DE CONFIGURACIÓN DE BASE DE DATOS POSTGRESQL
-- Sistema de Gestión de Tests Automatizados con Playwright
-- ===============================================================

-- Crear la base de datos (ejecutar como superusuario)
-- CREATE DATABASE buse_testing_db;
-- \c buse_testing_db;

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ===============================================================
-- ESQUEMAS
-- ===============================================================

-- Crear esquemas para organizar mejor las tablas
CREATE SCHEMA IF NOT EXISTS testing;
CREATE SCHEMA IF NOT EXISTS evidence;
CREATE SCHEMA IF NOT EXISTS analytics;

-- ===============================================================
-- TABLAS PRINCIPALES
-- ===============================================================

-- Tabla de Proyectos/Aplicaciones
CREATE TABLE testing.projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    base_url VARCHAR(500),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'archived')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Tabla de Suites de Prueba
CREATE TABLE testing.test_suites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES testing.projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'archived')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(project_id, name)
);

-- Tabla de Casos de Prueba
CREATE TABLE testing.test_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    suite_id UUID REFERENCES testing.test_suites(id) ON DELETE SET NULL,
    project_id UUID REFERENCES testing.projects(id) ON DELETE CASCADE,
    
    -- Información básica del caso
    nombre VARCHAR(255) NOT NULL,
    codigo VARCHAR(100) UNIQUE, -- Código único del caso (ej: TC001)
    tipo VARCHAR(50) DEFAULT 'funcional' CHECK (tipo IN ('funcional', 'integracion', 'regresion', 'smoke', 'ui', 'api')),
    prioridad VARCHAR(20) DEFAULT 'media' CHECK (prioridad IN ('alta', 'media', 'baja', 'critica')),
    
    -- Contenido del caso de prueba
    historia_usuario TEXT,
    objetivo TEXT NOT NULL,
    precondicion TEXT,
    pasos TEXT NOT NULL,
    datos_prueba TEXT,
    resultado_esperado TEXT NOT NULL,
    
    -- Información técnica
    url_objetivo VARCHAR(500),
    selector_elementos JSONB DEFAULT '{}'::jsonb, -- Selectores CSS utilizados
    tiempo_estimado INTEGER, -- En segundos
    
    -- Metadatos y validación
    es_valido BOOLEAN DEFAULT true,
    problemas TEXT[],
    sugerencias TEXT[],
    tags TEXT[],
    
    -- Instrucciones generadas
    instrucciones_qa_pilot TEXT,
    instrucciones_browser_use TEXT,
    codigo_playwright TEXT,
    
    -- Control de versiones
    version INTEGER DEFAULT 1,
    version_anterior UUID REFERENCES testing.test_cases(id),
    
    -- Auditoría
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'review', 'approved', 'deprecated')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadatos adicionales
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Tabla de Ejecuciones Masivas/Batch
CREATE TABLE testing.bulk_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES testing.projects(id) ON DELETE CASCADE,
    suite_id UUID REFERENCES testing.test_suites(id) ON DELETE SET NULL,
    
    -- Información de la ejecución
    name VARCHAR(255),
    description TEXT,
    execution_mode VARCHAR(50) DEFAULT 'sequential' CHECK (execution_mode IN ('sequential', 'parallel', 'background')),
    
    -- Configuración
    show_browser BOOLEAN DEFAULT false,
    headless_mode BOOLEAN DEFAULT true,
    browser_type VARCHAR(20) DEFAULT 'chromium' CHECK (browser_type IN ('chromium', 'firefox', 'webkit')),
    capture_screenshots BOOLEAN DEFAULT true,
    max_timeout INTEGER DEFAULT 300, -- En segundos
    
    -- Estado y progreso
    status VARCHAR(50) DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'paused', 'completed', 'failed', 'cancelled')),
    total_cases INTEGER NOT NULL DEFAULT 0,
    current_case_index INTEGER DEFAULT 0,
    completed_cases INTEGER DEFAULT 0,
    failed_cases INTEGER DEFAULT 0,
    skipped_cases INTEGER DEFAULT 0,
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    
    -- Tiempos
    started_at TIMESTAMP WITH TIME ZONE,
    finished_at TIMESTAMP WITH TIME ZONE,
    estimated_duration INTEGER, -- En segundos
    actual_duration INTEGER, -- En segundos
    
    -- Resultados generales
    success_rate DECIMAL(5,2),
    error_summary TEXT,
    
    -- Auditoría
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    
    -- Metadatos adicionales
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Tabla de Ejecuciones Individuales
CREATE TABLE testing.test_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_case_id UUID NOT NULL REFERENCES testing.test_cases(id) ON DELETE CASCADE,
    bulk_execution_id UUID REFERENCES testing.bulk_executions(id) ON DELETE SET NULL,
    project_id UUID REFERENCES testing.projects(id) ON DELETE CASCADE,
    
    -- Información de la ejecución
    execution_order INTEGER, -- Orden en la ejecución masiva
    execution_type VARCHAR(50) DEFAULT 'manual' CHECK (execution_type IN ('manual', 'automated', 'scheduled', 'bulk')),
    
    -- Configuración de la ejecución
    browser_config JSONB DEFAULT '{}'::jsonb,
    environment VARCHAR(100) DEFAULT 'test',
    url_executed VARCHAR(500),
    
    -- Estado y resultado
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'passed', 'failed', 'skipped', 'error', 'timeout')),
    result_details TEXT,
    error_message TEXT,
    stack_trace TEXT,
    
    -- Métricas de rendimiento
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    steps_executed INTEGER DEFAULT 0,
    steps_total INTEGER DEFAULT 0,
    
    -- Información del script ejecutado
    script_path VARCHAR(500),
    script_hash VARCHAR(64), -- Hash del script para control de versiones
    return_code INTEGER,
    stdout_log TEXT,
    stderr_log TEXT,
    
    -- Validaciones automáticas
    validation_results JSONB DEFAULT '{}'::jsonb,
    assertions_passed INTEGER DEFAULT 0,
    assertions_failed INTEGER DEFAULT 0,
    
    -- Auditoría
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    executed_by VARCHAR(100),
    
    -- Metadatos adicionales
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Tabla de Evidencias/Screenshots
CREATE TABLE evidence.screenshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID NOT NULL REFERENCES testing.test_executions(id) ON DELETE CASCADE,
    test_case_id UUID REFERENCES testing.test_cases(id) ON DELETE CASCADE,
    
    -- Información del screenshot
    name VARCHAR(255) NOT NULL,
    description TEXT,
    step_number INTEGER,
    screenshot_type VARCHAR(50) DEFAULT 'step' CHECK (screenshot_type IN ('initial', 'step', 'final', 'error', 'validation')),
    
    -- Archivo y ruta
    file_path VARCHAR(1000) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size_bytes BIGINT,
    file_format VARCHAR(10) DEFAULT 'png',
    file_hash VARCHAR(64),
    
    -- Metadatos de la imagen
    width INTEGER,
    height INTEGER,
    is_full_page BOOLEAN DEFAULT false,
    
    -- Contexto de captura
    url_captured VARCHAR(500),
    selector_captured VARCHAR(500), -- Si se capturó un elemento específico
    timestamp_ms BIGINT, -- Timestamp en milisegundos desde inicio de ejecución
    
    -- Base64 data (opcional, para screenshots pequeños)
    base64_data TEXT,
    
    -- Estado y validación
    is_valid BOOLEAN DEFAULT true,
    processing_status VARCHAR(50) DEFAULT 'processed' CHECK (processing_status IN ('pending', 'processing', 'processed', 'failed')),
    
    -- Auditoría
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadatos adicionales
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Tabla de Logs de Ejecución
CREATE TABLE evidence.execution_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID NOT NULL REFERENCES testing.test_executions(id) ON DELETE CASCADE,
    
    -- Información del log
    log_level VARCHAR(20) DEFAULT 'INFO' CHECK (log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    message TEXT NOT NULL,
    step_number INTEGER,
    timestamp_ms BIGINT, -- Timestamp en milisegundos desde inicio de ejecución
    
    -- Contexto del log
    source VARCHAR(100), -- browser, playwright, qa_pilot, etc.
    category VARCHAR(50), -- navigation, action, validation, error, etc.
    
    -- Datos estructurados adicionales
    details JSONB DEFAULT '{}'::jsonb,
    
    -- Auditoría
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Métricas y Analytics
CREATE TABLE analytics.execution_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID NOT NULL REFERENCES testing.test_executions(id) ON DELETE CASCADE,
    test_case_id UUID REFERENCES testing.test_cases(id) ON DELETE CASCADE,
    project_id UUID REFERENCES testing.projects(id) ON DELETE CASCADE,
    
    -- Métricas de tiempo
    page_load_time_ms INTEGER,
    total_execution_time_ms INTEGER,
    network_idle_time_ms INTEGER,
    dom_content_loaded_ms INTEGER,
    
    -- Métricas de interacción
    clicks_count INTEGER DEFAULT 0,
    form_fills_count INTEGER DEFAULT 0,
    navigations_count INTEGER DEFAULT 0,
    waits_count INTEGER DEFAULT 0,
    
    -- Métricas de red
    requests_count INTEGER DEFAULT 0,
    failed_requests_count INTEGER DEFAULT 0,
    total_bytes_downloaded BIGINT DEFAULT 0,
    total_bytes_uploaded BIGINT DEFAULT 0,
    
    -- Métricas de rendimiento
    memory_usage_mb DECIMAL(10,2),
    cpu_usage_percent DECIMAL(5,2),
    
    -- Métricas de errores
    javascript_errors_count INTEGER DEFAULT 0,
    console_errors_count INTEGER DEFAULT 0,
    network_errors_count INTEGER DEFAULT 0,
    
    -- Información del navegador
    browser_version VARCHAR(100),
    viewport_width INTEGER,
    viewport_height INTEGER,
    user_agent TEXT,
    
    -- Datos adicionales
    performance_data JSONB DEFAULT '{}'::jsonb,
    
    -- Auditoría
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadatos adicionales
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Tabla de Configuraciones Globales
CREATE TABLE testing.configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(255) NOT NULL UNIQUE,
    value TEXT,
    data_type VARCHAR(50) DEFAULT 'string' CHECK (data_type IN ('string', 'integer', 'boolean', 'json', 'array')),
    category VARCHAR(100),
    description TEXT,
    is_system BOOLEAN DEFAULT false,
    is_encrypted BOOLEAN DEFAULT false,
    
    -- Auditoría
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100)
);

-- ===============================================================
-- ÍNDICES PARA RENDIMIENTO
-- ===============================================================

-- Índices para test_cases
CREATE INDEX idx_test_cases_suite ON testing.test_cases(suite_id);
CREATE INDEX idx_test_cases_project ON testing.test_cases(project_id);
CREATE INDEX idx_test_cases_status ON testing.test_cases(status);
CREATE INDEX idx_test_cases_tipo ON testing.test_cases(tipo);
CREATE INDEX idx_test_cases_created ON testing.test_cases(created_at);
CREATE INDEX idx_test_cases_tags ON testing.test_cases USING gin(tags);
CREATE INDEX idx_test_cases_es_valido ON testing.test_cases(es_valido);

-- Índices para test_executions
CREATE INDEX idx_executions_case ON testing.test_executions(test_case_id);
CREATE INDEX idx_executions_bulk ON testing.test_executions(bulk_execution_id);
CREATE INDEX idx_executions_project ON testing.test_executions(project_id);
CREATE INDEX idx_executions_status ON testing.test_executions(status);
CREATE INDEX idx_executions_start_time ON testing.test_executions(start_time);
CREATE INDEX idx_executions_duration ON testing.test_executions(duration_seconds);
CREATE INDEX idx_executions_type ON testing.test_executions(execution_type);

-- Índices para bulk_executions
CREATE INDEX idx_bulk_executions_project ON testing.bulk_executions(project_id);
CREATE INDEX idx_bulk_executions_suite ON testing.bulk_executions(suite_id);
CREATE INDEX idx_bulk_executions_status ON testing.bulk_executions(status);
CREATE INDEX idx_bulk_executions_created ON testing.bulk_executions(created_at);
CREATE INDEX idx_bulk_executions_started ON testing.bulk_executions(started_at);

-- Índices para screenshots
CREATE INDEX idx_screenshots_execution ON evidence.screenshots(execution_id);
CREATE INDEX idx_screenshots_case ON evidence.screenshots(test_case_id);
CREATE INDEX idx_screenshots_type ON evidence.screenshots(screenshot_type);
CREATE INDEX idx_screenshots_created ON evidence.screenshots(created_at);
CREATE INDEX idx_screenshots_step ON evidence.screenshots(step_number);

-- Índices para execution_logs
CREATE INDEX idx_logs_execution ON evidence.execution_logs(execution_id);
CREATE INDEX idx_logs_level ON evidence.execution_logs(log_level);
CREATE INDEX idx_logs_created ON evidence.execution_logs(created_at);
CREATE INDEX idx_logs_source ON evidence.execution_logs(source);
CREATE INDEX idx_logs_step ON evidence.execution_logs(step_number);

-- Índices para metrics
CREATE INDEX idx_metrics_execution ON analytics.execution_metrics(execution_id);
CREATE INDEX idx_metrics_case ON analytics.execution_metrics(test_case_id);
CREATE INDEX idx_metrics_project ON analytics.execution_metrics(project_id);
CREATE INDEX idx_metrics_created ON analytics.execution_metrics(created_at);

-- ===============================================================
-- TRIGGERS PARA AUDITORÍA
-- ===============================================================

-- Función para actualizar timestamp automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar trigger a las tablas principales
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON testing.projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_test_suites_updated_at BEFORE UPDATE ON testing.test_suites FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_test_cases_updated_at BEFORE UPDATE ON testing.test_cases FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bulk_executions_updated_at BEFORE UPDATE ON testing.bulk_executions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_test_executions_updated_at BEFORE UPDATE ON testing.test_executions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_screenshots_updated_at BEFORE UPDATE ON evidence.screenshots FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_configurations_updated_at BEFORE UPDATE ON testing.configurations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===============================================================
-- FUNCIONES AUXILIARES
-- ===============================================================

-- Función para calcular duración de ejecución
CREATE OR REPLACE FUNCTION calculate_execution_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.end_time IS NOT NULL AND NEW.start_time IS NOT NULL THEN
        NEW.duration_seconds = EXTRACT(EPOCH FROM (NEW.end_time - NEW.start_time))::INTEGER;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_execution_duration 
    BEFORE UPDATE ON testing.test_executions 
    FOR EACH ROW EXECUTE FUNCTION calculate_execution_duration();

-- Función para calcular progreso de ejecución masiva
CREATE OR REPLACE FUNCTION update_bulk_execution_progress()
RETURNS TRIGGER AS $$
DECLARE
    total INTEGER;
    completed INTEGER;
    failed INTEGER;
BEGIN
    -- Obtener estadísticas de la ejecución masiva
    SELECT 
        be.total_cases,
        COUNT(CASE WHEN te.status IN ('passed', 'failed', 'skipped') THEN 1 END),
        COUNT(CASE WHEN te.status = 'failed' THEN 1 END)
    INTO total, completed, failed
    FROM testing.bulk_executions be
    LEFT JOIN testing.test_executions te ON te.bulk_execution_id = be.id
    WHERE be.id = COALESCE(NEW.bulk_execution_id, OLD.bulk_execution_id)
    GROUP BY be.id, be.total_cases;
    
    -- Actualizar progreso en la ejecución masiva
    UPDATE testing.bulk_executions 
    SET 
        completed_cases = COALESCE(completed, 0),
        failed_cases = COALESCE(failed, 0),
        progress_percentage = CASE 
            WHEN total > 0 THEN (COALESCE(completed, 0)::DECIMAL / total * 100)
            ELSE 0 
        END,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = COALESCE(NEW.bulk_execution_id, OLD.bulk_execution_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- Crear triggers separados para cada operación
CREATE TRIGGER update_bulk_progress_on_execution_insert
    AFTER INSERT ON testing.test_executions
    FOR EACH ROW 
    WHEN (NEW.bulk_execution_id IS NOT NULL)
    EXECUTE FUNCTION update_bulk_execution_progress();

CREATE TRIGGER update_bulk_progress_on_execution_update
    AFTER UPDATE ON testing.test_executions
    FOR EACH ROW 
    WHEN (NEW.bulk_execution_id IS NOT NULL OR OLD.bulk_execution_id IS NOT NULL)
    EXECUTE FUNCTION update_bulk_execution_progress();

CREATE TRIGGER update_bulk_progress_on_execution_delete
    AFTER DELETE ON testing.test_executions
    FOR EACH ROW 
    WHEN (OLD.bulk_execution_id IS NOT NULL)
    EXECUTE FUNCTION update_bulk_execution_progress();

-- ===============================================================
-- VISTAS ÚTILES
-- ===============================================================

-- Vista de resumen de casos de prueba
CREATE VIEW testing.test_cases_summary AS
SELECT 
    tc.id,
    tc.nombre,
    tc.codigo,
    tc.tipo,
    tc.prioridad,
    tc.status,
    p.name as project_name,
    ts.name as suite_name,
    tc.es_valido,
    tc.created_at,
    -- Estadísticas de ejecución
    COUNT(te.id) as total_executions,
    COUNT(CASE WHEN te.status = 'passed' THEN 1 END) as passed_executions,
    COUNT(CASE WHEN te.status = 'failed' THEN 1 END) as failed_executions,
    CASE 
        WHEN COUNT(te.id) > 0 THEN 
            ROUND((COUNT(CASE WHEN te.status = 'passed' THEN 1 END)::DECIMAL / COUNT(te.id) * 100), 2)
        ELSE NULL 
    END as success_rate,
    MAX(te.start_time) as last_execution
FROM testing.test_cases tc
LEFT JOIN testing.projects p ON tc.project_id = p.id
LEFT JOIN testing.test_suites ts ON tc.suite_id = ts.id
LEFT JOIN testing.test_executions te ON tc.id = te.test_case_id
GROUP BY tc.id, tc.nombre, tc.codigo, tc.tipo, tc.prioridad, tc.status, 
         p.name, ts.name, tc.es_valido, tc.created_at;

-- Vista de métricas de ejecución
CREATE VIEW analytics.execution_analytics AS
SELECT 
    te.id as execution_id,
    tc.nombre as test_case_name,
    tc.codigo as test_case_code,
    p.name as project_name,
    te.status,
    te.duration_seconds,
    te.start_time,
    te.end_time,
    em.page_load_time_ms,
    em.total_execution_time_ms,
    em.clicks_count,
    em.form_fills_count,
    em.javascript_errors_count,
    COUNT(s.id) as screenshots_count,
    COUNT(el.id) as logs_count
FROM testing.test_executions te
JOIN testing.test_cases tc ON te.test_case_id = tc.id
JOIN testing.projects p ON te.project_id = p.id
LEFT JOIN analytics.execution_metrics em ON te.id = em.execution_id
LEFT JOIN evidence.screenshots s ON te.id = s.execution_id
LEFT JOIN evidence.execution_logs el ON te.id = el.execution_id
GROUP BY te.id, tc.nombre, tc.codigo, p.name, te.status, te.duration_seconds,
         te.start_time, te.end_time, em.page_load_time_ms, em.total_execution_time_ms,
         em.clicks_count, em.form_fills_count, em.javascript_errors_count;

-- ===============================================================
-- DATOS INICIALES
-- ===============================================================

-- Configuraciones por defecto
INSERT INTO testing.configurations (key, value, data_type, category, description, is_system) VALUES
('default_browser', 'chromium', 'string', 'execution', 'Navegador por defecto para ejecuciones', true),
('default_timeout', '300', 'integer', 'execution', 'Timeout por defecto en segundos', true),
('screenshot_enabled', 'true', 'boolean', 'evidence', 'Habilitar capturas de pantalla por defecto', true),
('max_parallel_executions', '3', 'integer', 'performance', 'Máximo número de ejecuciones paralelas', true),
('log_retention_days', '90', 'integer', 'maintenance', 'Días de retención de logs', true),
('evidence_retention_days', '365', 'integer', 'maintenance', 'Días de retención de evidencias', true);

-- Proyecto por defecto
INSERT INTO testing.projects (name, description, base_url, created_by) VALUES
('Default Project', 'Proyecto por defecto para casos de prueba', 'https://example.com', 'system');

-- ===============================================================
-- COMENTARIOS FINALES
-- ===============================================================

-- Para crear usuarios y permisos, ejecutar como superusuario:
/*
-- Crear usuario para la aplicación
CREATE USER buse_app WITH PASSWORD 'tu_password_seguro';

-- Otorgar permisos
GRANT CONNECT ON DATABASE buse_testing_db TO buse_app;
GRANT USAGE ON SCHEMA testing, evidence, analytics TO buse_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA testing, evidence, analytics TO buse_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA testing, evidence, analytics TO buse_app;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA testing, evidence, analytics TO buse_app;

-- Para futuras tablas
ALTER DEFAULT PRIVILEGES IN SCHEMA testing GRANT ALL ON TABLES TO buse_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA evidence GRANT ALL ON TABLES TO buse_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT ALL ON TABLES TO buse_app;
*/

-- ===============================================================
-- PROCEDIMIENTOS ALMACENADOS ÚTILES
-- ===============================================================

-- Función para limpiar evidencias antiguas
CREATE OR REPLACE FUNCTION cleanup_old_evidence()
RETURNS INTEGER AS $$
DECLARE
    retention_days INTEGER;
    deleted_count INTEGER := 0;
    temp_count INTEGER;
BEGIN
    -- Obtener días de retención desde configuración
    SELECT value::INTEGER INTO retention_days 
    FROM testing.configurations 
    WHERE key = 'evidence_retention_days';
    
    IF retention_days IS NULL THEN
        retention_days := 365; -- Por defecto 1 año
    END IF;
    
    -- Eliminar screenshots antiguos
    DELETE FROM evidence.screenshots 
    WHERE created_at < (CURRENT_TIMESTAMP - INTERVAL '1 day' * retention_days);
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Eliminar logs antiguos  
    DELETE FROM evidence.execution_logs 
    WHERE created_at < (CURRENT_TIMESTAMP - INTERVAL '1 day' * retention_days);
    
    GET DIAGNOSTICS temp_count = ROW_COUNT;
    deleted_count := deleted_count + temp_count;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener estadísticas del proyecto
CREATE OR REPLACE FUNCTION get_project_stats(project_uuid UUID)
RETURNS TABLE (
    total_cases INTEGER,
    valid_cases INTEGER,
    total_executions INTEGER,
    successful_executions INTEGER,
    failed_executions INTEGER,
    success_rate DECIMAL(5,2),
    avg_execution_time DECIMAL(10,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT tc.id)::INTEGER as total_cases,
        COUNT(DISTINCT CASE WHEN tc.es_valido = true THEN tc.id END)::INTEGER as valid_cases,
        COUNT(te.id)::INTEGER as total_executions,
        COUNT(CASE WHEN te.status = 'passed' THEN 1 END)::INTEGER as successful_executions,
        COUNT(CASE WHEN te.status = 'failed' THEN 1 END)::INTEGER as failed_executions,
        CASE 
            WHEN COUNT(te.id) > 0 THEN 
                ROUND((COUNT(CASE WHEN te.status = 'passed' THEN 1 END)::DECIMAL / COUNT(te.id) * 100), 2)
            ELSE 0 
        END as success_rate,
        COALESCE(AVG(te.duration_seconds), 0)::DECIMAL(10,2) as avg_execution_time
    FROM testing.test_cases tc
    LEFT JOIN testing.test_executions te ON tc.id = te.test_case_id
    WHERE tc.project_id = project_uuid;
END;
$$ LANGUAGE plpgsql;

COMMENT ON DATABASE buse_testing_db IS 'Base de datos para el sistema de gestión de tests automatizados con Playwright';