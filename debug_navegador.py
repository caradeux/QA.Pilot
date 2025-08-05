# -*- coding: utf-8 -*-
"""
Script de Debug para el Problema del Navegador
==============================================
Este script ayuda a diagnosticar por qué el navegador no se abre visible.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from browser_use import Agent, Browser, BrowserConfig, BrowserContextConfig

load_dotenv()

async def test_browser_visibility(headless_mode=False):
    """
    Prueba simple para verificar que el navegador se abre visible
    """
    print(f"🧪 PRUEBA: Navegador con headless={headless_mode}")
    
    try:
        # Configurar navegador
        browser = Browser(
            config=BrowserConfig(
                headless=headless_mode,
                new_context_config=BrowserContextConfig(
                    browser_window_size={"width": 1280, "height": 720}
                )
            )
        )
        
        print(f"✅ Navegador configurado: headless={headless_mode}")
        
        # Configurar LLM
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if not anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY no encontrada")
        
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=anthropic_key,
            temperature=0.1
        )
        
        # Crear agente
        agent = Agent(
            task="Navegar a https://www.google.com y buscar 'test'",
            llm=llm,
            browser=browser
        )
        
        print(f"🌍 Navegando a Google...")
        
        # Ejecutar navegación simple
        await agent.browser_context.navigate_to("https://www.google.com")
        
        print(f"⏰ Manteniendo navegador abierto por 10 segundos...")
        print(f"👀 ¿PUEDES VER EL NAVEGADOR CON GOOGLE?")
        
        await asyncio.sleep(10)
        
        print(f"✅ Prueba completada")
        
        # Cerrar navegador
        await browser.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Ejecutar pruebas con diferentes configuraciones"""
    print("=" * 50)
    print("DIAGNÓSTICO DEL PROBLEMA DEL NAVEGADOR")
    print("=" * 50)
    
    # Prueba 1: Con navegador visible (headless=False)
    print("\n1. PRUEBA CON NAVEGADOR VISIBLE")
    await test_browser_visibility(headless_mode=False)
    
    print("\n" + "=" * 50)
    print("Si no viste el navegador en la prueba anterior,")
    print("el problema está en la configuración del sistema.")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main()) 