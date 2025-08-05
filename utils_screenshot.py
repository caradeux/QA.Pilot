# -*- coding: utf-8 -*-
"""
Utilidad para Capturas de Pantalla con Browser-Use
=================================================
Módulo que proporciona funcionalidades simples para tomar capturas de pantalla
del navegador usando browser-use en tu proyecto de testing.

Uso:
    from utils_screenshot import ScreenshotManager, capturar_paso_simple
    
    # En tu test
    screenshot_manager = ScreenshotManager(task_id="mi_test")
    await screenshot_manager.capturar_paso(agent.browser_context, 1, "Inicio de test")
"""

import os
import base64
import time
import re
import logging
from typing import Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class ScreenshotManager:
    """
    Gestor simple para capturas de pantalla usando browser-use.
    """
    
    def __init__(self, task_id: str = None, base_dir: str = "test_screenshots"):
        """
        Inicializa el gestor de capturas.
        
        Args:
            task_id: ID único del test (se genera automáticamente si no se proporciona)
            base_dir: Directorio base donde guardar las capturas
        """
        self.task_id = task_id or f"test_{int(time.time())}"
        self.base_dir = base_dir
        self.screenshot_dir = os.path.join(base_dir, self.task_id)
        self.contador_pasos = 0
        self.capturas = []
        
        # Crear directorio si no existe
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        logger.info(f"📸 ScreenshotManager inicializado para test: {self.task_id}")
        logger.info(f"📁 Directorio de capturas: {self.screenshot_dir}")
    
    async def capturar_paso(
        self, 
        browser_context, 
        num_paso: Optional[int] = None, 
        descripcion: str = "Captura", 
        full_page: bool = True
    ) -> Optional[str]:
        """
        Toma una captura del navegador usando browser_context.take_screenshot()
        
        Args:
            browser_context: El contexto del navegador de browser-use
            num_paso: Número del paso (se auto-incrementa si no se proporciona)
            descripcion: Descripción de la captura
            full_page: Si capturar página completa o solo viewport
            
        Returns:
            str: Ruta del archivo de captura guardado o None si falla
        """
        try:
            # Incrementar contador si no se especifica número de paso
            if num_paso is None:
                self.contador_pasos += 1
                num_paso = self.contador_pasos
            
            # Crear nombre de archivo seguro
            timestamp = int(time.time())
            safe_desc = re.sub(r'[^a-zA-Z0-9_]', '_', descripcion[:30])
            filename = f"paso_{num_paso:03d}_{safe_desc}_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            
            logger.info(f"📷 Capturando paso {num_paso}: {descripcion}")
            
            # Tomar captura usando browser-use
            screenshot_b64 = await browser_context.take_screenshot(full_page=full_page)
            
            # Convertir base64 a bytes y guardar
            screenshot_bytes = base64.b64decode(screenshot_b64)
            with open(filepath, 'wb') as f:
                f.write(screenshot_bytes)
            
            # Registrar captura
            captura_info = {
                'paso': num_paso,
                'descripcion': descripcion,
                'filename': filename,
                'filepath': filepath,
                'timestamp': timestamp,
                'full_page': full_page,
                'size_bytes': len(screenshot_bytes)
            }
            self.capturas.append(captura_info)
            
            logger.info(f"✅ Captura del paso {num_paso} guardada: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Error capturando paso {num_paso}: {str(e)}")
            return None
    
    async def capturar_inicial(self, browser_context, descripcion: str = "Estado inicial") -> Optional[str]:
        """Captura el estado inicial del test"""
        return await self.capturar_paso(browser_context, 0, descripcion)
    
    async def capturar_final(self, browser_context, descripcion: str = "Estado final") -> Optional[str]:
        """Captura el estado final del test"""
        return await self.capturar_paso(browser_context, 999, descripcion)
    
    def obtener_capturas(self) -> list:
        """Retorna la lista de capturas realizadas"""
        return self.capturas.copy()
    
    def obtener_directorio(self) -> str:
        """Retorna el directorio donde se guardan las capturas"""
        return self.screenshot_dir
    
    def limpiar_capturas(self) -> bool:
        """Elimina todas las capturas del directorio"""
        try:
            import shutil
            if os.path.exists(self.screenshot_dir):
                shutil.rmtree(self.screenshot_dir)
                logger.info(f"🗑️ Capturas eliminadas: {self.screenshot_dir}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error eliminando capturas: {e}")
            return False


