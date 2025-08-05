# -*- coding: utf-8 -*-
"""
Ejemplo de Uso de la Utilidad de Capturas de Pantalla
=====================================================
Este archivo muestra diferentes formas de usar la nueva utilidad de capturas
en tu proyecto con browser-use.
"""

import asyncio
import os
from langchain_anthropic import ChatAnthropic
from browser_use import Agent, Browser, BrowserConfig
from utils_screenshot import ScreenshotManager, capturar_paso_simple, auto_screenshot, integrar_captura_con_sistema

async def ejemplo_basico_screenshot_manager():
    """
    Ejemplo básico usando ScreenshotManager - RECOMENDADO
    """
    print("🔵 Ejemplo 1: Uso básico con ScreenshotManager")
    
    # Configurar browser-use
    browser = Browser(config=BrowserConfig(headless=False))
    
    try:
        # Configurar LLM
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=os.getenv('ANTHROPIC_API_KEY'),
            temperature=0.1
        )
        
        # Crear agent
        agent = Agent(
            task="Navega a https://www.google.com y busca 'Python testing'",
            llm=llm,
            browser=browser
        )
        
        # ⭐ CREAR GESTOR DE CAPTURAS
        screenshot_manager = ScreenshotManager(task_id="ejemplo_basico")
        
        print("📷 Tomando captura inicial...")
        # Captura inicial
        await screenshot_manager.capturar_inicial(
            agent.browser_context, 
            "Página inicial antes de ejecutar"
        )
        
        print("🚀 Ejecutando test...")
        # Ejecutar test
        await agent.run(max_steps=5)
        
        print("📷 Tomando capturas durante la ejecución...")
        # Capturas durante la ejecución
        await screenshot_manager.capturar_paso(
            agent.browser_context, 
            1, 
            "Después de buscar Python testing"
        )
        
        await screenshot_manager.capturar_paso(
            agent.browser_context, 
            2, 
            "Página de resultados"
        )
        
        # Captura final
        await screenshot_manager.capturar_final(
            agent.browser_context, 
            "Estado final del test"
        )
        
        # Mostrar información de capturas
        capturas = screenshot_manager.obtener_capturas()
        print(f"✅ Se tomaron {len(capturas)} capturas")
        print(f"📁 Guardadas en: {screenshot_manager.obtener_directorio()}")
        
        for captura in capturas:
            print(f"  📸 Paso {captura['paso']}: {captura['descripcion']}")
        
    finally:
        await browser.close()


async def ejemplo_captura_simple():
    """
    Ejemplo usando la función simple para capturas rápidas
    """
    print("🟢 Ejemplo 2: Capturas simples y rápidas")
    
    browser = Browser(config=BrowserConfig(headless=False))
    
    try:
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=os.getenv('ANTHROPIC_API_KEY'),
            temperature=0.1
        )
        
        agent = Agent(
            task="Navega a https://httpbin.org/html",
            llm=llm,
            browser=browser
        )
        
        # ⭐ CAPTURAS SIMPLES
        print("📷 Captura antes de ejecutar...")
        await capturar_paso_simple(
            agent.browser_context, 
            "Estado inicial httpbin",
            directorio="capturas_rapidas"
        )
        
        await agent.run(max_steps=3)
        
        print("📷 Captura después de ejecutar...")
        await capturar_paso_simple(
            agent.browser_context, 
            "Página cargada httpbin",
            directorio="capturas_rapidas"
        )
        
    finally:
        await browser.close()


async def ejemplo_integracion_sistema():
    """
    Ejemplo de integración con el sistema de tracking existente
    """
    print("🟡 Ejemplo 3: Integración con sistema de tracking")
    
    browser = Browser(config=BrowserConfig(headless=False))
    
    try:
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=os.getenv('ANTHROPIC_API_KEY'),
            temperature=0.1
        )
        
        agent = Agent(
            task="Navega a https://www.example.com",
            llm=llm,
            browser=browser
        )
        
        task_id = "test_12345"
        
        # ⭐ INTEGRACIÓN CON SISTEMA EXISTENTE
        print("📷 Captura integrada con sistema...")
        captura_info = await integrar_captura_con_sistema(
            agent.browser_context,
            task_id,
            "Página de ejemplo cargada"
        )
        
        if captura_info:
            print("✅ Captura integrada exitosamente:")
            print(f"  URL: {captura_info['url']}")
            print(f"  Archivo: {captura_info['name']}")
            print(f"  Ruta: {captura_info['path']}")
        
        await agent.run(max_steps=2)
        
        # Otra captura integrada
        captura_info_2 = await integrar_captura_con_sistema(
            agent.browser_context,
            task_id,
            "Estado final example.com"
        )
        
        if captura_info_2:
            print("✅ Segunda captura integrada exitosamente")
        
    finally:
        await browser.close()


