from pydantic import SecretStr
# -*- coding: utf-8 -*-
import sys, os, asyncio, base64, traceback, re, time, random, json
# Eliminar pyautogui, no lo necesitamos porque usamos capturas del navegador
from langchain_anthropic import ChatAnthropic
from browser_use import Agent
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig


# Función para capturar pantalla en cada paso
async def capturar_paso(browser_context, num_paso, descripcion):
    try:
        # Tomar captura de pantalla
        screenshot_b64 = await browser_context.take_screenshot(full_page=True)
        
        # Convertir a bytes
        screenshot_bytes = base64.b64decode(screenshot_b64)
        
        # Crear nombre de archivo seguro para el paso
        timestamp = int(time.time())
        safe_desc = re.sub(r'[^a-zA-Z0-9_]', '_', descripcion[:30])
        filename = f"paso_{num_paso}_{safe_desc}_{timestamp}.png"
        
        # Obtener el nombre del script actual para usar como subdirectorio
        # __file__ se refiere al script que se está ejecutando actualmente
        script_name_without_ext = os.path.splitext(os.path.basename(__file__))[0]
        screenshot_subdir = os.path.join(os.getcwd(), "test_screenshots", script_name_without_ext)
        os.makedirs(screenshot_subdir, exist_ok=True) # Asegurar que el subdirectorio exista
        
        # Guardar archivo en el subdirectorio
        filepath = os.path.join(screenshot_subdir, filename)
        with open(filepath, 'wb') as f:
            f.write(screenshot_bytes)
        
        print(f"Captura del paso {num_paso} guardada en: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error al capturar paso {num_paso}: {str(e)}")
        traceback.print_exc()
        return None


async def main():
    browser = None
    agent = None
    
    try:
        print("DEBUG: Iniciando test...")
        print("DEBUG: Inicializando browser...")
        browser = Browser(
            config=BrowserConfig(
                headless=False,
                new_context_config=BrowserContextConfig(
                    browser_window_size={"width": 1920, "height": 1080},
                    minimum_wait_page_load_time=1.0,
                    wait_for_network_idle_page_load_time=2.0,
                    maximum_wait_page_load_time=15.0,
                    wait_between_actions=0.5
                )
            )
        )
        print("DEBUG: Browser inicializado correctamente con viewport 1920x1080")

        print("DEBUG: Configurando LLM...")
        # Obtener clave API
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if not anthropic_key:
            try:
                from dotenv import load_dotenv
                load_dotenv()
                anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            except ImportError:
                pass
                
        if not anthropic_key:
            env_path = os.path.join(os.getcwd(), '.env')
            if os.path.exists(env_path):
                try:
                    with open(env_path, 'r') as f:
                        for line in f:
                            if line.startswith('ANTHROPIC_API_KEY='):
                                anthropic_key = line.split('=', 1)[1].strip()
                                break
                except:
                    pass
        
        if not anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY no encontrada")
        
        llm = # Verificar si la clave es SecretStr
if isinstance(anthropic_key, SecretStr):
    anthropic_key = anthropic_key.get_secret_value()
# Verificar si la clave es SecretStr
if isinstance(anthropic_key, SecretStr):
    anthropic_key = anthropic_key.get_secret_value()
# Verificar si la clave es SecretStr
if isinstance(anthropic_key, SecretStr):
    anthropic_key = anthropic_key.get_secret_value()
# Verificar si la clave es SecretStr
if isinstance(anthropic_key, SecretStr):
    anthropic_key = anthropic_key.get_secret_value()
# Verificar si la clave es SecretStr
if isinstance(anthropic_key, SecretStr):
    anthropic_key = anthropic_key.get_secret_value()
# Verificar si la clave es SecretStr
if isinstance(anthropic_key, SecretStr):
    anthropic_key = anthropic_key.get_secret_value()
# Verificar si la clave es SecretStr
if isinstance(anthropic_key, SecretStr):
    anthropic_key = anthropic_key.get_secret_value()
# Verificar si la clave es SecretStr
if isinstance(anthropic_key, SecretStr):
    anthropic_key = anthropic_key.get_secret_value()
# Verificar si la clave es SecretStr
if isinstance(anthropic_key, SecretStr):
    anthropic_key = anthropic_key.get_secret_value()
