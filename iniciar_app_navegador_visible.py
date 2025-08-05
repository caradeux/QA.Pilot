#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Iniciador de Aplicación Web con Navegador Visible Garantizado
===========================================================
Este script asegura que el navegador se abra VISIBLE cuando 
se presiona "Iniciar Vuelo" en la aplicación web.
"""

import os
import sys
import subprocess
import traceback
from pathlib import Path

def verificar_archivos_necesarios():
    """Verifica que todos los archivos necesarios estén presentes"""
    archivos_requeridos = [
        'app.py',
        'utils_screenshot.py',
        'app_integration_screenshots_fixed.py'
    ]
    
    archivos_faltantes = []
    for archivo in archivos_requeridos:
        if not os.path.exists(archivo):
            archivos_faltantes.append(archivo)
    
    if archivos_faltantes:
        print(f"❌ Archivos faltantes: {', '.join(archivos_faltantes)}")
        return False
    
    print("✅ Todos los archivos necesarios están presentes")
    return True

def main():
    """Función principal"""
    print("🎯 MODO: Aplicación Web con Navegador Visible Garantizado")
    print("=" * 65)
    print("🌐 El navegador se abrirá VISIBLE cuando presiones 'Iniciar Vuelo'")
    print("📷 Las capturas se tomarán automáticamente")
    print("🔧 Usa implementación directa de browser-use")
    print()
    
    # Verificar archivos
    if not verificar_archivos_necesarios():
        return 1
    
    try:
        print("🚀 INICIANDO APLICACIÓN WEB CON NAVEGADOR VISIBLE")
        print("=" * 60)
        
        # Mostrar configuración
        print("🔧 Configuración:")
        print("   - Navegador: SIEMPRE VISIBLE (headless=False forzado)")
        print("   - Capturas: Automáticas")
        print("   - Implementación: browser-use directo")
        print("   - Control: Navegación manual")
        print()
        
        # Código Python para ejecutar la aplicación con integración
        codigo_iniciar = '''
import sys
import os

# ⭐ INTEGRAR CAPTURAS CORREGIDAS ANTES DE IMPORTAR APP
print("🔧 Integrando navegador visible...")
import app_integration_screenshots_fixed

# Ahora importar y ejecutar la aplicación
print("🚀 Iniciando aplicación...")
from app import app

if __name__ == "__main__":
    try:
        print("🌐 Aplicación disponible en: http://127.0.0.1:8503")
        print("✅ Navegador será VISIBLE al presionar 'Iniciar Vuelo'")
        print("📷 Capturas automáticas habilitadas")
        print("-" * 50)
        app.run(host="127.0.0.1", port=8503, debug=False)
    except KeyboardInterrupt:
        print("\\n🛑 Aplicación detenida por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")
'''
        
        # Ejecutar la aplicación
        process = subprocess.Popen(
            [sys.executable, '-c', codigo_iniciar],
            cwd=os.getcwd(),
            env=os.environ.copy()
        )
        
        print("🌟 ¡Aplicación iniciada!")
        print("🔗 Abre tu navegador en: http://127.0.0.1:8503")
        print("🎯 Marca 'Capturar Vuelo' y presiona 'Iniciar Vuelo'")
        print("👀 El navegador se abrirá VISIBLE automáticamente")
        print()
        print("⏹️ Presiona Ctrl+C para detener")
        
        # Esperar hasta que el usuario termine
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo aplicación...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            print("✅ Aplicación detenida")
            
    except Exception as e:
        print(f"❌ Error iniciando aplicación: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 