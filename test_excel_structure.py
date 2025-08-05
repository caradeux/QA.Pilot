#!/usr/bin/env python3
"""
Script de prueba para validar el analizador de Excel con estructura URL + Paso a Paso
"""

import pandas as pd
import os
from excel_test_analyzer import ExcelTestAnalyzer

def create_test_excel():
    """Crea un archivo Excel de prueba con la estructura URL + Paso a Paso"""
    
    # Datos de prueba basados en la imagen proporcionada
    data = {
        'Nº CP': ['CP001', 'CP002'],
        'URL': [
            'https://www.mercadolibre.cl/',
            'https://www.mercadolibre.cl/'
        ],
        'Paso a Paso': [
            '''Localizar la barra de búsqueda en la parte superior de la página
Hacer clic en el campo de búsqueda
Escribir el término de búsqueda "iPhone 15"
Presionar Enter o hacer clic en el botón de búsqueda (icono de lupa)
Esperar a que cargue la página de resultados
Verificar que se muestren productos relacionados con iPhone 15''',
            
            '''Localizar la barra de búsqueda en la parte superior de la página
Hacer clic en el campo de búsqueda
Escribir el término de búsqueda "iPhone 15"
Presionar Enter o hacer clic en el botón de búsqueda (icono de lupa)
Esperar a que cargue la página de resultados
Verificar que se muestren productos relacionados con iPhone 15'''
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Crear archivo Excel
    excel_path = 'test_structure.xlsx'
    df.to_excel(excel_path, index=False)
    
    print(f"✅ Archivo de prueba creado: {excel_path}")
    return excel_path

def test_analyzer():
    """Prueba el analizador con la estructura URL + Paso a Paso"""
    
    print("🧪 PRUEBA: Analizador de Excel con estructura URL + Paso a Paso")
    print("=" * 60)
    
    # Crear archivo de prueba
    excel_path = create_test_excel()
    
    try:
        # Inicializar analizador
        analyzer = ExcelTestAnalyzer()
        
        # Extraer casos de prueba
        print("\n📊 Extrayendo casos de prueba...")
        test_cases = analyzer.extract_test_cases(excel_path)
        
        print(f"✅ Se extrajeron {len(test_cases)} casos de prueba")
        
        # Mostrar resultados
        for i, case in enumerate(test_cases, 1):
            print(f"\n📝 CASO {i}: {case.id}")
            print(f"   URL Destino: {case.url_extraida}")
            print(f"   Misión: {case.pasos[:100]}...")
            
            # Generar instrucciones QA-Pilot
            instructions = analyzer._generate_qa_pilot_instructions(case)
            print(f"   Instrucciones QA-Pilot: {instructions[:150]}...")
        
        # Analizar con IA si está disponible
        if analyzer.client:
            print("\n🤖 Analizando casos con IA...")
            analyzed_cases = analyzer.analyze_with_hybrid_approach(test_cases, data_mode='simulated')
            
            print(f"✅ Análisis con IA completado")
            
            for case in analyzed_cases:
                print(f"\n🎯 CASO OPTIMIZADO: {case.id}")
                print(f"   ✅ Válido: {case.es_valido}")
                print(f"   🔧 Instrucciones: {case.instrucciones_qa_pilot[:200]}...")
                if case.problemas:
                    print(f"   ⚠️ Problemas: {', '.join(case.problemas)}")
                if case.sugerencias:
                    print(f"   💡 Sugerencias: {', '.join(case.sugerencias)}")
        
        print("\n🎉 PRUEBA COMPLETADA EXITOSAMENTE")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Limpiar archivo de prueba
        if os.path.exists(excel_path):
            os.remove(excel_path)
            print(f"🧹 Archivo de prueba eliminado: {excel_path}")

if __name__ == "__main__":
    test_analyzer() 