# -*- coding: utf-8 -*-
import sys, os, asyncio, base64, traceback, re, time, random, json, pyautogui
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

# Configuración del navegador con parámetros dinámicos
browser = Browser(
    config=BrowserConfig(
        headless=False,  # Usar parámetro dinámico
        # No especificar browser_binary_path para usar navegador built-in de Playwright
    )
)

# --- Captura de pantalla utilitaria ---

# Funciones para tomar capturas usando pyautogui
import os
import time
import re
import pyautogui

async def tomar_captura_navegador(page, descripcion, paso_num=None):
    try:
        timestamp = int(time.time())
        safe_desc = re.sub(r'[^a-zA-Z0-9_]', '_', descripcion[:30])
        
        if paso_num:
            filename = f"paso_{paso_num}_{safe_desc}_{timestamp}.png"
        else:
            filename = f"{safe_desc}_{timestamp}.png"
        
        # Crear directorio para capturas
        script_name = os.path.splitext(os.path.basename(__file__))[0]
        task_id = script_name.replace('test_', '') if script_name.startswith('test_') else script_name
        screenshot_subdir = os.path.join(os.getcwd(), "test_screenshots", task_id)
        os.makedirs(screenshot_subdir, exist_ok=True)
        
        screenshot_path = os.path.join(screenshot_subdir, filename)
        
        # Estrategia 1: Usar browser_context del agente directamente
        try:
            if hasattr(agent, 'browser_context') and agent.browser_context:
                print(f"DEBUG: Intentando captura con browser_context del agente...")
                # Asegurar que el contexto esté inicializado
                try:
                    await agent.browser_context.get_state()
                except:
                    pass  # Si falla, continuamos
                
                screenshot_b64 = await agent.browser_context.take_screenshot(full_page=False)
                
                # Convertir base64 a imagen
                import base64
                from PIL import Image
                import io
                
                screenshot_data = base64.b64decode(screenshot_b64)
                screenshot_image = Image.open(io.BytesIO(screenshot_data))
                screenshot_image.save(screenshot_path)
                
                print(f"✅ Captura del navegador guardada en: {screenshot_path}")
                return screenshot_path
        except Exception as e:
            print(f"DEBUG: Error con browser_context del agente: {e}")
        
        # Estrategia 2: Usar browser y obtener el contexto activo
        try:
            if hasattr(agent, 'browser') and agent.browser:
                print(f"DEBUG: Intentando captura vía browser...")
                # Obtener el contexto activo del browser
                if hasattr(agent.browser, 'contexts') and agent.browser.contexts:
                    context = agent.browser.contexts[0]  # Primer contexto
                    screenshot_b64 = await context.take_screenshot(full_page=False)
                    
                    import base64
                    from PIL import Image
                    import io
                    
                    screenshot_data = base64.b64decode(screenshot_b64)
                    screenshot_image = Image.open(io.BytesIO(screenshot_data))
                    screenshot_image.save(screenshot_path)
                    
                    print(f"✅ Captura del navegador (vía browser) guardada en: {screenshot_path}")
                    return screenshot_path
                else:
                    print("DEBUG: No se encontraron contextos en el browser")
        except Exception as e:
            print(f"DEBUG: Error con browser: {e}")
        
        # Estrategia 3: Usar página activa directamente
        try:
            if hasattr(agent, 'browser_context') and agent.browser_context:
                print(f"DEBUG: Intentando captura con página activa...")
                # Obtener la página activa
                pages = agent.browser_context.pages
                if pages:
                    page = pages[0]  # Primera página
                    screenshot_b64 = await page.screenshot(full_page=False)
                    
                    # Convertir bytes a base64 si es necesario
                    if isinstance(screenshot_b64, bytes):
                        import base64
                        screenshot_b64 = base64.b64encode(screenshot_b64).decode()
                    
                    import base64
                    from PIL import Image
                    import io
                    
                    screenshot_data = base64.b64decode(screenshot_b64)
                    screenshot_image = Image.open(io.BytesIO(screenshot_data))
                    screenshot_image.save(screenshot_path)
                    
                    print(f"✅ Captura de página activa guardada en: {screenshot_path}")
                    return screenshot_path
        except Exception as e:
            print(f"DEBUG: Error con página activa: {e}")
            
        # Estrategia 4: Fallback - usar pyautogui pero con ventana enfocada
        try:
            print("DEBUG: Usando captura del sistema como fallback...")
            # Intentar enfocar la ventana del navegador antes de capturar
            import pygetwindow as gw
            try:
                # Buscar ventana del navegador
                chrome_windows = gw.getWindowsWithTitle('Chrome')
                if not chrome_windows:
                    chrome_windows = gw.getWindowsWithTitle('Chromium')
                if not chrome_windows:
                    chrome_windows = gw.getWindowsWithTitle('Microsoft Edge')
                
                if chrome_windows:
                    chrome_windows[0].activate()
                    time.sleep(0.5)  # Esperar un poco para que se enfoque
            except:
                pass  # Si no se puede enfocar, continuamos
            
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)
            print(f"⚠️  Captura del sistema (fallback) guardada en: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            print(f"DEBUG: Error con fallback: {e}")
        
        # Si todo falla, crear una imagen de error
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((50, 50), f"Error capturando pantalla: {descripcion}", fill='red')
            img.save(screenshot_path)
            print(f"❌ Imagen de error guardada en: {screenshot_path}")
            return screenshot_path
        except:
            return None
        
    except Exception as e:
        print(f"ERROR al tomar captura: {str(e)}")
        return None

async def tomar_captura_inicial(agent=None):
    try:
        print("DEBUG: Tomando captura inicial...")
        os.makedirs(os.path.join(os.getcwd(), "test_screenshots"), exist_ok=True)
        await tomar_captura_navegador(agent, "inicio_test")
        print("Captura inicial tomada")
    except Exception as e:
        print(f"Error al tomar captura inicial: {str(e)}")

async def tomar_captura_final(agent=None):
    try:
        print("DEBUG: Tomando captura final...")
        await tomar_captura_navegador(agent, "fin_test")
        print("Captura final tomada")
    except Exception as e:
        print(f"Error al tomar captura final: {str(e)}")

async def tomar_captura_paso(agent, descripcion, paso_num=None):
    try:
        print(f"DEBUG: Captura del paso {paso_num}: {descripcion}")
        await tomar_captura_navegador(agent, descripcion, paso_num)
        print(f"Captura del paso {paso_num if paso_num else 'general'}: {descripcion}")
    except Exception as e:
        print(f"Error al tomar captura del paso: {str(e)}")


async def main():
    try:
                # Leer configuración headless desde variable de entorno
        headless_str = os.environ.get('HEADLESS', 'true').lower()
        headless = headless_str in ['true', '1', 'yes', 'on']
        
        print("DEBUG: Iniciando test con Playwright directo...")
        print(f"DEBUG: Configuración headless={headless})
        
        async with async_playwright() as p:
            # Lanzar navegador
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context()
            page = await context.new_page()
            
            print("DEBUG: Navegador iniciado")
            
            # Navegar a MercadoLibre
            print("🌐 Navegando a MercadoLibre...")
            await page.goto('https://www.mercadolibre.cl/')
            await page.wait_for_load_state('domcontentloaded')
            
            # Captura después de navegar
            await tomar_captura_navegador(page, 'Página cargada', paso_num=0)
            
            # Buscar "smartphone"
            print("🔍 Buscando 'smartphone'...")
            try:
                search_box = await page.wait_for_selector('input[name="as_word"]', timeout=10000)
                await search_box.fill('smartphone')
                await search_box.press('Enter')
                await page.wait_for_load_state('domcontentloaded')
                
                # Captura después de buscar
                await tomar_captura_navegador(page, "Escribe 'smartphone' en la barra de búsqueda y presiona Enter", paso_num=1)
                
                # Hacer clic en el primer producto
                print("🖱️ Haciendo clic en el primer producto...")
                first_product = await page.wait_for_selector('h2.ui-search-item__title', timeout=10000)
                await first_product.click()
                await page.wait_for_load_state('domcontentloaded')
                
                # Captura después de hacer clic
                await tomar_captura_navegador(page, "Haz clic en el **título** del **primer producto**", paso_num=2)
                
                # Esperar a que cargue
                print("⏳ Esperando a que cargue...")
                await page.wait_for_timeout(3000)
                
                # Captura final
                await tomar_captura_navegador(page, 'Test completado', paso_num=3)
                
            except Exception as e:
                print(f"Error durante la ejecución: {e}")
                # Tomar captura de error
                await tomar_captura_navegador(page, 'Error durante ejecución', paso_num=999)
            
            print("DEBUG: Test completado")
            
            await browser.close()
            print("DEBUG: Navegador cerrado")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(f"TRACEBACK: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(main())
