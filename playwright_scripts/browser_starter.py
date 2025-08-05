
# Browser Starter Script - Controla el lanzamiento único del navegador
from playwright.sync_api import sync_playwright
import os
import sys
import time
import tempfile

# Archivo de control que indicará que un navegador está en ejecución
CONTROL_FILE = os.path.join(tempfile.gettempdir(), "browser_control.txt")

def main():
    # Verificar si ya hay un navegador en ejecución mediante el archivo de control
    if os.path.exists(CONTROL_FILE):
        # Comprobar si el archivo de control es reciente (menos de 30 segundos)
        if time.time() - os.path.getmtime(CONTROL_FILE) < 30:
            print("ERROR: Ya hay un navegador en ejecución.")
            sys.exit(1)
        else:
            # El archivo es antiguo, eliminarlo
            try:
                os.remove(CONTROL_FILE)
                print("Eliminando archivo de control antiguo")
            except:
                print("No se pudo eliminar el archivo de control antiguo")
                sys.exit(1)
    
    # Crear archivo de control
    try:
        with open(CONTROL_FILE, "w") as f:
            f.write(f"started_at={time.time()}")
    except Exception as e:
        print(f"No se pudo crear el archivo de control: {e}")
        sys.exit(1)
    
    print("Iniciando navegador único - NO ABRIR OTRO NAVEGADOR")
    
    # Iniciar Playwright
    try:
        with sync_playwright() as p:
            # Lanzar navegador Chrome
            browser = p.chromium.launch(headless=False)
            
            # Crear contexto y página
            context = browser.new_context(viewport={"width": 1280, "height": 720})
            page = context.new_page()
            
            # Navegar a una URL de ejemplo
            page.goto("https://example.com")
            
            # Esperar a que el usuario cierre el navegador (5 minutos máximo)
            time.sleep(300)
            
            # Cerrar el navegador
            browser.close()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Eliminar archivo de control al terminar
        if os.path.exists(CONTROL_FILE):
            os.remove(CONTROL_FILE)
        print("Navegador cerrado y archivo de control eliminado")

if __name__ == "__main__":
    main()
