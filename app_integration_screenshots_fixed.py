# -*- coding: utf-8 -*-
"""
Integración Corregida de Capturas Mejoradas para App Web
========================================================
Esta versión reemplaza COMPLETAMENTE la función original con navegación manual
que garantiza que el navegador sea visible, igual que test_demo_mejorado_fixed.py
"""

import os
import sys
import asyncio
import traceback
import threading
import time
import uuid
from datetime import datetime
from utils_screenshot import ScreenshotManager

# Importar elementos necesarios
from app import test_status_db, db_lock, SCREENSHOTS_DIR, history_db

def run_test_background_with_browser_use_direct(task_id, url, instrucciones, headless, max_tiempo, screenshots, 
                                              gemini_key, model_name='claude-3-5-sonnet-20240620', browser='chrome', fullscreen=True):
    """
    Implementación DIRECTA usando browser-use con navegación manual.
    Garantiza que el navegador sea visible y las capturas funcionen.
    """
    print(f"🚀 [DIRECT] Iniciando test {task_id} con browser-use directo")
    print(f"📷 [DIRECT] Screenshots: {screenshots}, Headless: {headless}")
    print(f"🌐 [DIRECT] URL: {url}")
    
    # ⭐ VERIFICAR Y CORREGIR CONFIGURACIÓN DE NAVEGADOR
    # Si el usuario no marcó "modo sigiloso" (headless=False), asegurar que el navegador sea visible
    if not headless:
        print(f"✅ [DIRECT] Usuario quiere navegador VISIBLE - forzando headless=False")
        headless = False  # Asegurar que sea False
    else:
        print(f"⚠️ [DIRECT] Usuario seleccionó modo sigiloso - navegador será headless")
    
    # Inicializar gestor de capturas
    screenshot_manager = None
    if screenshots:
        try:
            screenshot_manager = ScreenshotManager(task_id=task_id[:8])
            test_dir = screenshot_manager.obtener_directorio()
            print(f"📁 [DIRECT] Capturas en: {test_dir}")
        except Exception as e:
            print(f"❌ [DIRECT] Error en ScreenshotManager: {e}")
    
    # Función para ejecutar test con browser-use
    async def ejecutar_con_browser_use():
        browser_instance = None
        agent = None
        
        try:
            # Actualizar estado
            with db_lock:
                if task_id in test_status_db:
                    test_status_db[task_id].update({
                        'status': 'running',
                        'message': 'Iniciando navegador...',
                        'current_action': 'Configurando browser-use...'
                    })
            
            # ⭐ IMPORTAR BROWSER-USE
            print(f"🔄 [DIRECT] Importando browser-use...")
            from browser_use import ChatAnthropic
            from browser_use import Agent, Browser, BrowserConfig, BrowserContextConfig
            
            # ⭐ CONFIGURAR LLM
            print(f"🤖 [DIRECT] Configurando LLM...")
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            if not anthropic_key:
                # Leer desde .env
                env_path = os.path.join(os.getcwd(), '.env')
                if os.path.exists(env_path):
                    with open(env_path, 'r') as f:
                        for line in f:
                            if line.startswith('ANTHROPIC_API_KEY='):
                                anthropic_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                                break
            
            if not anthropic_key:
                raise ValueError("❌ ANTHROPIC_API_KEY no encontrada")
            
            llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                api_key=anthropic_key,
                temperature=0.1,
                max_tokens=4000
            )
            
            # ⭐ CONFIGURAR NAVEGADOR (EXPLÍCITAMENTE VISIBLE)
            print(f"🌐 [DIRECT] Configurando navegador como {'HEADLESS' if headless else 'VISIBLE'}...")
            browser_instance = Browser(
                config=BrowserConfig(
                    headless=headless,  # Usar valor del parámetro
                    new_context_config=BrowserContextConfig(
                        browser_window_size={"width": 1920, "height": 1080},
                        minimum_wait_page_load_time=1.0,
                        wait_for_network_idle_page_load_time=2.0,
                        maximum_wait_page_load_time=15.0,
                        wait_between_actions=0.5
                    )
                )
            )
            
            # ⭐ CREAR AGENTE SIN TASK INICIAL (PARA CONTROL MANUAL)
            print(f"🤖 [DIRECT] Creando agente...")
            agent = Agent(
                task="",  # Task vacío para control manual
                llm=llm,
                browser=browser_instance,
                use_vision=True
            )
            
            # Actualizar estado
            with db_lock:
                if task_id in test_status_db:
                    test_status_db[task_id].update({
                        'current_action': 'Navegador iniciado, navegando...',
                        'screenshots': []
                    })
            
            # ⭐ CAPTURA INICIAL
            if screenshot_manager:
                print(f"📸 [DIRECT] Captura inicial...")
                await screenshot_manager.capturar_inicial(
                    agent.browser_context,
                    "Estado inicial antes de navegar"
                )
                await actualizar_capturas_en_db(screenshot_manager, task_id)
            
            # ⭐ ASIGNAR TASK ANTES DE NAVEGAR
            prompt_completo = f"Navega a {url} y luego:\n{instrucciones}"
            print(f"🎯 [DIRECT] Prompt enviado al agente:\n{prompt_completo}")
            agent.task = prompt_completo

            # ⭐ NAVEGACIÓN MANUAL (COMO EN TEST_DEMO_FIXED)
            print(f"🌍 [DIRECT] Navegando a: {url}")
            await agent.browser_context.navigate_to(url)
            await asyncio.sleep(2)  # Esperar carga
            
            # Captura después de navegar
            if screenshot_manager:
                print(f"📸 [DIRECT] Captura después de navegar...")
                await screenshot_manager.capturar_paso(
                    agent.browser_context,
                    1,
                    f"Página cargada: {url}"
                )
                await actualizar_capturas_en_db(screenshot_manager, task_id)

            # Actualizar estado
            with db_lock:
                if task_id in test_status_db:
                    test_status_db[task_id].update({
                        'current_action': 'Ejecutando instrucciones...'
                    })

            # ⭐ EJECUTAR INSTRUCCIONES CON RUN
            print(f"🚦 [DIRECT] Ejecutando agent.run(max_steps=15)...")
            resultado = await agent.run(max_steps=15)
            print(f"📝 [DIRECT] Resultado de agent.run: {resultado}")

            # Captura después de ejecutar
            if screenshot_manager:
                print(f"📸 [DIRECT] Captura después de ejecutar...")
                await screenshot_manager.capturar_paso(
                    agent.browser_context,
                    2,
                    "Instrucciones ejecutadas"
                )
                await actualizar_capturas_en_db(screenshot_manager, task_id)
            
            # ⭐ CAPTURA FINAL
            if screenshot_manager:
                print(f"📸 [DIRECT] Captura final...")
                await screenshot_manager.capturar_final(
                    agent.browser_context,
                    "Test completado exitosamente"
                )
                await actualizar_capturas_en_db(screenshot_manager, task_id)
                
                # Mostrar resumen
                capturas = screenshot_manager.obtener_capturas()
                print(f"🎉 [DIRECT] Test completado con {len(capturas)} capturas")
            
            # ⭐ PAUSA ANTES DE CERRAR (PARA VER RESULTADO)
            print(f"⏸️ [DIRECT] Manteniendo navegador visible por 3 segundos...")
            await asyncio.sleep(3)
            
            # Actualizar estado final
            with db_lock:
                if task_id in test_status_db:
                    test_status_db[task_id].update({
                        'status': 'success',
                        'message': 'Test completado exitosamente',
                        'current_action': 'Finalizado'
                    })
            
            print(f"✅ [DIRECT] Test completado exitosamente")
            
        except Exception as e:
            print(f"❌ [DIRECT] Error durante ejecución: {str(e)}")
            traceback.print_exc()
            
            # Captura de error
            if screenshot_manager and agent:
                try:
                    await screenshot_manager.capturar_paso(
                        agent.browser_context,
                        999,
                        f"Error: {str(e)[:50]}"
                    )
                    await actualizar_capturas_en_db(screenshot_manager, task_id)
                except:
                    pass
            
            # Actualizar estado de error
            with db_lock:
                if task_id in test_status_db:
                    test_status_db[task_id].update({
                        'status': 'error',
                        'message': f'Error: {str(e)}',
                        'current_action': 'Error'
                    })
            
        finally:
            # Cerrar navegador
            if browser_instance:
                try:
                    await browser_instance.close()
                    print(f"✅ [DIRECT] Navegador cerrado")
                except Exception as e:
                    print(f"⚠️ [DIRECT] Error cerrando navegador: {e}")
    
    # Ejecutar en hilo separado
    def ejecutar_en_hilo():
        try:
            # Ejecutar loop asyncio
            asyncio.run(ejecutar_con_browser_use())
        except Exception as e:
            print(f"❌ [DIRECT] Error en hilo: {e}")
            with db_lock:
                if task_id in test_status_db:
                    test_status_db[task_id].update({
                        'status': 'error',
                        'message': f'Error crítico: {str(e)}',
                        'current_action': 'Error crítico'
                    })
    
    # Iniciar en hilo separado
    thread = threading.Thread(target=ejecutar_en_hilo, daemon=True)
    thread.start()
    
    print(f"🚀 [DIRECT] Test iniciado en hilo separado")

