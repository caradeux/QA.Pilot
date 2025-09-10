# -*- coding: utf-8 -*-
import sys, os, asyncio, base64, traceback, re, time, random, json
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

# Función para capturar pantalla usando Playwright directamente
async def tomar_captura_navegador(page, descripcion, paso_num=None):
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
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"✅ Captura guardada en: {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"Error al tomar captura del paso: {str(e)}")
        return None

async def main():
    try:
        # Leer configuración headless desde variable de entorno
        headless_str = os.environ.get('HEADLESS', 'true').lower()
        headless = headless_str in ['true', '1', 'yes', 'on']
        
        print("DEBUG: Iniciando test con Playwright directo...")
        print(f"DEBUG: Configuración headless={headless}")
        
        async with async_playwright() as p:
            # Lanzar navegador con configuración headless
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
