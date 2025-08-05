# QA.Pilot - Automatización Inteligente de Pruebas Web

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Playwright](https://img.shields.io/badge/Playwright-Latest-orange.svg)](https://playwright.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

QA.Pilot es una plataforma avanzada de automatización de pruebas web que combina la inteligencia artificial con herramientas de testing para crear una experiencia de testing inteligente y eficiente.

## 🚀 Características Principales

- **Automatización Inteligente**: Utiliza Claude AI para interpretar instrucciones en lenguaje natural y ejecutar pruebas complejas
- **Multi-Navegador**: Soporte completo para Chrome, Firefox y Edge
- **Captura de Evidencias**: Screenshots automáticos y reportes detallados
- **Interfaz Web Intuitiva**: Dashboard moderno para configurar y ejecutar pruebas
- **Integración con Excel**: Carga masiva de casos de prueba desde archivos Excel
- **Base de Datos**: Almacenamiento persistente de resultados y configuraciones
- **Reportes Avanzados**: Generación de reportes en HTML y Word con evidencias
- **Suites de Pruebas**: Organización de pruebas en suites ejecutables

## 📋 Requisitos del Sistema

- **Python**: 3.11 o superior
- **Navegadores**: Chrome, Firefox, Edge (instalados)
- **API Keys**: Anthropic Claude, OpenAI, o Google Gemini
- **Sistema Operativo**: Windows, macOS, Linux

## 🛠️ Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/caradeux/QA.Pilot.git
cd QA.Pilot
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Instalar Playwright

```bash
playwright install
```

### 5. Configurar Variables de Entorno

Crear archivo `.env` basado en `env_example.txt`:

```env
# API Keys (al menos una es requerida)
ANTHROPIC_API_KEY=tu_clave_claude_aqui
OPENAI_API_KEY=tu_clave_openai_aqui
GEMINI_API_KEY=tu_clave_gemini_aqui

# Configuración de la aplicación
FLASK_SECRET_KEY=clave_secreta_muy_segura_aqui
FLASK_ENV=development

# Configuración de base de datos (opcional)
DATABASE_URL=sqlite:///qa_pilot.db
```

## 🚀 Uso Rápido

### Iniciar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en `http://127.0.0.1:5001`

### Ejecutar una Prueba Simple

1. Abre tu navegador y ve a `http://127.0.0.1:5001`
2. En la sección "Configuración de Vuelo":
   - **URL**: Ingresa la URL del sitio a probar
   - **Instrucciones**: Escribe las acciones a realizar (ej: "Buscar 'smartphone' y hacer clic en el primer resultado")
   - **Navegador**: Selecciona Chrome, Firefox o Edge
3. Haz clic en "INICIAR VUELO"
4. Revisa los resultados y capturas de pantalla

## 📊 Funcionalidades Avanzadas

### Carga Masiva desde Excel

1. Prepara un archivo Excel con tus casos de prueba
2. Ve a la sección "Ejecución Masiva"
3. Sube tu archivo Excel
4. Ejecuta todos los casos de prueba automáticamente

### Suites de Pruebas

1. Crea suites de pruebas organizadas
2. Ejecuta múltiples casos relacionados
3. Genera reportes consolidados

### Base de Datos

- Almacenamiento persistente de resultados
- Historial de ejecuciones
- Configuraciones guardadas

## 🏗️ Estructura del Proyecto

```
QA.Pilot/
├── app.py                          # Aplicación principal Flask
├── main.py                         # Punto de entrada alternativo
├── requirements.txt                # Dependencias Python
├── requirements_db.txt             # Dependencias de base de datos
├── templates/                      # Plantillas HTML
├── static/                         # Archivos estáticos (CSS, JS)
├── browser-use/                    # Librería browser-use integrada
├── playwright_scripts/             # Scripts de Playwright
├── test_scripts/                   # Scripts de prueba generados
├── test_screenshots/               # Capturas de pantalla
├── test_evidence/                  # Reportes de evidencia
├── docs/                           # Documentación
└── examples/                       # Ejemplos de uso
```

## 🔧 Configuración Avanzada

### Configuración de Base de Datos

```bash
# Instalar dependencias de base de datos
pip install -r requirements_db.txt

# Configurar base de datos
python db_integration.py
```

### Configuración de Navegadores

```python
# En tu script de prueba
browser_config = {
    "headless": False,           # Mostrar navegador
    "slow_mo": 1000,            # Ralentizar acciones
    "viewport": {"width": 1920, "height": 1080}
}
```

## 📈 Reportes y Evidencias

QA.Pilot genera varios tipos de reportes:

- **Reportes HTML**: Interactivos con capturas de pantalla
- **Reportes Word**: Documentos profesionales con evidencias
- **Logs Detallados**: Información completa de ejecución
- **Métricas**: Estadísticas de rendimiento y éxito

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

- **Documentación**: Revisa la carpeta `docs/`
- **Issues**: Reporta bugs en [GitHub Issues](https://github.com/caradeux/QA.Pilot/issues)
- **Ejemplos**: Consulta la carpeta `examples/` para casos de uso

## 🎯 Roadmap

- [ ] Integración con CI/CD
- [ ] Soporte para testing móvil
- [ ] API REST para integraciones
- [ ] Dashboard de métricas en tiempo real
- [ ] Soporte para testing de APIs
- [ ] Integración con herramientas de gestión de pruebas

---

**Desarrollado con ❤️ por el equipo de QA.Pilot** 