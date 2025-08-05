# Base de Datos PostgreSQL para el Sistema de Testing Automatizado

## Descripción

Este proyecto incluye una base de datos PostgreSQL completamente estructurada para manejar:

- ✅ **Casos de Prueba**: Gestión completa con metadatos, versioning y validación
- ✅ **Ejecuciones**: Tracking de ejecuciones individuales y masivas
- ✅ **Evidencias**: Screenshots, logs y métricas de rendimiento
- ✅ **Analytics**: Métricas detalladas y reportes de performance
- ✅ **Proyectos y Suites**: Organización jerárquica de tests
- ✅ **Configuraciones**: Sistema de configuración global

## Estructura de la Base de Datos

### Esquemas Organizados

```
buse_testing_db/
├── testing/          # Tablas principales de testing
│   ├── projects      # Proyectos/aplicaciones
│   ├── test_suites   # Suites de prueba
│   ├── test_cases    # Casos de prueba individuales
│   ├── bulk_executions    # Ejecuciones masivas
│   ├── test_executions    # Ejecuciones individuales
│   └── configurations     # Configuraciones globales
├── evidence/         # Evidencias y logs
│   ├── screenshots   # Capturas de pantalla
│   └── execution_logs     # Logs de ejecución
└── analytics/        # Métricas y analytics
    └── execution_metrics  # Métricas de rendimiento
```

### Características Principales

- **UUIDs como claves primarias** para escalabilidad
- **Timestamps automáticos** con triggers
- **Validación por constraints** para integridad de datos
- **Índices optimizados** para consultas rápidas
- **Relaciones bien definidas** con cascadas apropiadas
- **Metadatos JSONB** para flexibilidad
- **Vistas preparadas** para reportes

## Instalación y Configuración

### 1. Prerrequisitos

```bash
# Instalar PostgreSQL 14+
sudo apt update
sudo apt install postgresql postgresql-contrib

# O en Windows con chocolatey:
choco install postgresql

# O usando Docker:
docker run --name postgres-buse -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:14
```

### 2. Crear la Base de Datos

```sql
-- Conectar como superusuario
sudo -u postgres psql

-- Crear la base de datos
CREATE DATABASE buse_testing_db;

-- Crear usuario para la aplicación
CREATE USER buse_app WITH PASSWORD 'tu_password_seguro';

-- Otorgar permisos
GRANT CONNECT ON DATABASE buse_testing_db TO buse_app;
```

### 3. Ejecutar el Script de Configuración

```bash
# Ejecutar el script completo
psql -U postgres -d buse_testing_db -f db_complete_setup.sql

# O con el usuario de aplicación después de crearlo
psql -U buse_app -d buse_testing_db -f db_complete_setup.sql
```

### 4. Instalar Dependencias de Python

```bash
pip install -r requirements_db.txt
```

### 5. Configurar Variables de Entorno

```bash
# Crear archivo .env
DATABASE_URL=postgresql://buse_app:tu_password_seguro@localhost:5432/buse_testing_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=buse_testing_db
POSTGRES_USER=buse_app
POSTGRES_PASSWORD=tu_password_seguro
```

## Uso con SQLAlchemy

### Configuración Básica

```python
from db_models import DatabaseManager, Project, TestCase, TestExecution

# Inicializar el manager
DATABASE_URL = "postgresql://buse_app:password@localhost:5432/buse_testing_db"
db_manager = DatabaseManager(DATABASE_URL)

# Crear tablas (solo primera vez)
db_manager.create_tables()

# Inicializar datos por defecto
db_manager.init_default_data()
```

### Ejemplos de Uso

#### Crear un Proyecto

```python
session = db_manager.get_session()

# Crear nuevo proyecto
project = Project(
    name="Mi Aplicación Web",
    description="Tests para la aplicación principal",
    base_url="https://miapp.com",
    created_by="admin"
)

session.add(project)
session.commit()
```

#### Crear un Caso de Prueba

