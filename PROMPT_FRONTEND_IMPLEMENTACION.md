# Prompt de Implementación Frontend - Inovabiz QA Pilot

## 🎨 Guía de Diseño y Estilos

### **Concepto Visual**
Implementar una interfaz moderna y profesional para una herramienta de automatización de pruebas QA con un enfoque tecnológico y empresarial. El diseño debe transmitir confianza, eficiencia y sofisticación técnica.

---

## 🎯 **Paleta de Colores Principal**

### **Colores Base**
```css
/* Azul Tecnológico Principal */
--tech-primary: #2563eb;           /* Azul principal */
--tech-primary-dark: #1d4ed8;      /* Azul oscuro */
--tech-primary-light: #3b82f6;     /* Azul claro */
--tech-primary-glow: rgba(37, 99, 235, 0.4); /* Efecto glow */

/* Verde de Éxito */
--tech-accent: #10b981;            /* Verde principal */
--tech-accent-dark: #059669;       /* Verde oscuro */
--tech-accent-glow: rgba(16, 185, 129, 0.3); /* Efecto glow */

/* Escala de Grises Elegante */
--tech-dark: #0f172a;              /* Fondo principal oscuro */
--tech-dark-light: #1e293b;        /* Fondo secundario */
--tech-dark-lighter: #334155;      /* Elementos elevados */
--tech-light: #ffffff;             /* Texto claro */
--tech-light-dark: #f8fafc;        /* Fondo claro */
--tech-light-darker: #e2e8f0;      /* Bordes claros */
```

### **Colores de Estado**
```css
--tech-success: #22c55e;           /* Éxito */
--tech-warning: #f59e0b;           /* Advertencia */
--tech-danger: #ef4444;            /* Error */
--tech-info: #3b82f6;              /* Información */
```

---

## 🔤 **Tipografía**

### **Fuentes Principales**
- **Poppins**: Títulos y elementos principales (600-800 weight)
- **Inter**: Texto del cuerpo y elementos secundarios (400-600 weight)
- **JetBrains Mono**: Código y elementos técnicos (400-600 weight)

### **Jerarquía Tipográfica**
```css
h1, h2, h3, h4, h5, h6 {
    font-family: 'Poppins', 'Inter', sans-serif;
    font-weight: 600;
    letter-spacing: -0.025em;
}

body, p, .btn, .form-control {
    font-family: 'Poppins', 'Inter', sans-serif;
    font-weight: 400;
    line-height: 1.6;
}

code, pre, .tech-terminal {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
}
```

---

## 🏗️ **Estructura de Componentes**

### **1. Header Corporativo**
- **Posición**: Fijo en la parte superior
- **Fondo**: Glassmorphism con blur y transparencia
- **Logo**: Icono de robot con animación flotante
- **Navegación**: Menú horizontal con efectos hover
- **Efectos**: Backdrop filter y bordes sutiles

### **2. Paneles de Contenido**
- **Fondo**: Gradiente sutil con overlay corporativo
- **Bordes**: Redondeados con sombras elegantes
- **Hover**: Transformación suave y efectos de elevación
- **Contenido**: Padding generoso y espaciado consistente

### **3. Formularios**
- **Inputs**: Bordes redondeados con estados de focus
- **Labels**: Iconos integrados con efectos glow
- **Validación**: Estados visuales claros (éxito/error)
- **Placeholders**: Texto descriptivo y útil

### **4. Botones**
- **Estilo**: Gradientes con efectos de profundidad
- **Estados**: Hover, active, disabled claramente diferenciados
- **Iconos**: Font Awesome integrado
- **Animaciones**: Transiciones suaves y efectos ripple

---

## ✨ **Efectos Visuales**

### **Animaciones Principales**
```css
/* Fade In */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Logo Flotante */
@keyframes logoFloat {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-5px); }
}

/* Glow Effect */
@keyframes logoGlow {
    0%, 100% { filter: drop-shadow(0 0 5px var(--tech-primary-glow)); }
    50% { filter: drop-shadow(0 0 15px var(--tech-primary-glow)); }
}
```

### **Efectos de Interacción**
- **Hover**: Transformaciones suaves y cambios de color
- **Focus**: Outlines con colores de marca
- **Active**: Efectos de presión y feedback visual
- **Loading**: Spinners y animaciones de carga

---

## 📱 **Responsive Design**

### **Breakpoints**
```css
/* Mobile First */
@media (max-width: 767.98px) {
    /* Ajustes para móviles */
}

@media (min-width: 768px) and (max-width: 991.98px) {
    /* Ajustes para tablets */
}

@media (min-width: 992px) {
    /* Ajustes para desktop */
}
```

