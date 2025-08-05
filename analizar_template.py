#!/usr/bin/env python3
"""
Análisis del archivo Template.xlsx del usuario
"""

import pandas as pd
from excel_test_analyzer import ExcelTestAnalyzer

def analizar_template():
    """Analiza el archivo Template.xlsx del usuario"""
    
    print('🔍 ANALIZANDO TU ARCHIVO: C:\\Template.xlsx')
    print('='*50)

    try:
        # Mostrar contenido raw
        print('📊 CONTENIDO RAW (primeras 15 filas):')
        df_raw = pd.read_excel('C:\\Template.xlsx', header=None)
        print(df_raw.head(15))
        
        print(f'\n📏 Dimensiones del archivo: {df_raw.shape}')
        
        # Probar detección
        print('\n🔍 DETECCIÓN DE HEADERS:')
        analyzer = ExcelTestAnalyzer()
        header_row, header_columns = analyzer.detect_headers(df_raw)
        
        if header_row == -1:
            print('❌ NO SE DETECTARON HEADERS')
            
            # Buscar manualmente
            print('\n🔍 BÚSQUEDA MANUAL DE HEADERS:')
            for i in range(min(20, len(df_raw))):
                row_data = [str(val) for val in df_raw.iloc[i] if pd.notna(val) and str(val).strip()]
                if len(row_data) >= 2:
                    print(f'   Fila {i}: {row_data}')
                    if any('url' in str(val).lower() for val in row_data):
                        print(f'   ✅ Posible header con URL en fila {i}')
        else:
            print(f'✅ Headers detectados en fila {header_row}: {header_columns}')
            
            # Intentar extraer casos
            print('\n📋 EXTRAYENDO CASOS:')
            test_cases = analyzer.extract_test_cases('C:\\Template.xlsx')
            
            if test_cases:
                print(f'✅ Se extrajeron {len(test_cases)} casos:')
                for i, case in enumerate(test_cases, 1):
                    print(f'   Caso {i}: {case.id} -> {case.url_extraida}')
                    if case.pasos:
                        print(f'      Pasos: {case.pasos[:100]}...')
            else:
                print('❌ No se extrajeron casos')
                
    except Exception as e:
        print(f'❌ ERROR: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analizar_template() 