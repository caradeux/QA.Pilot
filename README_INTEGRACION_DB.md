# 🚀 Integración de Base de Datos PostgreSQL con QA-Pilot

## 📋 Resumen

Esta documentación describe la integración completa de PostgreSQL con tu aplicación Flask QA-Pilot. La integración permite:

- ✅ **Persistencia de datos**: Almacenar casos de prueba, ejecuciones y resultados
- ✅ **Análisis automático**: Los casos de Excel se guardan automáticamente en BD
- ✅ **Seguimiento histórico**: Mantener registro completo de todas las ejecuciones
- ✅ **Métricas avanzadas**: Generar reportes y estadísticas de testing
- ✅ **Escalabilidad**: Soporte para múltiples proyectos y usuarios

## 🗄️ Estructura de Base de Datos

### Esquemas Principales

```sql
-- Esquema principal de testing
SCHEMA testing:
  - projects (proyectos)
  - test_suites (suites de prueba)  
  - test_cases (casos de prueba)
  - bulk_executions (ejecuciones masivas)
  - test_executions (ejecuciones individuales)
  - configurations (configuraciones)

-- Esquema de evidencias
SCHEMA evidence:
  - screenshots (capturas de pantalla)
  - execution_logs (logs de ejecución)

-- Esquema de analíticas
SCHEMA analytics:
  - execution_metrics (métricas de rendimiento)
```

### Tablas Principales

#### 📁 **Projects** (Proyectos)
```sql
- id (UUID, PK)
- name (nombre del proyecto)
- description (descripción)
- base_url (URL base para pruebas)
- status (activo/inactivo)
- created_by (creador)
- metadata_json (configuración adicional)
```

#### 📋 **Test Cases** (Casos de Prueba)
```sql
- id (UUID, PK)
- project_id (FK a projects)
- nombre (nombre del caso)
- codigo (código único)
- tipo (funcional/regresión/etc.)
- prioridad (alta/media/baja)
- objetivo (descripción del objetivo)
- pasos (pasos de ejecución)
- resultado_esperado (resultado esperado)
- url_objetivo (URL a probar)
- instrucciones_browser_use (instrucciones para browser-use)
- instrucciones_qa_pilot (instrucciones para QA-Pilot)
- es_valido (si el caso es válido)
- status (borrador/activo/archivado)
```

#### 🚀 **Bulk Executions** (Ejecuciones Masivas)
```sql
- id (UUID, PK)
- project_id (FK a projects)
- name (nombre de la ejecución)
- execution_mode (secuencial/paralelo)
- total_cases (total de casos)
- completed_cases (casos completados)
- failed_cases (casos fallidos)
- progress_percentage (porcentaje de progreso)
- status (en_cola/ejecutando/completado/fallido)
- started_at, finished_at (tiempos)
```

#### ▶️ **Test Executions** (Ejecuciones Individuales)
```sql
- id (UUID, PK)
- test_case_id (FK a test_cases)
- bulk_execution_id (FK a bulk_executions, opcional)
- status (pendiente/ejecutando/exitoso/fallido)
- start_time, end_time (tiempos de ejecución)
- return_code (código de retorno)
- stdout_log, stderr_log (logs de salida)
- script_path (ruta del script ejecutado)
- browser_config (configuración del navegador)
```

#### 📸 **Screenshots** (Capturas de Pantalla)
```sql
- id (UUID, PK)
- execution_id (FK a test_executions)
- name (nombre de la captura)
- step_number (número de paso)
- screenshot_type (inicio/paso/fin/error)
- file_path (ruta del archivo)
- timestamp_ms (timestamp en milisegundos)
- url_captured (URL capturada)
```

## 🔧 Archivos de Integración

### 1. **db_integration.py**
Clase principal de integración con métodos para:
- `DatabaseIntegration()`: Clase principal
- `test_connection()`: Probar conexión
- `save_excel_test_case()`: Guardar casos desde Excel
- `create_bulk_execution()`: Crear ejecución masiva
- `save_test_execution()`: Guardar resultado de ejecución
- `get_test_cases()`: Obtener casos de prueba
- `update_bulk_execution_status()`: Actualizar progreso

### 2. **Modificaciones en app.py**
```python
# Nuevas rutas agregadas:
@app.route('/database')          # Página de estado de BD
@app.route('/database_status')   # API de estado
@app.route('/api/test_cases')    # API para obtener casos
@app.route('/api/save_test_to_db') # API para migrar desde historial
```

### 3. **Modificaciones en excel_api_routes.py**
- Integración automática al analizar Excel
- Guardado automático de casos válidos en BD
- Creación de ejecuciones masivas con tracking en BD

### 4. **Nueva Interfaz Web**
- **Navegación**: Nuevo enlace "Base de Datos" en sidebar
- **Página de Estado**: `/database` muestra estadísticas en tiempo real
- **Dashboard**: Conexión, casos, ejecuciones, proyectos

## 📱 Funcionalidades Integradas

### 🔄 **Flujo Automático Excel → BD**

1. **Análisis de Excel**: Usuario sube archivo Excel
2. **Extracción de Casos**: Se extraen y validan los casos
3. **Guardado Automático**: Casos válidos se guardan en PostgreSQL
4. **Feedback**: Se informa al usuario del resultado

