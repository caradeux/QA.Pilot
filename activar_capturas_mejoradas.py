# -*- coding: utf-8 -*-
"""
Activador de Capturas Mejoradas
===============================
Script simple para activar las capturas mejoradas en tu aplicación web.
Ejecutar ANTES de iniciar app.py para habilitar automáticamente las capturas mejoradas.
"""

import sys
import os

def activar_capturas_mejoradas():
    """
    Activa las capturas mejoradas en la aplicación.
    """
    print("🚀 ACTIVANDO CAPTURAS MEJORADAS PARA APLICACIÓN WEB")
    print("=" * 60)
    
    try:
        # Verificar que los archivos necesarios existen
        archivos_requeridos = [
            'utils_screenshot.py',
            'app_integration_screenshots.py',
            'app.py'
        ]
        
        archivos_faltantes = []
        for archivo in archivos_requeridos:
            if not os.path.exists(archivo):
                archivos_faltantes.append(archivo)
        
        if archivos_faltantes:
            print("❌ ERROR: Archivos faltantes:")
            for archivo in archivos_faltantes:
                print(f"   - {archivo}")
            return False
        
        print("✅ Todos los archivos necesarios están presentes")
        
        # Importar módulos necesarios
        print("📦 Importando módulos...")
        
        # Importar utilidad de capturas
        try:
            from utils_screenshot import ScreenshotManager
            print("✅ utils_screenshot.py importado correctamente")
        except Exception as e:
            print(f"❌ Error importando utils_screenshot: {e}")
            return False
        
        # Importar integración
        try:
            import app_integration_screenshots
            print("✅ app_integration_screenshots.py importado correctamente")
            print("🔧 Parche aplicado automáticamente")
        except Exception as e:
            print(f"❌ Error importando integración: {e}")
            return False
        
        print("\n🎉 ¡CAPTURAS MEJORADAS ACTIVADAS EXITOSAMENTE!")
        print("📷 Las capturas automáticas funcionarán cuando presiones 'Iniciar Vuelo'")
        print("📁 Las capturas se organizarán automáticamente en directorios separados")
        print("⚡ Funciones simplificadas integradas con tu sistema existente")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_integracion():
    """
    Verifica que la integración esté funcionando correctamente.
    """
    print("\n🔍 VERIFICANDO INTEGRACIÓN...")
    
    try:
        # Verificar que app.py se puede importar
        import app
        print("✅ app.py importado correctamente")
        
        # Verificar que las funciones están parcheadas
        if hasattr(app, '_original_run_test_background'):
            print("✅ Función run_test_background parcheada correctamente")
        else:
            print("⚠️  run_test_background no está parcheada (puede ser normal)")
        
        # Verificar utilidades de captura
        from utils_screenshot import ScreenshotManager
        test_manager = ScreenshotManager(task_id="test_verification")
        test_dir = test_manager.obtener_directorio()
        print(f"✅ ScreenshotManager funciona - Directorio: {test_dir}")
        
        print("✅ Verificación completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

def mostrar_instrucciones():
    """
    Muestra instrucciones de uso.
    """
    print("\n📖 INSTRUCCIONES DE USO:")
    print("=" * 40)
    print("1. ✅ Ejecuta este script una vez para activar las capturas mejoradas")
    print("2. 🚀 Inicia tu aplicación normalmente: python app.py")
    print("3. 🌐 Ve a http://127.0.0.1:8503/")
    print("4. ✔️ Asegúrate de marcar la casilla 'Capturar Vuelo' en la interfaz")
    print("5. 🎯 Presiona 'Iniciar Vuelo' - las capturas mejoradas se activarán automáticamente")
    print("\n📷 CAPTURAS AUTOMÁTICAS:")
    print("   - 📸 Captura inicial al comenzar el test")
    print("   - 🔄 Capturas automáticas en momentos clave")
    print("   - 📸 Captura final al completar el test")
    print("   - 🗂️  Organización automática en carpetas")
    print("   - 📊 Integración completa con el sistema existente")
    print("\n🔧 DESACTIVAR (opcional):")
    print("   - Ejecuta: python activar_capturas_mejoradas.py --desactivar")

def desactivar_capturas():
    """
    Desactiva las capturas mejoradas y restaura funcionalidad original.
    """
    print("🔄 DESACTIVANDO CAPTURAS MEJORADAS...")
    
    try:
        from app_integration_screenshots import unpatch_app
        if unpatch_app():
            print("✅ Capturas mejoradas desactivadas")
            print("🔄 Funcionalidad original restaurada")
            return True
        else:
            print("❌ Error desactivando capturas")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """
    Función principal.
    """
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        if sys.argv[1] == '--desactivar':
            return desactivar_capturas()
        elif sys.argv[1] == '--verificar':
            return verificar_integracion()
        elif sys.argv[1] == '--help':
            mostrar_instrucciones()
            return True
    
    # Activación normal
    print("🎯 MODO: Activación de Capturas Mejoradas")
    print("💡 Para ver opciones adicionales: python activar_capturas_mejoradas.py --help")
    print()
    
    # Activar capturas
    if activar_capturas_mejoradas():
        # Verificar integración
        if verificar_integracion():
            mostrar_instrucciones()
            
            print("\n🏁 LISTO PARA USAR!")
            print("🚀 Puedes iniciar tu aplicación con: python app.py")
            print("📷 Las capturas mejoradas estarán activas automáticamente")
            
            return True
    
    print("\n❌ Activación fallida")
    return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✨ ¡Activación completada exitosamente!")
    else:
        print("\n💥 Error durante la activación")
        sys.exit(1) 