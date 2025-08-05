from browser_use import Agent
from langchain_openai import ChatOpenAI
import asyncio
import json
from datetime import datetime

class WebTester:
    def __init__(self, base_url=None):
        self.base_url = base_url
        self.test_results = []
        
    async def run_test(self, test_description):
        """
        Ejecuta una prueba basada en una descripción en lenguaje natural
        
        Args:
            test_description (str): Descripción de la prueba a realizar
        """
        # Preparar la tarea con navegación explícita
        task = f"""
        INSTRUCCIONES DE NAVEGACIÓN:
        Primero, ejecuta este comando exactamente como está escrito:
        playwright_navigate({{"url": "{self.base_url}"}})

        Después de la navegación, espera 5 segundos y luego procede con:
        {test_description}
        """
        
        # Crear y ejecutar el agente
        agent = Agent(
            task=task,
            llm=ChatOpenAI(model="gpt-4")
        )
        
        # Registrar el inicio de la prueba
        test_start = datetime.now()
        
        try:
            # Ejecutar la prueba
            await agent.run()
            
            # Registrar el resultado
            self.test_results.append({
                "description": test_description,
                "url": self.base_url,
                "timestamp": test_start.isoformat(),
                "status": "success",
                "duration": (datetime.now() - test_start).total_seconds()
            })
            
        except Exception as e:
            # Registrar el error
            self.test_results.append({
                "description": test_description,
                "url": self.base_url,
                "timestamp": test_start.isoformat(),
                "status": "failed",
                "error": str(e),
                "duration": (datetime.now() - test_start).total_seconds()
            })
            raise
    
    def save_results(self, filename="test_results.json"):
        """Guarda los resultados de las pruebas en un archivo JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False) 