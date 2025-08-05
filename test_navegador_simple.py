# -*- coding: utf-8 -*-
"""
Test Simple de Navegador Visible
===============================
Script para verificar que el navegador se abre visible.
"""

import os
import asyncio
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from browser_use import Agent, Browser, BrowserConfig, BrowserContextConfig

load_dotenv()

async def test_navegador_visible():
    """Prueba simple para verificar navegador visible"""
    
    print("🧪 INICIANDO PRUEBA DE NAVEGADOR VISIBLE")
    print("=" * 50)
    
    try:
        # 1. Configurar navegador EXPLÍCITAMENTE como visible
        print("🌐 Configurando navegador en modo VISIBLE...")
        browser = Browser(
            config=BrowserConfig(
                headless=False,  # EXPLÍCITAMENTE visible
                new_context_config=BrowserContextConfig(
                    browser_window_size={"width": 1280, "height": 720}
                )
            )
        )
        print("✅ Navegador configurado como VISIBLE")
        
        # 2. Configurar LLM
        print("🤖 Configurando LLM...")
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if not anthropic_key:
            # Leer desde .env si no está en el entorno
            env_path = os.path.join(os.getcwd(), '.env')
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('ANTHROPIC_API_KEY='):
                            anthropic_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                            break
        
        if not anthropic_key:
            raise ValueError("❌ ANTHROPIC_API_KEY no encontrada en .env")
        
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=anthropic_key,
            temperature=0.1
        )
        print("✅ LLM configurado correctamente")
        
        # 3. Crear agente
        print("🤖 Creando agente...")
        agent = Agent(
            task="Navegar a Google",
            llm=llm,
            browser=browser
        )
        print("✅ Agente creado")
        
        # 4. Navegar a Google
        print("🌍 Navegando a Google...")
        await agent.browser_context.navigate_to("https://www.google.com")
        print("✅ Navegación completada")
        
        # 5. Mantener abierto para que el usuario vea
        print("\n" + "🎉" * 25)
        print("👀 ¡DEBERÍAS VER EL NAVEGADOR CHROME CON GOOGLE!")
        print("🕒 Manteniendo abierto por 15 segundos...")
        print("🎉" * 25)
        
        await asyncio.sleep(15)
        
        # 6. Cerrar navegador
        print("\n🔒 Cerrando navegador...")
        await browser.close()
        print("✅ Navegador cerrado")
        
        print("\n✅ PRUEBA COMPLETADA EXITOSAMENTE")
        print("Si viste el navegador, ¡todo funciona bien!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n💡 CONSEJOS:")
        print("1. Verifica que ANTHROPIC_API_KEY esté en el archivo .env")
        print("2. Asegúrate de que Chrome esté instalado")
        print("3. Prueba ejecutar como administrador")

if __name__ == "__main__":
    print("🚀 INICIANDO TEST DE NAVEGADOR VISIBLE")
    asyncio.run(test_navegador_visible()) 