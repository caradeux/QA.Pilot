# -*- coding: utf-8 -*-
import sys, os, asyncio, base64, traceback, re, time, random, json
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from browser_use import Agent, Browser, BrowserConfig

# Cargar variables de entorno
load_dotenv()


# Función para capturar pantalla en cada paso (compatible con browser-use 0.2.6)
async def capturar_paso(num_paso, descripcion):
    try:
        # En browser-use 0.2.6, las capturas se manejan automáticamente
        # Esta función es principalmente para logging
        timestamp = int(time.time())
        safe_desc = re.sub(r'[^a-zA-Z0-9_]', '_', descripcion[:30])
        
        print(f"Paso {num_paso}: {descripcion} - {timestamp}")
        
        # Crear directorio para capturas si no existe
        script_name_without_ext = os.path.splitext(os.path.basename(__file__))[0]
        screenshot_subdir = os.path.join(os.getcwd(), "test_screenshots", script_name_without_ext)
        os.makedirs(screenshot_subdir, exist_ok=True)
        
        return f"paso_{num_paso}_{safe_desc}_{timestamp}"
    except Exception as e:
        print(f"Error al procesar paso {num_paso}: {str(e)}")
        return None


async def main():
    try:
        print("DEBUG: Iniciando test...")
        
        print("DEBUG: Configurando LLM...")
        # Obtener clave API
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if not anthropic_key:
            env_path = os.path.join(os.getcwd(), '.env')
            if os.path.exists(env_path):
                try:
                    with open(env_path, 'r') as f:
                        for line in f:
                            if line.startswith('ANTHROPIC_API_KEY='):
                                anthropic_key = line.split('=', 1)[1].strip()
                                break
                except:
                    pass
        
        if not anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY no encontrada")
        
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20240620",
            api_key=anthropic_key,
            temperature=0.0,
            timeout=100
        )
        print("DEBUG: LLM configurado correctamente")

        print("DEBUG: Creando agente con nueva API...")
        # Definir la tarea completa incluyendo navegación
        task_instructions = """Navega a https://www.mercadolibre.cl y luego: 1. Buscar 'smartphone'2. Seleccionar el primer resultado3. Ver detalles"""
        
        # Crear BrowserSession con configuración headless
        
        # Crear configuración del navegador para browser-use 0.2.6
        browser_config = BrowserConfig(headless=False)
        browser = Browser(config=browser_config)
        
        # Crear agente con la nueva API simplificada de browser-use 0.2.6
        agent = Agent(
            task=task_instructions,
            llm=llm,
            browser=browser
        )
        print("DEBUG: Agente creado correctamente con nueva API")

        # Crear directorio para capturas si no existe (directorio base)
        os.makedirs(os.path.join(os.getcwd(), "test_screenshots"), exist_ok=True)


        # En browser-use 0.2.6, el agente maneja automáticamente los pasos
        # Solo registramos los pasos para logging
        print("DEBUG: Registrando pasos para seguimiento...")
        
        # Paso 1: Buscar 'smartphone'
        print(f"Paso planificado 1: Buscar 'smartphone'")
        await capturar_paso(1, "Buscar 'smartphone'")
        
        # Paso 2: Seleccionar el primer resultado
        print(f"Paso planificado 2: Seleccionar el primer resultado")
        await capturar_paso(2, "Seleccionar el primer resultado")
        
        # Paso 3: Ver detalles
        print(f"Paso planificado 3: Ver detalles")
        await capturar_paso(3, "Ver detalles")
        
        
        # Ejecutar el agente con la nueva API simplificada
        print("DEBUG: Ejecutando agente con las instrucciones...")
        # En browser-use 0.2.6, el agente maneja automáticamente la navegación y ejecución
        result = await agent.run()
        print("INFO: Resultado final:", result)
        
        # Devolver resultado
        return result
    except Exception as e:
        print("ERROR GENERAL:", str(e))
        traceback.print_exc()
        raise

if __name__ == "__main__":
    try:
        print("DEBUG: Iniciando ejecución del script")
            
        # Ejecutar función principal
        print("Iniciando ejecución principal")
        asyncio.run(main())
        print("Ejecución completada con éxito")
        sys.exit(0)
    except Exception as e:
        print("ERROR FATAL:", str(e))
        traceback.print_exc()
        sys.exit(1)
