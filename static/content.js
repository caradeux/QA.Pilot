/**
 * QA-Pilot Content Enhancements
 * Añade funcionalidad interactiva a la interfaz de usuario
 */

// Función para inicializar los elementos de la interfaz de manera segura
function initializeUIElements() {
    try {
        // Obtener referencias a los elementos del DOM con verificación de existencia
        const uiElements = {
            startButton: document.getElementById('start-test-btn'),
            taskForm: document.getElementById('test-form'),
            monitorButton: document.getElementById('monitor-btn'),
            telemetrySection: document.getElementById('telemetrySection')
        };
    
    // Asignar event listeners solo si los elementos existen
    try {
        if (uiElements.startButton && typeof uiElements.startButton.addEventListener === 'function') {
            uiElements.startButton.addEventListener('click', function(e) {
                console.log('Iniciando vuelo...');
                // El formulario maneja el envío de datos naturalmente
            });
        }
        
        if (uiElements.taskForm && typeof uiElements.taskForm.addEventListener === 'function') {
            uiElements.taskForm.addEventListener('submit', function(e) {
                // Podemos agregar validación adicional aquí si es necesario
                console.log('Formulario enviado');
            });
        }
        
        if (uiElements.monitorButton) {
            // Este event listener ya existe en direct_monitor.js, no duplicar
            console.log('Monitor button encontrado');
        }
    } catch (error) {
        console.warn('Error configurando event listeners principales:', error);
    }
    
    // Agregar feedback visual cuando el usuario interactúa con campos de texto
    try {
        const textInputs = document.querySelectorAll('input[type="text"], input[type="url"], textarea');
        if (textInputs && textInputs.length > 0) {
            textInputs.forEach(input => {
                if (input && typeof input.addEventListener === 'function') {
                    input.addEventListener('focus', function() {
                        this.classList.add('tech-input-active');
                    });
                    
                    input.addEventListener('blur', function() {
                        this.classList.remove('tech-input-active');
                    });
                }
            });
        }
    } catch (error) {
        console.warn('Error configurando inputs de texto:', error);
    }
    
    // Mejorar interactividad en los rangos
    try {
        const rangeInputs = document.querySelectorAll('input[type="range"]');
        if (rangeInputs && rangeInputs.length > 0) {
            rangeInputs.forEach(range => {
                if (range && typeof range.addEventListener === 'function') {
                    range.addEventListener('input', function() {
                        // La actualización del valor ya está manejada por el atributo oninput
                        console.log(`Rango actualizado: ${this.value}`);
                    });
                }
            });
        }
    } catch (error) {
        console.warn('Error configurando inputs de rango:', error);
    }
    
    console.log('Inicialización de elementos UI completada');
    } catch (error) {
        console.error('Error en initializeUIElements:', error);
    }
}

// Inicializar cuando el DOM esté listo con manejo de errores
function safeInitialize() {
    try {
        initializeUIElements();
    } catch (error) {
        console.warn('Error durante la inicialización de UI:', error);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', safeInitialize);
} else {
    // Si el DOM ya está cargado, inicializar inmediatamente
    safeInitialize();
}

// Exportar funciones útiles al ámbito global
window.QAPilot = {
    refreshUI: initializeUIElements,
    version: '1.0.0'
}; 