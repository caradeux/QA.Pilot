# -*- coding: utf-8 -*-
"""
Test de Verificación: Browser-Use 0.2.6
=======================================
Script simple para verificar que browser-use abre el navegador en modo visible.
"""

import asyncio
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from browser_use import Agent, Browser, BrowserConfig

load_dotenv()

async def test_browser_visibility():
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
            task="Navegar a https://www.google.com y buscar 'test'",
            llm=llm,
            browser=browser
        )
        
        print("🌍 Ejecutando tarea...")
        
        # Ejecutar con límites estrictos
        result = await agent.run(max_steps=3)
        
        print(f"✅ Test completado: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if browser:
            try:
                await browser.close()
                print("🔒 Navegador cerrado")
            except:
                pass

if __name__ == "__main__":
    asyncio.run(test_browser_visibility()) 