ChatAnthropic(
            model_name="claude-3-5-sonnet-20240620",
            api_key=anthropic_key,
    # Verificar si la clave de API es un objeto SecretStr y extraer su valor
    if isinstance(anthropic_key, SecretStr):
        anthropic_key = anthropic_key.get_secret_value()
    # Verificar si la clave de API es un objeto SecretStr y extraer su valor
    if isinstance(anthropic_key, SecretStr):
        anthropic_key = anthropic_key.get_secret_value()
    # Verificar si la clave de API es un objeto SecretStr y extraer su valor
    if isinstance(anthropic_key, SecretStr):
        anthropic_key = anthropic_key.get_secret_value()
    # Verificar si la clave de API es un objeto SecretStr y extraer su valor
    if isinstance(anthropic_key, SecretStr):
        anthropic_key = anthropic_key.get_secret_value()
    # Verificar si la clave de API es un objeto SecretStr y extraer su valor
    if isinstance(anthropic_key, SecretStr):
        anthropic_key = anthropic_key.get_secret_value()
    # Verificar si la clave de API es un objeto SecretStr y extraer su valor
    if isinstance(anthropic_key, SecretStr):
        anthropic_key = anthropic_key.get_secret_value()
    # Verificar si la clave de API es un objeto SecretStr y extraer su valor
    if isinstance(anthropic_key, SecretStr):
        anthropic_key = anthropic_key.get_secret_value()
    # Verificar si la clave de API es un objeto SecretStr y extraer su valor
    if isinstance(anthropic_key, SecretStr):
        anthropic_key = anthropic_key.get_secret_value()
    # Verificar si la clave de API es un objeto SecretStr y extraer su valor
    if isinstance(anthropic_key, SecretStr):
        anthropic_key = anthropic_key.get_secret_value()
            temperature=0.0,
            timeout=100
        )
        print("DEBUG: LLM configurado correctamente")

        print("DEBUG: Creando agente...")
        # Definir la tarea como variable separada
        task_instructions = """1. Buscar Noticias2. Ingresa al primer resultado"""
        
        agent = Agent(
            task=task_instructions,
            llm=llm,
            browser=browser,
            use_vision=True
        )
        print("DEBUG: Agente creado correctamente")

        # Crear directorio para capturas si no existe (directorio base)
        # El subdirectorio específico del test se creará en la función capturar_paso
        os.makedirs(os.path.join(os.getcwd(), "test_screenshots"), exist_ok=True)

        # Navegar a la URL inicial
        print(f"DEBUG: Navegando a la URL inicial: https://www.google.cl")
        await agent.browser_context.navigate_to("https://www.google.cl")
        print("DEBUG: Navegación inicial completada")
        
        # Hacer una pausa breve para permitir que la página se cargue completamente
        await asyncio.sleep(2)
        
        # Capturar pantalla inicial
        await capturar_paso(agent.browser_context, 0, "Inicio - Página cargada")


        # Ejecutando paso 1: Buscar Noticias
        print(f"Ejecutando paso 1: Buscar Noticias")
        # Agregar un pequeño retraso para permitir que la página se actualice
        await asyncio.sleep(1)
        # Capturar pantalla para este paso
        await capturar_paso(agent.browser_context, 1, "Buscar Noticias")

        # Ejecutando paso 2: Ingresa al primer resultado
        print(f"Ejecutando paso 2: Ingresa al primer resultado")
        # Agregar un pequeño retraso para permitir que la página se actualice
        await asyncio.sleep(1)
        # Capturar pantalla para este paso
        await capturar_paso(agent.browser_context, 2, "Ingresa al primer resultado")

        
        # Ejecutar el agente
        print("DEBUG: Ejecutando agente con las instrucciones...")
        # No pasar task_instructions a agent.run() para evitar errores con la API actual
        result = await agent.run(max_steps=50)
        print("INFO: Resultado final:", result)
        
        # Capturar pantalla final
        await capturar_paso(agent.browser_context, 999, "Resultado final")
        
        # Devolver resultado
        return result
    except Exception as e:
        print("ERROR GENERAL:", str(e))
        traceback.print_exc()
        raise
    finally:
        if browser:
            print("DEBUG: Cerrando navegador...")
            await browser.close()

if __name__ == "__main__":
    try:
        print("DEBUG: Iniciando ejecución del script")
            
        # Ejecutar función principal
        print("Iniciando ejecución principal")
        asyncio.run(main())
        print("Ejecución completada con éxito")
        sys.exit(0)
    except Exception as e:
        print("ERROR FATAL:", str(e))
        traceback.print_exc()
        sys.exit(1)
