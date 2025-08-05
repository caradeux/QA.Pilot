# -*- coding: utf-8 -*-
import sys, os, asyncio, base64, traceback, re, time, random, json, pyautogui
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from browser_use import Agent, Browser, BrowserConfig

load_dotenv()

# Configuración del navegador con parámetros dinámicos
browser = Browser(
    config=BrowserConfig(
        headless=False,  # Usar parámetro dinámico
        extra_browser_args=[
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-dev-shm-usage"
        ]
        # No especificar browser_binary_path para usar navegador built-in de Playwright
    )
)

# --- Captura de pantalla utilitaria ---

# Funciones para tomar capturas usando Playwright y enfocando la ventana
import os
import time
import re
import asyncio
import pygetwindow as gw

async def tomar_captura_navegador(agent, descripcion, paso_num=None):
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
        # Obtener la página activa
        page = agent.browser_context.pages[0]
        # Esperar a que la página esté completamente cargada
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(1)  # Espera adicional para asegurar renderizado
        # Enfocar la ventana del navegador (solo Windows)
        try:
            windows = gw.getWindowsWithTitle('Chrome') or gw.getWindowsWithTitle('Chromium')
            if windows:
                windows[0].activate()
                time.sleep(0.5)
        except Exception as e:
            print(f"No se pudo enfocar la ventana: {e}")
        # Tomar la captura
        await page.screenshot(path=screenshot_path)
        print(f"✅ Captura guardada en: {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"Error al tomar captura del paso: {str(e)}")
    

async def main():
    try:
        print("DEBUG: Iniciando test...")
        print(f"DEBUG: Configuración headless={False}")
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if not anthropic_key:
            env_path = os.path.join(os.getcwd(), '.env')
            if os.path.exists(env_path):
                try:
                    with open(env_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip() and not line.startswith('#'):
                                key, value = line.strip().split('=', 1)
                                if key == 'ANTHROPIC_API_KEY':
                                    anthropic_key = value.strip('"').strip("'")
                                    os.environ['ANTHROPIC_API_KEY'] = anthropic_key
                                    break
                except Exception as e:
                    print(f"Error leyendo .env: {e}")
        if not anthropic_key:
            raise Exception("ANTHROPIC_API_KEY no encontrada")
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=anthropic_key,
            temperature=0.1,
            max_tokens=4000
        )
        agent = Agent(
            task="Navega a https://www.mercadolibre.cl/ y luego: 1. Escribe 'smartphone' en la barra de b?squeda y presiona Enter2. Haz clic en el **t?tulo** del **primer producto**3. Espera a que cargue",
            llm=llm,
            browser=browser
        )
        print("DEBUG: Agente creado")
        await agent.run(max_steps=15)
        print("DEBUG: Test completado exitosamente")

        # --- Captura después de navegar ---
        await tomar_captura_navegador(agent, 'Página cargada', paso_num=0)

        # --- Captura después de cada paso numerado ---
        await tomar_captura_navegador(agent, "Escribe 'smartphone' en la barra de búsqueda y presiona Enter", paso_num=1)
        await tomar_captura_navegador(agent, "Haz clic en el **título** del **primer producto**", paso_num=2)
        await tomar_captura_navegador(agent, "Espera a que cargue", paso_num=3)

        # --- Captura final ---
        await tomar_captura_navegador(agent, 'Test completado', paso_num=999)

    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(f"TRACEBACK: {traceback.format_exc()}")
    finally:
        try:
            await browser.close()
            print("DEBUG: Navegador cerrado")
        except Exception as e:
            print(f"Error al cerrar navegador: {e}")

if __name__ == "__main__":
    asyncio.run(main())
