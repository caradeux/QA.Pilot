# -*- coding: utf-8 -*-
import asyncio
import os
import time
from playwright.async_api import async_playwright

async def test_screenshot():
    """Prueba simple de captura de pantalla con Playwright"""
    try:
        print("🔍 Iniciando prueba de captura de pantalla...")
        
        async with async_playwright() as p:
            # Lanzar navegador
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            print("🌐 Navegando a Google...")
            await page.goto('https://www.google.com')
            await page.wait_for_load_state('networkidle')
            
            # Crear directorio para capturas
            screenshot_dir = os.path.join(os.getcwd(), "test_screenshots", "test_simple")
            os.makedirs(screenshot_dir, exist_ok=True)
            
            # Tomar captura
            timestamp = int(time.time())
            screenshot_path = os.path.join(screenshot_dir, f"test_simple_{timestamp}.png")
            
            print(f"📸 Tomando captura de pantalla...")
            await page.screenshot(path=screenshot_path, full_page=True)
            
            print(f"✅ Captura guardada en: {screenshot_path}")
            
            # Verificar que el archivo existe
            if os.path.exists(screenshot_path):
                file_size = os.path.getsize(screenshot_path)
                print(f"📁 Archivo creado correctamente. Tamaño: {file_size} bytes")
            else:
                print("❌ Error: El archivo no se creó")
            
            await browser.close()
            print("🔚 Navegador cerrado")
            
    except Exception as e:
        print(f"❌ Error en la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_screenshot()) 