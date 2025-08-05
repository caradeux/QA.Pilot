"""
Script to add routes to a Flask app at runtime.
"""
from flask import Flask, jsonify
import os
import sys
import importlib.util

def register_routes(app):
    """
    This function explicitly registers important routes that might have been missed.
    Call this right before app.run() to ensure all routes are properly registered.
    """
    # Check if certain routes need to be registered
    registered_rules = [rule.rule for rule in app.url_map.iter_rules()]
    
    # Define handlers for the missing routes
    if '/list_test_suites' not in registered_rules:
        @app.route('/list_test_suites')
        def list_test_suites():
            """Lista todas las suites de prueba disponibles."""
            try:
                # Import the real function's module
                from playwright_scripts.suites_manager import list_suites
                
                # Call the imported function
                suites = list_suites()
                return jsonify({
                    'status': 'success',
                    'suites': [suite.to_dict() for suite in suites]
                })
            except Exception as e:
                import traceback
                print(f"ERROR: Error al listar suites: {str(e)}")
                print(traceback.format_exc())
                return jsonify({
                    'status': 'error',
                    'message': f'Error al listar suites: {str(e)}'
                }), 500
    
    if '/debug/routes' not in registered_rules:
        @app.route('/debug/routes')
        def debug_routes():
            """Vista para depuración que muestra todas las rutas disponibles."""
            rules = []
            for rule in sorted(app.url_map.iter_rules(), key=lambda x: x.rule):
                rules.append({
                    'endpoint': rule.endpoint,
                    'methods': list(rule.methods),
                    'rule': rule.rule
                })
            
            return jsonify({
                'status': 'success',
                'app_name': app.name,
                'routes_count': len(rules),
                'routes': rules
            })
            
    # Add any other missing routes here if needed
            
    print("\nRegistered routes after patch:")
    for rule in sorted(app.url_map.iter_rules(), key=lambda x: x.rule):
        print(f"- {rule.rule} ({rule.endpoint})")
    
    return app

# The following is a simple test when this file is run directly
if __name__ == "__main__":
    # Create a test app to verify the function works
    test_app = Flask("test_app")
    
    @test_app.route('/')
    def index():
        return "Test route"
    
    print("Routes before registration:")
    for rule in test_app.url_map.iter_rules():
        print(f"- {rule.rule}")
    
    # Register additional routes
    register_routes(test_app)
    
    print("\nTest complete!") 