### **Adaptaciones Móviles**
- **Navegación**: Menú hamburguesa con overlay
- **Formularios**: Campos apilados verticalmente
- **Botones**: Tamaños táctiles apropiados
- **Contenido**: Scroll horizontal en tablas

---

## 🎭 **Estados de Interfaz**

### **Estados de Carga**
- **Spinners**: Animaciones circulares con colores de marca
- **Skeletons**: Placeholders animados para contenido
- **Progress bars**: Barras de progreso con gradientes

### **Estados de Éxito/Error**
- **Alertas**: Banners con iconos y colores apropiados
- **Notificaciones**: Toasts con animaciones de entrada/salida
- **Validación**: Feedback inmediato en formularios

### **Estados Vacíos**
- **Ilustraciones**: Iconos descriptivos
- **Mensajes**: Texto motivacional y orientativo
- **Acciones**: Botones de call-to-action claros

---

## 🔧 **Componentes Específicos**

### **Tarjetas de Test**
```css
.tech-card {
    background: linear-gradient(135deg, var(--tech-dark-light), var(--tech-dark-lighter));
    border: 1px solid var(--tech-border);
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.3s ease;
}

.tech-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
    border-color: var(--tech-primary);
}
```

### **Terminal de Logs**
```css
.tech-terminal {
    background: var(--tech-dark);
    border: 1px solid var(--tech-border);
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
    padding: 1rem;
    max-height: 400px;
    overflow-y: auto;
}
```

### **Modales**
```css
.modal-content {
    background: linear-gradient(135deg, var(--tech-dark-light), var(--tech-dark-lighter));
    border: 1px solid var(--tech-border);
    border-radius: 16px;
    backdrop-filter: blur(20px);
}
```

---

## 🎨 **Elementos Decorativos**

### **Partículas de Fondo**
- **Efecto**: Partículas flotantes sutiles
- **Color**: Variaciones de azul y verde
- **Movimiento**: Animación lenta y relajante
- **Opacidad**: Muy baja para no distraer

### **Gradientes**
- **Fondos**: Gradientes radiales y lineales sutiles
- **Botones**: Gradientes con dirección 135deg
- **Cards**: Gradientes con transparencias

### **Sombras**
- **Profundidad**: Múltiples capas de sombra
- **Color**: Sombras con color de marca
- **Difuminado**: Valores altos para suavidad

---

## 🚀 **Optimizaciones de Performance**

### **Animaciones**
- **Hardware Acceleration**: Usar transform y opacity
- **Reducir Repaints**: Minimizar cambios de layout
- **Debounce**: Para eventos de scroll y resize

### **Imágenes**
- **Formatos**: WebP con fallbacks
- **Lazy Loading**: Para imágenes pesadas
- **Optimización**: Compresión y tamaños apropiados

---

## 📋 **Checklist de Implementación**

### **Estructura Base**
- [ ] Configurar variables CSS
- [ ] Implementar tipografías
- [ ] Crear sistema de grid
- [ ] Configurar breakpoints

### **Componentes Core**
- [ ] Header con navegación
- [ ] Sistema de paneles
- [ ] Formularios y inputs
- [ ] Botones y CTAs
- [ ] Modales y overlays

### **Estados y Feedback**
- [ ] Estados de carga
- [ ] Mensajes de error/éxito
- [ ] Validación de formularios
- [ ] Notificaciones

### **Responsive**
- [ ] Mobile navigation
- [ ] Tablet adaptations
- [ ] Desktop optimizations
- [ ] Touch interactions

### **Performance**
- [ ] Optimizar animaciones
- [ ] Lazy loading
- [ ] Minificación CSS
- [ ] Testing cross-browser

---

## 🎯 **Objetivos de UX**

1. **Claridad**: Información organizada y fácil de encontrar
2. **Eficiencia**: Flujos de trabajo optimizados
3. **Confianza**: Feedback visual constante
4. **Accesibilidad**: Cumplir estándares WCAG
5. **Consistencia**: Patrones de diseño unificados

---

## 🔍 **Consideraciones Técnicas**

- **Compatibilidad**: IE11+, Chrome, Firefox, Safari, Edge
- **Accesibilidad**: ARIA labels, keyboard navigation
- **SEO**: Meta tags, structured data
- **Analytics**: Event tracking para interacciones clave

---

*Este prompt debe servir como guía completa para implementar el frontend del proyecto Inovabiz QA Pilot, manteniendo la coherencia visual y la experiencia de usuario profesional.* 