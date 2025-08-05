#!/usr/bin/env python3
"""
Demo: Carga de archivo Excel con estructura URL + Paso a Paso para ejecución individual
"""

import pandas as pd
import json
from excel_test_analyzer import ExcelTestAnalyzer

def demo_carga_excel():
    """Demostración de carga y análisis de Excel con estructura URL + Paso a Paso"""
    
    print("🎯 DEMO: Carga de Excel con estructura URL + Paso a Paso (Destino + Misión)")
    print("=" * 70)
    
    # Ruta del archivo Excel (ajustar según tu archivo)
    excel_path = input("📁 Ingresa la ruta de tu archivo Excel (o presiona Enter para usar Template.xlsx): ").strip()
    
    if not excel_path:
        excel_path = "test_evidencia/template/Template.xlsx"
    
    try:
        # Verificar que el archivo existe
        import os
        if not os.path.exists(excel_path):
            print(f"❌ Error: No se encontró el archivo {excel_path}")
            return
        
        print(f"\n📂 Cargando archivo: {excel_path}")
        
        # Inicializar analizador
        analyzer = ExcelTestAnalyzer()
        
        # Extraer casos de prueba
        print("\n📊 Analizando estructura del Excel...")
        test_cases = analyzer.extract_test_cases(excel_path)
        
        if not test_cases:
            print("❌ No se encontraron casos de prueba válidos en el archivo")
            return
        
        print(f"✅ Se extrajeron {len(test_cases)} casos de prueba")
        
        # Mostrar estructura detectada
        first_case = test_cases[0]
        if hasattr(first_case, 'url_extraida') and first_case.url_extraida:
            print(f"🎯 Estructura detectada: URL + Paso a Paso (Destino + Misión)")
            print(f"   📍 Destino ejemplo: {first_case.url_extraida}")
            print(f"   📝 Misión ejemplo: {first_case.pasos[:100]}...")
        
        # Analizar casos con IA si está disponible
        analyzed_cases = test_cases
        if analyzer.client:
            print(f"\n🤖 Analizando casos con Claude IA...")
            analyzed_cases = analyzer.analyze_with_hybrid_approach(test_cases, data_mode='simulated')
            print(f"✅ Análisis completado")
        
        # Mostrar casos listos para ejecución
        print(f"\n📋 CASOS LISTOS PARA EJECUCIÓN INDIVIDUAL:")
        print("=" * 50)
        
        casos_validos = 0
        casos_json = []
        
        for i, case in enumerate(analyzed_cases, 1):
            print(f"\n🔸 CASO {i}: {case.id}")
            print(f"   📍 Destino: {case.url_extraida or 'No especificado'}")
            print(f"   ✅ Válido: {'Sí' if case.es_valido else 'No'}")
            
            if case.es_valido:
                casos_validos += 1
                
                # Preparar estructura para QA-Pilot
                case_data = {
                    "id": case.id,
                    "nombre": case.nombre or f"Caso {case.id}",
                    "url": case.url_extraida,
                    "pasos": case.instrucciones_qa_pilot or case.pasos,
                    "objetivo": case.objetivo or "Prueba de funcionalidad web",
                    "datos_prueba": case.datos_prueba or "Datos simulados",
                    "resultado_esperado": case.resultado_esperado or "Ejecución exitosa"
                }
                casos_json.append(case_data)
                
                print(f"   🔧 Instrucciones optimizadas: {case.instrucciones_qa_pilot[:100] if case.instrucciones_qa_pilot else 'N/A'}...")
            
            if case.problemas:
                print(f"   ⚠️ Problemas: {len(case.problemas)} identificados")
                for problema in case.problemas[:2]:  # Mostrar solo los primeros 2
                    print(f"      • {problema}")
            
            if case.sugerencias:
                print(f"   💡 Sugerencias: {len(case.sugerencias)} disponibles")
        
        print(f"\n📊 RESUMEN:")
        print(f"   📝 Total de casos: {len(analyzed_cases)}")
        print(f"   ✅ Casos válidos para ejecución: {casos_validos}")
        print(f"   ⚠️ Casos que necesitan corrección: {len(analyzed_cases) - casos_validos}")
        
        # Guardar casos válidos para el sistema QA-Pilot
        if casos_validos > 0:
            output_file = "casos_para_qa_pilot.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(casos_json, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Casos válidos guardados en: {output_file}")
            print(f"   📤 Estos casos están listos para cargar en QA-Pilot")
            
            # Mostrar ejemplo de cómo usar en QA-Pilot
            print(f"\n🚀 CÓMO EJECUTAR EN QA-PILOT:")
            print("   1. Ve a http://127.0.0.1:8503/excel_bulk_execution")
            print("   2. Carga tu archivo Excel original")
            print("   3. Verifica que los casos aparezcan correctamente")
            print("   4. Usa el botón 'Ejecutar' individual para cada caso")
            print("   5. Configura si quieres ver el navegador o ejecutar en background")
            
            # Mostrar primer caso como ejemplo
            if casos_json:
                primer_caso = casos_json[0]
                print(f"\n📋 EJEMPLO DE CASO LISTO:")
                print(f"   🆔 ID: {primer_caso['id']}")
                print(f"   📍 URL: {primer_caso['url']}")
                print(f"   📝 Pasos: {primer_caso['pasos'][:150]}...")
        
        print(f"\n🎉 ANÁLISIS COMPLETADO - Casos listos para ejecución individual")
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_carga_excel() 