# -*- coding: utf-8 -*-
"""
Test de Verificación: Navegador Visible
=======================================
Script simple para verificar que browser-use abre el navegador en modo visible.
"""

import asyncio
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from browser_use import Agent, Browser, BrowserConfig, BrowserContextConfig
from utils_screenshot import capturar_paso_simple

load_dotenv()

async def test_navegador_visible():
    """
    Test mínimo para verificar que el navegador se abre visible.
    """
    browser = None
    
    try:
        print("🧪 PRUEBA: Verificando que el navegador se abre visible...")
        
        # Configurar navegador EXPLÍCITAMENTE como no-headless
        print("🌐 Configurando navegador en modo visible...")
        browser = Browser(
            config=BrowserConfig(
                headless=False,  # ⚠️ EXPLÍCITO
                new_context_config=BrowserContextConfig(
                    browser_window_size={"width": 1280, "height": 720}
                )
            )
        )
        print("✅ Browser configurado como visible")
        
        # Configurar LLM mínimo
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if not anthropic_key:
            env_path = os.path.join(os.getcwd(), '.env')
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('ANTHROPIC_API_KEY='):
                            anthropic_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                            break
        
        if not anthropic_key:
            raise ValueError("❌ ANTHROPIC_API_KEY requerida")
        
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=anthropic_key,
            temperature=0.1
        )
        
        # Crear agente simple
        agent = Agent(
            task="",  # Sin task específico
            llm=llm,
            browser=browser
        )
        print("✅ Agente creado")
        
        # Navegar a una página simple
        print("🌍 Navegando a Google...")
        await agent.browser_context.navigate_to("https://www.google.com")
        print("✅ Navegación completada")
        
        # Pausa para que puedas VER el navegador
        print("\n" + "="*50)
        print("👀 ¿PUEDES VER EL NAVEGADOR CON GOOGLE.COM?")
        print("="*50)
        print("⏰ Manteniendo abierto por 15 segundos...")
        print("🔍 Verifica que el navegador sea VISIBLE")
        await asyncio.sleep(15)
        
        # Tomar una captura simple
        print("📸 Tomando captura de prueba...")
        await capturar_paso_simple(
            agent.browser_context,
            "test_visibilidad",
            "Navegador visible en Google"
        )
        print("✅ Captura tomada exitosamente")
        
        print("\n🎉 ¡PRUEBA EXITOSA!")
        print("✅ El navegador debería haber sido visible")
        print("📸 Captura guardada en test_screenshots/")
        
    except Exception as e:
        print(f"❌ ERROR en la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        if browser:
            print("\n🔒 Cerrando navegador...")
            await browser.close()
            print("✅ Navegador cerrado")


if __name__ == "__main__":
    print("🧪 INICIANDO PRUEBA DE VISIBILIDAD DEL NAVEGADOR")
    print("=" * 60)
    print("🎯 Objetivo: Verificar que browser-use abre ventana visible")
    print("⚠️  Si no ves el navegador, hay un problema de configuración")
    print()
    
    try:
        asyncio.run(test_navegador_visible())
    except KeyboardInterrupt:
        print("\n⚠️ Prueba interrumpida")
    except Exception as e:
        print(f"\n💥 Error fatal: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🏁 Prueba finalizada") 