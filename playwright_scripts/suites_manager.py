#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Administrador de Suites de Prueba para Playwright
-------------------------------------------------
Este módulo permite administrar colecciones de casos de prueba (suites)
para ejecutarlos en conjunto.
"""

import os
import json
import uuid
import time
from datetime import datetime

# Directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUITES_DIR = os.path.join(BASE_DIR, "suites")
CASOS_DIR = os.path.join(BASE_DIR, "casos")

# Crear directorio de suites si no existe
os.makedirs(SUITES_DIR, exist_ok=True)

class TestSuite:
    """Representa una suite de pruebas que contiene múltiples casos."""
    
    def __init__(self, suite_id=None, name="", description="", cases=None):
        """Inicializa una nueva suite de pruebas.
        
        Args:
            suite_id (str): ID único de la suite. Si no se proporciona, se generará uno nuevo.
            name (str): Nombre descriptivo de la suite
            description (str): Descripción de la suite
            cases (list): Lista de casos de prueba (nombres de archivo)
        """
        self.id = suite_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.cases = cases or []
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def to_dict(self):
        """Convierte la suite a un diccionario para serialización."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "cases": self.cases,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea una instancia de TestSuite desde un diccionario."""
        suite = cls(
            suite_id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            cases=data.get("cases", [])
        )
        suite.created_at = data.get("created_at", suite.created_at)
        suite.updated_at = data.get("updated_at", suite.updated_at)
        return suite
    
    def add_case(self, case_filename):
        """Añade un caso a la suite.
        
        Args:
            case_filename (str): Nombre del archivo del caso de prueba
        
        Returns:
            bool: True si se añadió correctamente, False si ya existía
        """
        if case_filename not in self.cases:
            self.cases.append(case_filename)
            self.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def remove_case(self, case_filename):
        """Elimina un caso de la suite.
        
        Args:
            case_filename (str): Nombre del archivo del caso de prueba
        
        Returns:
            bool: True si se eliminó correctamente, False si no existía
        """
        if case_filename in self.cases:
            self.cases.remove(case_filename)
            self.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def save(self):
        """Guarda la suite en un archivo JSON.
        
        Returns:
            str: Ruta del archivo guardado
        """
        # Crear nombre de archivo seguro
        filename = f"suite_{self.id}.json"
        filepath = os.path.join(SUITES_DIR, filename)
        
        # Guardar el archivo
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        
        return filepath

def list_suites():
    """Lista todas las suites disponibles.
    
    Returns:
        list: Lista de objetos TestSuite
    """
    suites = []
    
    # Verificar que el directorio existe
    if not os.path.exists(SUITES_DIR):
        os.makedirs(SUITES_DIR, exist_ok=True)
        return suites
    
    # Buscar archivos .json en el directorio de suites
    for filename in os.listdir(SUITES_DIR):
        if filename.endswith('.json') and filename.startswith('suite_'):
            filepath = os.path.join(SUITES_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    suite_data = json.load(f)
                    suites.append(TestSuite.from_dict(suite_data))
            except Exception as e:
                print(f"Error al cargar suite {filename}: {e}")
    
    # Ordenar por fecha de actualización (más reciente primero)
    suites.sort(key=lambda x: x.updated_at, reverse=True)
    return suites

def get_suite(suite_id):
    """Obtiene una suite por su ID.
    
    Args:
        suite_id (str): ID de la suite
    
    Returns:
        TestSuite: Objeto de suite si se encuentra, None en caso contrario
    """
    filename = f"suite_{suite_id}.json"
    filepath = os.path.join(SUITES_DIR, filename)
    
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                suite_data = json.load(f)
                return TestSuite.from_dict(suite_data)
        except Exception as e:
            print(f"Error al cargar suite {suite_id}: {e}")
    
    return None

def delete_suite(suite_id):
    """Elimina una suite por su ID.
    
    Args:
        suite_id (str): ID de la suite
    
    Returns:
        bool: True si se eliminó correctamente, False en caso contrario
    """
    filename = f"suite_{suite_id}.json"
    filepath = os.path.join(SUITES_DIR, filename)
    
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            print(f"Error al eliminar suite {suite_id}: {e}")
    
    return False

def list_cases():
    """Lista todos los casos de prueba disponibles.
    
    Returns:
        list: Lista de información de casos (diccionarios)
    """
    cases = []
    
    # Verificar que el directorio existe
    if not os.path.exists(CASOS_DIR):
        return cases
    
    # Buscar archivos .py en el directorio de casos
    for filename in os.listdir(CASOS_DIR):
        if filename.endswith('.py') and not filename.startswith('__'):
            filepath = os.path.join(CASOS_DIR, filename)
            
            # Obtener información básica del archivo
            try:
                case_info = {
                    "filename": filename,
                    "name": os.path.splitext(filename)[0],
                    "path": filepath,
                    "size": os.path.getsize(filepath),
                    "modified": os.path.getmtime(filepath),
                    "modified_date": datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Intentar extraer descripción del docstring
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read(2000)  # Leer solo las primeras líneas
                    
                    # Extraer docstring si existe
                    import re
                    docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                    if docstring_match:
                        docstring = docstring_match.group(1).strip()
                        # Tomar la primera línea como descripción
                        description = docstring.split('\n')[0].strip()
                        case_info["description"] = description
                    else:
                        case_info["description"] = f"Script de prueba: {case_info['name']}"
                
                cases.append(case_info)
            except Exception as e:
                print(f"Error al procesar caso {filename}: {e}")
    
    # Ordenar por fecha de modificación (más reciente primero)
    cases.sort(key=lambda x: x.get('modified', 0), reverse=True)
    return cases

# Prueba básica del módulo
if __name__ == "__main__":
    print("Administrador de Suites de Prueba")
    print("================================")
    
    # Listar casos disponibles
    print("\nCasos disponibles:")
    cases = list_cases()
    for i, case in enumerate(cases, 1):
        print(f"{i}. {case['name']} - {case['description']}")
    
    # Listar suites existentes
    print("\nSuites existentes:")
    suites = list_suites()
    for i, suite in enumerate(suites, 1):
        print(f"{i}. {suite.name} - {suite.description} ({len(suite.cases)} casos)")
    
    # Crear una suite de prueba si no hay ninguna
    if not suites:
        print("\nCreando suite de ejemplo...")
        new_suite = TestSuite(name="Suite de Ejemplo", description="Una suite de prueba creada automáticamente")
        
        # Agregar casos si hay disponibles
        if cases:
            for case in cases[:2]:  # Agregar los primeros 2 casos
                new_suite.add_case(case["filename"])
                print(f"  + Agregado caso: {case['name']}")
        
        # Guardar
        filepath = new_suite.save()
        print(f"Suite guardada en: {filepath}") 