```python
# Ejemplo de respuesta con BD integrada:
{
  "success": true,
  "test_cases": [...],
  "summary": {...},
  "database_save": {
    "success": true,
    "saved_cases": 5,
    "case_ids": ["uuid1", "uuid2", ...]
  }
}
```

### 🚀 **Ejecuciones Masivas con Tracking**

1. **Creación**: Se crea registro en `bulk_executions`
2. **Seguimiento**: Progreso se actualiza en tiempo real
3. **Resultados**: Cada ejecución individual se guarda
4. **Evidencias**: Screenshots se vinculan a ejecuciones

### 📊 **Dashboard de Estado**

La página `/database` muestra:
- **Estado de Conexión**: PostgreSQL activo/inactivo
- **Estadísticas**: Proyectos, casos, ejecuciones
- **Casos Recientes**: Lista de casos en BD
- **Migración**: Herramientas para migrar desde historial

## 🛠️ Instalación y Configuración

### 1. **Verificar Dependencias**
```bash
# Las dependencias ya están instaladas:
pip list | grep -E "(psycopg2|sqlalchemy|alembic)"
```

### 2. **Configuración de Conexión**
El archivo `config_db.env` ya está configurado:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=buse_testing_db
DB_USER=postgres
DB_PASSWORD=root
```

### 3. **Verificar Base de Datos**
```bash
# Ejecutar script de pruebas
python test_integration.py
```

## 🔍 Pruebas y Verificación

### **Script de Pruebas Completas**
```bash
python test_integration.py
```

Este script verifica:
- ✅ Importaciones correctas
- ✅ Conexión a PostgreSQL
- ✅ Guardado de casos de prueba
- ✅ Ejecuciones masivas
- ✅ Rutas de Flask
- ✅ Integración con Excel

### **Verificación Manual**

1. **Iniciar aplicación**:
   ```bash
   python app.py
   ```

2. **Acceder a dashboard**:
   - Ir a `http://localhost:5000/database`
   - Verificar conexión y estadísticas

3. **Probar Excel**:
   - Ir a "Excel a QA-Pilot"
   - Subir archivo Excel
   - Verificar mensaje de guardado en BD

## 📈 Beneficios de la Integración

### **Para el Usuario**
- 🎯 **Organización**: Casos organizados por proyectos
- 📊 **Seguimiento**: Historial completo de ejecuciones
- 🔍 **Búsqueda**: Filtrar y buscar casos fácilmente
- 📈 **Métricas**: Estadísticas de éxito/fallo
- 💾 **Persistencia**: Datos seguros en PostgreSQL

### **Para el Sistema**
- ⚡ **Rendimiento**: Consultas optimizadas con índices
- 🔄 **Escalabilidad**: Soporte para múltiples usuarios
- 🛡️ **Integridad**: Relaciones y validaciones de BD
- 🔧 **Mantenimiento**: Backups y gestión centralizados
- 📋 **Reportes**: Generación de reportes avanzados

## 🔮 Próximas Mejoras

### **Funcionalidades Pendientes**
- [ ] **Usuarios y Roles**: Sistema de autenticación
- [ ] **Reportes Avanzados**: Dashboards con gráficos
- [ ] **API REST**: Endpoints para integración externa
- [ ] **Webhooks**: Notificaciones de estado
- [ ] **Exportación**: Excel/PDF de resultados
- [ ] **Programación**: Ejecuciones automáticas

### **Optimizaciones Técnicas**
- [ ] **Cache**: Redis para consultas frecuentes
- [ ] **Async**: Procesamiento asíncrono
- [ ] **Monitoring**: Métricas de rendimiento
- [ ] **Backup**: Automatización de respaldos

## 🆘 Troubleshooting

### **Problemas Comunes**

#### Error de Conexión
```bash
# Verificar PostgreSQL
pg_isready -h localhost -p 5432

# Verificar credenciales
psql -h localhost -U postgres -d buse_testing_db
```

#### Error de Importaciones
```bash
# Verificar dependencias
pip install -r requirements_db.txt

# Verificar PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

#### Error de Permisos
```sql
-- Verificar permisos en PostgreSQL
GRANT ALL PRIVILEGES ON DATABASE buse_testing_db TO postgres;
GRANT ALL ON SCHEMA testing TO postgres;
```

### **Logs de Depuración**
```python
# Habilitar logs de SQLAlchemy
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

## 📞 Soporte

Si encuentras problemas:

1. **Ejecutar pruebas**: `python test_integration.py`
2. **Verificar logs**: Revisar `app_debug.log`
3. **Revisar conexión**: Verificar PostgreSQL activo
4. **Validar configuración**: Comprobar `config_db.env`

## 🎉 ¡Integración Completada!

Tu aplicación QA-Pilot ahora tiene integración completa con PostgreSQL:

- ✅ **Base de datos configurada y conectada**
- ✅ **Casos de Excel se guardan automáticamente**
- ✅ **Ejecuciones masivas con seguimiento en BD**
- ✅ **Dashboard de estado funcional**
- ✅ **APIs para consultar datos**
- ✅ **Estructura escalable para futuro crecimiento**

¡Disfruta de tu nuevo sistema de testing automatizado con persistencia de datos! 🚀 