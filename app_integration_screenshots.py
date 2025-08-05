# -*- coding: utf-8 -*-
"""
Integración de Capturas Mejoradas para App Web
==============================================
Este módulo modifica la función run_test_background existente para integrar
la nueva utilidad de capturas cuando se presiona "Iniciar Vuelo" en la web.
"""

import os
import sys
import asyncio
import traceback
import threading
import time
from datetime import datetime
from utils_screenshot import ScreenshotManager, integrar_captura_con_sistema

# Importar elementos necesarios de la app principal
from app import test_status_db, db_lock, SCREENSHOTS_DIR

def run_test_background_with_enhanced_screenshots(task_id, url, instrucciones, headless, max_tiempo, screenshots, 
                                                gemini_key, model_name='claude-3-5-sonnet-20240620', browser='chrome', fullscreen=True):
    """
    Versión mejorada de run_test_background que integra las capturas automáticas.
    Reemplaza la función original para usar las capturas simplificadas.
    """
    print(f"🚀 [ENHANCED] Iniciando test {task_id} con capturas mejoradas")
    print(f"📷 [ENHANCED] Screenshots habilitadas: {screenshots}")
    print(f"🌐 [ENHANCED] URL: {url}")
    print(f"🎮 [ENHANCED] Browser: {browser}, Headless: {headless}")
    
    # ⭐ INICIALIZAR GESTOR DE CAPTURAS
    screenshot_manager = None
    if screenshots:
        try:
            screenshot_manager = ScreenshotManager(task_id=task_id[:8])  # Usar parte del task_id
            print(f"✅ [ENHANCED] ScreenshotManager inicializado: {screenshot_manager.obtener_directorio()}")
            
            # Integrar con el sistema existente
            test_dir = screenshot_manager.obtener_directorio()
            
            # Actualizar test_status_db con el directorio de capturas
            with db_lock:
                if task_id in test_status_db:
                    test_status_db[task_id]['test_dir'] = test_dir
                    test_status_db[task_id]['screenshots'] = []
                    test_status_db[task_id]['screenshot_manager'] = screenshot_manager
                    print(f"📁 [ENHANCED] Directorio de capturas configurado: {test_dir}")
        except Exception as e:
            print(f"❌ [ENHANCED] Error inicializando ScreenshotManager: {e}")
            screenshot_manager = None
    
    # ⭐ FUNCIÓN DE CAPTURA INTEGRADA
    def capturar_con_manager(descripcion, paso_num=None):
        """Función interna que usa el ScreenshotManager si está disponible"""
        if not screenshot_manager:
            return False
            
        try:
            # Determinar si es captura inicial, paso, o final
            if paso_num is None:
                # Captura general
                result = asyncio.run(screenshot_manager.capturar_paso(
                    None,  # No tenemos browser_context en este punto
                    999,  # Número genérico
                    descripcion
                ))
            elif paso_num == 0:
                # Captura inicial
                result = asyncio.run(screenshot_manager.capturar_inicial(
                    None,
                    descripcion
                ))
            elif paso_num >= 900:
                # Captura final
                result = asyncio.run(screenshot_manager.capturar_final(
                    None,
                    descripcion
                ))
            else:
                # Captura de paso
                result = asyncio.run(screenshot_manager.capturar_paso(
                    None,
                    paso_num,
                    descripcion
                ))
            
            # Actualizar test_status_db con la nueva captura
            capturas = screenshot_manager.obtener_capturas()
            if capturas:
                with db_lock:
                    if task_id in test_status_db:
                        # Convertir capturas del manager al formato esperado
                        screenshots_list = []
                        for captura in capturas:
                            screenshots_list.append({
                                'url': f'/media/screenshots/{os.path.relpath(captura["filepath"], SCREENSHOTS_DIR).replace(os.path.sep, "/")}',
                                'path': captura['filepath'],
                                'name': captura['filename']
                            })
                        test_status_db[task_id]['screenshots'] = screenshots_list
                        print(f"📸 [ENHANCED] Captura registrada: {descripcion}")
            
            return True
        except Exception as e:
            print(f"❌ [ENHANCED] Error en captura: {e}")
            return False
    
    # ⭐ FUNCIÓN MEJORADA PARA LEER OUTPUT CON CAPTURAS
    def stream_reader_enhanced(stream, output_key):
        """Versión mejorada del stream reader que integra capturas automáticas"""
        last_human_status = ""
        step_counter = 0
        
        try:
            for line_bytes in iter(stream.readline, b''):
                if not line_bytes:
                    break
                
                # Decodificar línea
                try:
                    decoded_line = line_bytes.decode('utf-8', errors='replace')
                    decoded_line = ''.join(c if ord(c) < 128 else '?' for c in decoded_line)
                except:
                    decoded_line = "[Error de decodificación]\n"
                
                # ⭐ DETECTAR MOMENTOS CLAVE PARA CAPTURAS AUTOMÁTICAS
                human_status_update = None
                should_capture = False
                capture_description = ""
                
                if output_key == 'stdout':
                    if "DEBUG: Iniciando función main()" in decoded_line:
                        human_status_update = "Inicializando sistema..."
                        should_capture = True
                        capture_description = "Sistema inicializado"
                        step_counter = 0
                    elif "DEBUG: Inicializando Browser..." in decoded_line:
                        human_status_update = "Iniciando navegador..."
                        should_capture = True
                        capture_description = "Navegador iniciado"
                        step_counter = 1
                    elif "DEBUG: Navegando a URL:" in decoded_line or "DEBUG: Navegando a la URL inicial:" in decoded_line:
                        human_status_update = "Navegando a la página..."
                        should_capture = True
                        capture_description = f"Navegando a {url}"
                        step_counter = 2
                    elif "DEBUG: Ejecutando tarea principal del agente" in decoded_line or "DEBUG: Ejecutando agente con las instrucciones" in decoded_line:
                        human_status_update = "Ejecutando instrucciones..."
                        should_capture = True
                        capture_description = "Ejecutando instrucciones principales"
                        step_counter = 3
                    elif "CAPTURA: " in decoded_line or "CAPTURA HTML2CANVAS: " in decoded_line:
                        human_status_update = "Capturando estado actual..."
                        should_capture = True
                        capture_description = "Captura automática del estado"
                        step_counter += 1
                    elif "DEBUG: Cerrando el navegador..." in decoded_line:
                        human_status_update = "Finalizando test..."
                        should_capture = True
                        capture_description = "Test finalizado"
                        step_counter = 999  # Captura final
                    # Detectar pasos numerados
                    elif "Ejecutando paso " in decoded_line:
                        import re
                        match = re.search(r"Ejecutando paso (\d+)[:.]?\s*(.+)?", decoded_line)
                        if match:
                            paso_num = int(match.group(1))
                            paso_desc = match.group(2) if match.group(2) else f"Paso {paso_num}"
                            human_status_update = f"Ejecutando paso {paso_num}: {paso_desc[:30]}..."
                            should_capture = True
                            capture_description = f"Paso {paso_num}: {paso_desc[:50]}"
                            step_counter = paso_num + 10  # Offset para evitar conflictos
                
                # ⭐ REALIZAR CAPTURA AUTOMÁTICA SI ES NECESARIO
                if should_capture and screenshot_manager and screenshots:
                    print(f"📸 [ENHANCED] Tomando captura automática: {capture_description}")
                    # Ejecutar captura en hilo separado para no bloquear
                    threading.Thread(
                        target=capturar_con_manager,
                        args=(capture_description, step_counter),
                        daemon=True
                    ).start()
                
                # Actualizar base de datos como siempre
                with db_lock:
                    if task_id in test_status_db:
                        if output_key not in test_status_db[task_id]:
                            test_status_db[task_id][output_key] = ''
                        
                        test_status_db[task_id][output_key] += decoded_line
                        
                        if human_status_update and human_status_update != last_human_status:
                            test_status_db[task_id]['current_action'] = human_status_update
                            last_human_status = human_status_update
                            
                            if step_counter is not None:
                                test_status_db[task_id]['current_step'] = step_counter
                                
        except Exception as e:
            print(f"❌ [ENHANCED] Error en stream_reader_enhanced: {e}")
            traceback.print_exc()
    
    # ⭐ IMPORTAR Y EJECUTAR LA FUNCIÓN ORIGINAL PERO CON MEJORAS
    try:
        # Importar la función original
        from app import run_test_background as original_run_test_background
        
        # Parchar temporalmente la función stream_reader
        original_function = original_run_test_background
        
        # Ejecutar función original con nuestras mejoras
        # Nota: La función original maneja toda la lógica compleja,
        # nosotros solo mejoramos las capturas
        
        print(f"🔄 [ENHANCED] Ejecutando función original con capturas mejoradas...")
        
        # Ejecutar en hilo separado para manejar capturas async
        def execute_with_enhancements():
            try:
                # Captura inicial si está habilitada
                if screenshot_manager and screenshots:
                    print(f"📸 [ENHANCED] Tomando captura inicial...")
                    capturar_con_manager("Estado inicial antes de ejecutar test", 0)
                
                # Llamar función original
                result = original_run_test_background(
                    task_id, url, instrucciones, headless, max_tiempo, screenshots,
                    gemini_key, model_name, browser, fullscreen
                )
                
                # Captura final si está habilitada
                if screenshot_manager and screenshots:
                    print(f"📸 [ENHANCED] Tomando captura final...")
                    capturar_con_manager("Estado final después de completar test", 999)
                    
                    # Mostrar resumen
                    capturas = screenshot_manager.obtener_capturas()
                    print(f"🎉 [ENHANCED] Test completado con {len(capturas)} capturas")
                
                return result
                
            except Exception as e:
                print(f"❌ [ENHANCED] Error durante ejecución: {e}")
                # Captura de error
                if screenshot_manager and screenshots:
                    capturar_con_manager(f"Error durante ejecución: {str(e)[:50]}", 998)
                raise
        
        # Ejecutar
        return execute_with_enhancements()
        
    except Exception as e:
        print(f"❌ [ENHANCED] Error crítico en función mejorada: {e}")
        traceback.print_exc()
        
        # Fallback a función original sin mejoras
        from app import run_test_background as fallback_function
        print(f"🔄 [ENHANCED] Fallback a función original...")
        return fallback_function(
            task_id, url, instrucciones, headless, max_tiempo, screenshots,
            gemini_key, model_name, browser, fullscreen
        )

