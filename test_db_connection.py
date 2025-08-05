#!/usr/bin/env python3
"""
Script para probar la conexión a PostgreSQL y verificar la configuración de la base de datos.
Ejecutar después de instalar el script SQL.
"""

import os
import sys
from dotenv import load_dotenv
from db_models import DatabaseManager
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    """Cargar configuración desde archivo de entorno"""
    # Intentar cargar desde .env primero, luego config_db.env
    if os.path.exists('.env'):
        load_dotenv('.env')
        logger.info("Configuración cargada desde .env")
    elif os.path.exists('config_db.env'):
        load_dotenv('config_db.env')
        logger.info("Configuración cargada desde config_db.env")
    else:
        logger.warning("No se encontró archivo de configuración. Usando valores por defecto.")
    
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME', 'playwright_testing_db'),
        'username': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
    }
    
    return config

def test_connection():
    """Probar conexión a la base de datos"""
    try:
        config = load_config()
        
        if not config['password']:
            logger.error("⚠️  Debes configurar DB_PASSWORD en tu archivo de configuración")
            return False
        
        logger.info(f"🔍 Intentando conectar a PostgreSQL:")
        logger.info(f"   Host: {config['host']}")
        logger.info(f"   Puerto: {config['port']}")
        logger.info(f"   Base de datos: {config['database']}")
        logger.info(f"   Usuario: {config['username']}")
        
        # Inicializar DatabaseManager
        db_manager = DatabaseManager(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            username=config['username'],
            password=config['password']
        )
        
        # Probar conexión
        session = db_manager.get_session()
        try:
            # Verificar que las tablas existen
            result = session.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'testing'")
            tables = [row[0] for row in result.fetchall()]
            
            logger.info("✅ Conexión exitosa a PostgreSQL")
            logger.info(f"📊 Tablas encontradas en schema 'testing': {tables}")
            
            if len(tables) >= 6:  # Esperamos al menos 6 tablas principales
                logger.info("✅ Todas las tablas principales están creadas")
                return True
            else:
                logger.warning(f"⚠️  Solo se encontraron {len(tables)} tablas. Verifica que el script SQL se ejecutó correctamente.")
                return False
        finally:
            session.close()
                
    except Exception as e:
        logger.error(f"❌ Error de conexión: {str(e)}")
        logger.error("💡 Verifica que:")
        logger.error("   1. PostgreSQL esté ejecutándose")
        logger.error("   2. La base de datos exista")
        logger.error("   3. Las credenciales sean correctas")
        logger.error("   4. El script SQL se haya ejecutado")
        return False

def test_basic_operations():
    """Probar operaciones básicas de la base de datos"""
    try:
        config = load_config()
        db_manager = DatabaseManager(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            username=config['username'],
            password=config['password']
        )
        
        from db_models import Project, TestSuite, TestCase
        
        session = db_manager.get_session()
        try:
            # Crear un proyecto de prueba
            test_project = Project(
                name="Test Project",
                description="Proyecto de prueba para verificar la base de datos",
                status="active"
            )
            session.add(test_project)
            session.commit()
            
            logger.info("✅ Proyecto de prueba creado exitosamente")
            
            # Limpiar el proyecto de prueba
            session.delete(test_project)
            session.commit()
            
            logger.info("✅ Operaciones básicas funcionando correctamente")
            return True
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"❌ Error en operaciones básicas: {str(e)}")
        return False

def main():
    """Función principal"""
    logger.info("🚀 Iniciando pruebas de conexión a PostgreSQL...")
    logger.info("=" * 60)
    
    # Probar conexión
    if not test_connection():
        logger.error("❌ Falló la prueba de conexión")
        return 1
    
    # Probar operaciones básicas
    if not test_basic_operations():
        logger.error("❌ Fallaron las operaciones básicas")
        return 1
    
    logger.info("=" * 60)
    logger.info("🎉 ¡Todas las pruebas pasaron exitosamente!")
    logger.info("💡 La base de datos está lista para usar")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 