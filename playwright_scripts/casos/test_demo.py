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
        
        # Verificar si la clave es SecretStr
        if isinstance(anthropic_key, SecretStr):
            anthropic_key = anthropic_key.get_secret_value()
            
        llm = ChatAnthropic(
            model_name="claude-3-5-sonnet-20240620",
            api_key=anthropic_key,
            temperature=0.0,
            timeout=100
        )
        print("DEBUG: LLM configurado correctamente")

        print("DEBUG: Creando agente...")
        # Definir la tarea como variable separada
        task_instructions = """1. Buscar 'smartphone'2. Seleccionar el primer resultado3. Ver detalles"""
        
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
        print(f"DEBUG: Navegando a la URL inicial: https://www.mercadolibre.cl")
        await agent.browser_context.navigate_to("https://www.mercadolibre.cl")
        print("DEBUG: Navegación inicial completada")
        
        # Hacer una pausa breve para permitir que la página se cargue completamente
        await asyncio.sleep(2)
        
        # Capturar pantalla inicial
        await capturar_paso(agent.browser_context, 0, "Inicio - Página cargada")


        # Código para ejecutar pasos individuales
        # Nota: Esta implementación usa la API actualizada de Browser-Use
        # que no permite pasar 'task' como parámetro a agent.run()
        
        # Para ejecutar pasos individuales, usaremos una técnica alternativa
        # enviando instrucciones al navegador directamente
        
        
        # Ejecutando paso 1: Buscar 'smartphone'
        print(f"Ejecutando paso 1: Buscar 'smartphone'")
        
        # La instrucción específica para este paso
        instruccion_paso_1 = '''
        Buscar 'smartphone'
        '''
        
        # Enviar la instrucción directamente al navegador
        print(f"Ejecutando instrucción para paso 1...")
        
        # Instrucción personalizada para cada tipo de paso
        if "buscar 'smartphone'" == "buscar 'smartphone'" or "buscar" in "buscar 'smartphone'":
            # Localizar el elemento de búsqueda y llenarlo
            search_input = await agent.browser_context.get_locate_element_by_css_selector('input[name="as_word"]')
            if search_input:
                await search_input.fill('smartphone')
                # Hacer clic en el botón de búsqueda
                search_button = await agent.browser_context.get_locate_element_by_css_selector('.nav-search-btn')
                if search_button:
                    await search_button.click()
                else:
                    print("No se encontró el botón de búsqueda")
            else:
                print("No se encontró el campo de búsqueda")
        elif "seleccionar" in "buscar 'smartphone'" or "primer resultado" in "buscar 'smartphone'":
            # Hacer clic en el primer resultado
            result_link = await agent.browser_context.get_locate_element_by_css_selector('.ui-search-result__content a')
            if result_link:
                await result_link.click()
            else:
                print("No se encontró el primer resultado")
        elif "ver" in "buscar 'smartphone'" or "detalle" in "buscar 'smartphone'":
            # Simplemente esperar a que se cargue la página de detalles
            await asyncio.sleep(2)
        else:
            # Para otros tipos de pasos, se necesitaría implementar la lógica específica
            print(f"Ejecutando paso genérico 1: Buscar 'smartphone'")
            # Si no sabemos manejar este tipo de paso, dejar que el agente lo maneje
            # No usar 'task' como parámetro - usar la API correcta
            await agent.run(max_steps=5)
        
        # Esperar un momento para que se complete la acción
        await asyncio.sleep(1)
        
        # Capturar pantalla de este paso
        await capturar_paso(agent.browser_context, 1, "Buscar 'smartphone'")
        
        # Ejecutando paso 2: Seleccionar el primer resultado
        print(f"Ejecutando paso 2: Seleccionar el primer resultado")
        
        # La instrucción específica para este paso
        instruccion_paso_2 = '''
        Seleccionar el primer resultado
        '''
        
        # Enviar la instrucción directamente al navegador
        print(f"Ejecutando instrucción para paso 2...")
        
        # Instrucción personalizada para cada tipo de paso
        if "seleccionar el primer resultado" == "buscar 'smartphone'" or "buscar" in "seleccionar el primer resultado":
            # Localizar el elemento de búsqueda y llenarlo
            search_input = await agent.browser_context.get_locate_element_by_css_selector('input[name="as_word"]')
            if search_input:
                await search_input.fill('smartphone')
                # Hacer clic en el botón de búsqueda
                search_button = await agent.browser_context.get_locate_element_by_css_selector('.nav-search-btn')
                if search_button:
                    await search_button.click()
                else:
                    print("No se encontró el botón de búsqueda")
            else:
                print("No se encontró el campo de búsqueda")
        elif "seleccionar" in "seleccionar el primer resultado" or "primer resultado" in "seleccionar el primer resultado":
            # Hacer clic en el primer resultado
            result_link = await agent.browser_context.get_locate_element_by_css_selector('.ui-search-result__content a')
            if result_link:
                await result_link.click()
            else:
                print("No se encontró el primer resultado")
        elif "ver" in "seleccionar el primer resultado" or "detalle" in "seleccionar el primer resultado":
            # Simplemente esperar a que se cargue la página de detalles
            await asyncio.sleep(2)
        else:
            # Para otros tipos de pasos, se necesitaría implementar la lógica específica
            print(f"Ejecutando paso genérico 2: Seleccionar el primer resultado")
            # Si no sabemos manejar este tipo de paso, dejar que el agente lo maneje
            # No usar 'task' como parámetro - usar la API correcta
            await agent.run(max_steps=5)
        
        # Esperar un momento para que se complete la acción
        await asyncio.sleep(1)
        
        # Capturar pantalla de este paso
        await capturar_paso(agent.browser_context, 2, "Seleccionar el primer resultado")
        
        # Ejecutando paso 3: Ver detalles
        print(f"Ejecutando paso 3: Ver detalles")
        
        # La instrucción específica para este paso
        instruccion_paso_3 = '''
        Ver detalles
        '''
        
        # Enviar la instrucción directamente al navegador
        print(f"Ejecutando instrucción para paso 3...")
        
        # Instrucción personalizada para cada tipo de paso
        if "ver detalles" == "buscar 'smartphone'" or "buscar" in "ver detalles":
            # Localizar el elemento de búsqueda y llenarlo
            search_input = await agent.browser_context.get_locate_element_by_css_selector('input[name="as_word"]')
            if search_input:
                await search_input.fill('smartphone')
                # Hacer clic en el botón de búsqueda
                search_button = await agent.browser_context.get_locate_element_by_css_selector('.nav-search-btn')
                if search_button:
                    await search_button.click()
                else:
                    print("No se encontró el botón de búsqueda")
            else:
                print("No se encontró el campo de búsqueda")
        elif "seleccionar" in "ver detalles" or "primer resultado" in "ver detalles":
            # Hacer clic en el primer resultado
            result_link = await agent.browser_context.get_locate_element_by_css_selector('.ui-search-result__content a')
            if result_link:
                await result_link.click()
            else:
                print("No se encontró el primer resultado")
        elif "ver" in "ver detalles" or "detalle" in "ver detalles":
            # Simplemente esperar a que se cargue la página de detalles
            await asyncio.sleep(2)
        else:
            # Para otros tipos de pasos, se necesitaría implementar la lógica específica
            print(f"Ejecutando paso genérico 3: Ver detalles")
            # Si no sabemos manejar este tipo de paso, dejar que el agente lo maneje
            # No usar 'task' como parámetro - usar la API correcta
            await agent.run(max_steps=5)
        
        # Esperar un momento para que se complete la acción
        await asyncio.sleep(1)
        
        # Capturar pantalla de este paso
        await capturar_paso(agent.browser_context, 3, "Ver detalles")
        
        
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
