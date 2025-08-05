#!/usr/bin/env python3
"""
Test específico para la nueva estructura URL + Paso a Paso
Basado exactamente en las imágenes proporcionadas por el usuario
"""

import pandas as pd
import os
from excel_test_analyzer import ExcelTestAnalyzer

def create_test_with_exact_structure():
    """Crea un Excel con la estructura exacta mostrada en las imágenes"""
    
    print("🧪 Creando Excel con estructura exacta URL + Paso a Paso...")
    
    # Datos exactos de las imágenes
    data = {
        # Columnas exactas como en las imágenes
        '': [4, 5],  # Números de fila
        'URL': [
            'https://www.mercadolibre.cl/',
            'https://www.mercadolibre.cl/'
        ],
        'Paso a Paso': [
            '''Localizar la barra de búsqueda en la parte superior de la página
Hacer clic en el campo de búsqueda
Escribir el término de búsqueda "iPhone 15"
Presionar Enter o hacer clic en el botón de búsqueda (icono de lupa)
Verificar que se muestre el detalle''',
            
            '''Localizar la barra de búsqueda en la parte superior de la página
Hacer clic en el campo de búsqueda
Escribir el término de búsqueda "Smart TV"
Presionar Enter o hacer clic en el botón de búsqueda (icono de lupa)
Esperar a que cargue la página de resultados
Verificar que se muestre el detalle'''
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Agregar headers en la fila correcta (fila 3 según imagen)
    excel_path = 'test_estructura_exacta.xlsx'
    
    # Crear archivo con estructura similar a la imagen
    with pd.ExcelWriter(excel_path) as writer:
        # Crear algunas filas vacías primero
        empty_df = pd.DataFrame([[''] * 3, [''] * 3])  # Filas 1-2 vacías
        empty_df.to_excel(writer, sheet_name='Sheet1', index=False, header=False, startrow=0)
        
        # Agregar los datos reales empezando desde fila 3
        df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=3)
    
    print(f"✅ Archivo de prueba creado: {excel_path}")
    return excel_path

def test_nueva_estructura():
    """Prueba el analizador con la estructura exacta"""
    
    print("🎯 TEST: Estructura Nueva URL + Paso a Paso")
    print("=" * 60)
    
    # Crear archivo de prueba
    excel_path = create_test_with_exact_structure()
    
    try:
        print(f"\n📂 Analizando archivo: {excel_path}")
        
        # Mostrar contenido del archivo para debug
        print(f"\n🔍 CONTENIDO DEL ARCHIVO:")
        df_debug = pd.read_excel(excel_path, header=None)
        print(df_debug.head(10))
        
        # Inicializar analizador
        analyzer = ExcelTestAnalyzer()
        
        # Extraer casos de prueba
        print(f"\n📊 Extrayendo casos de prueba...")
        test_cases = analyzer.extract_test_cases(excel_path)
        
        if not test_cases:
            print("❌ NO SE EXTRAJERON CASOS DE PRUEBA")
            print("🔍 Verificando detección de headers...")
            
            # Debug: verificar detección manual
            df_raw = pd.read_excel(excel_path, header=None)
            header_row, header_columns = analyzer.detect_headers(df_raw)
            print(f"Header detectado en fila: {header_row}")
            print(f"Columnas detectadas: {header_columns}")
            
            if header_row >= 0:
                df_with_header = pd.read_excel(excel_path, header=header_row)
                print(f"Columnas del DataFrame: {list(df_with_header.columns)}")
                mapping = analyzer._map_columns(df_with_header.columns)
                print(f"Mapeo de columnas: {mapping}")
            
            return
        
        print(f"✅ Se extrajeron {len(test_cases)} casos de prueba")
        
        # Mostrar casos extraídos
        for i, case in enumerate(test_cases, 1):
            print(f"\n📝 CASO {i}:")
            print(f"   🆔 ID: {case.id}")
            print(f"   📍 URL Extraída: {case.url_extraida}")
            print(f"   📝 Pasos (primeros 150 chars): {case.pasos[:150]}...")
            
            # Generar instrucciones
            instructions = analyzer._generate_qa_pilot_instructions(case)
            print(f"   🔧 Instrucciones QA-Pilot: {instructions[:200]}...")
        
        # Analizar con IA si está disponible
        if analyzer.client:
            print(f"\n🤖 Analizando con Claude IA...")
            analyzed_cases = analyzer.analyze_with_hybrid_approach(test_cases, data_mode='simulated')
            
            for case in analyzed_cases:
                print(f"\n🎯 CASO OPTIMIZADO: {case.id}")
                print(f"   ✅ Válido: {case.es_valido}")
                if case.instrucciones_qa_pilot:
                    print(f"   🔧 Instrucciones optimizadas: {case.instrucciones_qa_pilot[:250]}...")
                if case.problemas:
                    print(f"   ⚠️ Problemas ({len(case.problemas)}): {case.problemas[:2]}")
                if case.sugerencias:
                    print(f"   💡 Sugerencias ({len(case.sugerencias)}): {case.sugerencias[:2]}")
        
        print(f"\n🎉 TEST COMPLETADO EXITOSAMENTE")
        
    except Exception as e:
        print(f"❌ Error durante el test: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Limpiar archivo de prueba
        try:
            if os.path.exists(excel_path):
                os.remove(excel_path)
                print(f"🧹 Archivo de prueba eliminado: {excel_path}")
        except:
            print(f"⚠️ No se pudo eliminar el archivo: {excel_path}")

if __name__ == "__main__":
    test_nueva_estructura() 