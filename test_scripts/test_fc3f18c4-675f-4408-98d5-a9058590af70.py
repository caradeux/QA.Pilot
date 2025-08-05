# -*- coding: utf-8 -*-
import sys, os, asyncio
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from browser_use import Agent, Browser, BrowserConfig

load_dotenv()

# Configuración mínima del navegador
browser = Browser(
    config=BrowserConfig(
        headless=False,
        browser_class='chromium'
    )
)

async def main():
    try:
        print("DEBUG: Iniciando test...")
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if not anthropic_key:
            raise Exception("ANTHROPIC_API_KEY no encontrada")
        
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=anthropic_key,
            temperature=0.1,
            max_tokens=4000
        )
        
        agent = Agent(
            task="Navega a https://www.mercadolibre.cl/ y luego: 1. Escribe 'smartphone' en la barra de búsqueda y presiona Enter
2. Haz clic en el **título** del **primer producto**
3. Espera a que cargue",
            llm=llm,
            browser=browser
        )
        
        print("DEBUG: Agente creado")
        await agent.run(max_steps=15)
        print("DEBUG: Test completado exitosamente")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        print(f"TRACEBACK: {traceback.format_exc()}")
    finally:
        try:
            await browser.close()
            print("DEBUG: Navegador cerrado")
        except Exception as e:
            print(f"Error al cerrar navegador: {e}")

if __name__ == "__main__":
    asyncio.run(main())
