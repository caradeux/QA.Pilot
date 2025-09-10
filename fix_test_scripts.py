# -*- coding: utf-8 -*-
import os
import re
import glob

def fix_test_script(file_path):
    """Actualiza un script de prueba para usar Playwright directamente"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar si ya está actualizado
        if 'from playwright.async_api import async_playwright' in content:
            print(f"✅ {os.path.basename(file_path)} ya está actualizado")
            return
        
        # Reemplazar imports
        content = re.sub(
            r'from langchain_anthropic import ChatAnthropic\nfrom browser_use import Agent, Browser, BrowserConfig',
            'from playwright.async_api import async_playwright',
            content
        )
        
        # Reemplazar configuración del navegador
        content = re.sub(
            r'# Configuración del navegador con parámetros dinámicos\nbrowser = Browser\(\s*config=BrowserConfig\(\s*headless=True,\s*browser_class=\'chromium\',\s*extra_browser_args=\[\]\s*\)\s*\)',
            '',
            content
        )
        
        # Actualizar función de captura
        content = re.sub(
            r'async def tomar_captura_navegador\(agent, descripcion, paso_num=None\):',
            'async def tomar_captura_navegador(page, descripcion, paso_num=None):',
            content
        )
        
        # Actualizar llamada a screenshot
        content = re.sub(
            r'page = agent\.browser_context\.pages\[0\]\s*await page\.screenshot\(path=screenshot_path\)',
            'await page.screenshot(path=screenshot_path, full_page=True)',
            content
        )
        
        # Reemplazar función main completa
        new_main = '''async def main():
    try:
        print("DEBUG: Iniciando test con Playwright directo...")
        print(f"DEBUG: Configuración headless={False}")
        
        async with async_playwright() as p:
            # Lanzar navegador
            browser = await p.chromium.launch(headless=False)
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
        print(f"TRACEBACK: {traceback.format_exc()}")'''
        
        # Reemplazar la función main existente
        content = re.sub(
            r'async def main\(\):.*?if __name__ == "__main__":',
            new_main + '\n\nif __name__ == "__main__":',
            content,
            flags=re.DOTALL
        )
        
        # Escribir el archivo actualizado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ {os.path.basename(file_path)} actualizado correctamente")
        
    except Exception as e:
        print(f"❌ Error actualizando {os.path.basename(file_path)}: {e}")

def main():
    """Actualiza todos los scripts de prueba"""
    test_scripts_dir = 'test_scripts'
    
    if not os.path.exists(test_scripts_dir):
        print(f"❌ Directorio {test_scripts_dir} no encontrado")
        return
    
    # Obtener todos los archivos .py en test_scripts
    script_files = glob.glob(os.path.join(test_scripts_dir, 'test_*.py'))
    
    print(f"🔧 Actualizando {len(script_files)} scripts de prueba...")
    
    for script_file in script_files:
        fix_test_script(script_file)
    
    print("🎉 Proceso de actualización completado")

if __name__ == "__main__":
    main() 