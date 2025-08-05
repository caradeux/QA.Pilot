# 📸 Guía de Migración: Capturas de Pantalla con Browser-Use

## 🎯 Objetivo

Esta guía te ayuda a **migrar tus scripts existentes** de capturas de pantalla complejas a la nueva **utilidad simplificada** que usa `browser_context.take_screenshot()` directamente desde browser-use.

---

## 🔄 Comparación: Antes vs Después

### ❌ ANTES (Código Complejo - 173 líneas)

```python
# Función compleja con múltiples estrategias de fallback
async def tomar_captura_navegador(agent, descripcion, paso_num=None):
    try:
        # ... 50+ líneas de código complejo ...
        
        # Estrategia 1: browser_context del agente
        try:
            screenshot_b64 = await agent.browser_context.take_screenshot(full_page=False)
            # ... más código ...
        except Exception as e:
            print(f"DEBUG: Error con browser_context del agente: {e}")
        
        # Estrategia 2: browser y contexto activo  
        try:
            if hasattr(agent.browser, 'contexts') and agent.browser.contexts:
                context = agent.browser.contexts[0]
                # ... más código ...
        except Exception as e:
            print(f"DEBUG: Error con browser: {e}")
        
        # Estrategia 3: página activa directamente
        try:
            pages = agent.browser_context.pages
            # ... más código ...
        except Exception as e:
            print(f"DEBUG: Error con página activa: {e}")
            
        # Estrategia 4: Fallback pyautogui
        try:
            screenshot = pyautogui.screenshot()
            # ... más código ...
        except Exception as e:
            print(f"DEBUG: Error con fallback: {e}")
        
        # Si todo falla, crear imagen de error
        # ... más código ...
        
    except Exception as e:
        print(f"ERROR al tomar captura: {str(e)}")
        return None
```

### ✅ DESPUÉS (Código Simple - 3 líneas)

```python
# Importar la utilidad
from utils_screenshot import ScreenshotManager

# Crear gestor
screenshots = ScreenshotManager("mi_test")

# Tomar captura
await screenshots.capturar_paso(agent.browser_context, 1, "Mi captura")
```

---

## 🚀 Migración Paso a Paso

### Paso 1: Preparar el Entorno

1. **Copia los archivos nuevos** a tu proyecto:
   ```bash
   # Asegúrate de tener estos archivos en tu proyecto:
   utils_screenshot.py
   ejemplo_uso_capturas.py
   test_demo_mejorado.py
   ```

2. **Verifica que browser-use funciona** correctamente:
   ```python
   # En tu script, asegúrate de que esto funcione:
   screenshot_b64 = await agent.browser_context.take_screenshot()
   ```

### Paso 2: Migrar un Script Existente

#### 🔧 Opción A: Migración Mínima (Más Rápida)

**Solo necesitas cambiar 3 cosas:**

1. **Agregar import:**
   ```python
   from utils_screenshot import ScreenshotManager
   ```

2. **Crear gestor después de crear el agent:**
   ```python
   # Después de: agent = Agent(...)
   screenshots = ScreenshotManager("nombre_de_tu_test")
   ```

3. **Reemplazar llamadas complejas:**
   ```python
   # ANTES:
   await capturar_paso(agent.browser_context, 1, "Mi descripción")
   
   # DESPUÉS:
   await screenshots.capturar_paso(agent.browser_context, 1, "Mi descripción")
   ```

#### 🔧 Opción B: Migración Completa (Más Limpia)

Usa `test_demo_mejorado.py` como plantilla y copia la estructura completa.

### Paso 3: Casos Específicos

#### Para scripts con `pyautogui`:
```python
# ANTES:
screenshot = pyautogui.screenshot()
screenshot.save(screenshot_path)

# DESPUÉS:
await screenshots.capturar_paso(agent.browser_context, None, "Captura automática")
```

#### Para scripts con múltiples estrategias:
```python
# ANTES: 50+ líneas de código con try/except múltiples

# DESPUÉS:
await screenshots.capturar_paso(agent.browser_context, paso_num, descripcion)
# Si falla, ya maneja el error internamente
```