def patch_app_for_enhanced_screenshots():
    """
    Parcha la aplicación principal para usar las capturas mejoradas.
    Debe llamarse después de importar app.py
    """
    try:
        print("🔧 [PATCH] Aplicando parche para capturas mejoradas...")
        
        # Importar módulos necesarios
        import app
        
        # Respaldar función original
        if not hasattr(app, '_original_run_test_background'):
            app._original_run_test_background = app.run_test_background
            print("💾 [PATCH] Función original respaldada")
        
        # Reemplazar con versión mejorada
        app.run_test_background = run_test_background_with_enhanced_screenshots
        print("✅ [PATCH] Función reemplazada con versión mejorada")
        
        # También parchear la función unificada si existe
        if hasattr(app, 'run_test_background_unified'):
            app._original_run_test_background_unified = app.run_test_background_unified
            
            def enhanced_unified(task_id, url, instrucciones, headless, max_tiempo, screenshots, 
                               gemini_key, model_name='claude-3-5-sonnet-20240620', browser='chrome', fullscreen=True):
                # Siempre usar nuestra versión mejorada
                return run_test_background_with_enhanced_screenshots(
                    task_id, url, instrucciones, headless, max_tiempo, screenshots,
                    gemini_key, model_name, browser, fullscreen
                )
            
            app.run_test_background_unified = enhanced_unified
            print("✅ [PATCH] Función unificada también parcheada")
        
        return True
        
    except Exception as e:
        print(f"❌ [PATCH] Error aplicando parche: {e}")
        traceback.print_exc()
        return False

def unpatch_app():
    """
    Restaura las funciones originales (para debugging)
    """
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
    # Auto-parchar cuando se importa el módulo
    print("🚀 [AUTO] Iniciando integración automática de capturas mejoradas...")
    if patch_app_for_enhanced_screenshots():
        print("✅ [AUTO] Integración completada exitosamente")
        print("📷 [AUTO] Las capturas mejoradas se activarán automáticamente al presionar 'Iniciar Vuelo'")
    else:
        print("❌ [AUTO] Error en integración automática")

if __name__ == "__main__":
    print("🧪 [TEST] Ejecutando en modo de prueba...")
    print("Para integrar con tu app web, simplemente importa este módulo:")
    print("  from app_integration_screenshots import patch_app_for_enhanced_screenshots")
    print("  patch_app_for_enhanced_screenshots()")
    print("O simplemente importa el módulo:")
    print("  import app_integration_screenshots") 