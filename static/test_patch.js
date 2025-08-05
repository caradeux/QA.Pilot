/**
 * Test Monitoring Patch
 * This script patches the existing test monitoring code in the UI
 */

(function() {
    console.log("Test Patch loaded - patching monitoring functionality");
    
    // Function to intercept the testform submit event
    function patchTestForm() {
        // Try different potential selectors for the test form
        const testForm = 
            document.getElementById('testForm') || 
            document.querySelector('form[action="/run_test"]') ||
            document.querySelector('form');
        
        if (!testForm) {
            console.warn("Test form not found, cannot patch");
            
            // Add manual monitoring for any test that starts
            setupGlobalMonitoring();
            return false;
        }
        
        console.log("Patching test form with ID:", testForm.id || "(no id)");
        
        // Preserve the original submit handler
        const originalSubmit = testForm.onsubmit;
        
        testForm.onsubmit = function(event) {
            // Try to call the original handler if it exists
            let originalResult = true;
            if (typeof originalSubmit === 'function') {
                originalResult = originalSubmit.call(this, event);
            }
            
            // If the original handler returns false, respect that
            if (originalResult === false) {
                return false;
            }
            
            // Prevent the default form submission
            event.preventDefault();
            
            console.log("Patched test form submission");
            
            // Create a FormData object from the form
            const formData = new FormData(testForm);
            
            // Show loading indicator
            const loadingIndicator = document.getElementById('loadingIndicator') || document.querySelector('.loading-indicator');
            if (loadingIndicator) loadingIndicator.style.display = 'block';
            
            const testResults = document.getElementById('testResults') || document.querySelector('.test-results');
            if (testResults) testResults.style.display = 'none';
            
            const errorMessage = document.getElementById('errorMessage') || document.querySelector('.error-message');
            if (errorMessage) errorMessage.style.display = 'none';
            
            // Submit form with fetch
            fetch('/run_test', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Test started:", data);
                
                if (data.status === 'success') {
                    // Update UI to show test started
                    const statusMessage = document.getElementById('statusMessage') || document.querySelector('.status-message');
                    if (statusMessage) {
                        statusMessage.textContent = data.message;
                        statusMessage.style.display = 'block';
                    }
                    
                    // Initialize monitoring with our helper
                    TestMonitor.init(data.task_id, handleTestStatusUpdate);
                } else {
                    // Show error
                    if (errorMessage) {
                        errorMessage.textContent = data.message || 'Error starting test';
                        errorMessage.style.display = 'block';
                    }
                    if (loadingIndicator) loadingIndicator.style.display = 'none';
                }
            })
            .catch(error => {
                console.error("Error starting test:", error);
                if (errorMessage) {
                    errorMessage.textContent = `Error: ${error.message}`;
                    errorMessage.style.display = 'block';
                }
                if (loadingIndicator) loadingIndicator.style.display = 'none';
            });
            
            // Prevent default form submission
            return false;
        };
        
        return true;
    }
    
    // Function to set up global monitoring for test start events
    function setupGlobalMonitoring() {
        console.log("Setting up global monitoring for test starts");
        
        // Create a MutationObserver to watch for changes to the DOM
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                // Look for success message elements that might indicate a test has started
                const successElements = document.querySelectorAll('.alert-success, .success-message');
                
                for (const elem of successElements) {
                    if (elem.textContent.includes('Test started successfully')) {
                        // Try to extract task ID from page or from URL parameters
                        let taskId = null;
                        
                        // Try from URL
                        const urlParams = new URLSearchParams(window.location.search);
                        taskId = urlParams.get('task_id');
                        
                        // If not found, try to find it in the page text
                        if (!taskId) {
                            const pageText = document.body.textContent;
                            const taskMatch = pageText.match(/task[_\s]?id[:\s]+([a-zA-Z0-9_]+)/i);
                            if (taskMatch && taskMatch[1]) {
                                taskId = taskMatch[1];
                            }
                        }
                        
                        // If we found a task ID, start monitoring
                        if (taskId) {
                            console.log("Found test start indicator with task ID:", taskId);
                            TestMonitor.init(taskId, handleTestStatusUpdate);
                            
                            // Stop observing once we've found and handled a test start
                            observer.disconnect();
                        }
                    }
                }
            });
        });
        
        // Start observing the document with the configured parameters
        observer.observe(document.body, { childList: true, subtree: true });
    }
    
    // Function to handle test status updates
    function handleTestStatusUpdate(data) {
        console.log("Status update received:", data);
        
        // Update progress indicator if available
        const progressElement = document.getElementById('testProgress') || document.querySelector('.test-progress');
        if (progressElement && typeof data.progress === 'number') {
            if (progressElement.tagName === 'PROGRESS') {
                progressElement.value = data.progress;
            }
            progressElement.textContent = `${data.progress}%`;
        }
        
        // Update status message
        const statusElement = document.getElementById('statusMessage') || document.querySelector('.status-message');
        if (statusElement && data.message) {
            statusElement.textContent = data.message;
        }
        
        // Handle completed tests
        if (data.status === 'completed') {
            const loadingIndicator = document.getElementById('loadingIndicator') || document.querySelector('.loading-indicator');
            if (loadingIndicator) loadingIndicator.style.display = 'none';
            
            // Show results section
            const resultsElement = document.getElementById('testResults') || document.querySelector('.test-results');
            if (resultsElement) {
                resultsElement.style.display = 'block';
                
                // Try to update results UI based on existing structure
                if (data.results && data.results.screenshots) {
                    // Find screenshots container
                    const screenshotsContainer = document.querySelector('.screenshots-container') || 
                                              document.querySelector('.screenshots') ||
                                              document.querySelector('.test-screenshots');
                    if (screenshotsContainer) {
                        updateScreenshots(screenshotsContainer, data.results.screenshots);
                    }
                }
                
                // Update steps if available
                if (data.results && data.results.steps) {
                    const stepsContainer = document.querySelector('.steps-container') || 
                                        document.querySelector('.steps') ||
                                        document.querySelector('.test-steps');
                    if (stepsContainer) {
                        updateSteps(stepsContainer, data.results.steps);
                    }
                }
            }
        }
        
        // Handle errors
        if (data.status === 'error') {
            const loadingIndicator = document.getElementById('loadingIndicator') || document.querySelector('.loading-indicator');
            if (loadingIndicator) loadingIndicator.style.display = 'none';
            
            const errorMessage = document.getElementById('errorMessage') || document.querySelector('.error-message');
            if (errorMessage) {
                errorMessage.textContent = data.message || 'Error during test execution';
                errorMessage.style.display = 'block';
            }
        }
    }
    
    // Helper function to update screenshots
    function updateScreenshots(container, screenshots) {
        if (!Array.isArray(screenshots) || screenshots.length === 0) {
            return;
        }
        
        // Clear existing content
        container.innerHTML = '';
        
        // Add each screenshot
        screenshots.forEach((screenshot, index) => {
            const card = document.createElement('div');
            card.className = 'screenshot-card';
            card.innerHTML = `
                <div class="screenshot-header">
                    <h5>${screenshot.name || `Screenshot ${index + 1}`}</h5>
                    <div class="screenshot-timestamp">${screenshot.timestamp || ''}</div>
                </div>
                <div class="screenshot-image">
                    <img src="${screenshot.url}" alt="${screenshot.name || `Screenshot ${index + 1}`}" class="img-fluid">
                </div>
            `;
            container.appendChild(card);
        });
    }
    
    // Helper function to update steps
    function updateSteps(container, steps) {
        if (!Array.isArray(steps) || steps.length === 0) {
            return;
        }
        
        // Clear existing content
        container.innerHTML = '';
        
        // Add each step
        steps.forEach((step, index) => {
            const stepItem = document.createElement('div');
            stepItem.className = `step-item step-${step.status}`;
            stepItem.innerHTML = `
                <div class="step-number">${index + 1}</div>
                <div class="step-content">
                    <div class="step-action">${step.action}</div>
                    <div class="step-details">${step.details}</div>
                    <div class="step-duration">${step.duration}s</div>
                </div>
            `;
            container.appendChild(stepItem);
        });
    }
    
    // Intercept XHR for global monitoring
    function interceptXHR() {
        const origOpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function() {
            this.addEventListener('load', function() {
                // Check if this is a response from the run_test endpoint
                if (this.responseURL.includes('/run_test')) {
                    try {
                        const data = JSON.parse(this.responseText);
                        if (data.status === 'success' && data.task_id) {
                            console.log("Intercepted successful test start with task_id:", data.task_id);
                            TestMonitor.init(data.task_id, handleTestStatusUpdate);
                        }
                    } catch (e) {
                        console.error("Error parsing intercepted response:", e);
                    }
                }
            });
            origOpen.apply(this, arguments);
        };
    }
    
    // Wait for document to be ready
    function init() {
        console.log("Initializing test patch");
        
        // Patch test form submission
        const formPatched = patchTestForm();
        
        // If form patching failed, intercept XHR as a fallback
        if (!formPatched) {
            interceptXHR();
        }
        
        // Add a listener for the test started event
        window.addEventListener('test-started', function(e) {
            console.log("Test started event received:", e.detail);
            if (e.detail && e.detail.task_id) {
                TestMonitor.init(e.detail.task_id, handleTestStatusUpdate);
            }
        });
        
        // Intercept fetch API calls
        const originalFetch = window.fetch;
        window.fetch = function() {
            const url = arguments[0];
            const promise = originalFetch.apply(this, arguments);
            
            // If this is a call to run_test, intercept the response
            if (typeof url === 'string' && url.includes('/run_test')) {
                return promise.then(response => {
                    // Clone the response so we can read it and still return the original
                    const clone = response.clone();
                    
                    clone.json().then(data => {
                        if (data.status === 'success' && data.task_id) {
                            console.log("Intercepted fetch to run_test with task_id:", data.task_id);
                            TestMonitor.init(data.task_id, handleTestStatusUpdate);
                        }
                    }).catch(e => {
                        console.error("Error parsing fetch response:", e);
                    });
                    
                    return response;
                });
            }
            
            return promise;
        };
    }
    
    // Run initialization when DOM is loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})(); 