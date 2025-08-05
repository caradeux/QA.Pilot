#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificación de requisitos para QA-Pilot
Este script verifica y asegura que Playwright esté instalado correctamente
"""
import os
import sys
import subprocess
import time

def verificar_playwright():
    """Verifica si Playwright está instalado y lo instala si es necesario"""
    print("Verificando instalación de Playwright...")
    
    # Verificar si el módulo playwright está instalado
    try:
        import playwright
        print(f"[OK] Playwright está instalado")
        instalar_navegadores = True
    except ImportError:
        print("[ERROR] Playwright no está instalado. Procediendo a instalar...")
        
        # Instalar playwright
        try:
            print("Ejecutando: pip install playwright")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
            print("[OK] Playwright instalado correctamente")
            instalar_navegadores = True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Error al instalar Playwright: {e}")
            return False
    
    # Verificar si los navegadores están instalados
    if instalar_navegadores:
        try:
            # Intentar importar playwright nuevamente (en caso de que se acabe de instalar)
            import playwright
            
            # Verificar si los navegadores ya están instalados (verificando si existe la carpeta)
            import platform
            home_dir = os.path.expanduser("~")
            
            # Determinar la ruta según el sistema operativo
            if platform.system() == "Windows":
                browser_path = os.path.join(home_dir, "AppData", "Local", "ms-playwright")
            elif platform.system() == "Darwin":  # macOS
                browser_path = os.path.join(home_dir, "Library", "Caches", "ms-playwright")
            else:  # Linux y otros
                browser_path = os.path.join(home_dir, ".cache", "ms-playwright")
            
            if os.path.exists(browser_path):
                print("[OK] Navegadores de Playwright ya instalados")
            else:
                print("Instalando navegadores para Playwright...")
                subprocess.check_call([sys.executable, "-m", "playwright", "install"])
                print("[OK] Navegadores instalados correctamente")
        except (ImportError, subprocess.CalledProcessError) as e:
            print(f"[ERROR] Error al instalar navegadores: {e}")
            return False
    
    return True

def verificar_carpetas():
    """Verifica y crea las carpetas necesarias"""
    print("\nVerificando carpetas necesarias...")
    
    # Verificar carpeta de scripts
    carpetas = [
        "playwright_scripts",
        "playwright_scripts/casos",
        "test_screenshots"
    ]
    
    for carpeta in carpetas:
        if not os.path.exists(carpeta):
            print(f"Creando carpeta: {carpeta}")
            os.makedirs(carpeta, exist_ok=True)
        else:
            print(f"[OK] Carpeta existente: {carpeta}")
    
    return True

def verificar_permisos_scripts():
    """Verifica y arregla permisos de scripts"""
    print("\nVerificando permisos de scripts...")
    
    carpeta_casos = "playwright_scripts/casos"
    if not os.path.exists(carpeta_casos):
        print(f"[ERROR] La carpeta {carpeta_casos} no existe")
        return False
    
    # En sistemas tipo Unix, asegurar que los scripts sean ejecutables
    if sys.platform != "win32":
        try:
            for archivo in os.listdir(carpeta_casos):
                if archivo.endswith(".py"):
                    ruta_completa = os.path.join(carpeta_casos, archivo)
                    os.chmod(ruta_completa, 0o755)  # Permisos rwxr-xr-x
                    print(f"[OK] Permisos establecidos: {ruta_completa}")
        except Exception as e:
            print(f"[ERROR] Error al establecer permisos: {e}")
            return False
    
    return True

def verificar_todo():
    """Ejecuta todas las verificaciones"""
    print("==== VERIFICACIÓN DE REQUISITOS PARA QA-PILOT ====\n")
    
    # Verificar Playwright
    if not verificar_playwright():
        print("\n[ERROR] Falló la verificación de Playwright")
        return False
    
    # Verificar carpetas
    if not verificar_carpetas():
        print("\n[ERROR] Falló la verificación de carpetas")
        return False
    
    # Verificar permisos de scripts
    if not verificar_permisos_scripts():
        print("\n[ERROR] Falló la verificación de permisos")
        return False
    
    print("\n[OK] Todas las verificaciones completadas exitosamente")
    print("\nEl sistema está listo para ejecutar pruebas con Playwright")
    return True

if __name__ == "__main__":
    try:
        if verificar_todo():
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error fatal durante las verificaciones: {e}")
        sys.exit(1) 