#### Para integración con sistema de tracking:
```python
# ANTES: Código manual para tracking

# DESPUÉS:
from utils_screenshot import integrar_captura_con_sistema

captura_info = await integrar_captura_con_sistema(
    agent.browser_context,
    task_id,
    "Mi descripción"
)
# captura_info contiene: url, path, name, timestamp
```

---

## 📋 Lista de Verificación para Migración

### ✅ Pre-migración
- [ ] Backup de scripts originales
- [ ] `utils_screenshot.py` copiado al proyecto
- [ ] Verificar que browser-use funciona correctamente
- [ ] Comprobar que `agent.browser_context.take_screenshot()` funciona

### ✅ Durante la migración
- [ ] Importar `ScreenshotManager`
- [ ] Crear instancia del gestor después del agent
- [ ] Reemplazar llamadas a funciones complejas
- [ ] Mantener misma lógica de timing (await asyncio.sleep si es necesario)
- [ ] Verificar que los directorios de destino son correctos

### ✅ Post-migración
- [ ] Probar script migrado
- [ ] Verificar que las capturas se guardan correctamente
- [ ] Comprobar que los archivos tienen nombres descriptivos
- [ ] Validar integración con sistema de evidencia existente
- [ ] Eliminar código obsoleto (funciones complejas de captura)

---

## 🎯 Ejemplos de Migración por Tipo

### 1. Script Simple (como test_demo.py)

```python
# ANTES - Función compleja
async def capturar_paso(browser_context, num_paso, descripcion):
    try:
        screenshot_b64 = await browser_context.take_screenshot(full_page=True)
        screenshot_bytes = base64.b64decode(screenshot_b64)
        # ... 30+ líneas más ...
    except Exception as e:
        # ... manejo de errores ...

# DESPUÉS - Uso simple
from utils_screenshot import ScreenshotManager

async def main():
    # ... tu código original ...
    screenshots = ScreenshotManager("test_demo")
    
    # Captura inicial
    await screenshots.capturar_inicial(agent.browser_context)
    
    # Tu lógica de test
    await agent.run()
    
    # Capturas adicionales
    await screenshots.capturar_paso(agent.browser_context, 1, "Después del test")
    await screenshots.capturar_final(agent.browser_context)
```

### 2. Script con Integración de Sistema

```python
# ANTES - Código manual de tracking
with db_lock:
    if task_id in test_status_db:
        if 'screenshots' not in test_status_db[task_id]:
            test_status_db[task_id]['screenshots'] = []
        
        relative_path = os.path.relpath(output_path, SCREENSHOTS_DIR)
        url_path = relative_path.replace(os.path.sep, '/')
        
        test_status_db[task_id]['screenshots'].append({
            'url': f'/media/screenshots/{url_path}',
            'path': output_path,
            'name': os.path.basename(output_path)
        })

# DESPUÉS - Integración automática
from utils_screenshot import integrar_captura_con_sistema

captura_info = await integrar_captura_con_sistema(
    agent.browser_context,
    task_id,
    "Mi captura"
)

if captura_info:
    # La información ya está en el formato correcto para tu sistema
    # captura_info = {'url': '...', 'path': '...', 'name': '...', ...}
    pass
```

### 3. Script con Decorador Automático

```python
# NUEVO - Para funciones que quieres capturar automáticamente
from utils_screenshot import auto_screenshot

@auto_screenshot("Test de login")
async def test_login(agent):
    # Automáticamente toma captura antes y después
    await agent.run()
    
@auto_screenshot("Test de búsqueda")  
async def test_busqueda(agent):
    # Automáticamente toma captura antes y después
    await agent.run()
```

---

## 🛠️ Herramientas de Ayuda

### Script de Migración Automática

