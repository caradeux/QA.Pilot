# -*- coding: utf-8 -*-
"""
Iniciador de Aplicación con Capturas Mejoradas
==============================================
Script que inicia la aplicación web con las capturas mejoradas ya integradas.
Uso: python iniciar_app_con_capturas.py
"""

import sys
import os

def main():
    """
    Inicia la aplicación con capturas mejoradas integradas.
    """
    print("🚀 INICIANDO APLICACIÓN WEB CON CAPTURAS MEJORADAS")
    print("=" * 60)
    
    try:
        # Verificar archivos necesarios
        if not os.path.exists('app.py'):
            print("❌ ERROR: app.py no encontrado")
            return False
        
        if not os.path.exists('utils_screenshot.py'):
            print("❌ ERROR: utils_screenshot.py no encontrado")
            return False
        
        if not os.path.exists('app_integration_screenshots.py'):
            print("❌ ERROR: app_integration_screenshots.py no encontrado")
            return False
        
        print("✅ Todos los archivos necesarios están presentes")
        
        # Integrar capturas mejoradas ANTES de importar app
        print("🔧 Integrando capturas mejoradas...")
        
        try:
            # Importar e integrar automáticamente
            import app_integration_screenshots
            print("✅ Capturas mejoradas integradas automáticamente")
        except Exception as e:
            print(f"❌ Error integrando capturas: {e}")
            print("🔄 Continuando con funcionalidad básica...")
        
        # Importar y ejecutar aplicación principal
        print("📦 Importando aplicación principal...")
        import app
        
        print("✅ Aplicación importada correctamente")
        print("\n🎉 ¡APLICACIÓN LISTA CON CAPTURAS MEJORADAS!")
        print("📷 Las capturas automáticas están activas")
        print("🌐 Accede a: http://127.0.0.1:8503/")
        print("🎯 Marca 'Capturar Vuelo' y presiona 'Iniciar Vuelo'")
        
        # Verificar puerto y host de la aplicación
        if hasattr(app.app, 'run'):
            host = getattr(app.app, 'host', '127.0.0.1')
            port = getattr(app.app, 'port', 8503)
            print(f"📡 Servidor ejecutándose en: http://{host}:{port}/")
        
        # Ejecutar aplicación
        print("\n🚀 Iniciando servidor Flask...")
        print("=" * 60)
        
        # Ejecutar app.py como si fuera el script principal
        if hasattr(app, 'app') and hasattr(app.app, 'run'):
            app.app.run(host='127.0.0.1', port=8503, debug=False)
        else:
            # Fallback: ejecutar usando exec
            print("🔄 Ejecutando usando método alternativo...")
            exec(open('app.py').read())
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️ Aplicación interrumpida por el usuario")
        return True
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 MODO: Inicio de Aplicación con Capturas Mejoradas")
    print("💡 Este script integra automáticamente las capturas mejoradas")
    print("📷 No necesitas ejecutar activar_capturas_mejoradas.py por separado")
    print()
    
    success = main()
    
    if not success:
        print("\n💥 Error durante el inicio")
        print("🔧 Intenta ejecutar manualmente:")
        print("   1. python activar_capturas_mejoradas.py")
        print("   2. python app.py")
        sys.exit(1)
    else:
        print("\n✨ ¡Aplicación finalizada correctamente!") 