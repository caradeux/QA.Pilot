/**
 * jQuery Polyfill and Error Handler
 * This script ensures jQuery is available and provides backup functionality
 */

// Check if jQuery is loaded, if not provide a basic implementation
if (typeof jQuery === 'undefined') {
    console.warn('jQuery is not loaded! Using a basic polyfill for critical functions.');
    
    // Create a minimal jQuery-like function
    window.$ = window.jQuery = function(selector) {
        // Basic implementation of jQuery selector
        const elements = document.querySelectorAll(selector);
        
        // Return an object with some basic jQuery-like methods
        return {
            elements: elements,
            length: elements.length,
            
            // Basic version of jQuery's ready method
            ready: function(callback) {
                if (document.readyState === 'complete' || document.readyState === 'interactive') {
                    setTimeout(callback, 1);
                } else {
                    document.addEventListener('DOMContentLoaded', callback);
                }
                return this;
            },
            
            // Basic implementation of click
            click: function(callback) {
                this.elements.forEach(el => el.addEventListener('click', callback));
                return this;
            },
            
            // Basic implementation of change
            change: function(callback) {
                this.elements.forEach(el => el.addEventListener('change', callback));
                return this;
            },
            
            // Basic implementation of hide
            hide: function() {
                this.elements.forEach(el => el.style.display = 'none');
                return this;
            },
            
            // Basic implementation of show
            show: function() {
                this.elements.forEach(el => el.style.display = '');
                return this;
            },
            
            // Basic implementation of text
            text: function(text) {
                if (text === undefined) {
                    return this.elements.length > 0 ? this.elements[0].textContent : '';
                }
                this.elements.forEach(el => el.textContent = text);
                return this;
            },
            
            // Basic implementation of html
            html: function(html) {
                if (html === undefined) {
                    return this.elements.length > 0 ? this.elements[0].innerHTML : '';
                }
                this.elements.forEach(el => el.innerHTML = html);
                return this;
            },
            
            // Basic implementation of val
            val: function(value) {
                if (value === undefined) {
                    return this.elements.length > 0 ? this.elements[0].value : '';
                }
                this.elements.forEach(el => el.value = value);
                return this;
            }
        };
    };
    
    // Add a basic AJAX implementation
    window.$.ajax = function(options) {
        const xhr = new XMLHttpRequest();
        
        xhr.open(options.type || 'GET', options.url, true);
        
        if (options.contentType) {
            xhr.setRequestHeader('Content-Type', options.contentType);
        }
        
        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                if (options.success) {
                    let response;
                    try {
                        response = JSON.parse(xhr.responseText);
                    } catch (e) {
                        response = xhr.responseText;
                    }
                    options.success(response);
                }
            } else {
                if (options.error) {
                    options.error(xhr);
                }
            }
        };
        
        xhr.onerror = function() {
            if (options.error) {
                options.error(xhr);
            }
        };
        
        xhr.send(options.data || null);
        
        return {
            abort: function() {
                xhr.abort();
            }
        };
    };
    
    // Add a basic getJSON implementation
    window.$.getJSON = function(url, data, success) {
        if (typeof data === 'function') {
            success = data;
            data = null;
        }
        
        return window.$.ajax({
            url: url,
            type: 'GET',
            data: data,
            success: success,
            error: function(xhr) {
                console.error('Error in getJSON:', xhr);
            }
        });
    };
    
    console.log('jQuery polyfill loaded successfully');
} else {
    console.log('jQuery is already loaded:', jQuery.fn.jquery);
}

// Add an error handler for jQuery operations
window.handleJQueryError = function(error) {
    console.error('jQuery error:', error);
    alert('Se ha producido un error en la interfaz. Por favor, recarga la página.');
};

// Add a global error handler
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    if (event.error && event.error.toString().includes('$')) {
        console.warn('Possible jQuery error detected, attempting to recover...');
        // Check to see if jQuery exists now (it might have loaded after the error)
        if (typeof jQuery !== 'undefined') {
            console.log('jQuery is now available, retrying operation');
            if (location.reload) {
                // Reload the page if the error is jQuery-related
                location.reload();
            }
        }
    }
});

console.log('jQuery error handler installed'); 