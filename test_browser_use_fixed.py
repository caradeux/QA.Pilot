# -*- coding: utf-8 -*-
import sys, os, asyncio, base64, traceback, re, time, random, json
from dotenv import load_dotenv
from browser_use import Agent, Browser, BrowserConfig

load_dotenv()

# Configuración del navegador
browser = Browser(
    config=BrowserConfig(
        headless=False,  # Mostrar navegador para debugging
        browser_class='chromium',
        extra_browser_args=[]
    )
)

# Función para capturar pantalla usando Playwright directamente
async def tomar_captura_directa(browser_context, descripcion, paso_num=None):
    try:
        timestamp = int(time.time())
        safe_desc = re.sub(r'[^a-zA-Z0-9_]', '_', descripcion[:30])
        if paso_num:
            filename = f"paso_{paso_num}_{safe_desc}_{timestamp}.png"
        else:
            filename = f"{safe_desc}_{timestamp}.png"
        
        script_name = os.path.splitext(os.path.basename(__file__))[0]
        task_id = script_name.replace('test_', '') if script_name.startswith('test_') else script_name
        screenshot_subdir = os.path.join(os.getcwd(), "test_screenshots", task_id)
        os.makedirs(screenshot_subdir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_subdir, filename)
        
        # Usar Playwright directamente para capturar
        pages = browser_context.pages
        if pages:
            page = pages[0]  # Primera página
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"✅ Captura guardada en: {screenshot_path}")
            return screenshot_path
        else:
            print("❌ No hay páginas disponibles para capturar")
            return None
    except Exception as e:
        print(f"Error al tomar captura: {str(e)}")
        traceback.print_exc()
        return None

async def main():
    try:
        print("DEBUG: Iniciando test con browser-use...")
        print(f"DEBUG: Configuración headless={False}")
        
        # Usar una tarea simple que no requiera LLM
        agent = Agent(
            task="Navega a https://www.google.com y toma una captura de pantalla",
            browser=browser
        )
        
        print("DEBUG: Agente creado")
        
        # Ejecutar solo la navegación básica
        await agent.browser_context.new_page()
        page = agent.browser_context.pages[0]
        await page.goto('https://www.google.com')
        await page.wait_for_load_state('networkidle')
        
        print("DEBUG: Navegación completada")
        
        # Tomar capturas usando nuestra función personalizada
        await tomar_captura_directa(agent.browser_context, 'Página cargada', paso_num=1)
        await tomar_captura_directa(agent.browser_context, 'Test completado', paso_num=2)
        
        print("DEBUG: Test completado exitosamente")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(f"TRACEBACK: {traceback.format_exc()}")
    finally:
        try:
            await browser.close()
            print("DEBUG: Navegador cerrado")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main()) 