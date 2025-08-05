from tasks.testing.web_tester import WebTester
import asyncio
from dotenv import load_dotenv
load_dotenv()

async def main():
    # Crear una instancia del tester con la URL de demoblaze
    tester = WebTester(base_url="https://www.demoblaze.com")
    
    # Test simplificado para verificar la navegación
    test_description = """
    Prueba de navegación básica:
    1. Ejecutar el siguiente comando exactamente:
       playwright_navigate({"url": "https://www.demoblaze.com"})
    
    2. Esperar 5 segundos para asegurar la carga
    
    3. Tomar una captura de pantalla:
       playwright_screenshot({"name": "navegacion_inicial"})
    
    4. Verificar el contenido:
       playwright_get_visible_text({"random_string": "check"})
    """
    
    try:
        # Ejecutar el test
        await tester.run_test(test_description)
        
        # Guardar los resultados
        tester.save_results("demoblaze_test_results.json")
        print("Test de navegación básica completado. Resultados guardados en demoblaze_test_results.json")
        
    except Exception as e:
        print(f"Error durante la ejecución del test: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 