📸 Guía para implementar y usar capturas de pantalla en browser-use
Este documento explica cómo integrar la funcionalidad de capturas de pantalla con Playwright en tu proyecto basado en el repositorio browser-use.

1. Archivos y clases que debes modificar
browser_use/browser/browser.py: aquí va la función principal para tomar capturas (take_screenshot) y la integración en la clase Browser.

browser_use/agent.py o donde esté la clase Agent o BrowserSession: para invocar la función de captura según las tareas o flags.

Código que maneja CLI o UI: para añadir flags relacionados a capturas (como --screenshot, --full_page, etc).

2. Añadir los imports necesarios
Agrega al inicio de los archivos donde usarás la función:

python
Copiar
Editar
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import logging
3. Función principal para capturar pantalla
Coloca esta función en browser_use/browser/browser.py:

python
Copiar
Editar
def take_screenshot(url: str,
                    path: str = None,
                    full_page: bool = False,
                    clip: dict = None,
                    selector: str = None,
                    omit_background: bool = False,
                    encoding: str = None,
                    headless: bool = True,
                    wait_until: str = 'networkidle',
                    timeout: int = 30000) -> bytes:
    """
    Toma una captura de pantalla del navegador usando Playwright.

    Parámetros:
      - url: URL a visitar.
      - path: ruta para guardar la imagen (opcional).
      - full_page: si se debe capturar toda la página.
      - clip: dict con {x, y, width, height} para recortar.
      - selector: CSS selector para capturar solo un elemento.
      - omit_background: si omite fondo en formato png con transparencia.
      - encoding: si 'base64', retorna la imagen en base64.
      - headless: ejecuta navegador en modo headless o visible.
      - wait_until: evento para esperar antes de capturar ('load', 'domcontentloaded', 'networkidle').
      - timeout: tiempo máximo de espera en ms.

    Retorna:
      - Bytes de la imagen o string base64 (si encoding='base64').
    """
    logging.info(f"Launching browser – headless={headless}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        logging.info(f"Navigating to {url} (wait_until={wait_until}, timeout={timeout}ms)")
        page.goto(url, wait_until=wait_until, timeout=timeout)

        if selector:
            logging.info(f"Waiting for selector: {selector}")
            page.wait_for_selector(selector, timeout=timeout)
            img = page.locator(selector).screenshot(path=path,
                                                     omit_background=omit_background,
                                                     encoding=encoding)
        else:
            opts = {k: v for k, v in dict(path=path,
                                          full_page=full_page,
                                          clip=clip,
                                          omit_background=omit_background,
                                          encoding=encoding).items() if v is not None}
            logging.info(f"Taking screenshot with opts: {opts}")
            img = page.screenshot(**opts)

        browser.close()
        return img
4. Integrar la función en la clase Browser
Dentro de browser_use/browser/browser.py, localiza o crea la clase Browser e incorpora:

python
Copiar
Editar
class Browser:
    # Ejemplo simple de integración
    def __init__(self, debug=False):
        self.debug = debug

    def screenshot(self, url: str, **kwargs):
        try:
            return take_screenshot(url,
                                   headless=(not self.debug),
                                   **kwargs)
        except PlaywrightTimeoutError as e:
            logging.error(f"Screenshot timeout for {url}: {e}")
            raise
5. Invocar la captura desde la clase Agent o BrowserSession
En tu clase que orquesta la ejecución (Agent, BrowserSession o similar), asegúrate de que cuando el usuario active la opción --screenshot, llame a:

python
Copiar
Editar
img = browser.screenshot(url,
                         path=path,
                         full_page=full_page,
                         clip=clip,
                         selector=selector,
                         omit_background=omit_background,
                         encoding=encoding,
                         headless=headless,
                         wait_until=wait_until,
                         timeout=timeout)
6. Añadir y manejar flags CLI o inputs UI para capturas
Para que el usuario pueda controlar la captura, agrega estas opciones a tu parser de argumentos CLI:

python
Copiar
Editar
parser.add_argument('--screenshot', action='store_true', help='Tomar captura de pantalla')
parser.add_argument('--full_page', action='store_true', help='Captura de pantalla full-page')
parser.add_argument('--clip', type=str, help='Recorte en formato x,y,width,height')
parser.add_argument('--selector', type=str, help='Capturar selector CSS específico')
parser.add_argument('--omit_background', action='store_true', help='Omitir fondo en png')
parser.add_argument('--encoding', choices=['base64'], help='Codificación de la imagen')
parser.add_argument('--show-browser', action='store_true', help='Mostrar navegador (no headless)')
parser.add_argument('--wait_until', type=str, default='networkidle', help='Evento de espera')
parser.add_argument('--timeout', type=int, default=30000, help='Timeout en milisegundos')
Convierte la opción clip en un diccionario:

python
Copiar
Editar
if args.clip:
    x, y, w, h = map(int, args.clip.split(','))
    clip = dict(x=x, y=y, width=w, height=h)
else:
    clip = None
7. Ejemplo de ejecución CLI
bash
Copiar
Editar
browser-use run --url https://example.com \
  --screenshot \
  --full_page \
  --path out.png \
  --show-browser

browser-use run --url https://example.com \
  --screenshot \
  --clip "0,0,800,600" \
  --omit_background

browser-use run --url https://example.com \
  --screenshot \
  --selector ".main" \
  --encoding base64
8. Guardar o mostrar la imagen
Si path está definido y encoding no es base64, la imagen se guarda en disco.

Si encoding='base64', la función devuelve un string codificado en base64 que puede ser mostrado o enviado.

9. Tests unitarios recomendados
Crear tests para validar capturas:

python
Copiar
Editar
def test_full_page_screenshot(tmp_path):
    img = take_screenshot("https://example.com", full_page=True,
                          path=str(tmp_path/"full.png"))
    assert (tmp_path/"full.png").exists()

def test_selector_screenshot_base64():
    b64 = take_screenshot("https://example.com",
                          selector="h1",
                          encoding="base64")
    assert isinstance(b64, str) and len(b64) > 0
10. Logs y manejo de errores
Se usa logging.info para seguimiento.

Captura excepciones PlaywrightTimeoutError para manejar timeouts.

Siempre cerrar el navegador con browser.close().

