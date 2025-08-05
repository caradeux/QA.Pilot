# -*- coding: utf-8 -*-
"""
Test Demo Mejorado con Utilidad de Capturas
==========================================
Versión simplificada del test_demo.py original usando la nueva utilidad
de capturas de pantalla. Muestra cómo reemplazar el código complejo
con una implementación simple y limpia.
"""

import sys
import os
import asyncio
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from browser_use import Agent, Browser, BrowserConfig, BrowserContextConfig

# ⭐ IMPORTAR LA NUEVA UTILIDAD DE CAPTURAS
from utils_screenshot import ScreenshotManager

# Cargar variables de entorno
load_dotenv()

async def main():
    """
    Test demo usando la nueva utilidad de capturas.
    Muestra la diferencia de simplicidad comparado con el código original.
    """
    browser = None
    agent = None
    
    try:
        print("🚀 Iniciando test demo mejorado...")
        
        # ===== CONFIGURACIÓN DEL NAVEGADOR =====
        print("🌐 Inicializando browser...")
        browser = Browser(
            config=BrowserConfig(
                headless=False,
                new_context_config=BrowserContextConfig(
                    browser_window_size={"width": 1920, "height": 1080},
                    minimum_wait_page_load_time=1.0,
                    wait_for_network_idle_page_load_time=2.0,
                    maximum_wait_page_load_time=15.0,
                    wait_between_actions=0.5
                )
            )
        )
        print("✅ Browser configurado correctamente")

        # ===== CONFIGURACIÓN DEL LLM =====
        print("🤖 Configurando LLM...")
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not anthropic_key:
            # Intentar cargar desde archivo .env
            env_path = os.path.join(os.getcwd(), '.env')
            if os.path.exists(env_path):
                try:
                    with open(env_path, 'r') as f:
                        for line in f:
                            if line.startswith('ANTHROPIC_API_KEY='):
                                anthropic_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                                break
                except Exception as e:
                    print(f"Error leyendo .env: {e}")
        
        if not anthropic_key:
            raise ValueError("❌ ANTHROPIC_API_KEY no encontrada. Configúrala en .env o como variable de entorno")
        
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=anthropic_key,
            temperature=0.1,
            max_tokens=4000
        )
        print("✅ LLM configurado correctamente")

        # ===== CREAR AGENTE =====
        print("🤖 Creando agente...")
        task_instructions = """Navega a https://www.mercadolibre.cl y luego:
        1. Buscar 'smartphone' 
        2. Seleccionar el primer resultado
        3. Ver detalles del producto"""
        
        agent = Agent(
            task=task_instructions,
            llm=llm,
            browser=browser
        )
        print("✅ Agente creado correctamente")

        # ⭐ ===== CONFIGURAR GESTOR DE CAPTURAS (NUEVO) =====
        print("📷 Configurando gestor de capturas...")
        screenshots = ScreenshotManager(task_id="test_demo_mejorado")
        print(f"✅ Capturas se guardarán en: {screenshots.obtener_directorio()}")

        # ⭐ ===== CAPTURA INICIAL =====
        print("📸 Tomando captura inicial...")
        await screenshots.capturar_inicial(
            agent.browser_context, 
            "Estado inicial antes de ejecutar test"
        )

        # ===== EJECUTAR TEST =====
        print("🔥 Ejecutando test de MercadoLibre...")
        
        # Ejecutar el test completo
        await agent.run(max_steps=8)
        
        # ⭐ ===== CAPTURAS DURANTE LA EJECUCIÓN =====
        print("📸 Tomando capturas de progreso...")
        
        # Captura después de la búsqueda
        await screenshots.capturar_paso(
            agent.browser_context,
            1,
            "Búsqueda de smartphone completada"
        )
        
        # Pequeña pausa para permitir carga
        await asyncio.sleep(2)
        
        # Captura de la página de resultados
        await screenshots.capturar_paso(
            agent.browser_context,
            2,
            "Página de resultados mostrada"
        )
        
        # ⭐ ===== CAPTURA FINAL =====
        print("📸 Tomando captura final...")
        await screenshots.capturar_final(
            agent.browser_context,
            "Estado final después de completar test"
        )

        # ===== MOSTRAR RESUMEN =====
        capturas = screenshots.obtener_capturas()
        print("\n" + "="*60)
        print("🎉 ¡TEST COMPLETADO EXITOSAMENTE!")
        print("="*60)
        print(f"📊 Total de capturas tomadas: {len(capturas)}")
        print(f"📁 Directorio: {screenshots.obtener_directorio()}")
        print("\n📸 Capturas realizadas:")
        
        for i, captura in enumerate(capturas, 1):
            size_mb = captura['size_bytes'] / (1024*1024)
            print(f"  {i}. Paso {captura['paso']:03d}: {captura['descripcion']}")
            print(f"     📄 Archivo: {captura['filename']}")
            print(f"     💾 Tamaño: {size_mb:.2f} MB")
            print(f"     🔗 Ruta: {captura['filepath']}")
            print()
        
        print("✨ Test demo mejorado completado exitosamente")
        
    except Exception as e:
        print(f"❌ ERROR durante la ejecución: {str(e)}")
        
        # ⭐ CAPTURA DE ERROR (OPCIONAL)
        if 'screenshots' in locals() and 'agent' in locals():
            try:
                await screenshots.capturar_paso(
                    agent.browser_context,
                    999,
                    f"Estado de error: {str(e)[:50]}"
                )
                print("📸 Captura de error tomada")
            except:
                pass
        
        import traceback
        traceback.print_exc()
        
    finally:
        # Cerrar navegador
        if browser:
            try:
                await browser.close()
                print("✅ Navegador cerrado correctamente")
            except Exception as e:
                print(f"⚠️ Error cerrando navegador: {e}")

        print("\n🏁 Test finalizado")


if __name__ == "__main__":
    print("🔧 Ejecutando test_demo_mejorado.py")
    print("📖 Este script demuestra el uso de la nueva utilidad de capturas")
    print("🔄 Comparado con test_demo.py original, este es mucho más simple\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrumpido por el usuario")
    except Exception as e:
        print(f"\n💥 Error fatal: {e}")
        import traceback
        traceback.print_exc() 