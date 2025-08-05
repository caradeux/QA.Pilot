// Script de prueba para verificar funcionamiento de modales
// Ejecutar en consola del navegador para diagnosticar problemas

console.log('🧪 Iniciando prueba de modales...');

function testModalFunctionality() {
    const results = {
        modalsFound: [],
        modalsWorking: [],
        modalsFailing: [],
        zIndexIssues: [],
        interactionIssues: []
    };
    
    // 1. Encontrar todos los modales
    const modals = document.querySelectorAll('.modal');
    console.log(`📋 Modales encontrados: ${modals.length}`);
    
    modals.forEach(modal => {
        const modalId = modal.id || 'sin-id';
        results.modalsFound.push(modalId);
        console.log(`🔍 Analizando modal: ${modalId}`);
        
        // Verificar z-index
        const computedStyle = window.getComputedStyle(modal);
        const zIndex = computedStyle.zIndex;
        console.log(`  📊 Z-index: ${zIndex}`);
        
        if (zIndex === 'auto' || parseInt(zIndex) < 1050) {
            results.zIndexIssues.push({
                modal: modalId,
                zIndex: zIndex,
                issue: 'Z-index demasiado bajo'
            });
        }
        
        // Verificar elementos interactivos
        const interactiveElements = modal.querySelectorAll(`
            .btn, .form-control, .form-select, input, textarea, .btn-close,
            button, a[role="button"], [data-bs-dismiss], [data-bs-toggle]
        `);
        
        console.log(`  🎯 Elementos interactivos: ${interactiveElements.length}`);
        
        let interactionProblems = 0;
        interactiveElements.forEach(element => {
            const elementStyle = window.getComputedStyle(element);
            const pointerEvents = elementStyle.pointerEvents;
            const elementZIndex = elementStyle.zIndex;
            
            if (pointerEvents === 'none') {
                interactionProblems++;
                results.interactionIssues.push({
                    modal: modalId,
                    element: element.tagName + (element.className ? '.' + element.className.split(' ')[0] : ''),
                    issue: 'pointer-events: none'
                });
            }
            
            if (elementZIndex === 'auto' || parseInt(elementZIndex) < 1055) {
                interactionProblems++;
                results.interactionIssues.push({
                    modal: modalId,
                    element: element.tagName + (element.className ? '.' + element.className.split(' ')[0] : ''),
                    issue: `Z-index bajo: ${elementZIndex}`
                });
            }
        });
        
        if (interactionProblems === 0) {
            results.modalsWorking.push(modalId);
            console.log(`  ✅ Modal ${modalId} parece funcionar correctamente`);
        } else {
            results.modalsFailing.push({
                modal: modalId,
                problems: interactionProblems
            });
            console.log(`  ❌ Modal ${modalId} tiene ${interactionProblems} problemas`);
        }
    });
    
    // 2. Verificar elementos que pueden interferir
    console.log('\n🔍 Verificando elementos que pueden interferir...');
    
    const particles = document.querySelector('.elegant-particles');
    if (particles) {
        const particlesStyle = window.getComputedStyle(particles);
        console.log(`  🎨 Partículas - Z-index: ${particlesStyle.zIndex}, Pointer-events: ${particlesStyle.pointerEvents}`);
    }
    
    const loader = document.querySelector('.premium-loader-overlay');
    if (loader) {
        const loaderStyle = window.getComputedStyle(loader);
        console.log(`  ⏳ Loader - Z-index: ${loaderStyle.zIndex}, Display: ${loaderStyle.display}`);
    }
    
    const backdrops = document.querySelectorAll('.modal-backdrop');
    console.log(`  🎭 Backdrops encontrados: ${backdrops.length}`);
    backdrops.forEach((backdrop, index) => {
        const backdropStyle = window.getComputedStyle(backdrop);
        console.log(`    Backdrop ${index}: Z-index: ${backdropStyle.zIndex}, Pointer-events: ${backdropStyle.pointerEvents}`);
    });
    
    // 3. Mostrar resumen
    console.log('\n📊 RESUMEN DE PRUEBA:');
    console.log(`✅ Modales funcionando: ${results.modalsWorking.length}`);
    console.log(`❌ Modales con problemas: ${results.modalsFailing.length}`);
    console.log(`⚠️ Problemas de Z-index: ${results.zIndexIssues.length}`);
    console.log(`🎯 Problemas de interacción: ${results.interactionIssues.length}`);
    
    if (results.zIndexIssues.length > 0) {
        console.log('\n⚠️ PROBLEMAS DE Z-INDEX:');
        results.zIndexIssues.forEach(issue => {
            console.log(`  - ${issue.modal}: ${issue.issue} (${issue.zIndex})`);
        });
    }
    
    if (results.interactionIssues.length > 0) {
        console.log('\n🎯 PROBLEMAS DE INTERACCIÓN:');
        results.interactionIssues.forEach(issue => {
            console.log(`  - ${issue.modal} > ${issue.element}: ${issue.issue}`);
        });
    }
    
    return results;
}