```python
# Crear caso de prueba
test_case = TestCase(
    project_id=project.id,
    nombre="Login con credenciales válidas",
    codigo="TC001",
    tipo="funcional",
    prioridad="alta",
    objetivo="Verificar que el usuario puede hacer login correctamente",
    pasos="1. Ir a página de login\n2. Ingresar email y password\n3. Hacer clic en Entrar",
    datos_prueba="Email: test@example.com\nPassword: password123",
    resultado_esperado="Usuario logueado y redirigido al dashboard",
    url_objetivo="https://miapp.com/login",
    tags=["login", "authentication", "smoke"],
    created_by="qa_engineer"
)

session.add(test_case)
session.commit()
```

#### Registrar una Ejecución

```python
# Crear ejecución
execution = TestExecution(
    test_case_id=test_case.id,
    project_id=project.id,
    execution_type="automated",
    environment="staging",
    url_executed="https://staging.miapp.com/login",
    status="running",
    executed_by="automation_bot"
)

session.add(execution)
session.commit()

# Actualizar con resultados
execution.status = "passed"
execution.end_time = func.current_timestamp()
execution.result_details = "Login exitoso, usuario redirigido correctamente"
session.commit()
```

#### Agregar Screenshots

```python
from db_models import Screenshot
import os

screenshot = Screenshot(
    execution_id=execution.id,
    test_case_id=test_case.id,
    name="login_success",
    description="Pantalla después del login exitoso",
    step_number=3,
    screenshot_type="validation",
    file_path="/screenshots/login_success_20240115.png",
    file_name="login_success_20240115.png",
    file_size_bytes=os.path.getsize("/screenshots/login_success_20240115.png"),
    width=1920,
    height=1080,
    is_full_page=True,
    url_captured="https://staging.miapp.com/dashboard"
)

session.add(screenshot)
session.commit()
```

### Consultas Útiles

#### Estadísticas de Proyecto

```python
# Usar función predefinida
stats = session.execute(
    text("SELECT * FROM get_project_stats(:project_id)"),
    {"project_id": project.id}
).fetchone()

print(f"Total casos: {stats.total_cases}")
print(f"Tasa de éxito: {stats.success_rate}%")
```

#### Casos con Mayor Tasa de Fallo

```python
# Consulta con la vista preparada
failed_cases = session.query(
    text("SELECT * FROM testing.test_cases_summary WHERE success_rate < 80 ORDER BY success_rate")
).all()
```

#### Ejecuciones Recientes

```python
from datetime import datetime, timedelta

recent_executions = session.query(TestExecution)\
    .filter(TestExecution.start_time >= datetime.now() - timedelta(days=7))\
    .order_by(TestExecution.start_time.desc())\
    .all()
```

## Funciones Administrativas

### Limpieza de Evidencias Antiguas

```sql
-- Ejecutar limpieza manual
SELECT cleanup_old_evidence();

-- Programar con cron (ejemplo para eliminar evidencias >1 año)
-- 0 2 * * 0 psql -U buse_app -d buse_testing_db -c "SELECT cleanup_old_evidence();"
```

### Backup de la Base de Datos

```bash
# Backup completo
pg_dump -U buse_app -d buse_testing_db -f backup_$(date +%Y%m%d).sql

# Backup solo esquema
pg_dump -U buse_app -d buse_testing_db --schema-only -f schema_backup.sql

# Backup solo datos
pg_dump -U buse_app -d buse_testing_db --data-only -f data_backup.sql
```

### Restaurar Backup

```bash
# Restaurar desde backup
psql -U buse_app -d buse_testing_db -f backup_20240115.sql
```

## Integración con la Aplicación Existente

### Modificar `excel_api_routes.py`

