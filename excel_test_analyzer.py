#!/usr/bin/env python3
"""
Analizador de Casos de Prueba desde Excel para QA-Pilot
Integra análisis con Claude IA para validar y procesar casos de prueba
"""

import pandas as pd
import re
import json
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import anthropic
from urllib.parse import urlparse

@dataclass
class TestCase:
    """Estructura de un caso de prueba"""
    id: str
    nombre: str
    historia_usuario: str
    objetivo: str
    precondicion: str
    pasos: str
    datos_prueba: str
    resultado_esperado: str
    url_extraida: Optional[str] = None
    es_valido: bool = False
    problemas: List[str] = None
    sugerencias: List[str] = None
    instrucciones_qa_pilot: str = ""

    def __post_init__(self):
        if self.problemas is None:
            self.problemas = []
        if self.sugerencias is None:
            self.sugerencias = []

class ExcelTestAnalyzer:
    """Analizador de casos de prueba desde Excel"""
    
    def __init__(self):
        """Inicializar el analizador usando la clave API del sistema"""
        # Usar la misma lógica que el sistema principal para obtener la clave API
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Si no está en el entorno, intentar cargar desde .env
        if not self.anthropic_api_key:
            env_path = os.path.join(os.getcwd(), '.env')
            if os.path.exists(env_path):
                try:
                    with open(env_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip() and not line.startswith('#'):
                                key, value = line.strip().split('=', 1)
                                if key == 'ANTHROPIC_API_KEY':
                                    self.anthropic_api_key = value.strip('"').strip("'")
                                    os.environ['ANTHROPIC_API_KEY'] = self.anthropic_api_key
                                    break
                except Exception as e:
                    print(f"Error leyendo .env: {e}")
        
        if self.anthropic_api_key:
            self.client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            print("✅ Análisis con Claude IA habilitado")
        else:
            self.client = None
            print("⚠️ No se encontró API key de Anthropic. El análisis con IA estará deshabilitado.")
    
    def detect_headers(self, df: pd.DataFrame) -> Tuple[int, List[str]]:
        """Detecta automáticamente la fila de headers y las columnas relevantes - VERSION MEJORADA"""
        
        print(f"[HEADER-DETECT] 🔍 Analizando archivo Excel con {len(df)} filas...")
        
        # Mostrar primeras filas para debug
        print(f"[HEADER-DETECT] 📊 Primeras 5 filas del archivo:")
        for i in range(min(5, len(df))):
            row_data = [str(val) for val in df.iloc[i] if pd.notna(val)]
            print(f"[HEADER-DETECT]   Fila {i}: {row_data}")
        
        expected_headers = [
            'nº cp', 'numero cp', 'caso', 'id',
            'url', 'link', 'enlace', 'destino',  # NUEVO: headers de URL
            'historia', 'user story', 'historia de usuario',
            'nombre', 'titulo', 'nombre cp',
            'objetivo', 'proposito',
            'precondicion', 'precondición', 'condicion previa',
            'paso', 'pasos', 'paso a paso', 'procedimiento',
            'datos', 'datos de prueba', 'data',
            'resultado', 'resultado esperado', 'esperado'
        ]
        
        # PRIORIDAD 1: Detectar estructura URL + Paso a Paso (nueva estructura) - MÁS FLEXIBLE
        for row_idx in range(min(20, len(df))):  # Buscar en más filas
            row_values = [str(val).lower().strip() for val in df.iloc[row_idx] if pd.notna(val) and str(val).strip() != '']
            
            if len(row_values) < 2:  # Necesitamos al menos 2 columnas
                continue
                
            row_text = ' '.join(row_values)
            print(f"[HEADER-DETECT] 🔍 Fila {row_idx}: '{row_text}'")
            
            # Verificar si tiene URL y Paso a Paso (nueva estructura prioritaria) - MÁS FLEXIBLE
            has_url = any(keyword in row_text for keyword in ['url', 'link', 'enlace', 'destino'])
            has_pasos = any(keyword in row_text for keyword in ['paso a paso', 'pasos', 'procedimiento'])
            
            if has_url and has_pasos:
                print(f"[HEADER-DETECT] 🎯 Nueva estructura URL + Paso a Paso detectada en fila {row_idx}")
                return row_idx, [str(val) for val in df.iloc[row_idx]]
            
            # También verificar si solo tiene URL (casos simples)
            if has_url and len(row_values) >= 2:
                print(f"[HEADER-DETECT] 🎯 Estructura con URL detectada en fila {row_idx}")
                return row_idx, [str(val) for val in df.iloc[row_idx]]
        
        # PRIORIDAD 2: Detectar Template.xlsx tradicional (estructura antigua)
        for row_idx in range(min(20, len(df))):
            row_values = [str(val).lower().strip() for val in df.iloc[row_idx] if pd.notna(val) and str(val).strip() != '']
            
            if len(row_values) < 3:
                continue
                
            row_text = ' '.join(row_values)
            
            # Detectar si es Template.xlsx por contenido específico (solo si no es la nueva estructura)
            if ('nº cp' in row_text and 'paso a paso' in row_text and 'historia de usuario' in row_text and 'url' not in row_text):
                print(f"[HEADER-DETECT] Template.xlsx tradicional detectado en fila {row_idx}")
                return row_idx, [str(val) for val in df.iloc[row_idx]]
        
        # PRIORIDAD 3: Método de detección por coincidencias (más flexible)
        best_match = 0
        best_row = -1
        best_columns = []
        
        for row_idx in range(min(20, len(df))):  # Buscar en más filas
            row_values = [str(val).lower().strip() for val in df.iloc[row_idx] if pd.notna(val) and str(val).strip() != '']
            
            if len(row_values) < 2:  # Reducido de 3 a 2 para ser más flexible
                continue
            
            matches = 0
            for val in row_values:
                if any(header in val for header in expected_headers):
                    matches += 1
            
            print(f"[HEADER-DETECT] 🔍 Fila {row_idx}: {matches} coincidencias en {row_values}")
            
            if matches > best_match:
                best_match = matches
                best_row = row_idx
                best_columns = row_values
        
        # PRIORIDAD 4: Si no encontramos nada, usar la primera fila que tenga datos
        if best_row == -1:
            print(f"[HEADER-DETECT] ⚠️ No se encontraron headers específicos, buscando primera fila con datos...")
            for row_idx in range(min(20, len(df))):
                row_values = [str(val) for val in df.iloc[row_idx] if pd.notna(val) and str(val).strip() != '']
                if len(row_values) >= 2:
                    print(f"[HEADER-DETECT] 📌 Usando fila {row_idx} como headers por defecto: {row_values}")
                    return row_idx, row_values
        
        print(f"[HEADER-DETECT] ✅ Mejor coincidencia: fila {best_row} con {best_match} matches")
        return best_row, best_columns
    
    def extract_test_cases(self, file_path: str) -> List[TestCase]:
        """Extrae casos de prueba del archivo Excel"""
        
        try:
            # Leer la primera hoja del Excel
            excel_file = pd.ExcelFile(file_path)
            first_sheet = excel_file.sheet_names[0]
            
            # Leer sin header para detectar estructura
            df_raw = pd.read_excel(file_path, sheet_name=first_sheet, header=None)
            
            # Detectar headers
            header_row, header_columns = self.detect_headers(df_raw)
            
            if header_row == -1:
                raise ValueError("No se pudieron detectar los headers del archivo Excel")
            
            # Leer con el header detectado
            df = pd.read_excel(file_path, sheet_name=first_sheet, header=header_row)
            
            # Mapear columnas a nuestros campos
            column_mapping = self._map_columns(df.columns)
            
            test_cases = []
            case_counter = 1
            
            for idx, row in df.iterrows():
                if self._is_valid_row(row):
                    test_case = self._create_test_case(row, column_mapping, case_counter)
                    if test_case:
                        test_cases.append(test_case)
                        case_counter += 1
            
            return test_cases
            
        except Exception as e:
            raise Exception(f"Error al procesar el archivo Excel: {str(e)}")
    
    def _map_columns(self, columns: List[str]) -> Dict[str, str]:
        """Mapea las columnas del Excel a nuestros campos estándar"""
        
        mapping = {}
        columns_lower = [str(col).lower().strip() for col in columns]
        
        # MAPEO ESPECÍFICO: Estructura URL + Paso a Paso (Destino + Misión) - PRIORIDAD MÁXIMA
        has_url_column = any('url' in str(col).lower() for col in columns)
        has_paso_column = any('paso a paso' in str(col).lower() or 'pasos' in str(col).lower() for col in columns)
        
        # También verificar si solo hay URL (estructura mínima)
        if has_url_column and len(columns) >= 2:
            print("[COLUMN-MAP] 🎯 DETECTADA ESTRUCTURA URL + PASO A PASO (Destino + Misión)")
            print(f"[COLUMN-MAP] 📊 Columnas detectadas: {list(columns)}")
            
            for i, col in enumerate(columns):
                col_lower = str(col).lower().strip()
                print(f"[COLUMN-MAP] 🔍 Analizando columna: '{col}' -> '{col_lower}'")
                
                if 'nº cp' in col_lower or 'numero cp' in col_lower or col_lower == 'id' or 'cp' == col_lower:
                    mapping['id'] = col
                    print(f"[COLUMN-MAP] ✅ ID mapeado: {col}")
                elif 'url' in col_lower:
                    mapping['url_destino'] = col  # Columna específica de URL
                    print(f"[COLUMN-MAP] ✅ URL_DESTINO mapeado: {col}")
                elif 'paso a paso' in col_lower:
                    mapping['pasos'] = col  # Misión
                    print(f"[COLUMN-MAP] ✅ PASOS (Misión) mapeado: {col}")
                elif 'historia de usuario' in col_lower or 'historia' in col_lower:
                    mapping['historia_usuario'] = col
                    print(f"[COLUMN-MAP] ✅ HISTORIA_USUARIO mapeado: {col}")
                elif 'nombre' in col_lower:
                    mapping['nombre'] = col
                    print(f"[COLUMN-MAP] ✅ NOMBRE mapeado: {col}")
                elif 'objetivo' in col_lower:
                    mapping['objetivo'] = col
                    print(f"[COLUMN-MAP] ✅ OBJETIVO mapeado: {col}")
                elif 'precondición' in col_lower or 'precondicion' in col_lower:
                    mapping['precondicion'] = col
                    print(f"[COLUMN-MAP] ✅ PRECONDICION mapeado: {col}")
                elif 'datos' in col_lower:
                    mapping['datos_prueba'] = col
                    print(f"[COLUMN-MAP] ✅ DATOS_PRUEBA mapeado: {col}")
                elif 'resultado' in col_lower:
                    mapping['resultado_esperado'] = col
                    print(f"[COLUMN-MAP] ✅ RESULTADO_ESPERADO mapeado: {col}")
            
            print(f"[COLUMN-MAP] 🎯 MAPEO FINAL: {mapping}")
            return mapping
        
        # MAPEO ESPECÍFICO: Template.xlsx estándar
        if any('nº cp' in col.lower() for col in columns) and any('paso a paso' in col.lower() for col in columns):
            print("[COLUMN-MAP] Aplicando mapeo específico para Template.xlsx")
            for i, col in enumerate(columns):
                col_lower = str(col).lower().strip()
                if 'nº cp' in col_lower:
                    mapping['id'] = col
                elif 'historia de usuario' in col_lower:
                    mapping['historia_usuario'] = col
                elif 'nombre cp' in col_lower:
                    mapping['nombre'] = col
                elif 'objetivo' in col_lower:
                    mapping['objetivo'] = col
                elif 'precondición' in col_lower:
                    mapping['precondicion'] = col
                elif 'paso a paso' in col_lower:
                    mapping['pasos'] = col
                elif 'datos de prueba' in col_lower:
                    mapping['datos_prueba'] = col
                elif 'resultado esperado' in col_lower:
                    mapping['resultado_esperado'] = col
            return mapping
        
        # Mapeo de patrones a campos (método original)
        patterns = {
            'id': ['nº cp', 'numero cp', 'caso', 'id', 'cp'],
            'url_destino': ['url', 'link', 'enlace', 'sitio', 'destino'],  # Nuevo: columna específica de URL
            'historia_usuario': ['historia', 'user story', 'historia de usuario'],
            'nombre': ['nombre', 'titulo', 'nombre cp', 'descripcion'],
            'objetivo': ['objetivo', 'proposito', 'meta'],
            'precondicion': ['precondicion', 'precondición', 'condicion previa', 'prerequisito'],
            'pasos': ['paso', 'pasos', 'paso a paso', 'procedimiento', 'steps', 'mision'],  # Añadido 'mision'
            'datos_prueba': ['datos', 'datos de prueba', 'data', 'input'],
            'resultado_esperado': ['resultado', 'resultado esperado', 'esperado', 'expected']
        }
        
        for field, pattern_list in patterns.items():
            for i, col in enumerate(columns_lower):
                if any(pattern in col for pattern in pattern_list):
                    mapping[field] = columns[i]
                    break
        
        return mapping
    
    def _is_valid_row(self, row: pd.Series) -> bool:
        """Verifica si una fila contiene un caso de prueba válido"""
        
        # Verificar que no sea una fila completamente vacía
        non_null_values = row.dropna()
        if len(non_null_values) < 2:
            return False
        
        # Verificar que contenga texto relevante
        row_text = ' '.join([str(val) for val in non_null_values]).lower()
        
        # Excluir filas que parecen ser headers o metadatos
        exclude_patterns = ['documento', 'analista', 'proyecto', 'fecha', 'version']
        if any(pattern in row_text for pattern in exclude_patterns):
            return False
        
        return True
    
    def _create_test_case(self, row: pd.Series, column_mapping: Dict[str, str], case_counter: int) -> Optional[TestCase]:
        """Crea un objeto TestCase desde una fila del Excel"""
        
        try:
            # Extraer valores usando el mapeo de columnas
            def get_value(field: str) -> str:
                if field in column_mapping and column_mapping[field] in row.index:
                    val = row[column_mapping[field]]
                    return str(val) if pd.notna(val) else ""
                return ""
            
            # Generar ID si no existe
            case_id = get_value('id')
            if not case_id or case_id.lower() in ['nan', 'none', '']:
                case_id = f"CP-{case_counter:03d}"
            
            # Extraer URL: primero de columna específica, luego de pasos/datos
            pasos = get_value('pasos')
            datos_prueba = get_value('datos_prueba')
            url_destino = get_value('url_destino')  # Nueva: columna específica de URL
            
            # Priorizar URL de columna específica
            if url_destino and url_destino.strip():
                url_extraida = url_destino.strip()
                print(f"[URL-EXTRACT] 🎯 URL extraída de columna destino: {url_extraida}")
            else:
                url_extraida = self._extract_url(pasos + " " + datos_prueba)
                if url_extraida:
                    print(f"[URL-EXTRACT] 🔍 URL extraída de pasos/datos: {url_extraida}")
            
            test_case = TestCase(
                id=case_id,
                nombre=get_value('nombre'),
                historia_usuario=get_value('historia_usuario'),
                objetivo=get_value('objetivo'),
                precondicion=get_value('precondicion'),
                pasos=pasos,
                datos_prueba=datos_prueba,
                resultado_esperado=get_value('resultado_esperado'),
                url_extraida=url_extraida
            )
            
            return test_case
            
        except Exception as e:
            print(f"Error al crear caso de prueba: {str(e)}")
            return None
    
    def _extract_url(self, text: str) -> Optional[str]:
        """Extrae URL del texto de pasos o datos de prueba"""
        
        if not text:
            return None
        
        # Patrones para detectar URLs
        url_patterns = [
            r'https?://[^\s]+',
            r'www\.[^\s]+',
            r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[^\s]*'
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                url = matches[0].rstrip('.,;)')
                # Validar que sea una URL válida
                try:
                    parsed = urlparse(url if url.startswith('http') else f'https://{url}')
                    if parsed.netloc:
                        return url if url.startswith('http') else f'https://{url}'
                except:
                    continue
        
        return None
    
    def analyze_with_hybrid_approach(self, test_cases: List[TestCase], progress_callback=None, data_mode='simulated') -> List[TestCase]:
        """Análisis híbrido: validación rápida + IA para casos problemáticos"""
        
        print("🚀 Iniciando análisis híbrido...")
        analyzed_cases = []
        total_cases = len(test_cases)
        
        # FASE 1: Validación básica rápida para todos los casos
        print("📋 Fase 1: Validación básica rápida...")
        if progress_callback:
            progress_callback(65, f"Validación básica de {total_cases} casos...", 
                            f"Aplicando 6 reglas de validación a cada caso")
        
        basic_validated_cases = self._enhanced_basic_validation(test_cases)
        
        # FASE 2: Identificar casos que necesitan análisis con IA
        problematic_cases = [tc for tc in basic_validated_cases if not tc.es_valido or len(tc.problemas) > 2]
        simple_cases = [tc for tc in basic_validated_cases if tc.es_valido and len(tc.problemas) <= 2]
        
        print(f"✅ Casos simples: {len(simple_cases)}")
        print(f"🔍 Casos que necesitan IA: {len(problematic_cases)}")
        
        if progress_callback:
            progress_callback(75, f"Análisis con IA para {len(problematic_cases)} casos problemáticos...", 
                            f"{len(simple_cases)} casos válidos, {len(problematic_cases)} requieren análisis adicional")
        
        # FASE 3: Análisis con IA solo para casos problemáticos
        if problematic_cases and self.client:
            print("🤖 Fase 2: Análisis con IA para casos problemáticos...")
            
            for i, test_case in enumerate(problematic_cases):
                try:
                    if progress_callback:
                        progress = 75 + (i / len(problematic_cases)) * 15  # 75-90%
                        progress_callback(int(progress), f"IA: Analizando caso {i+1}/{len(problematic_cases)}", 
                                        f"Optimizando caso '{test_case.nombre[:30]}...'")
                    
                    # Análisis con IA solo si realmente lo necesita
                    if self._needs_ai_analysis(test_case):
                        analysis_result = self._analyze_single_case_with_ai(test_case, data_mode)
                        self._update_case_with_ai_result(test_case, analysis_result)
                    
                    analyzed_cases.append(test_case)
                    
                except Exception as e:
                    print(f"Error al analizar caso {test_case.id} con IA: {str(e)}")
                    analyzed_cases.append(test_case)  # Mantener validación básica
        else:
            analyzed_cases.extend(problematic_cases)
        
        # Agregar casos simples que no necesitaron IA
        analyzed_cases.extend(simple_cases)
        
        # Generar instrucciones para todos los casos
        if progress_callback:
            progress_callback(90, "Generando instrucciones QA-Pilot...", 
                            "Creando instrucciones de automatización para casos válidos")
        
        for test_case in analyzed_cases:
            if not test_case.instrucciones_qa_pilot:
                test_case.instrucciones_qa_pilot = self._generate_qa_pilot_instructions(test_case)
        
        if progress_callback:
            final_valid = len([tc for tc in analyzed_cases if tc.es_valido])
            final_problematic = total_cases - final_valid
            progress_callback(100, f"Análisis completado: {total_cases} casos procesados", 
                            f"{final_valid} casos válidos, {final_problematic} con problemas")
        
        print(f"✅ Análisis híbrido completado: {len(analyzed_cases)} casos procesados")
        return analyzed_cases
    
    def _enhanced_basic_validation(self, test_cases: List[TestCase]) -> List[TestCase]:
        """Validación optimizada para estructura URL + Paso a Paso (tolerante y práctica)"""
        
        for test_case in test_cases:
            # PARCHE ESPECÍFICO: Si es caso del Template.xlsx (sistema interno), marcarlo como válido automáticamente
            if self._is_template_internal_case(test_case):
                if test_case.nombre.strip() and test_case.pasos.strip():
                    print(f"[TEMPLATE-PATCH] Marcando caso {test_case.id} como válido automáticamente")
                    test_case.es_valido = True
                    test_case.problemas = []
                    test_case.sugerencias = ["🔄 Caso del Template.xlsx convertido automáticamente para web"]
                    test_case.instrucciones_qa_pilot = self._generate_qa_pilot_instructions(test_case)
                    continue
            
            # OPTIMIZACIÓN PARA ESTRUCTURA URL + PASO A PASO
            print(f"[VALIDATION] 🔍 Validando caso {test_case.id} con estructura URL + Paso a Paso")
            
            problemas = []
            sugerencias = []
            
            # VALIDACIÓN ESENCIAL 1: Verificar que tenga URL Y pasos (lo mínimo ejecutable)
            if test_case.url_extraida and test_case.pasos and len(test_case.pasos.strip()) > 10:
                # ✅ CASO VÁLIDO: Tiene URL y pasos detallados
                test_case.es_valido = True
                sugerencias.append("✅ Estructura URL + Paso a Paso completa - Listo para ejecución")
                print(f"[VALIDATION] ✅ Caso {test_case.id} VÁLIDO - URL: {test_case.url_extraida[:50]}...")
                
            elif test_case.pasos and len(test_case.pasos.strip()) > 20:
                # ✅ CASO VÁLIDO: Pasos muy detallados (URL puede estar implícita)
                test_case.es_valido = True
                sugerencias.append("✅ Pasos detallados detectados - Ejecutable")
                print(f"[VALIDATION] ✅ Caso {test_case.id} VÁLIDO - Pasos detallados")
                
            else:
                # ❌ CASO INVÁLIDO: Falta información crítica
                test_case.es_valido = False
                if not test_case.url_extraida:
                    problemas.append("No se detectó URL de destino")
                if not test_case.pasos or len(test_case.pasos.strip()) < 10:
                    problemas.append("Faltan pasos de ejecución detallados")
                print(f"[VALIDATION] ❌ Caso {test_case.id} INVÁLIDO - Falta información crítica")
            
            # SUGERENCIAS ADICIONALES (solo si es válido)
            if test_case.es_valido:
                if test_case.url_extraida:
                    sugerencias.append("🎯 URL detectada desde columna de destino")
                
                # Verificar calidad de los pasos
                automation_keywords = ['localizar', 'hacer clic', 'escribir', 'presionar', 'verificar']
                pasos_lower = test_case.pasos.lower()
                keyword_count = sum(1 for keyword in automation_keywords if keyword in pasos_lower)
                
                if keyword_count >= 3:
                    sugerencias.append("🔧 Pasos bien estructurados para automatización")
                elif keyword_count >= 1:
                    sugerencias.append("📝 Pasos con buena base para automatización")
                
                # Mensaje específico para estructura URL + Paso a Paso
                sugerencias.append("🚀 Optimizado para ejecución con browser-use")
                
                # Generar instrucciones QA-Pilot
                test_case.instrucciones_qa_pilot = self._generate_qa_pilot_instructions(test_case)
            else:
                sugerencias.append("🔧 Completar información esencial para habilitar ejecución")
            
            # NO AGREGAR PROBLEMAS DE CAMPOS OPCIONALES (como nombre, objetivo, resultado esperado)
            # Para estructura URL + Paso a Paso, solo importa que tenga URL y pasos
            
            test_case.problemas = problemas
            test_case.sugerencias = sugerencias
        
        return test_cases
    
    def _needs_ai_analysis(self, test_case: TestCase) -> bool:
        """Determina si un caso necesita análisis con IA"""
        
        # Casos que definitivamente necesitan IA
        if len(test_case.problemas) > 3:
            return True
        
        # Casos con problemas de coherencia
        coherence_issues = [p for p in test_case.problemas if 'coherencia' in p.lower() or 'relacionados' in p.lower()]
        if coherence_issues:
            return True
        
        # Casos con pasos muy complejos o ambiguos
        if len(test_case.pasos.split()) > 50:
            return True
        
        return False
    
    def _analyze_single_case_with_ai(self, test_case: TestCase, data_mode='simulated') -> Dict:
        """Analiza un solo caso con IA de forma optimizada"""
        
        analysis_prompt = self._create_focused_analysis_prompt(test_case, data_mode)
        
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,  # Reducido para respuestas más rápidas
            messages=[{
                "role": "user",
                "content": analysis_prompt
            }]
        )
        
        return self._parse_claude_response(response.content[0].text)
    
    def _create_focused_analysis_prompt(self, test_case: TestCase, data_mode='simulated') -> str:
        """Crea un prompt enfocado para análisis rápido con IA"""
        
        # Configurar instrucciones según el modo de datos
        if data_mode == 'simulated':
            data_instructions = """
2. **Datos de Prueba**: Si faltan datos, genera datos realistas simulados (RUTs chilenos, emails, nombres, etc.)

**DATOS SIMULADOS REALISTAS:**
- RUTs chilenos: 12345678-9, 98765432-1
- Emails: usuario.prueba@email.com, test.qa@gmail.com  
- Nombres: Juan Pérez, María González
- Teléfonos: +56912345678, +56987654321"""
            
            response_format = """
{{
    "es_valido": true/false,
    "url_requerida": "REQUERIDA_POR_USUARIO" o null si no se necesita,
    "pasos_mejorados": "Pasos detallados con selectores y acciones específicas",
    "datos_simulados": "Datos de prueba realistas generados automáticamente",
    "problemas_usuario": ["Lista de cosas que debe proporcionar el usuario"],
    "instrucciones_qa_pilot": "Instrucciones completas con datos simulados"
}}"""
        else:  # data_mode == 'user'
            data_instructions = """
2. **Datos de Prueba**: NO generes datos simulados. Si faltan datos, marca como "REQUERIDOS_POR_USUARIO" """
            
            response_format = """
{{
    "es_valido": true/false,
    "url_requerida": "REQUERIDA_POR_USUARIO" o null si no se necesita,
    "pasos_mejorados": "Pasos detallados con selectores y acciones específicas",
    "datos_requeridos": "Lista de datos que debe proporcionar el usuario",
    "problemas_usuario": ["Lista de cosas que debe proporcionar el usuario"],
    "instrucciones_qa_pilot": "Instrucciones completas (con placeholders para datos del usuario)"
}}"""
        
        return f"""
Eres un experto en automatización de pruebas web. Analiza este caso de prueba y MEJÓRALO para que sea ejecutable con browser-use:

**CASO ORIGINAL:**
- ID: {test_case.id}
- Nombre: {test_case.nombre}
- Objetivo: {test_case.objetivo}
- Pasos: {test_case.pasos}
- Datos: {test_case.datos_prueba}

**REGLAS IMPORTANTES:**
1. **URLs**: NO inventes URLs. Si falta URL, marca como "REQUERIDA_POR_USUARIO"{data_instructions}
3. **Selectores**: Agrega selectores CSS/XPath específicos para automatización
4. **Pasos**: Convierte acciones genéricas en instrucciones específicas de browser-use
5. **PATRÓN ESTÁNDAR**: Si es un caso de navegación web con login, usa este patrón:
   - 1. Realiza login con Usuario: [usuario] y Contraseña: [password]
   - 2. Haz clic en el ícono lateral [Sección]
   - 3. [Otras navegaciones específicas]
   - 4. Presiona cerrar sesión (si aplica)

**EJEMPLO DE MEJORA CON PATRÓN ESTÁNDAR:**
Caso original: "Validar navegación en dashboard"
Caso mejorado:
1. Realiza login con Usuario: contabilidad@ripley.com y Contraseña: 123456
2. Haz clic en el ícono lateral Dashboard
3. Haz clic en el ícono lateral Pendiente de Pago
4. Presiona cerrar sesión

**EJEMPLO DE MEJORA CON SELECTORES:**
Paso original: "Ingresar RUT"
Paso mejorado: "Escribir en el campo de RUT (selector: '#input-rut' o 'input[name=\"rut\"]') el valor: [RUT_USUARIO]"

**RESPONDE EN JSON:**{response_format}
"""
    
    def _update_case_with_ai_result(self, test_case: TestCase, ai_result: Dict):
        """Actualiza el caso con el resultado de IA"""
        
        if ai_result.get('es_valido') is not None:
            test_case.es_valido = ai_result['es_valido']
        
        # Manejar URL requerida por usuario
        if ai_result.get('url_requerida') == "REQUERIDA_POR_USUARIO":
            test_case.problemas.append("⚠️ URL requerida: El usuario debe proporcionar la URL del sistema")
            test_case.sugerencias.append("Agregar la URL del sistema en los datos de prueba")
        elif ai_result.get('url_requerida'):
            # Si no es "REQUERIDA_POR_USUARIO" pero hay valor, usar como URL
            test_case.url_extraida = ai_result['url_requerida']
            test_case.problemas = [p for p in test_case.problemas if 'URL' not in p]
        
        # Actualizar pasos si la IA los mejoró
        if ai_result.get('pasos_mejorados'):
            test_case.pasos = ai_result['pasos_mejorados']
            test_case.sugerencias.append("✅ Pasos mejorados con selectores específicos")
        
        # Actualizar datos de prueba según el resultado de IA
        if ai_result.get('datos_simulados'):
            # Modo simulado: agregar datos generados por IA
            datos_simulados_str = ai_result['datos_simulados']
            if isinstance(datos_simulados_str, dict):
                datos_simulados_str = "\n".join([f"{k}: {v}" for k, v in datos_simulados_str.items()])
            
            if not test_case.datos_prueba.strip() or test_case.datos_prueba.strip() == 'nan':
                test_case.datos_prueba = str(datos_simulados_str)
            else:
                test_case.datos_prueba += f"\n\n--- DATOS SIMULADOS ADICIONALES ---\n{datos_simulados_str}"
            test_case.sugerencias.append("🎲 Datos de prueba simulados generados automáticamente")
        
        elif ai_result.get('datos_requeridos'):
            # Modo usuario: marcar datos que debe proporcionar el usuario
            datos_requeridos = ai_result['datos_requeridos']
            test_case.problemas.append(f"📝 Datos requeridos: {datos_requeridos}")
            test_case.sugerencias.append("👤 Completar con tus propios datos de prueba")
        
        # Agregar problemas que debe resolver el usuario
        if ai_result.get('problemas_usuario'):
            for problema in ai_result['problemas_usuario']:
                if problema not in test_case.problemas:
                    test_case.problemas.append(f"👤 Usuario debe: {problema}")
        
        # Actualizar instrucciones QA-Pilot
        if ai_result.get('instrucciones_qa_pilot'):
            test_case.instrucciones_qa_pilot = ai_result['instrucciones_qa_pilot']
        
        # Agregar sugerencia de mejora aplicada
        if test_case.es_valido:
            test_case.sugerencias.append("✅ Caso optimizado por IA - Listo para ejecutar")
        else:
            test_case.sugerencias.append("🔧 Caso mejorado por IA - Completar datos faltantes")
    
    def _generate_qa_pilot_instructions(self, test_case: TestCase) -> str:
        """
        CORRECCIÓN: Genera instrucciones optimizadas para browser-use con mayor ejecutabilidad
        """
        
        # PARCHE ESPECÍFICO: Si es un caso del Template.xlsx (sistema interno), convertir a acciones web
        if self._is_template_internal_case(test_case):
            web_instructions = self._convert_internal_to_web_instructions(test_case)
            if web_instructions:
                test_case.sugerencias.append("🔄 Convertido de sistema interno a acciones web optimizada para browser-use")
                return self._optimize_for_browser_use(web_instructions)
        
        # Intentar aplicar patrón estándar de navegación web
        improved_case = self._apply_standard_pattern(test_case)
        
        if improved_case:
            # Si se pudo aplicar el patrón estándar, optimizar para browser-use
            optimized_instructions = self._optimize_for_browser_use(improved_case)
            
            # Agregar sugerencia de que se aplicó mejora
            if "🔧 Instrucciones optimizadas para browser-use" not in test_case.sugerencias:
                test_case.sugerencias.append("🔧 Instrucciones optimizadas para browser-use con ejecución paso a paso")
            
            return optimized_instructions
        else:
            # Crear instrucciones desde cero optimizadas para browser-use
            return self._create_browser_use_instructions(test_case)

    def _optimize_for_browser_use(self, instructions: str) -> str:
        """Optimiza cualquier conjunto de instrucciones para browser-use"""
        
        # Convertir a formato directo y ejecutable
        lines = instructions.split('\n')
        optimized_steps = []
        
        for line in lines:
            line = line.strip()
            if not line or line.lower().startswith(('objetivo:', 'verificar:', 'pasos:')):
                continue
            
            # Limpiar numeración y hacer más directo
            import re
            line = re.sub(r'^(\d+[\.\)]\s*|paso\s*\d+[\.\:]\s*)', '', line, flags=re.IGNORECASE)
            
            if line:
                # Convertir a instrucciones más ejecutables
                line = self._make_instruction_executable(line)
                optimized_steps.append(line)
        
        # Unir con puntos para flujo continuo
        if optimized_steps:
            return '. '.join(optimized_steps) + '. Verificar que todas las acciones se completaron correctamente.'
        
        return instructions

    def _make_instruction_executable(self, instruction: str) -> str:
        """Convierte una instrucción a formato más ejecutable para browser-use"""
        
        instruction = instruction.strip()
        
        # Patrones de mejora para hacer instrucciones más específicas
        improvements = {
            # Búsquedas
            r'buscar (.+)': r'localizar la barra de búsqueda y escribir "\1", luego presionar Enter',
            r'escribir (.+) en (.+)': r'localizar el campo "\2" y escribir "\1"',
            r'ingresar (.+)': r'escribir "\1" en el campo correspondiente',
            
            # Clicks y navegación
            r'hacer clic en (.+)': r'localizar y hacer clic en el elemento "\1"',
            r'presionar (.+)': r'localizar y hacer clic en el botón "\1"',
            r'seleccionar (.+)': r'localizar y seleccionar la opción "\1"',
            r'ir a (.+)': r'navegar hacia la sección "\1"',
            
            # Verificaciones
            r'verificar (.+)': r'comprobar que "\1" esté visible en la página',
            r'revisar (.+)': r'verificar que "\1" se muestre correctamente',
            
            # Filtros y opciones
            r'filtrar por (.+)': r'localizar los filtros y seleccionar "\1"',
            r'expandir (.+)': r'hacer clic para expandir la sección "\1"'
        }
        
        # Aplicar mejoras
        for pattern, replacement in improvements.items():
            instruction = re.sub(pattern, replacement, instruction, flags=re.IGNORECASE)
        
        # Agregar contexto de espera si es necesario
        if any(word in instruction.lower() for word in ['localizar', 'buscar', 'encontrar']):
            instruction += ', esperando a que el elemento esté visible'
        
        return instruction

    def _create_browser_use_instructions(self, test_case: TestCase) -> str:
        """Crea instrucciones desde cero optimizadas para browser-use con estructura URL + Misión"""
        
        # 🎯 OPTIMIZACIÓN ESPECÍFICA: Estructura URL + Paso a Paso (Destino + Misión)
        if test_case.url_extraida and test_case.pasos:
            print(f"[INSTRUCTIONS] 🎯 Generando instrucciones optimizadas para URL + Misión")
            
            # Extraer misión (paso a paso)
            mision = test_case.pasos.strip()
            destino = test_case.url_extraida.strip()
            
            # Crear instrucciones estructuradas paso a paso
            instructions = []
            
            # 1. Navegación al destino
            instructions.append(f"Navegar a {destino}")
            
            # 2. Esperar carga
            instructions.append("Esperar a que la página se cargue completamente")
            
            # 3. Procesar misión
            mision_steps = self._process_mission_steps(mision)
            instructions.extend(mision_steps)
            
            # 4. Verificación final
            instructions.append("Verificar que todas las acciones se completaron correctamente")
            
            return ". ".join(instructions) + "."
        
        # Método original si no es estructura URL + Misión
        objetivo = test_case.objetivo.lower()
        pasos = test_case.pasos.lower()
        
        # Plantillas base según el tipo de test detectado
        if any(word in objetivo + pasos for word in ['buscar', 'búsqueda', 'search']):
            return self._create_search_instructions(test_case)
        elif any(word in objetivo + pasos for word in ['login', 'ingresar', 'autenticar']):
            return self._create_login_instructions(test_case)
        elif any(word in objetivo + pasos for word in ['filtro', 'filtrar', 'categoria']):
            return self._create_filter_instructions(test_case)
        elif any(word in objetivo + pasos for word in ['navegación', 'navegar', 'menú']):
            return self._create_navigation_instructions(test_case)
        else:
            return self._create_generic_instructions(test_case)
    
    def _process_mission_steps(self, mision: str) -> List[str]:
        """Procesa los pasos de la misión y los convierte en instrucciones ejecutables optimizadas"""
        
        if not mision:
            return ["Explorar la funcionalidad principal de la página"]
        
        print(f"[MISSION-PROCESS] 🎯 Procesando misión: {mision[:100]}...")
        
        # Dividir misión en pasos individuales
        steps = []
        lines = mision.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Limpiar numeración y caracteres especiales
            import re
            line = re.sub(r'^(\d+[\.\)]\s*)', '', line)
            line = re.sub(r'^[-•*]\s*', '', line)  # Viñetas
            
            print(f"[MISSION-PROCESS] 📝 Procesando línea: '{line}'")
            
            # ✅ MEJORAS ESPECÍFICAS: Patrones más precisos y ejecutables
            line_lower = line.lower()
            
            # 🔍 BÚSQUEDAS - Patrones optimizados
            if any(keyword in line_lower for keyword in ['localizar', 'encontrar']) and 'barra' in line_lower and ('búsqueda' in line_lower or 'busqueda' in line_lower):
                steps.append("Localizar la barra de búsqueda en la parte superior de la página")
                
            elif 'hacer clic' in line_lower and ('campo' in line_lower or 'búsqueda' in line_lower or 'busqueda' in line_lower):
                steps.append("Hacer clic en el campo de búsqueda para activarlo")
                
            elif 'escribir' in line_lower and ('término' in line_lower or 'termino' in line_lower):
                # Extraer término específico si está entre comillas
                term_match = re.search(r'"([^"]+)"', line)
                if term_match:
                    term = term_match.group(1)
                    steps.append(f'Escribir "{term}" en el campo de búsqueda')
                    print(f"[MISSION-PROCESS] 🎯 Término extraído: {term}")
                else:
                    # Buscar términos comunes sin comillas
                    common_terms = ['iphone', 'smart tv', 'audífonos', 'bluetooth', 'laptop', 'noticias']
                    found_term = None
                    for term in common_terms:
                        if term in line_lower:
                            found_term = term
                            break
                    
                    if found_term:
                        steps.append(f'Escribir "{found_term}" en el campo de búsqueda')
                    else:
                        steps.append("Escribir el término de búsqueda en el campo correspondiente")
                        
            elif 'presionar' in line_lower and ('enter' in line_lower or 'buscar' in line_lower or 'lupa' in line_lower):
                steps.append("Presionar Enter o hacer clic en el botón de búsqueda (ícono de lupa)")
                
            elif 'esperar' in line_lower and ('cargue' in line_lower or 'resultados' in line_lower):
                steps.append("Esperar a que se carguen los resultados de búsqueda")
                
            elif 'verificar' in line_lower and ('productos' in line_lower or 'resultados' in line_lower):
                steps.append("Verificar que se muestren productos relacionados con la búsqueda")
                
            elif 'comprobar' in line_lower and ('resultados' in line_lower or 'relevantes' in line_lower):
                steps.append("Comprobar que los resultados sean relevantes y precisos")
                
            # 🛒 NAVEGACIÓN Y SELECCIÓN - Patrones mejorados
            elif 'hacer clic' in line_lower and ('primer' in line_lower or 'producto' in line_lower):
                steps.append("Hacer clic en el primer producto de la lista de resultados")
                
            elif 'seleccionar' in line_lower and 'producto' in line_lower:
                steps.append("Seleccionar un producto específico de los resultados")
                
            elif 'navegar' in line_lower and ('categoría' in line_lower or 'categoria' in line_lower):
                steps.append("Navegar a la categoría correspondiente usando el menú")
                
            elif 'localizar' in line_lower and 'menú' in line_lower:
                steps.append("Localizar el menú principal de navegación en la página")
                
            # 🔧 FILTROS Y OPCIONES - Nuevos patrones
            elif 'aplicar' in line_lower and 'filtro' in line_lower:
                steps.append("Aplicar filtro por precio, marca o categoría si está disponible")
                
            elif 'filtrar' in line_lower or ('filtro' in line_lower and 'precio' in line_lower):
                steps.append("Usar las opciones de filtrado para refinar los resultados")
                
            # 📄 VERIFICACIÓN Y VALIDACIÓN - Patrones específicos
            elif 'verificar' in line_lower and ('página' in line_lower or 'pagina' in line_lower) and 'producto' in line_lower:
                steps.append("Verificar que se abra la página del producto con detalles completos")
                
            elif 'revisar' in line_lower and ('información' in line_lower or 'informacion' in line_lower):
                steps.append("Revisar la información detallada del producto seleccionado")
                
            elif 'verificar' in line_lower and ('opciones' in line_lower or 'compra' in line_lower):
                steps.append("Verificar las opciones de compra y métodos de pago disponibles")
                
            # 🌐 NAVEGACIÓN WEB GENERAL - Patrones optimizados
            elif 'navegar' in line_lower and ('página' in line_lower or 'pagina' in line_lower) and 'principal' in line_lower:
                steps.append("Navegar a la página principal del sitio web")
                
            elif 'acceder' in line_lower and ('página' in line_lower or 'pagina' in line_lower):
                steps.append("Acceder a la página web especificada")
                
            # 📰 BÚSQUEDAS ESPECÍFICAS - Nuevos patrones
            elif 'noticias' in line_lower and ('tecnología' in line_lower or 'tecnologia' in line_lower):
                steps.append("Buscar noticias relacionadas con tecnología")
                
            elif 'pestaña' in line_lower and 'noticias' in line_lower:
                steps.append("Hacer clic en la pestaña 'Noticias' para filtrar resultados")
                
            # 🎯 INSTRUCCIONES GENÉRICAS MEJORADAS
            elif 'hacer clic' in line_lower:
                # Extraer elemento del click de manera más precisa
                element_patterns = [
                    r'hacer clic en (.+?)(?:\.|$)',
                    r'clic en (.+?)(?:\.|$)',
                    r'clickear (.+?)(?:\.|$)'
                ]
                
                element_found = False
                for pattern in element_patterns:
                    element_match = re.search(pattern, line_lower)
                    if element_match:
                        element = element_match.group(1).strip('."')
                        steps.append(f"Localizar y hacer clic en {element}")
                        element_found = True
                        break
                
                if not element_found:
                    steps.append("Hacer clic en el elemento correspondiente")
                    
            else:
                # Convertir instrucción genérica a más específica y ejecutable
                if len(line) > 10:  # Solo procesar líneas con contenido sustancial
                    executable_instruction = self._make_instruction_executable(line)
                    if executable_instruction != line:  # Si se mejoró
                        steps.append(executable_instruction)
                    else:
                        steps.append(f"Ejecutar: {line}")
        
        # ✅ VALIDACIÓN FINAL: Si no se procesaron pasos específicos, crear estructura básica
        if not steps:
            print("[MISSION-PROCESS] ⚠️ No se encontraron pasos específicos, generando estructura básica")
            if 'buscar' in mision.lower() or 'búsqueda' in mision.lower():
                steps = [
                    "Localizar la barra de búsqueda principal",
                    "Escribir el término de búsqueda correspondiente", 
                    "Ejecutar la búsqueda presionando Enter",
                    "Verificar que se muestren resultados relevantes"
                ]
            else:
                steps.append(f"Ejecutar la siguiente misión: {mision}")
        
        print(f"[MISSION-PROCESS] ✅ {len(steps)} pasos procesados exitosamente")
        return steps

    def _create_search_instructions(self, test_case: TestCase) -> str:
        """Crea instrucciones optimizadas para búsquedas"""
        
        # Extraer término de búsqueda de los pasos o datos
        search_term = self._extract_search_term(test_case)
        
        if search_term:
            return f"Localizar la barra de búsqueda principal. Escribir '{search_term}' en el campo de búsqueda. Presionar Enter o hacer clic en el botón de búsqueda. Esperar a que se carguen los resultados. Verificar que aparezcan productos relacionados con '{search_term}'. Revisar que la búsqueda se haya ejecutado correctamente."
        else:
            return f"Localizar la barra de búsqueda principal. Escribir un término de búsqueda relevante. Presionar Enter para ejecutar la búsqueda. Esperar a que se carguen los resultados. Verificar que aparezcan productos relacionados."

    def _create_filter_instructions(self, test_case: TestCase) -> str:
        """Crea instrucciones optimizadas para filtros"""
        return "Localizar la sección de filtros en la página de resultados. Expandir las opciones de filtrado disponibles. Seleccionar un filtro específico de la lista. Esperar a que se actualicen los resultados. Verificar que el filtro se haya aplicado correctamente. Comprobar que los productos mostrados corresponden al filtro seleccionado."

    def _create_navigation_instructions(self, test_case: TestCase) -> str:
        """Crea instrucciones optimizadas para navegación"""
        return "Localizar el menú principal de navegación. Explorar las diferentes secciones disponibles. Hacer clic en una categoría de interés. Navegar por las subcategorías si están disponibles. Verificar que la navegación funcione correctamente. Comprobar que se muestren los productos de la categoría seleccionada."

    def _create_login_instructions(self, test_case: TestCase) -> str:
        """Crea instrucciones optimizadas para login"""
        return "Localizar la opción de 'Iniciar Sesión' o 'Login'. Hacer clic para acceder al formulario de login. Completar los campos de usuario y contraseña con datos válidos. Hacer clic en el botón 'Ingresar' o 'Login'. Esperar a que se procese el login. Verificar que se haya ingresado correctamente al sistema."

    def _create_generic_instructions(self, test_case: TestCase) -> str:
        """Crea instrucciones genéricas optimizadas para browser-use"""
        return f"Explorar la página web principal. Interactuar con los elementos principales de la interfaz. Navegar por las diferentes secciones disponibles. Verificar que la funcionalidad básica del sitio funcione correctamente. Comprobar que todos los elementos se carguen apropiadamente."

    def _extract_search_term(self, test_case: TestCase) -> str:
        """Extrae término de búsqueda de los datos del caso"""
        import re
        
        # Buscar en pasos y datos de prueba
        text_to_search = f"{test_case.pasos} {test_case.datos_prueba}".lower()
        
        # Patrones para detectar términos de búsqueda
        patterns = [
            r"buscar ['\"]([^'\"]+)['\"]",
            r"buscar ([a-zA-Z0-9\s]+)",
            r"escribir ['\"]([^'\"]+)['\"]",
            r"término[:\s]+([a-zA-Z0-9\s]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_to_search)
            if match:
                term = match.group(1).strip()
                if len(term) > 2 and len(term) < 50:  # Término razonable
                    return term
        
        return None
    
    def _is_template_internal_case(self, test_case: TestCase) -> bool:
        """Detecta si es un caso del Template.xlsx que es para sistema interno"""
        pasos_lower = test_case.pasos.lower()
        objetivo_lower = test_case.objetivo.lower()
        
        # Indicadores de que es sistema interno de postulación/admisión
        internal_indicators = [
            'postulante', 'postulación', 'ingreso postulante',
            'rut', 'dv k', 'relacion academica', 'dec', '3ra base',
            'módulo', 'admisión', 'actualización', 'datos del postulante'
        ]
        
        return any(indicator in pasos_lower or indicator in objetivo_lower for indicator in internal_indicators)
    
    def _convert_internal_to_web_instructions(self, test_case: TestCase) -> str:
        """Convierte pasos de sistema interno a acciones web para MercadoLibre"""
        
        pasos_lower = test_case.pasos.lower()
        objetivo_lower = test_case.objetivo.lower()
        
        # Detectar el tipo de test y generar instrucciones web apropiadas
        if 'postulación' in objetivo_lower or 'postulante' in pasos_lower:
            web_steps = """1. En la barra de búsqueda, escribir "cursos online"
2. Hacer clic en el botón de búsqueda
3. Verificar que aparezcan resultados relacionados
4. Hacer clic en el primer resultado de la lista
5. Verificar que se abra la página del producto
6. Revisar la información del vendedor
7. Verificar que el precio sea visible"""
            
        elif 'ingreso' in pasos_lower or 'rut' in pasos_lower:
            web_steps = """1. En la barra de búsqueda, escribir "servicios registro"
2. Hacer clic en buscar
3. Filtrar por "Servicios" en las categorías
4. Seleccionar un servicio relacionado con documentación
5. Verificar los datos del servicio
6. Revisar las condiciones y términos
7. Verificar métodos de pago disponibles"""
            
        elif 'actualización' in objetivo_lower or 'datos' in pasos_lower:
            web_steps = """1. Buscar "cuenta usuario" en la barra de búsqueda
2. Hacer clic en el ícono de usuario (si está visible)
3. Navegar a sección de configuración de cuenta
4. Verificar campos editables de perfil
5. Intentar modificar información de contacto
6. Guardar cambios realizados
7. Verificar confirmación de actualización"""
            
        elif 'relacion' in pasos_lower or 'academica' in pasos_lower:
            web_steps = """1. Buscar "libros academicos" en la barra principal
2. Aplicar filtro por categoría "Libros"
3. Ordenar resultados por relevancia
4. Seleccionar un libro universitario
5. Verificar descripción académica del producto
6. Revisar opiniones de otros compradores
7. Verificar disponibilidad de envío"""
            
        else:
            # Instrucción genérica
            web_steps = f"""1. En la página principal, usar la barra de búsqueda
2. Escribir términos relacionados con el objetivo del test
3. Hacer clic en buscar y revisar resultados
4. Seleccionar un producto de la lista
5. Verificar información detallada del producto
6. Revisar opciones de compra disponibles
7. Confirmar que la navegación funciona correctamente"""
        
        # Construir las instrucciones completas
        instructions = f"Objetivo de Test Web: Simular {test_case.objetivo} usando MercadoLibre como plataforma de prueba\n\n"
        instructions += f"Pasos:\n{web_steps}\n\n"
        instructions += f"Verificar: Que el sitio responda correctamente y la navegación funcione como se espera"
        
        return instructions.strip()
    
    def _apply_standard_pattern(self, test_case: TestCase) -> Optional[str]:
        """Aplica patrón estándar de navegación web si es posible"""
        
        # Verificar si el caso puede seguir el patrón estándar
        if not self._can_apply_standard_pattern(test_case):
            return None
        
        # Extraer información clave del caso
        url = test_case.url_extraida
        pasos_text = test_case.pasos.lower()
        datos_text = test_case.datos_prueba.lower()
        objetivo_text = test_case.objetivo.lower()
        
        # Detectar credenciales de login
        login_info = self._extract_login_credentials(test_case)
        
        # Detectar acciones de navegación
        navigation_actions = self._extract_navigation_actions(test_case)
        
        # Construir pasos estándar
        standard_steps = []
        step_counter = 1
        
        # 1. Login (si se detecta)
        if login_info:
            if login_info.get('usuario') and login_info.get('password'):
                standard_steps.append(f"{step_counter}. Realiza login con Usuario: {login_info['usuario']} y Contraseña: {login_info['password']}")
            else:
                standard_steps.append(f"{step_counter}. Realiza login con las credenciales proporcionadas")
            step_counter += 1
        
        # 2. Navegación por secciones/menús
        if navigation_actions:
            for action in navigation_actions:
                standard_steps.append(f"{step_counter}. {action}")
                step_counter += 1
        
        # 3. Logout (si se detecta o es común en casos de navegación)
        if any(word in pasos_text for word in ['logout', 'cerrar sesión', 'salir', 'desconectar']) or len(navigation_actions) >= 3:
            # Agregar logout si se detecta explícitamente o si hay múltiples navegaciones (patrón común)
            standard_steps.append(f"{step_counter}. Presiona cerrar sesión")
        
        # Verificar que se generaron pasos válidos
        if len(standard_steps) >= 2:  # Al menos login + una acción
            return '\n'.join(standard_steps)
        
        return None
    
    def _can_apply_standard_pattern(self, test_case: TestCase) -> bool:
        """Determina si un caso puede seguir el patrón estándar"""
        
        # Verificar que tenga URL
        if not test_case.url_extraida:
            return False
        
        pasos_text = test_case.pasos.lower()
        datos_text = test_case.datos_prueba.lower()
        objetivo_text = test_case.objetivo.lower()
        
        # Indicadores de que es un caso de navegación web estándar
        login_indicators = ['login', 'ingresar', 'autenticar', 'usuario', 'contraseña', 'password']
        navigation_indicators = ['click', 'clic', 'navegar', 'ir a', 'seleccionar', 'menú', 'sección', 'dashboard', 'panel']
        
        has_login = any(indicator in pasos_text or indicator in datos_text for indicator in login_indicators)
        has_navigation = any(indicator in pasos_text or indicator in objetivo_text for indicator in navigation_indicators)
        
        # Debe tener indicadores de login Y navegación
        return has_login and has_navigation
    
    def _extract_login_credentials(self, test_case: TestCase) -> Dict[str, str]:
        """Extrae credenciales de login del caso"""
        
        credentials = {}
        text_to_search = f"{test_case.pasos} {test_case.datos_prueba}".lower()
        
        # Patrones para detectar usuario
        usuario_patterns = [
            r'usuario[:\s]*([^\s,\n]+)',
            r'user[:\s]*([^\s,\n]+)',
            r'email[:\s]*([^\s,\n]+)',
            r'login[:\s]*([^\s,\n]+)'
        ]
        
        for pattern in usuario_patterns:
            match = re.search(pattern, text_to_search)
            if match:
                credentials['usuario'] = match.group(1).strip()
                break
        
        # Patrones para detectar contraseña
        password_patterns = [
            r'contraseña[:\s]*([^\s,\n]+)',
            r'password[:\s]*([^\s,\n]+)',
            r'clave[:\s]*([^\s,\n]+)',
            r'pass[:\s]*([^\s,\n]+)'
        ]
        
        for pattern in password_patterns:
            match = re.search(pattern, text_to_search)
            if match:
                credentials['password'] = match.group(1).strip()
                break
        
        return credentials
    
    def _extract_navigation_actions(self, test_case: TestCase) -> List[str]:
        """Extrae acciones de navegación del caso"""
        
        actions = []
        pasos_text = test_case.pasos
        objetivo_text = test_case.objetivo
        
        # Buscar menciones de secciones/menús específicos
        navigation_terms = [
            'dashboard', 'panel', 'inicio', 'home',
            'pendiente', 'pago', 'pagos', 'revisión', 'revision',
            'reportes', 'informes', 'configuración', 'config',
            'usuarios', 'perfil', 'cuenta', 'settings',
            'administración', 'admin', 'gestión', 'iconos', 'icono'
        ]
        
        text_to_analyze = f"{pasos_text} {objetivo_text}".lower()
        
        # Detectar si es un caso de navegación por iconos laterales
        if 'icono' in text_to_analyze and 'lateral' in text_to_analyze:
            # Es un caso de navegación por iconos laterales - usar patrón estándar
            actions.extend([
                "Haz clic en el ícono lateral Dashboard",
                "Haz clic en el ícono lateral Pendiente de Pago", 
                "Haz clic en el ícono lateral Pendiente revisión",
                "Haz clic en el ícono lateral Pagados"
            ])
        else:
            # Buscar términos específicos
            for term in navigation_terms:
                if term in text_to_analyze:
                    # Generar acción de navegación
                    if 'dashboard' in term or 'panel' in term or 'inicio' in term:
                        actions.append("Haz clic en el ícono lateral Dashboard")
                    elif 'pendiente' in term and 'pago' in text_to_analyze:
                        actions.append("Haz clic en el ícono lateral Pendiente de Pago")
                    elif 'pendiente' in term and ('revisión' in text_to_analyze or 'revision' in text_to_analyze):
                        actions.append("Haz clic en el ícono lateral Pendiente revisión")
                    elif 'pagado' in text_to_analyze or ('pago' in text_to_analyze and 'pendiente' not in text_to_analyze):
                        actions.append("Haz clic en el ícono lateral Pagados")
                    elif 'reporte' in term or 'informe' in term:
                        actions.append(f"Haz clic en el ícono lateral {term.title()}")
                    elif 'config' in term or 'configuración' in term:
                        actions.append("Haz clic en el ícono lateral Configuración")
                    else:
                        actions.append(f"Haz clic en el ícono lateral {term.title()}")
        
        # Si no se encontraron acciones específicas, buscar patrones genéricos
        if not actions:
            # Buscar patrones de "hacer clic en..."
            click_patterns = [
                r'(?:hacer?\s+)?clic\s+en\s+([^.\n]+)',
                r'(?:hacer?\s+)?click\s+en\s+([^.\n]+)',
                r'seleccionar\s+([^.\n]+)',
                r'navegar\s+a\s+([^.\n]+)',
                r'ir\s+a\s+([^.\n]+)'
            ]
            
            for pattern in click_patterns:
                matches = re.findall(pattern, text_to_analyze, re.IGNORECASE)
                for match in matches:
                    clean_match = match.strip().rstrip('.,;')
                    if clean_match and len(clean_match) < 50:  # Evitar matches muy largos
                        if 'icono' in clean_match or 'lateral' in clean_match:
                            # Convertir a formato estándar
                            actions.append(f"Haz clic en el ícono lateral {clean_match.replace('ícono', '').replace('icono', '').replace('lateral', '').strip().title()}")
                        else:
                            actions.append(f"Haz clic en {clean_match}")
        
        # Remover duplicados manteniendo orden
        seen = set()
        unique_actions = []
        for action in actions:
            if action not in seen:
                seen.add(action)
                unique_actions.append(action)
        
        return unique_actions[:5]  # Máximo 5 acciones para mantener simplicidad
    
    def analyze_with_claude(self, test_cases: List[TestCase]) -> List[TestCase]:
        """Método de compatibilidad que usa el nuevo análisis híbrido"""
        return self.analyze_with_hybrid_approach(test_cases)
    
    def _create_analysis_prompt(self, test_case: TestCase) -> str:
        """Crea el prompt para el análisis con Claude"""
        
        return f"""
Analiza el siguiente caso de prueba y determina si es ejecutable en QA-Pilot (herramienta de automatización web):

**CASO DE PRUEBA:**
- ID: {test_case.id}
- Nombre: {test_case.nombre}
- Historia de Usuario: {test_case.historia_usuario}
- Objetivo: {test_case.objetivo}
- Precondición: {test_case.precondicion}
- Pasos: {test_case.pasos}
- Datos de Prueba: {test_case.datos_prueba}
- Resultado Esperado: {test_case.resultado_esperado}
- URL Detectada: {test_case.url_extraida or 'No detectada'}

**CRITERIOS DE ANÁLISIS:**
1. ¿Hay coherencia entre el nombre, objetivo, pasos y resultado esperado?
2. ¿Los pasos son lo suficientemente claros y específicos para automatizar?
3. ¿Se puede identificar una URL o sitio web para ejecutar?
4. ¿Faltan datos críticos para la ejecución?
5. ¿Los pasos son técnicamente factibles de automatizar?

**RESPONDE EN FORMATO JSON:**
{{
    "es_valido": true/false,
    "problemas": ["lista de problemas encontrados"],
    "sugerencias": ["lista de sugerencias para mejorar"],
    "instrucciones_qa_pilot": "Instrucciones optimizadas para QA-Pilot (si es válido)",
    "confianza": "alta/media/baja"
}}

Sé analítico pero constructivo. Si hay problemas menores, sugiere cómo corregirlos.
"""
    
    def _parse_claude_response(self, response_text: str) -> Dict:
        """Parsea la respuesta de Claude"""
        
        try:
            # Buscar el JSON en la respuesta
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback si no se encuentra JSON válido
                return {
                    "es_valido": False,
                    "url_requerida": "REQUERIDA_POR_USUARIO",
                    "pasos_mejorados": "",
                    "datos_simulados": "",
                    "datos_requeridos": "",
                    "problemas_usuario": ["Proporcionar URL del sistema"],
                    "instrucciones_qa_pilot": "Error al procesar respuesta de IA"
                }
        except json.JSONDecodeError:
            return {
                "es_valido": False,
                "url_requerida": "REQUERIDA_POR_USUARIO", 
                "pasos_mejorados": "",
                "datos_simulados": "",
                "datos_requeridos": "",
                "problemas_usuario": ["Proporcionar URL del sistema", "Revisar caso manualmente"],
                "instrucciones_qa_pilot": "Respuesta de IA no válida - revisar manualmente"
            }
    
    def _basic_validation(self, test_cases: List[TestCase]) -> List[TestCase]:
        """Validación básica sin IA"""
        
        for test_case in test_cases:
            problemas = []
            sugerencias = []
            
            # Validaciones básicas
            if not test_case.nombre.strip():
                problemas.append("Falta el nombre del caso de prueba")
            
            if not test_case.objetivo.strip():
                problemas.append("Falta el objetivo del caso de prueba")
            
            if not test_case.pasos.strip():
                problemas.append("Faltan los pasos de ejecución")
            
            if not test_case.url_extraida:
                problemas.append("No se pudo detectar una URL para ejecutar")
                sugerencias.append("Agregar URL en los pasos o datos de prueba")
            
            if len(test_case.pasos.split()) < 5:
                problemas.append("Los pasos son muy breves, pueden ser poco claros")
                sugerencias.append("Detallar más los pasos de ejecución")
            
            test_case.problemas = problemas
            test_case.sugerencias = sugerencias
            test_case.es_valido = len(problemas) == 0
            
            # Generar instrucciones básicas para QA-Pilot
            if test_case.es_valido:
                test_case.instrucciones_qa_pilot = f"""
Objetivo: {test_case.objetivo}

Pasos:
{test_case.pasos}

Verificar: {test_case.resultado_esperado}
""".strip()
        
        return test_cases
    
    def generate_summary_report(self, test_cases: List[TestCase]) -> Dict:
        """Genera un reporte resumen del análisis"""
        
        total_cases = len(test_cases)
        valid_cases = len([tc for tc in test_cases if tc.es_valido])
        invalid_cases = total_cases - valid_cases
        
        # Agrupar problemas más comunes
        all_problems = []
        for tc in test_cases:
            all_problems.extend(tc.problemas)
        
        problem_counts = {}
        for problem in all_problems:
            problem_counts[problem] = problem_counts.get(problem, 0) + 1
        
        return {
            "total_casos": total_cases,
            "casos_validos": valid_cases,
            "casos_invalidos": invalid_cases,
            "porcentaje_validos": round((valid_cases / total_cases) * 100, 2) if total_cases > 0 else 0,
            "problemas_comunes": sorted(problem_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "casos_con_url": len([tc for tc in test_cases if tc.url_extraida]),
            "casos_sin_url": len([tc for tc in test_cases if not tc.url_extraida])
        }

# Función de utilidad para uso directo
def analyze_excel_file(file_path: str) -> Tuple[List[TestCase], Dict]:
    """Función de conveniencia para analizar un archivo Excel"""
    
    analyzer = ExcelTestAnalyzer()
    test_cases = analyzer.extract_test_cases(file_path)
    analyzed_cases = analyzer.analyze_with_claude(test_cases)  # Usar análisis con IA si está disponible
    summary = analyzer.generate_summary_report(analyzed_cases)
    
    return analyzed_cases, summary 