async def actualizar_capturas_en_db(screenshot_manager, task_id):
    """Actualiza las capturas en la base de datos del test"""
    try:
        capturas = screenshot_manager.obtener_capturas()
        if capturas:
            with db_lock:
                if task_id in test_status_db:
                    # Convertir al formato esperado por la aplicación
                    screenshots_list = []
                    for captura in capturas:
                        rel_path = os.path.relpath(captura["filepath"], SCREENSHOTS_DIR)
                        url_path = rel_path.replace(os.path.sep, '/')
                        screenshots_list.append({
                            'url': f'/media/screenshots/{url_path}',
                            'path': captura['filepath'],
                            'name': captura['filename']
                        })
                    test_status_db[task_id]['screenshots'] = screenshots_list
    except Exception as e:
        print(f"❌ Error actualizando capturas en DB: {e}")

def patch_app_for_direct_browser_use():
    """
    Parcha la aplicación para usar browser-use directo.
    """
    try:
        print("🔧 [PATCH-DIRECT] Aplicando parche para browser-use directo...")
        
        import app
        
        # Respaldar función original
        if not hasattr(app, '_original_run_test_background'):
            app._original_run_test_background = app.run_test_background
            print("💾 [PATCH-DIRECT] Función original respaldada")
        
        # Reemplazar con implementación directa
        app.run_test_background = run_test_background_with_browser_use_direct
        print("✅ [PATCH-DIRECT] Función reemplazada con implementación directa")
        
        # También parchear función unificada
        if hasattr(app, 'run_test_background_unified'):
            app._original_run_test_background_unified = app.run_test_background_unified
            app.run_test_background_unified = run_test_background_with_browser_use_direct
            print("✅ [PATCH-DIRECT] Función unificada también parcheada")
        
        return True
        
    except Exception as e:
        print(f"❌ [PATCH-DIRECT] Error aplicando parche: {e}")
        traceback.print_exc()
        return False

def unpatch_app():
    """Restaura las funciones originales"""
    try:
        import app
        
        if hasattr(app, '_original_run_test_background'):
            app.run_test_background = app._original_run_test_background
            print("🔄 [UNPATCH] Función original restaurada")
        
        if hasattr(app, '_original_run_test_background_unified'):
            app.run_test_background_unified = app._original_run_test_background_unified
            print("🔄 [UNPATCH] Función unificada original restaurada")
            
        return True
        
    except Exception as e:
        print(f"❌ [UNPATCH] Error restaurando: {e}")
        return False

# ⭐ INTEGRACIÓN AUTOMÁTICA AL IMPORTAR
if __name__ != "__main__":
    print("🚀 [AUTO-DIRECT] Iniciando integración directa con browser-use...")
    if patch_app_for_direct_browser_use():
        print("✅ [AUTO-DIRECT] Integración directa completada")
        print("🌐 [AUTO-DIRECT] Navegador será VISIBLE cuando presiones 'Iniciar Vuelo'")
    else:
        print("❌ [AUTO-DIRECT] Error en integración directa")

if __name__ == "__main__":
    print("🧪 [TEST-DIRECT] Modo de prueba para implementación directa")
    print("Para usar: import app_integration_screenshots_fixed") 