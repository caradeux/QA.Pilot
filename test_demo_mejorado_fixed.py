# -*- coding: utf-8 -*-
"""
Test Demo Mejorado con Utilidad de Capturas - VERSIÓN CORREGIDA
==============================================================
Versión que combina la lógica exitosa del test_demo.py original
con la nueva utilidad de capturas simplificada.

Esta versión mantiene la navegación manual que funcionaba correctamente
pero usa las capturas simplificadas.
"""

import sys
import os
import asyncio
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from browser_use import Agent, Browser, BrowserConfig, BrowserContextConfig
from pydantic import SecretStr

# ⭐ IMPORTAR LA NUEVA UTILIDAD DE CAPTURAS
from utils_screenshot import ScreenshotManager

# Cargar variables de entorno
load_dotenv()

async def main():
    """
    Test demo corregido que mantiene la navegación manual exitosa
    pero usa las capturas simplificadas.
    """
    browser = None
    agent = None
    
    try:
        print("🚀 Iniciando test demo corregido...")
        
        # ===== CONFIGURACIÓN DEL NAVEGADOR (IGUAL QUE EL ORIGINAL) =====
        print("🌐 Inicializando browser...")
        browser = Browser(
            config=BrowserConfig(
                headless=False,  # ⚠️ EXPLÍCITAMENTE False
                new_context_config=BrowserContextConfig(
                    browser_window_size={"width": 1920, "height": 1080},
                    minimum_wait_page_load_time=1.0,
                    wait_for_network_idle_page_load_time=2.0,
                    maximum_wait_page_load_time=15.0,
                    wait_between_actions=0.5
                )
            )
        )
        print("✅ Browser configurado correctamente con viewport 1920x1080")

        # ===== CONFIGURACIÓN DEL LLM (IGUAL QUE EL ORIGINAL) =====
        print("🤖 Configurando LLM...")
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not anthropic_key:
            try:
                from dotenv import load_dotenv
                load_dotenv()
                anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            except ImportError:
                pass
                
        if not anthropic_key:
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
            raise ValueError("❌ ANTHROPIC_API_KEY no encontrada")
        
        # Verificar si la clave es SecretStr (como en el original)
        if isinstance(anthropic_key, SecretStr):
            anthropic_key = anthropic_key.get_secret_value()
            
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",  # Modelo actualizado
            api_key=anthropic_key,
            temperature=0.1,
            max_tokens=4000
        )
        print("✅ LLM configurado correctamente")

        # ===== CREAR AGENTE (IGUAL QUE EL ORIGINAL PERO SIN TASK INICIAL) =====
        print("🤖 Creando agente...")
        
        # ⚠️ CREAR AGENTE SIN TASK PARA NAVEGACIÓN MANUAL
        agent = Agent(
            task="",  # Task vacío para control manual
            llm=llm,
            browser=browser,
            use_vision=True  # Como en el original
        )
        print("✅ Agente creado correctamente")

        # ⭐ ===== CONFIGURAR GESTOR DE CAPTURAS =====
        print("📷 Configurando gestor de capturas...")
        screenshots = ScreenshotManager(task_id="test_demo_corregido")
        print(f"✅ Capturas se guardarán en: {screenshots.obtener_directorio()}")

        # ===== NAVEGACIÓN MANUAL (COMO EN EL ORIGINAL) =====
        print("🌐 Navegando a MercadoLibre...")
        await agent.browser_context.navigate_to("https://www.mercadolibre.cl")
        print("✅ Navegación inicial completada")
        
        # Pausa para permitir carga completa
        await asyncio.sleep(2)
        
        # ⭐ CAPTURA INICIAL
        print("📸 Tomando captura inicial...")
        await screenshots.capturar_inicial(
            agent.browser_context, 
            "Página inicial MercadoLibre cargada"
        )

        # ===== PASO 1: BUSCAR 'SMARTPHONE' =====
        print("🔍 Ejecutando paso 1: Buscar 'smartphone'...")
        
        try:
            # Localizar el elemento de búsqueda
            search_input = await agent.browser_context.get_locate_element_by_css_selector('input[name="as_word"]')
            if search_input:
                await search_input.fill('smartphone')
                print("✅ Texto 'smartphone' ingresado en búsqueda")
                
                # Hacer clic en el botón de búsqueda
                search_button = await agent.browser_context.get_locate_element_by_css_selector('.nav-search-btn')
                if search_button:
                    await search_button.click()
                    print("✅ Botón de búsqueda presionado")
                    
                    # Esperar resultados
                    await asyncio.sleep(3)
                    
                    # ⭐ CAPTURA DESPUÉS DE BÚSQUEDA
                    await screenshots.capturar_paso(
                        agent.browser_context,
                        1,
                        "Resultados búsqueda smartphone"
                    )
                else:
                    print("❌ No se encontró el botón de búsqueda")
            else:
                print("❌ No se encontró el campo de búsqueda")
                # Si no funciona la búsqueda manual, usar el agente
                print("🤖 Usando agente para búsqueda...")
                agent.task = "Busca 'smartphone' en la página"
                await agent.run(max_steps=3)
                
                await screenshots.capturar_paso(
                    agent.browser_context,
                    1,
                    "Búsqueda realizada por agente"
                )
                
        except Exception as e:
            print(f"⚠️ Error en búsqueda manual: {e}")
            # Fallback al agente
            print("🤖 Usando agente como fallback...")
            agent.task = "Busca 'smartphone' en MercadoLibre"
            await agent.run(max_steps=3)
            
            await screenshots.capturar_paso(
                agent.browser_context,
                1,
                "Búsqueda fallback por agente"
            )

        # ===== PASO 2: SELECCIONAR PRIMER RESULTADO =====
        print("🎯 Ejecutando paso 2: Seleccionar primer resultado...")
        
        try:
            # Intentar hacer clic en el primer resultado
            result_link = await agent.browser_context.get_locate_element_by_css_selector('.ui-search-result__content a')
            if result_link:
                await result_link.click()
                print("✅ Primer resultado seleccionado")
                
                # Esperar carga de página de producto
                await asyncio.sleep(3)
                
                # ⭐ CAPTURA DE PRODUCTO
                await screenshots.capturar_paso(
                    agent.browser_context,
                    2,
                    "Página de producto cargada"
                )
            else:
                print("❌ No se encontró el primer resultado")
                # Usar agente para seleccionar
                print("🤖 Usando agente para seleccionar...")
                agent.task = "Haz clic en el primer producto de los resultados"
                await agent.run(max_steps=3)
                
                await screenshots.capturar_paso(
                    agent.browser_context,
                    2,
                    "Producto seleccionado por agente"
                )
                
        except Exception as e:
            print(f"⚠️ Error seleccionando producto: {e}")
            # Fallback al agente
            print("🤖 Usando agente como fallback...")
            agent.task = "Selecciona el primer producto de los resultados de búsqueda"
            await agent.run(max_steps=3)
            
            await screenshots.capturar_paso(
                agent.browser_context,
                2,
                "Selección fallback por agente"
            )

        # ===== PASO 3: VER DETALLES =====
        print("👀 Ejecutando paso 3: Ver detalles del producto...")
        
        # Simplemente esperar a que se cargue y hacer scroll si es necesario
        await asyncio.sleep(2)
        
        # ⭐ CAPTURA FINAL
        print("📸 Tomando captura final...")
        await screenshots.capturar_final(
            agent.browser_context,
            "Detalles completos del producto"
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
            print()
        
        print("✨ Test demo corregido completado exitosamente")
        print("🌐 El navegador debería haber estado visible durante toda la ejecución")
        
    except Exception as e:
        print(f"❌ ERROR durante la ejecución: {str(e)}")
        
        # ⭐ CAPTURA DE ERROR
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
        # ⚠️ MANTENER NAVEGADOR ABIERTO PARA VERIFICAR
        print("\n⏸️  PAUSA: El navegador permanecerá abierto por 10 segundos para verificar...")
        print("🔍 Verifica que el navegador esté visible y las capturas sean correctas")
        await asyncio.sleep(10)
        
        # Cerrar navegador
        if browser:
            try:
                await browser.close()
                print("✅ Navegador cerrado correctamente")
            except Exception as e:
                print(f"⚠️ Error cerrando navegador: {e}")

        print("\n🏁 Test finalizado")


if __name__ == "__main__":
    print("🔧 Ejecutando test_demo_mejorado_fixed.py")
    print("📖 Este script mantiene la lógica exitosa del original")
    print("📷 Pero usa las capturas simplificadas")
    print("🌐 El navegador DEBE ser visible durante la ejecución\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrumpido por el usuario")
    except Exception as e:
        print(f"\n💥 Error fatal: {e}")
        import traceback
        traceback.print_exc() 