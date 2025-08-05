from playwright.sync_api import sync_playwright

def tomar_captura(page, paso, descripcion):
    nombre_archivo = f"paso_{paso}_{descripcion}.png"
    page.screenshot(path=nombre_archivo, full_page=True)
    print(f"Captura guardada: {nombre_archivo}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    # Paso 0: Inicio
    page.goto("https://www.google.com")
    tomar_captura(page, 0, "Inicio_Pagina_cargada")
    
    # Paso 1: Escribir búsqueda
    page.fill("input[name='q']", "browser-use")
    tomar_captura(page, 1, "Escribe_browser-use")
    
    # Paso 2: Hacer clic en buscar
    page.keyboard.press("Enter")
    page.wait_for_timeout(2000)  # Espera a que cargue resultados
    tomar_captura(page, 2, "Resultados_busqueda")
    
    browser.close()