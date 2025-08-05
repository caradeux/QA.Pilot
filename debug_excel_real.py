#!/usr/bin/env python3
"""
Debug para archivos Excel reales - Simular diferentes estructuras
"""

import pandas as pd
import os
from excel_test_analyzer import ExcelTestAnalyzer

def create_different_excel_structures():
    """Crea diferentes estructuras de Excel para probar la detección"""
    
    test_files = []
    
    # ESTRUCTURA 1: Como en la imagen (fila 4 con headers)
    print("📝 Creando Estructura 1: Headers en fila 4...")
    data1 = {
        'A': ['', '', '', 'URL', 'https://www.mercadolibre.cl/', 'https://www.mercadolibre.cl/'],
        'B': ['', '', '', 'Paso a Paso', 'Localizar la barra...', 'Localizar la barra...']
    }
    df1 = pd.DataFrame(data1)
    file1 = 'test_estructura_1.xlsx'
    df1.to_excel(file1, index=False, header=False)
    test_files.append(('Estructura 1 (headers fila 4)', file1))
    
    # ESTRUCTURA 2: Headers en primera fila
    print("📝 Creando Estructura 2: Headers en primera fila...")
    data2 = {
        'URL': ['https://www.mercadolibre.cl/', 'https://www.mercadolibre.cl/'],
        'Paso a Paso': ['Localizar la barra...', 'Localizar la barra...']
    }
    df2 = pd.DataFrame(data2)
    file2 = 'test_estructura_2.xlsx'
    df2.to_excel(file2, index=False)
    test_files.append(('Estructura 2 (headers fila 1)', file2))
    
    # ESTRUCTURA 3: Con filas vacías al inicio
    print("📝 Creando Estructura 3: Con filas vacías...")
    data3 = []
    # Agregar filas vacías
    for i in range(3):
        data3.append(['', ''])
    # Agregar headers
    data3.append(['URL', 'Paso a Paso'])
    # Agregar datos
    data3.append(['https://www.mercadolibre.cl/', 'Localizar la barra...'])
    data3.append(['https://www.mercadolibre.cl/', 'Localizar la barra...'])
    
    df3 = pd.DataFrame(data3)
    file3 = 'test_estructura_3.xlsx'
    df3.to_excel(file3, index=False, header=False)
    test_files.append(('Estructura 3 (con filas vacías)', file3))
    
    return test_files

def debug_excel_detection():
    """Debug completo de detección de Excel"""
    
    print("🔍 DEBUG: Detección de Estructura de Excel")
    print("=" * 60)
    
    # Crear estructuras de prueba
    test_files = create_different_excel_structures()
    
    analyzer = ExcelTestAnalyzer()
    
    for description, file_path in test_files:
        print(f"\n🧪 PROBANDO: {description}")
        print("-" * 40)
        
        try:
            print(f"📂 Archivo: {file_path}")
            
            # Mostrar contenido raw del archivo
            print(f"\n📊 CONTENIDO RAW DEL ARCHIVO:")
            df_raw = pd.read_excel(file_path, header=None)
            print(df_raw)
            
            # Probar detección de headers
            print(f"\n🔍 PROBANDO DETECCIÓN DE HEADERS:")
            header_row, header_columns = analyzer.detect_headers(df_raw)
            
            if header_row == -1:
                print("❌ NO SE DETECTARON HEADERS")
                continue
            else:
                print(f"✅ Headers detectados en fila {header_row}: {header_columns}")
            
            # Probar extracción completa
            print(f"\n📋 PROBANDO EXTRACCIÓN DE CASOS:")
            test_cases = analyzer.extract_test_cases(file_path)
            
            if test_cases:
                print(f"✅ Se extrajeron {len(test_cases)} casos:")
                for i, case in enumerate(test_cases, 1):
                    print(f"   Caso {i}: ID={case.id}, URL={case.url_extraida}")
            else:
                print("❌ NO SE EXTRAJERON CASOS")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Limpiar archivos de prueba
    print(f"\n🧹 Limpiando archivos de prueba...")
    for _, file_path in test_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"   ✅ Eliminado: {file_path}")
        except:
            print(f"   ⚠️ No se pudo eliminar: {file_path}")

def test_user_file():
    """Función para probar con el archivo real del usuario"""
    
    print(f"\n" + "="*60)
    print("🎯 PRUEBA CON TU ARCHIVO REAL")
    print("="*60)
    
    file_path = input("📁 Ingresa la ruta de tu archivo Excel (o presiona Enter para saltar): ").strip()
    
    if not file_path:
        print("⏭️ Saltando prueba con archivo real")
        return
    
    if not os.path.exists(file_path):
        print(f"❌ No se encontró el archivo: {file_path}")
        return
    
    try:
        analyzer = ExcelTestAnalyzer()
        
        print(f"\n📂 Analizando tu archivo: {file_path}")
        
        # Mostrar contenido raw
        print(f"\n📊 CONTENIDO RAW (primeras 10 filas):")
        df_raw = pd.read_excel(file_path, header=None)
        print(df_raw.head(10))
        
        # Probar detección
        print(f"\n🔍 DETECCIÓN DE HEADERS:")
        header_row, header_columns = analyzer.detect_headers(df_raw)
        
        if header_row == -1:
            print("❌ NO SE DETECTARON HEADERS en tu archivo")
            print("💡 Sugerencias:")
            print("   - Verifica que el archivo tenga columnas 'URL' y 'Paso a Paso'")
            print("   - Asegúrate de que no haya demasiadas filas vacías al inicio")
            print("   - Los headers deben estar en texto, no como fórmulas")
        else:
            print(f"✅ Headers detectados en fila {header_row}: {header_columns}")
            
            # Intentar extraer casos
            print(f"\n📋 EXTRAYENDO CASOS:")
            test_cases = analyzer.extract_test_cases(file_path)
            
            if test_cases:
                print(f"✅ ¡ÉXITO! Se extrajeron {len(test_cases)} casos:")
                for i, case in enumerate(test_cases, 1):
                    print(f"   Caso {i}: {case.id} -> {case.url_extraida}")
            else:
                print("❌ No se pudieron extraer casos válidos")
                
    except Exception as e:
        print(f"❌ ERROR con tu archivo: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_excel_detection()
    test_user_file() 