# Función simple para uso rápido
async def capturar_paso_simple(
    browser_context, 
    descripcion: str, 
    directorio: str = "test_screenshots",
    full_page: bool = True
) -> Optional[str]:
    """
    Función simple para tomar una captura rápida sin gestor.
    
    Args:
        browser_context: Contexto del navegador browser-use
        descripcion: Descripción de la captura
        directorio: Directorio donde guardar
        full_page: Si capturar página completa
        
    Returns:
        str: Ruta del archivo guardado o None si falla
    """
    try:
        # Crear directorio
        os.makedirs(directorio, exist_ok=True)
        
        # Crear nombre de archivo
        timestamp = int(time.time())
        safe_desc = re.sub(r'[^a-zA-Z0-9_]', '_', descripcion[:30])
        filename = f"captura_{safe_desc}_{timestamp}.png"
        filepath = os.path.join(directorio, filename)
        
        # Tomar captura
        screenshot_b64 = await browser_context.take_screenshot(full_page=full_page)
        screenshot_bytes = base64.b64decode(screenshot_b64)
        
        # Guardar archivo
        with open(filepath, 'wb') as f:
            f.write(screenshot_bytes)
        
        print(f"📷 Captura guardada: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ Error en captura simple: {e}")
        return None


# Decorador para capturar automáticamente en funciones de test
def auto_screenshot(descripcion: str = None, full_page: bool = True):
    """
    Decorador que captura automáticamente antes y después de ejecutar una función.
    
    Usage:
        @auto_screenshot("Función de login")
        async def mi_test_function(agent):
            # Tu código de test aquí
            pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Intentar extraer browser_context del primer argumento (agent)
            agent = args[0] if args else None
            if hasattr(agent, 'browser_context'):
                desc = descripcion or func.__name__
                
                # Captura antes
                await capturar_paso_simple(
                    agent.browser_context, 
                    f"Antes_{desc}",
                    full_page=full_page
                )
                
                # Ejecutar función
                result = await func(*args, **kwargs)
                
                # Captura después
                await capturar_paso_simple(
                    agent.browser_context, 
                    f"Después_{desc}",
                    full_page=full_page
                )
                
                return result
            else:
                # Si no hay browser_context, ejecutar normalmente
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Función de utilidad para integrar con sistema existente
async def integrar_captura_con_sistema(browser_context, task_id: str, descripcion: str) -> Optional[dict]:
    """
    Función que integra las capturas con el sistema de tracking existente.
    
    Args:
        browser_context: Contexto del navegador
        task_id: ID del test actual
        descripcion: Descripción de la captura
        
    Returns:
        dict: Información de la captura para el sistema de tracking
    """
    try:
        # Crear gestor temporal
        manager = ScreenshotManager(task_id)
        
        # Tomar captura
        filepath = await manager.capturar_paso(browser_context, None, descripcion)
        
        if filepath:
            # Crear información compatible con el sistema existente
            relative_path = os.path.relpath(filepath, "test_screenshots")
            url_path = relative_path.replace(os.path.sep, '/')
            
            return {
                'url': f'/media/screenshots/{url_path}',
                'path': filepath,
                'name': os.path.basename(filepath),
                'descripcion': descripcion,
                'timestamp': int(time.time())
            }
        return None
        
    except Exception as e:
        logger.error(f"❌ Error integrando captura: {e}")
        return None


if __name__ == "__main__":
    # Ejemplo de uso (solo para testing del módulo)
    print("🔧 Módulo utils_screenshot.py cargado correctamente")
    print("📚 Funciones disponibles:")
    print("  - ScreenshotManager: Gestor principal de capturas")
    print("  - capturar_paso_simple: Función simple para capturas rápidas")
    print("  - @auto_screenshot: Decorador para captura automática")
    print("  - integrar_captura_con_sistema: Integración con sistema existente") 