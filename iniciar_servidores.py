"""
Script para iniciar los servidores dedicados para la aplicación QA-Pilot
Este script inicia tanto el servidor de casos como el servidor de suites
"""
import subprocess
import sys
import os
import time
import threading
import signal

def verificar_playwright():
    """Verifica que Playwright esté instalado correctamente"""
    print("Verificando requisitos previos...")
    try:
        # Ruta al script de verificación
        verificar_script = os.path.join(os.path.dirname(__file__), "playwright_scripts", "verificar_requisitos.py")
        
        # Si el script no existe, lo ignoramos
        if not os.path.exists(verificar_script):
            print("Aviso: Script de verificación no encontrado. Continuando sin verificar requisitos.")
            return True
        
        # Ejecutar script de verificación
        result = subprocess.run([sys.executable, verificar_script], 
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
        
        # Mostrar salida del script
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # Verificar resultado
        if result.returncode != 0:
            print("Error: La verificación de requisitos ha fallado.")
            return False
        
        return True
    except Exception as e:
        print(f"Error al verificar requisitos: {str(e)}")
        return False

def run_server(script_path, name):
    """Ejecuta un servidor en un proceso independiente."""
    try:
        print(f"Iniciando servidor {name}...")
        process = subprocess.Popen([sys.executable, script_path], 
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   text=True,
                                   bufsize=1)
        
        # Mostrar la salida del proceso en tiempo real
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                print(f"[{name}] {line.rstrip()}")
        
        # Comprobar si el proceso terminó con error
        if process.returncode != 0:
            print(f"Error: El servidor {name} ha terminado con código {process.returncode}")
        else:
            print(f"El servidor {name} ha terminado correctamente")
    except Exception as e:
        print(f"Error al ejecutar el servidor {name}: {str(e)}")

def main():
    # Verificar requisitos primero
    if not verificar_playwright():
        print("No se han cumplido los requisitos previos. Abortando inicio de servidores.")
        return 1
    
    print("\n=== Iniciando servidores de QA-Pilot ===\n")
    
    # Obtener rutas absolutas de los servidores
    base_dir = os.path.dirname(os.path.abspath(__file__))
    direct_server_path = os.path.join(base_dir, "direct_server.py")
    suite_server_path = os.path.join(base_dir, "suite_server.py")
    
    # Comprobar que los archivos existen
    if not os.path.exists(direct_server_path):
        print(f"Error: No se encontró el archivo {direct_server_path}")
        return 1
    
    if not os.path.exists(suite_server_path):
        print(f"Error: No se encontró el archivo {suite_server_path}")
        return 1
    
    # Crear threads para los servidores
    server_threads = [
        threading.Thread(target=run_server, args=(direct_server_path, "Casos Playwright")),
        threading.Thread(target=run_server, args=(suite_server_path, "Suites"))
    ]
    
    # Iniciar servidores en threads separados
    for thread in server_threads:
        thread.daemon = True  # Hacer que los threads terminen cuando termine el programa principal
        thread.start()
        time.sleep(1)  # Pequeña pausa para evitar que los logs se mezclen
    
    print("\nServidores iniciados correctamente. Presione Ctrl+C para detener.")
    
    try:
        # Mantener el programa en ejecución
        while all(thread.is_alive() for thread in server_threads):
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDetención solicitada. Cerrando servidores...")
    except Exception as e:
        print(f"\nError inesperado: {str(e)}")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"Error fatal: {str(e)}")
        sys.exit(1) 