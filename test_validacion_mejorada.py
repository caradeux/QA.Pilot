#!/usr/bin/env python3
"""
Test para verificar la validación mejorada con estructura URL + Paso a Paso
"""

from excel_test_analyzer import ExcelTestAnalyzer

def test_validacion_mejorada():
    """Prueba la validación mejorada que es tolerante con estructura URL + Paso a Paso"""
    
    print("🧪 TEST: Validación Mejorada para URL + Paso a Paso")
    print("=" * 60)
    
    try:
        analyzer = ExcelTestAnalyzer()
        
        # Probar con el archivo real del usuario
        print("📂 Analizando tu archivo: C:\\Template.xlsx")
        test_cases = analyzer.extract_test_cases('C:\\Template.xlsx')
        
        if not test_cases:
            print("❌ No se extrajeron casos")
            return
        
        print(f"✅ Se extrajeron {len(test_cases)} casos")
        
        # Analizar con la validación mejorada
        print("\n🔍 APLICANDO VALIDACIÓN MEJORADA:")
        validated_cases = analyzer._enhanced_basic_validation(test_cases)
        
        # Mostrar resultados
        for i, case in enumerate(validated_cases, 1):
            print(f"\n📝 CASO {i}: {case.id}")
            print(f"   ✅ VÁLIDO: {case.es_valido}")
            print(f"   📍 URL: {case.url_extraida}")
            print(f"   📝 Pasos: {len(case.pasos)} caracteres")
            
            if case.problemas:
                print(f"   ⚠️ PROBLEMAS ({len(case.problemas)}):")
                for problema in case.problemas:
                    print(f"      • {problema}")
            else:
                print(f"   ✅ SIN PROBLEMAS")
            
            if case.sugerencias:
                print(f"   💡 SUGERENCIAS ({len(case.sugerencias)}):")
                for sugerencia in case.sugerencias[:3]:  # Solo mostrar las primeras 3
                    print(f"      • {sugerencia}")
        
        # Contar casos válidos
        casos_validos = sum(1 for case in validated_cases if case.es_valido)
        print(f"\n📊 RESUMEN:")
        print(f"   📝 Total de casos: {len(validated_cases)}")
        print(f"   ✅ Casos válidos: {casos_validos}")
        print(f"   ❌ Casos con problemas: {len(validated_cases) - casos_validos}")
        
        if casos_validos > 0:
            print(f"\n🎉 ¡ÉXITO! {casos_validos} casos listos para ejecución individual")
        else:
            print(f"\n⚠️ No hay casos válidos - revisar configuración")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_validacion_mejorada() 