```python
# migrate_script.py - Herramienta para migración automática
import re
import os

def migrar_script(archivo_original, archivo_destino):
    """Migra automáticamente un script a la nueva utilidad"""
    
    with open(archivo_original, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Agregar import si no existe
    if 'from utils_screenshot import' not in contenido:
        contenido = 'from utils_screenshot import ScreenshotManager\n' + contenido
    
    # Reemplazar función compleja por gestor simple
    patron_captura = r'async def capturar_paso\(.*?\):(.*?)return.*?'
    if re.search(patron_captura, contenido, re.DOTALL):
        # Encontrar main() y agregar gestor
        contenido = re.sub(
            r'(async def main\(\):.*?agent = Agent\(.*?\))',
            r'\1\n        screenshots = ScreenshotManager("migrado")',
            contenido,
            flags=re.DOTALL
        )
        
        # Reemplazar llamadas
        contenido = re.sub(
            r'await capturar_paso\(',
            r'await screenshots.capturar_paso(',
            contenido
        )
    
    with open(archivo_destino, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"✅ Script migrado: {archivo_original} -> {archivo_destino}")

# Uso:
# migrar_script('test_demo.py', 'test_demo_migrado.py')
```

### Validador de Migración

```python
# validar_migracion.py
import ast
import os

def validar_script_migrado(archivo):
    """Valida que un script migrado tenga la estructura correcta"""
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    checks = {
        'import_utils': 'from utils_screenshot import' in contenido,
        'screenshot_manager': 'ScreenshotManager(' in contenido,
        'capturar_paso': '.capturar_paso(' in contenido,
        'sin_pyautogui': 'pyautogui.screenshot()' not in contenido,
        'sin_funciones_complejas': 'Estrategia 1:' not in contenido
    }
    
    print(f"📋 Validación para {archivo}:")
    for check, resultado in checks.items():
        status = "✅" if resultado else "❌"
        print(f"  {status} {check}")
    
    return all(checks.values())

# Uso:
# validar_script_migrado('test_demo_migrado.py')
```

---

## 🔧 Resolución de Problemas

### Problema: "No se pueden tomar capturas"
```python
# Verificar que browser_context está disponible
if hasattr(agent, 'browser_context') and agent.browser_context:
    await screenshots.capturar_paso(agent.browser_context, 1, "Test")
else:
    print("❌ browser_context no disponible")
```

### Problema: "Las capturas están vacías o corruptas"
```python
# Verificar que la página está cargada antes de capturar
await asyncio.sleep(1)  # Esperar un poco
await screenshots.capturar_paso(agent.browser_context, 1, "Después de esperar")
```

### Problema: "Errores de permisos en directorio"
```python
# Usar directorio personalizado
screenshots = ScreenshotManager("mi_test", base_dir="./mi_directorio_capturas")
```

### Problema: "Integración con sistema existente no funciona"
```python
# Usar la función de integración específica
from utils_screenshot import integrar_captura_con_sistema

captura_info = await integrar_captura_con_sistema(
    agent.browser_context,
    task_id,
    "Mi descripción"
)

# Verificar resultado
if captura_info:
    print("✅ Integración exitosa")
    print(f"URL: {captura_info['url']}")
else:
    print("❌ Error en integración")
```

---

## 🎉 Beneficios de la Migración

### ✅ Simplicidad
- **Antes:** 50+ líneas de código complejo
- **Después:** 3 líneas simples

### ✅ Confiabilidad
- **Antes:** Múltiples puntos de fallo, fallbacks complejos
- **Después:** Uso directo de browser-use, más estable

### ✅ Mantenibilidad
- **Antes:** Código duplicado en cada script
- **Después:** Lógica centralizada en una utilidad

### ✅ Flexibilidad
- **Antes:** Difícil de personalizar
- **Después:** Múltiples opciones según necesidad

### ✅ Integración
- **Antes:** Código manual para tracking
- **Después:** Integración automática con sistema existente

---

## 🏆 Recomendaciones Finales

1. **Empieza con un script simple** para familiarizarte
2. **Usa ScreenshotManager** para la mayoría de casos
3. **Mantén el backup** de scripts originales hasta confirmar que todo funciona
4. **Aplica la migración gradualmente** no todos los scripts a la vez
5. **Personaliza según tus necesidades** la utilidad es flexible

¡La migración te ahorrará tiempo y hará tu código más confiable! 🚀 