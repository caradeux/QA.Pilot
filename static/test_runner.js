/**
 * Standalone Test Runner
 * This script provides direct injection functionality for test execution
 */

(function() {
    console.log("Test Runner loaded");
    
    // Function to run a test directly
    window.runTest = function(url, instructions, options) {
        console.log("Running test directly for URL:", url);
        
        // Default options
        options = options || {};
        
        // Create form data
        const formData = new FormData();
        formData.append('url', url);
        formData.append('instructions', instructions || '');
        formData.append('max_time', options.max_time || '600');
        formData.append('browser', options.browser || 'chrome');
        
        if (options.screenshots !== false) {
            formData.append('screenshots', 'on');
        }
        
        if (options.fullscreen !== false) {
            formData.append('fullscreen', 'on');
        }
        
        // Show status directly on the page
        const statusDiv = document.createElement('div');
        statusDiv.className = 'test-status-overlay';
        statusDiv.style.cssText = 'position:fixed;top:50px;left:50%;transform:translateX(-50%);background:#212136;color:white;padding:15px;border-radius:5px;z-index:9999;min-width:300px;text-align:center;box-shadow:0 0 15px rgba(0,0,0,0.5);';
        
        statusDiv.innerHTML = `
            <h3>Test Status</h3>
            <div class="status-message">Iniciando prueba...</div>
            <div class="progress-container" style="margin:10px 0;background:#333;border-radius:3px;height:20px;overflow:hidden;">
                <div class="progress-bar" style="width:0%;height:100%;background:#4a5feb;transition:width 0.3s;"></div>
            </div>
            <div class="test-details" style="font-size:12px;text-align:left;margin-top:10px;"></div>
        `;
        
        document.body.appendChild(statusDiv);
        
        // Function to update status
        function updateStatus(message, progress, details) {
            if (statusDiv) {
                const statusMsg = statusDiv.querySelector('.status-message');
                if (statusMsg) statusMsg.textContent = message || '';
                
                const progressBar = statusDiv.querySelector('.progress-bar');
                if (progressBar && typeof progress === 'number') {
                    progressBar.style.width = `${progress}%`;
                }
                
                if (details) {
                    const detailsElem = statusDiv.querySelector('.test-details');
                    if (detailsElem) {
                        // Convert object to formatted text
                        if (typeof details === 'object') {
                            let detailsText = '';
                            for (const [key, value] of Object.entries(details)) {
                                detailsText += `${key}: ${value}\n`;
                            }
                            detailsElem.textContent = detailsText;
                        } else {
                            detailsElem.textContent = details;
                        }
                    }
                }
            }
        }
        
        // Submit request
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
                updateStatus('Test started successfully', 10, data.details);
                
                // Start monitoring
                if (window.TestMonitor) {
                    TestMonitor.init(data.task_id, function(statusData) {
                        console.log("Test status update:", statusData);
                        
                        if (statusData.status === 'running') {
                            updateStatus(statusData.message || 'Test running...', statusData.progress || 30);
                        } else if (statusData.status === 'completed') {
                            updateStatus('Test completed', 100);
                            
                            // After 3 seconds, update with results
                            setTimeout(() => {
                                updateStatus('Test completed successfully', 100, 'Click to view results');
                                statusDiv.style.cursor = 'pointer';
                                statusDiv.addEventListener('click', () => {
                                    // Remove the status div
                                    statusDiv.remove();
                                    
                                    // Display results in a more detailed way
                                    displayResults(statusData.results);
                                });
                            }, 3000);
                        } else if (statusData.status === 'error') {
                            updateStatus(`Error: ${statusData.message}`, 100);
                            statusDiv.style.backgroundColor = '#a51d2d';
                        }
                    });
                } else {
                    console.error("TestMonitor not available");
                    updateStatus('Test monitoring not available', 0);
                }
                
                return data;
            } else {
                updateStatus(`Error: ${data.message}`, 0);
                statusDiv.style.backgroundColor = '#a51d2d';
                throw new Error(data.message || 'Unknown error starting test');
            }
        })
        .catch(error => {
            console.error("Error running test:", error);
            updateStatus(`Error: ${error.message}`, 0);
            statusDiv.style.backgroundColor = '#a51d2d';
        });
    };
    
    // Function to display results
    function displayResults(results) {
        if (!results) {
            console.error("No results to display");
            return;
        }
        
        // Create results container
        const resultsDiv = document.createElement('div');
        resultsDiv.className = 'test-results-overlay';
        resultsDiv.style.cssText = 'position:fixed;top:50px;left:50px;right:50px;bottom:50px;background:#212136;color:white;z-index:9999;border-radius:10px;box-shadow:0 0 20px rgba(0,0,0,0.7);display:flex;flex-direction:column;';
        
        // Add header and close button
        resultsDiv.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;padding:15px;border-bottom:1px solid #333;">
                <h2>Test Results</h2>
                <button id="close-results" style="background:none;border:none;color:white;font-size:24px;cursor:pointer;">&times;</button>
            </div>
            <div style="flex:1;overflow:auto;padding:20px;">
                <div class="results-content"></div>
            </div>
        `;
        
        document.body.appendChild(resultsDiv);
        
        // Add close button event listener
        document.getElementById('close-results').addEventListener('click', () => {
            resultsDiv.remove();
        });
        
        // Populate results content
        const resultsContent = resultsDiv.querySelector('.results-content');
        
        // Add screenshots section if available
        if (results.screenshots && results.screenshots.length > 0) {
            const screenshotsSection = document.createElement('div');
            screenshotsSection.innerHTML = `
                <h3>Screenshots</h3>
                <div class="screenshots-grid" style="display:grid;grid-template-columns:repeat(auto-fill, minmax(300px, 1fr));gap:20px;margin-top:15px;"></div>
            `;
            
            const screenshotsGrid = screenshotsSection.querySelector('.screenshots-grid');
            
            results.screenshots.forEach((screenshot, index) => {
                const card = document.createElement('div');
                card.style.cssText = 'background:#16213e;border-radius:5px;overflow:hidden;';
                card.innerHTML = `
                    <div style="padding:10px;border-bottom:1px solid #333;">
                        <h4 style="margin:0;">${screenshot.name || `Screenshot ${index + 1}`}</h4>
                        <div style="font-size:12px;color:#aaa;">${screenshot.timestamp || ''}</div>
                    </div>
                    <div style="padding:10px;">
                        <img src="${screenshot.url}" alt="${screenshot.name || `Screenshot ${index + 1}`}" style="max-width:100%;border-radius:3px;">
                    </div>
                `;
                screenshotsGrid.appendChild(card);
            });
            
            resultsContent.appendChild(screenshotsSection);
        }
        
        // Add steps section if available
        if (results.steps && results.steps.length > 0) {
            const stepsSection = document.createElement('div');
            stepsSection.innerHTML = `
                <h3>Test Steps</h3>
                <div class="steps-list" style="margin-top:15px;"></div>
            `;
            
            const stepsList = stepsSection.querySelector('.steps-list');
            
            results.steps.forEach((step, index) => {
                const stepItem = document.createElement('div');
                stepItem.style.cssText = 'display:flex;margin-bottom:15px;background:#16213e;border-radius:5px;overflow:hidden;';
                
                const statusColor = step.status === 'success' ? '#28a745' : (step.status === 'warning' ? '#ffc107' : '#dc3545');
                
                stepItem.innerHTML = `
                    <div style="width:40px;background:${statusColor};display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;">${index + 1}</div>
                    <div style="flex:1;padding:10px;">
                        <div style="font-weight:bold;">${step.action}</div>
                        <div style="margin-top:5px;">${step.details}</div>
                        <div style="font-size:12px;color:#aaa;margin-top:5px;">Duration: ${step.duration}s</div>
                    </div>
                `;
                
                stepsList.appendChild(stepItem);
            });
            
            resultsContent.appendChild(stepsSection);
        }
        
        // Add summary section
        const summarySection = document.createElement('div');
        summarySection.innerHTML = `
            <h3>Summary</h3>
            <div style="background:#16213e;padding:15px;border-radius:5px;margin-top:15px;">
                <div><strong>Success:</strong> ${results.success ? 'Yes' : 'No'}</div>
                <div><strong>Execution Time:</strong> ${results.execution_time || '?'}s</div>
            </div>
        `;
        
        resultsContent.appendChild(summarySection);
    }
    
    // Expose direct test execution function
    window.runDirectTest = function(taskId) {
        if (window.TestMonitor) {
            console.log("Running direct test with task ID:", taskId);
            TestMonitor.init(taskId, function(data) {
                console.log("Direct test status update:", data);
            });
        } else {
            console.error("TestMonitor not available for direct testing");
        }
    };
})(); 