@auto_screenshot("Test con decorador automático")
async def ejemplo_con_decorador(agent):
    """
    Ejemplo usando el decorador automático
    """
    print("🔴 Ejemplo 4: Decorador automático")
    
    # Esta función automáticamente toma capturas antes y después
    await agent.run(max_steps=3)
    
    return "Test completado con decorador"


async def ejemplo_decorador():
    """
    Wrapper para el ejemplo con decorador
    """
    browser = Browser(config=BrowserConfig(headless=False))
    
    try:
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=os.getenv('ANTHROPIC_API_KEY'),
            temperature=0.1
        )
        
        agent = Agent(
            task="Navega a https://httpbin.org/json",
            llm=llm,
            browser=browser
        )
        
        # El decorador automáticamente tomará capturas
        resultado = await ejemplo_con_decorador(agent)
        print(f"✅ {resultado}")
        
    finally:
        await browser.close()


async def ejemplo_modificar_script_existente():
    """
    Ejemplo de cómo modificar un script existente para agregar capturas
    """
    print("🟣 Ejemplo 5: Modificar script existente")
    
    # Esta es la forma MÁS SIMPLE de agregar capturas a un script existente
    
    browser = Browser(config=BrowserConfig(headless=False))
    
    try:
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=os.getenv('ANTHROPIC_API_KEY'),
            temperature=0.1
        )
        
        agent = Agent(
            task="Navega a https://www.mercadolibre.cl y busca 'laptop'",
            llm=llm,
            browser=browser
        )
        
        # ⭐ SOLAMENTE ESTAS 3 LÍNEAS PARA AGREGAR CAPTURAS A UN SCRIPT EXISTENTE:
        
        # 1. Importar la utilidad (ya está importada arriba)
        # 2. Crear gestor
        screenshots = ScreenshotManager("mercadolibre_test")
        
        # 3. Agregar capturas en puntos clave
        await screenshots.capturar_inicial(agent.browser_context, "MercadoLibre inicial")
        
        # Tu código original de test aquí
        await agent.run(max_steps=5)
        
        # Más capturas donde necesites
        await screenshots.capturar_paso(agent.browser_context, None, "Búsqueda completada")
        await screenshots.capturar_final(agent.browser_context, "Test finalizado")
        
        print(f"✅ Capturas guardadas en: {screenshots.obtener_directorio()}")
        
    finally:
        await browser.close()


async def main():
    """
    Ejecuta todos los ejemplos
    """
    print("🚀 Iniciando ejemplos de capturas de pantalla")
    print("=" * 60)
    
    # Verificar que la clave API existe
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ERROR: ANTHROPIC_API_KEY no configurada")
        print("Agrega tu clave API al archivo .env o como variable de entorno")
        return
    
    try:
        # Ejemplo 1: Básico con ScreenshotManager (RECOMENDADO)
        await ejemplo_basico_screenshot_manager()
        print("\n" + "─" * 60 + "\n")
        
        # Ejemplo 2: Capturas simples
        await ejemplo_captura_simple()
        print("\n" + "─" * 60 + "\n")
        
        # Ejemplo 3: Integración con sistema
        await ejemplo_integracion_sistema()
        print("\n" + "─" * 60 + "\n")
        
        # Ejemplo 4: Decorador automático
        await ejemplo_decorador()
        print("\n" + "─" * 60 + "\n")
        
        # Ejemplo 5: Modificar script existente (MÁS SIMPLE)
        await ejemplo_modificar_script_existente()
        
        print("\n🎉 ¡Todos los ejemplos completados exitosamente!")
        print("\n📋 RESUMEN DE OPCIONES:")
        print("  1. ScreenshotManager - Para control completo y organizado")
        print("  2. capturar_paso_simple - Para capturas rápidas")
        print("  3. @auto_screenshot - Para automatización con decoradores")
        print("  4. integrar_captura_con_sistema - Para tu sistema existente")
        print("\n🏆 RECOMENDACIÓN: Usa ScreenshotManager para la mayoría de casos")
        
    except Exception as e:
        print(f"❌ Error ejecutando ejemplos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 