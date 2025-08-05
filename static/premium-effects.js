// Efectos Premium para QA-Pilot
document.addEventListener('DOMContentLoaded', function() {
    
    // Aplicar animaciones de entrada ultra elegantes
    function applyEntranceAnimations() {
        const cards = document.querySelectorAll('.card, .tech-panel, .accordion-item');
        const buttons = document.querySelectorAll('.btn');
        
        // Animación de entrada elegante para cards
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(50px) scale(0.9)';
            card.style.filter = 'blur(10px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.8s cubic-bezier(0.23, 1, 0.32, 1)';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0) scale(1)';
                card.style.filter = 'blur(0)';
                
                // Agregar clase para efectos adicionales
                card.classList.add('elegant-entrance');
            }, index * 150);
        });
        
        // Agregar efectos premium a botones
        buttons.forEach(button => {
            button.classList.add('ripple-effect', 'elegant-hover');
        });
    }
    
    // Efecto de ondas en clicks
    function addRippleEffect() {
        document.addEventListener('click', function(e) {
            const target = e.target.closest('.ripple-effect');
            if (!target) return;
            
            const rect = target.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            const ripple = document.createElement('div');
            ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.3);
                transform: scale(0);
                animation: ripple 0.6s linear;
                left: ${x}px;
                top: ${y}px;
                width: ${size}px;
                height: ${size}px;
                pointer-events: none;
                z-index: 1060;
            `;
            
            target.style.position = 'relative';
            target.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
        
        // Agregar keyframes para ripple
        const style = document.createElement('style');
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Efecto parallax suave para el fondo
    function addParallaxEffect() {
        let ticking = false;
        
        function updateParallax() {
            const scrolled = window.pageYOffset;
            const parallaxElements = document.querySelectorAll('.tech-header, .tech-panel');
            
            parallaxElements.forEach((element, index) => {
                const speed = 0.5 + (index * 0.1);
                const yPos = -(scrolled * speed);
                element.style.transform = `translateY(${yPos}px)`;
            });
            
            ticking = false;
        }
        
        function requestTick() {
            if (!ticking) {
                requestAnimationFrame(updateParallax);
                ticking = true;
            }
        }
        
        window.addEventListener('scroll', requestTick);
    }
    
    // Efecto de hover ultra elegante para elementos interactivos
    function enhanceHoverEffects() {
        const interactiveElements = document.querySelectorAll('.card, .btn, .tech-panel, .accordion-item');
        
        interactiveElements.forEach(element => {
            element.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-8px) scale(1.03)';
                this.style.transition = 'all 0.4s cubic-bezier(0.23, 1, 0.32, 1)';
                this.style.filter = 'brightness(1.1) saturate(1.2)';
                this.style.boxShadow = '0 25px 60px rgba(0, 0, 0, 0.4), 0 0 40px rgba(37, 99, 235, 0.3)';
            });
            
            element.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
                this.style.filter = 'brightness(1) saturate(1)';
                this.style.boxShadow = '';
            });
        });
    }
    
    // Efecto de typing para textos importantes
    function addTypingEffect() {
        const typingElements = document.querySelectorAll('.tech-title, h1, h2');
        
        typingElements.forEach(element => {
            const text = element.textContent;
            element.textContent = '';
            element.style.borderRight = '2px solid rgba(0, 212, 255, 0.7)';
            element.style.animation = 'blink 1s infinite';
            
            let i = 0;
            const typeWriter = () => {
                if (i < text.length) {
                    element.textContent += text.charAt(i);
                    i++;
                    setTimeout(typeWriter, 50);
                } else {
                    element.style.borderRight = 'none';
                    element.style.animation = 'none';
                }
            };
            
            setTimeout(typeWriter, 500);
        });
        
        // Agregar keyframes para blink
        const style = document.createElement('style');
        style.textContent = `
            @keyframes blink {
                0%, 50% { border-color: rgba(0, 212, 255, 0.7); }
                51%, 100% { border-color: transparent; }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Contador animado para números
    function animateNumbers() {
        const numberElements = document.querySelectorAll('.stats-number, .badge');
        
        numberElements.forEach(element => {
            const finalNumber = parseInt(element.textContent) || 0;
            if (finalNumber === 0) return;
            
            let currentNumber = 0;
            const increment = finalNumber / 50;
            
            const timer = setInterval(() => {
                currentNumber += increment;
                if (currentNumber >= finalNumber) {
                    element.textContent = finalNumber;
                    clearInterval(timer);
                } else {
                    element.textContent = Math.floor(currentNumber);
                }
            }, 30);
        });
    }
    
    // Efecto de carga premium
    function showPremiumLoader() {
        const loader = document.createElement('div');
        loader.className = 'premium-loader-overlay';
        loader.innerHTML = `
            <div class="premium-loader">
                <div class="premium-loader-text">Cargando...</div>
            </div>
        `;
        
        loader.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(26, 26, 26, 0.95);
            backdrop-filter: blur(10px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1070;
            opacity: 1;
            transition: opacity 0.5s ease;
        `;
        
        const loaderText = loader.querySelector('.premium-loader-text');
        loaderText.style.cssText = `
            color: #ffffff;
            font-size: 1.2rem;
            margin-top: 2rem;
            text-align: center;
            animation: textGlow 2s ease-in-out infinite alternate;
        `;
        
        document.body.appendChild(loader);
        
        setTimeout(() => {
            loader.style.opacity = '0';
            setTimeout(() => {
                loader.remove();
            }, 500);
        }, 2000);
    }
    
    // Efecto de partículas elegantes
    function createElegantParticles() {
        const particleContainer = document.createElement('div');
        particleContainer.className = 'elegant-particles';
        particleContainer.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            overflow: hidden;
        `;
        
        document.body.appendChild(particleContainer);
        
        // Crear partículas elegantes
        for (let i = 0; i < 12; i++) {
            const particle = document.createElement('div');
            particle.style.cssText = `
                position: absolute;
                width: ${Math.random() * 3 + 1}px;
                height: ${Math.random() * 3 + 1}px;
                background: radial-gradient(circle, rgba(37, 99, 235, 0.4), rgba(16, 185, 129, 0.2));
                border-radius: 50%;
                animation: elegantFloat ${Math.random() * 25 + 20}s linear infinite;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                filter: blur(0.5px);
                box-shadow: 0 0 15px rgba(37, 99, 235, 0.2);
            `;
            
            particleContainer.appendChild(particle);
        }
        
        // Agregar keyframes para partículas elegantes
        const style = document.createElement('style');
        style.textContent = `
            @keyframes elegantFloat {
                0% {
                    transform: translateY(0px) rotate(0deg) scale(0);
                    opacity: 0;
                }
                10% {
                    opacity: 1;
                    transform: scale(1);
                }
                90% {
                    opacity: 1;
                }
                100% {
                    transform: translateY(-100vh) rotate(360deg) scale(0);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Funcionalidad elegante para sliders
    function enhanceSliders() {
        const sliders = document.querySelectorAll('input[type="range"]');
        
        sliders.forEach(slider => {
            // Crear tooltip elegante
            const tooltip = document.createElement('div');
            tooltip.className = 'slider-tooltip';
            tooltip.style.cssText = `
                position: absolute;
                background: var(--tech-gradient-primary);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 1rem;
                font-size: 0.875rem;
                font-weight: 600;
                pointer-events: none;
                opacity: 0;
                transform: translateX(-50%) translateY(-150%);
                transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
                box-shadow: var(--tech-shadow-elegant);
                                 z-index: 1060;
                 white-space: nowrap;
            `;
            
            // Posicionar tooltip
            slider.parentElement.style.position = 'relative';
            slider.parentElement.appendChild(tooltip);
            
            // Función para actualizar valor y posición
            function updateSlider() {
                const value = slider.value;
                const min = slider.min || 0;
                const max = slider.max || 100;
                const percentage = ((value - min) / (max - min)) * 100;
                
                // Actualizar tooltip
                let displayValue = value;
                if (slider.id.includes('time') || slider.id.includes('timeout')) {
                    displayValue = `${value} seg`;
                } else if (slider.id.includes('concurrent')) {
                    displayValue = `${value} prueba${value > 1 ? 's' : ''}`;
                }
                
                tooltip.textContent = displayValue;
                tooltip.style.left = `${percentage}%`;
                
                // Actualizar elementos relacionados
                const valueElement = document.getElementById(slider.id.replace('_', '-') + '-value') ||
                                   document.getElementById('tiempo-value') ||
                                   document.getElementById('timeout-value') ||
                                   document.getElementById('concurrentValue');
                
                if (valueElement) {
                    if (slider.id.includes('concurrent')) {
                        valueElement.textContent = `${value} prueba${value > 1 ? 's' : ''}`;
                    } else {
                        valueElement.textContent = value;
                    }
                }
                
                // Efecto de glow en el slider
                slider.style.boxShadow = `0 0 20px rgba(37, 99, 235, ${percentage / 100 * 0.5})`;
            }
            
                         // Eventos del slider
            slider.addEventListener('input', updateSlider);
            
            slider.addEventListener('mouseenter', () => {
                tooltip.style.opacity = '1';
                tooltip.style.transform = 'translateX(-50%) translateY(-150%) scale(1.05)';
                slider.style.transform = 'scale(1.02)';
                
                // Efecto de vibración sutil
                slider.style.animation = 'sliderHover 0.3s ease-out';
            });
            
            slider.addEventListener('mouseleave', () => {
                tooltip.style.opacity = '0';
                tooltip.style.transform = 'translateX(-50%) translateY(-150%) scale(1)';
                slider.style.transform = 'scale(1)';
                slider.style.animation = '';
            });
            
            slider.addEventListener('focus', () => {
                tooltip.style.opacity = '1';
                slider.style.outline = 'none';
                slider.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.3)';
            });
            
            slider.addEventListener('blur', () => {
                tooltip.style.opacity = '0';
                slider.style.boxShadow = '';
            });
            
            // Efecto de cambio de valor
            slider.addEventListener('change', () => {
                // Guardar valor en localStorage
                localStorage.setItem(`slider_${slider.id}`, slider.value);
                
                // Efecto de confirmación
                tooltip.style.background = 'var(--tech-gradient-accent)';
                tooltip.style.transform = 'translateX(-50%) translateY(-150%) scale(1.1)';
                
                setTimeout(() => {
                    tooltip.style.background = 'var(--tech-gradient-primary)';
                    tooltip.style.transform = 'translateX(-50%) translateY(-150%) scale(1)';
                }, 300);
                
                // Vibración en dispositivos móviles
                if (navigator.vibrate) {
                    navigator.vibrate(50);
                }
            });
            
            // Restaurar valor guardado
            const savedValue = localStorage.getItem(`slider_${slider.id}`);
            if (savedValue && savedValue !== slider.value) {
                slider.value = savedValue;
                updateSlider();
            }
            
            // Inicializar valor
            updateSlider();
        });
        
        // Agregar keyframes para animaciones de slider
        const sliderStyle = document.createElement('style');
        sliderStyle.textContent = `
            @keyframes sliderGlow {
                0%, 100% { filter: brightness(1) saturate(1); }
                50% { filter: brightness(1.2) saturate(1.3); }
            }
            
            @keyframes tooltipBounce {
                0%, 100% { transform: translateX(-50%) translateY(-150%) scale(1); }
                50% { transform: translateX(-50%) translateY(-160%) scale(1.1); }
            }
        `;
        document.head.appendChild(sliderStyle);
    }
    
    // Función para sincronizar sliders con el servidor
    function syncSlidersWithServer() {
        const sliders = document.querySelectorAll('input[type="range"]');
        const sliderData = {};
        
        sliders.forEach(slider => {
            sliderData[slider.id] = {
                value: slider.value,
                min: slider.min,
                max: slider.max,
                step: slider.step
            };
        });
        
        // Enviar datos al servidor (opcional)
        if (window.location.pathname.includes('config')) {
            console.log('📊 Configuración de sliders:', sliderData);
            
            // Aquí se podría hacer una llamada AJAX para guardar la configuración
            // fetch('/api/save-slider-config', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify(sliderData)
            // });
        }
    }
    
    // Función para manejar modales correctamente - VERSIÓN MEJORADA
    function fixModalZIndex() {
        console.log('🔧 Inicializando corrección de z-index para modales...');
        
        // Función para aplicar correcciones inmediatas
        function applyModalFixes(modal) {
            if (!modal) return;
            
            // Aplicar z-index y pointer-events inmediatamente
            modal.style.zIndex = '1055';
            modal.style.pointerEvents = 'auto';
            
            // Asegurar que el dialog y content sean interactivos
            const dialog = modal.querySelector('.modal-dialog');
            const content = modal.querySelector('.modal-content');
            
            if (dialog) {
                dialog.style.zIndex = '1055';
                dialog.style.pointerEvents = 'auto';
                dialog.style.position = 'relative';
            }
            
            if (content) {
                content.style.zIndex = '1055';
                content.style.pointerEvents = 'auto';
                content.style.position = 'relative';
            }
            
            // Asegurar que todos los elementos interactivos funcionen
            const interactiveElements = modal.querySelectorAll(`
                .btn, .form-control, .form-select, input, textarea, .btn-close,
                .dropdown-toggle, .nav-link, .accordion-button, .carousel-control-prev,
                .carousel-control-next, .close, button, a[role="button"],
                [data-bs-dismiss], [data-bs-toggle]
            `);
            
            interactiveElements.forEach(element => {
                element.style.pointerEvents = 'auto';
                element.style.position = 'relative';
                element.style.zIndex = '1056';
                element.style.cursor = 'pointer';
            });
            
            // Manejar backdrop
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.style.zIndex = '1050';
                backdrop.style.pointerEvents = 'auto';
            }
            
            // Reducir interferencia de efectos de fondo
            const particles = document.querySelector('.elegant-particles');
            if (particles) {
                particles.style.zIndex = '-10';
                particles.style.pointerEvents = 'none';
                particles.style.opacity = '0.1';
            }
            
            // Ocultar loader si está activo
            const loader = document.querySelector('.premium-loader-overlay');
            if (loader) {
                loader.style.display = 'none';
            }
            
            // Desactivar backdrop-filter en elementos que puedan interferir
            const elementsWithBackdrop = document.querySelectorAll('[style*="backdrop-filter"]:not(.modal):not(.modal *)');
            elementsWithBackdrop.forEach(element => {
                if (!element.closest('.modal')) {
                    element.style.pointerEvents = 'none';
                }
            });
        }
        
        // Función para restaurar efectos al cerrar modal
        function restoreEffects() {
            const particles = document.querySelector('.elegant-particles');
            if (particles) {
                particles.style.opacity = '1';
            }
            
            // Restaurar pointer-events de elementos con backdrop-filter
            const elementsWithBackdrop = document.querySelectorAll('[style*="backdrop-filter"]:not(.modal):not(.modal *)');
            elementsWithBackdrop.forEach(element => {
                element.style.pointerEvents = '';
            });
        }
        
        // Observador de mutaciones mejorado
        const modalObserver = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    const target = mutation.target;
                    
                    // Modal se está abriendo
                    if (target.classList.contains('modal') && target.classList.contains('show')) {
                        console.log('📖 Modal detectado abriéndose:', target.id);
                        applyModalFixes(target);
                    }
                    
                    // Modal se está cerrando
                    if (target.classList.contains('modal') && !target.classList.contains('show')) {
                        console.log('📕 Modal detectado cerrándose:', target.id);
                        // Pequeño delay para asegurar que el modal se ha cerrado completamente
                        setTimeout(restoreEffects, 100);
                    }
                }
                
                // Detectar nuevos modales añadidos al DOM
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === 1) { // Element node
                            if (node.classList && node.classList.contains('modal')) {
                                console.log('🆕 Nuevo modal detectado:', node.id);
                                // Observar el nuevo modal
                                modalObserver.observe(node, {
                                    attributes: true,
                                    attributeFilter: ['class']
                                });
                            }
                            
                            // Buscar modales dentro del nodo añadido
                            const modalsInNode = node.querySelectorAll && node.querySelectorAll('.modal');
                            if (modalsInNode) {
                                modalsInNode.forEach(modal => {
                                    console.log('🆕 Modal encontrado en nodo añadido:', modal.id);
                                    modalObserver.observe(modal, {
                                        attributes: true,
                                        attributeFilter: ['class']
                                    });
                                });
                            }
                        }
                    });
                }
            });
        });
        
        // Observar todos los modales existentes
        const existingModals = document.querySelectorAll('.modal');
        existingModals.forEach(modal => {
            console.log('👁️ Observando modal existente:', modal.id);
            modalObserver.observe(modal, {
                attributes: true,
                attributeFilter: ['class']
            });
        });
        
        // Observar el body para nuevos modales
        modalObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Aplicar correcciones a modales ya abiertos
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            console.log('🔄 Aplicando correcciones a modal ya abierto:', modal.id);
            applyModalFixes(modal);
        });
    }
    
    // Inicializar todos los efectos ultra elegantes
    function initPremiumEffects() {
        showPremiumLoader();
        
        setTimeout(() => {
            applyEntranceAnimations();
            addRippleEffect();
            enhanceHoverEffects();
            animateNumbers();
            createElegantParticles();
            enhanceSliders();
            syncSlidersWithServer();
            fixModalZIndex();
            
            console.log('✨ Efectos Ultra Elegantes QA-Pilot activados');
        }, 2500);
    }
    
    // Función mejorada para manejar eventos de Bootstrap
    function handleBootstrapEvents() {
        console.log('🎯 Configurando eventos de Bootstrap para modales...');
        
        // Evento antes de mostrar modal
        document.addEventListener('show.bs.modal', function(event) {
            const modal = event.target;
            console.log('🎬 Bootstrap show.bs.modal:', modal.id);
            
            // Aplicar correcciones inmediatamente
            modal.style.zIndex = '1055';
            modal.style.pointerEvents = 'auto';
            
            // Asegurar backdrop
            setTimeout(() => {
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.style.zIndex = '1050';
                    backdrop.style.pointerEvents = 'auto';
                }
            }, 10);
        });
        
        // Evento cuando el modal se ha mostrado completamente
        document.addEventListener('shown.bs.modal', function(event) {
            const modal = event.target;
            console.log('✅ Bootstrap shown.bs.modal:', modal.id);
            
            // Aplicar todas las correcciones
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
            
            // Asegurar elementos interactivos
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
        
        // Evento cuando se oculta el modal
        document.addEventListener('hidden.bs.modal', function(event) {
            const modal = event.target;
            console.log('🎭 Bootstrap hidden.bs.modal:', modal.id);
            
            // Restaurar efectos
            const particles = document.querySelector('.elegant-particles');
            if (particles) {
                particles.style.opacity = '1';
            }
        });
        
        // Evento para tooltips
        document.addEventListener('show.bs.tooltip', function(event) {
            setTimeout(() => {
                const tooltipElement = document.querySelector('.tooltip');
                if (tooltipElement) {
                    tooltipElement.style.zIndex = '1060';
                    tooltipElement.style.pointerEvents = 'auto';
                }
            }, 10);
        });
        
        // Manejar clics en backdrop para cerrar modales
        document.addEventListener('click', function(event) {
            if (event.target.classList.contains('modal-backdrop')) {
                console.log('🖱️ Click en backdrop detectado');
                // El comportamiento por defecto de Bootstrap debería manejar esto
            }
        });
    }
    
    // Inicializar
    initPremiumEffects();
    
    // Manejar eventos de Bootstrap
    handleBootstrapEvents();
    
    // Reinicializar en cambios de página (para SPAs)
    window.addEventListener('popstate', () => {
        initPremiumEffects();
        handleBootstrapEvents();
    });
}); 