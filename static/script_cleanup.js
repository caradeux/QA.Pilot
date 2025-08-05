/**
 * Script Cleanup - Detecta y maneja duplicados y problemas comunes
 */

// Función para detectar y eliminar scripts duplicados
(function() {
    console.log("Script cleanup: iniciando verificación de scripts duplicados");
    
    // Lista de scripts problemáticos conocidos
    const problematicScripts = [
        'prompt.js',
        'monitor.js'
    ];
    
    // Detectar y limpiar variables globales duplicadas
    if (typeof window.originalPrompt !== 'undefined') {
        console.log("Detectada variable originalPrompt duplicada - limpiando referencia");
        try {
            delete window.originalPrompt;
            console.log("Variable originalPrompt eliminada con éxito");
        } catch (e) {
            console.error("Error al limpiar variable:", e);
        }
    }
    
    // Verificar scripts cargados 
    let scriptElements = document.querySelectorAll('script');
    let scriptUrls = {};
    
    scriptElements.forEach(script => {
        let src = script.getAttribute('src');
        if (src) {
            // Verificar si es un script problemático
            const isProblematic = problematicScripts.some(problemScript => 
                src.includes(problemScript)
            );
            
            if (isProblematic) {
                console.warn(`Detectado script potencialmente problemático: ${src}`);
                
                // Si el script ya fue cargado antes, marcar para eliminar
                if (scriptUrls[src]) {
                    console.log(`Eliminando script duplicado: ${src}`);
                    try {
                        script.parentNode.removeChild(script);
                    } catch (e) {
                        console.error("Error al eliminar script:", e);
                    }
                } else {
                    // Marcar que ya vimos este script
                    scriptUrls[src] = true;
                }
            }
        }
    });
    
    // Implementar un parche para evitar futuras cargas duplicadas
    const originalAppendChild = Node.prototype.appendChild;
    Node.prototype.appendChild = function(child) {
        if (child.nodeName === 'SCRIPT' && child.src) {
            const src = child.src;
            
            // Verificar si es un script problemático
            const isProblematic = problematicScripts.some(problemScript => 
                src.includes(problemScript)
            );
            
            if (isProblematic && scriptUrls[src]) {
                console.warn(`Previniendo carga duplicada de: ${src}`);
                return child; // Devolver el child sin añadirlo
            }
            
            // Registrar este script como cargado
            scriptUrls[src] = true;
        }
        
        // Comportamiento normal para otros elementos o scripts no problemáticos
        return originalAppendChild.call(this, child);
    };
    
    console.log("Script cleanup completado");
})(); 