```python
# Agregar al inicio del archivo
from db_models import DatabaseManager, TestCase, TestExecution, Screenshot

# Configurar la base de datos
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://buse_app:password@localhost:5432/buse_testing_db')
db_manager = DatabaseManager(DATABASE_URL)

def save_test_case_to_db(case_data):
    """Guardar caso de prueba en la base de datos"""
    session = db_manager.get_session()
    try:
        # Obtener o crear proyecto por defecto
        project = session.query(Project).filter_by(name="Default Project").first()
        
        test_case = TestCase(
            project_id=project.id,
            nombre=case_data.get('nombre'),
            objetivo=case_data.get('objetivo'),
            pasos=case_data.get('pasos'),
            resultado_esperado=case_data.get('resultado_esperado'),
            url_objetivo=case_data.get('url_extraida'),
            es_valido=case_data.get('es_valido', True),
            problemas=case_data.get('problemas', []),
            sugerencias=case_data.get('sugerencias', []),
            instrucciones_qa_pilot=case_data.get('instrucciones_qa_pilot'),
            created_by="excel_import"
        )
        
        session.add(test_case)
        session.commit()
        return test_case.id
        
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
```

### Modificar las Ejecuciones

```python
def execute_single_case_with_db_tracking(case_data):
    """Ejecutar caso y guardarlo en BD"""
    session = db_manager.get_session()
    
    try:
        # Crear registro de ejecución
        execution = TestExecution(
            test_case_id=case_data['db_id'],
            project_id=case_data['project_id'],
            execution_type="bulk",
            status="pending",
            executed_by="automation_system"
        )
        session.add(execution)
        session.commit()
        
        # Ejecutar el caso
        result = execute_case_original_logic(case_data)
        
        # Actualizar resultado
        execution.status = "passed" if result['success'] else "failed"
        execution.end_time = func.current_timestamp()
        execution.result_details = result.get('details')
        execution.error_message = result.get('error')
        
        # Guardar screenshots si existen
        for screenshot_path in result.get('screenshots', []):
            save_screenshot_to_db(execution.id, screenshot_path)
        
        session.commit()
        return result
        
    except Exception as e:
        session.rollback()
        execution.status = "error"
        execution.error_message = str(e)
        session.commit()
        raise e
    finally:
        session.close()
```

## Monitoreo y Performance

### Queries de Monitoreo

```sql
-- Ver conexiones activas
SELECT pid, usename, application_name, client_addr, state, query_start, query
FROM pg_stat_activity 
WHERE datname = 'buse_testing_db';

-- Ver tamaño de tablas
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname IN ('testing', 'evidence', 'analytics')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Ver estadísticas de ejecución
SELECT 
    COUNT(*) as total_executions,
    COUNT(CASE WHEN status = 'passed' THEN 1 END) as passed,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
    ROUND(AVG(duration_seconds), 2) as avg_duration
FROM testing.test_executions 
WHERE start_time >= CURRENT_DATE - INTERVAL '7 days';
```

### Optimización

```sql
-- Reindexar tablas pesadas
REINDEX TABLE testing.test_executions;
REINDEX TABLE evidence.screenshots;

-- Actualizar estadísticas
ANALYZE testing.test_cases;
ANALYZE testing.test_executions;

-- Ver consultas lentas
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
```

## Troubleshooting

### Problemas Comunes

1. **Error de conexión**:
   ```
   FATAL: password authentication failed for user "buse_app"
   ```
   - Verificar password en .env
   - Revisar pg_hba.conf para permitir conexiones

2. **Permisos insuficientes**:
   ```
   permission denied for schema testing
   ```
   - Ejecutar los GRANT commands del script SQL

3. **Tablas no existen**:
   ```
   relation "testing.projects" does not exist
   ```
   - Ejecutar db_complete_setup.sql completo

### Logs Útiles

```bash
# Ver logs de PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-14-main.log

# En Docker
docker logs postgres-buse

# Habilitar log de consultas lentas en postgresql.conf
log_min_duration_statement = 1000  # Log queries > 1 segundo
```

## Siguientes Pasos

1. **Implementar Migraciones**: Usar Alembic para cambios de esquema
2. **Dashboard de Analytics**: Crear vistas web para las métricas
3. **API REST**: Exponer endpoints para CRUD de la BD
4. **Backups Automáticos**: Programar backups regulares
5. **Replicación**: Configurar réplicas para alta disponibilidad

---

Para más información o soporte, consulta la documentación del proyecto o contacta al equipo de desarrollo. 