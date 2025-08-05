#!/usr/bin/env python3
"""
Script para probar las rutas de ejecución masiva
"""

import requests
import json

def test_execution_routes():
    """Prueba las rutas de ejecución masiva"""
    
    base_url = "http://localhost:5000"
    
    # Datos de prueba
    test_cases = [
        {
            "id": "CP-001",
            "nombre": "Caso de prueba 1",
            "objetivo": "Probar funcionalidad básica",
            "pasos": "1. Abrir navegador\n2. Ir a URL\n3. Verificar contenido",
            "datos_prueba": "URL: https://example.com",
            "resultado_esperado": "Página carga correctamente",
            "es_valido": True,
            "url_extraida": "https://example.com"
        },
        {
            "id": "CP-002", 
            "nombre": "Caso de prueba 2",
            "objetivo": "Probar navegación",
            "pasos": "1. Login\n2. Navegar a dashboard",
            "datos_prueba": "Usuario: test, Password: 123",
            "resultado_esperado": "Dashboard visible",
            "es_valido": True,
            "url_extraida": "https://example.com/login"
        }
    ]
    
    print("🧪 Probando ruta de ejecución masiva...")
    
    try:
        # Probar ejecución masiva
        response = requests.post(
            f"{base_url}/api/execute_bulk_cases",
            json={
                "test_cases": test_cases,
                "execution_mode": "sequential"
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                execution_id = result.get('execution_id')
                print(f"✅ Ejecución iniciada exitosamente: {execution_id}")
                
                # Probar estado de ejecución
                print("\n🔍 Probando estado de ejecución...")
                status_response = requests.get(f"{base_url}/api/execution_status/{execution_id}")
                print(f"Status Code: {status_response.status_code}")
                print(f"Response: {status_response.text}")
                
            else:
                print(f"❌ Error en la respuesta: {result.get('error')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor. ¿Está ejecutándose en localhost:5000?")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    test_execution_routes() 