// Función para probar apertura de modales
function testModalOpening() {
    console.log('\n🚀 Probando apertura de modales...');
    
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(modal => {
        const modalId = modal.id;
        if (!modalId) return;
        
        console.log(`🔓 Intentando abrir modal: ${modalId}`);
        
        try {
            const bootstrapModal = new bootstrap.Modal(modal);
            
            // Escuchar eventos
            modal.addEventListener('shown.bs.modal', () => {
                console.log(`✅ Modal ${modalId} abierto exitosamente`);
                
                // Verificar si es clickeable
                setTimeout(() => {
                    const closeBtn = modal.querySelector('.btn-close, [data-bs-dismiss="modal"]');
                    if (closeBtn) {
                        const rect = closeBtn.getBoundingClientRect();
                        const elementAtPoint = document.elementFromPoint(rect.left + rect.width/2, rect.top + rect.height/2);
                        
                        if (elementAtPoint === closeBtn || closeBtn.contains(elementAtPoint)) {
                            console.log(`✅ Botón de cerrar de ${modalId} es clickeable`);
                        } else {
                            console.log(`❌ Botón de cerrar de ${modalId} está bloqueado por:`, elementAtPoint);
                        }
                    }
                    
                    // Cerrar modal después de la prueba
                    setTimeout(() => {
                        bootstrapModal.hide();
                    }, 1000);
                }, 500);
            });
            
            modal.addEventListener('hidden.bs.modal', () => {
                console.log(`🔒 Modal ${modalId} cerrado`);
            });
            
            // Abrir modal
            bootstrapModal.show();
            
        } catch (error) {
            console.error(`❌ Error al abrir modal ${modalId}:`, error);
        }
    });
}

// Función para aplicar correcciones inmediatas
function applyQuickFixes() {
    console.log('\n🔧 Aplicando correcciones rápidas...');
    
    // Corregir z-index de modales
    document.querySelectorAll('.modal').forEach(modal => {
        modal.style.zIndex = '1055';
        modal.style.pointerEvents = 'auto';
        
        const dialog = modal.querySelector('.modal-dialog');
        const content = modal.querySelector('.modal-content');
        
        if (dialog) {
            dialog.style.zIndex = '1055';
            dialog.style.pointerEvents = 'auto';
        }
        
        if (content) {
            content.style.zIndex = '1055';
            content.style.pointerEvents = 'auto';
        }
        
        // Corregir elementos interactivos
        const interactiveElements = modal.querySelectorAll(`
            .btn, .form-control, .form-select, input, textarea, .btn-close,
            button, a[role="button"], [data-bs-dismiss], [data-bs-toggle]
        `);
        
        interactiveElements.forEach(element => {
            element.style.pointerEvents = 'auto';
            element.style.zIndex = '1056';
            element.style.cursor = 'pointer';
        });
    });
    
    // Corregir partículas
    const particles = document.querySelector('.elegant-particles');
    if (particles) {
        particles.style.zIndex = '-10';
        particles.style.pointerEvents = 'none';
    }
    
    // Corregir backdrop
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
        backdrop.style.zIndex = '1050';
        backdrop.style.pointerEvents = 'auto';
    });
    
    console.log('✅ Correcciones aplicadas');
}

// Ejecutar pruebas automáticamente
console.log('🎯 Ejecutando prueba automática...');
const testResults = testModalFunctionality();

// Ofrecer opciones
console.log('\n🛠️ OPCIONES DISPONIBLES:');
console.log('- testModalFunctionality(): Ejecutar análisis completo');
console.log('- testModalOpening(): Probar apertura de todos los modales');
console.log('- applyQuickFixes(): Aplicar correcciones inmediatas');

// Si hay problemas, sugerir correcciones
if (testResults.modalsFailing.length > 0 || testResults.zIndexIssues.length > 0 || testResults.interactionIssues.length > 0) {
    console.log('\n⚠️ Se detectaron problemas. Ejecuta applyQuickFixes() para intentar corregirlos.');
}

// Exportar funciones para uso manual
window.modalTest = {
    testModalFunctionality,
    testModalOpening,
    applyQuickFixes
}; 