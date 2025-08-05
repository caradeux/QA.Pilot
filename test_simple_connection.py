#!/usr/bin/env python3
"""
Script simplificado para probar la conexión a PostgreSQL.
"""

import os
import sys
from dotenv import load_dotenv

def load_config():
    """Cargar configuración desde archivo de entorno"""
    # Intentar cargar desde config_db.env primero, luego .env
    if os.path.exists('config_db.env'):
        load_dotenv('config_db.env')
        print("📁 Configuración cargada desde config_db.env")
    elif os.path.exists('.env'):
        load_dotenv('.env')
        print("📁 Configuración cargada desde .env")
    else:
        print("⚠️  No se encontró archivo de configuración. Usando valores por defecto.")
    
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME', 'playwright_testing_db'),
        'username': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
    }
    
    return config

def main():
    print("🚀 Prueba de conexión simplificada a PostgreSQL...")
    print("=" * 60)
    
    try:
        # Cargar configuración
        config = load_config()
        
        if not config['password']:
            print("❌ ERROR: Debes configurar DB_PASSWORD en tu archivo de configuración")
            print("💡 Edita config_db.env y cambia 'tu_password_aqui' por tu contraseña real")
            return 1
        
        print(f"🔍 Intentando conectar a PostgreSQL:")
        print(f"   Host: {config['host']}")
        print(f"   Puerto: {config['port']}")
        print(f"   Base de datos: {config['database']}")
        print(f"   Usuario: {config['username']}")
        print()
        
        # Importar después de cargar la configuración
        from db_models_simple import DatabaseManager
        from sqlalchemy import text
        
        # Crear conexión
        db_manager = DatabaseManager(**config)
        
        # Probar conexión básica
        if db_manager.test_connection():
            print("✅ Conexión básica exitosa")
        else:
            print("❌ Error en conexión básica")
            return 1
        
        # Probar consulta a las tablas del esquema testing
        session = db_manager.get_session()
        try:
            result = session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'testing'"))
            tables = [row[0] for row in result.fetchall()]
            
            print(f"📊 Tablas encontradas en schema 'testing': {tables}")
            
            if len(tables) >= 3:  # Esperamos al menos 3 tablas principales
                print("✅ Las tablas principales están creadas")
            else:
                print(f"⚠️  Solo se encontraron {len(tables)} tablas")
                print("💡 Asegúrate de haber ejecutado el script SQL db_complete_setup.sql")
                
        except Exception as e:
            print(f"❌ Error consultando tablas: {e}")
            return 1
        finally:
            session.close()
        
        print("=" * 60)
        print("🎉 Prueba de conexión completada exitosamente!")
        print("💡 La base de datos está lista para usar")
        
        return 0
        
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("💡 Asegúrate de haber instalado las dependencias: pip install -r requirements_db.txt")
        return 1
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        print("💡 Verifica que:")
        print("   1. PostgreSQL esté ejecutándose")
        print("   2. La base de datos exista")
        print("   3. Las credenciales sean correctas")
        print("   4. El script SQL se haya ejecutado")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 