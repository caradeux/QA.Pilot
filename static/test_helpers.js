/**
 * Test Monitoring Helpers
 * This file provides reliable status polling for test execution
 */

// Store active test monitoring information
const testMonitor = {
    taskId: null,
    pollingInterval: null,
    statusCallback: null,
    maxPolls: 100,  // Maximum polling attempts
    pollCount: 0,
    pollDelay: 1000, // Poll every second
    isPolling: false
};

// Initialize test monitoring
function initTestMonitoring(taskId, statusCallback) {
    console.log("Initializing test monitoring for task:", taskId);
    
    // Clear any existing polling
    stopTestMonitoring();
    
    // Set up new monitoring
    testMonitor.taskId = taskId;
    testMonitor.statusCallback = statusCallback;
    testMonitor.pollCount = 0;
    testMonitor.isPolling = true;
    
    // Start polling immediately
    pollTestStatus();
    
    // Set up interval for continued polling
    testMonitor.pollingInterval = setInterval(pollTestStatus, testMonitor.pollDelay);
    
    return true;
}

// Poll the server for test status
function pollTestStatus() {
    if (!testMonitor.isPolling || !testMonitor.taskId) {
        console.warn("Test monitoring stopped or no taskId");
        stopTestMonitoring();
        return;
    }
    
    // Increment poll count
    testMonitor.pollCount++;
    
    // Check if we've exceeded max polls
    if (testMonitor.pollCount > testMonitor.maxPolls) {
        console.warn(`Exceeded maximum poll count (${testMonitor.maxPolls})`);
        stopTestMonitoring();
        
        // Notify with timeout error
        if (testMonitor.statusCallback) {
            testMonitor.statusCallback({
                status: 'error',
                message: 'Test monitoring timed out',
                details: 'Maximum polling attempts exceeded'
            });
        }
        return;
    }
    
    // Make the status request
    console.log(`Polling test status (${testMonitor.pollCount}/${testMonitor.maxPolls}): ${testMonitor.taskId}`);
    
    fetch(`/test_status/${testMonitor.taskId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Test status update received:", data);
            
            // Call the status callback with the data
            if (testMonitor.statusCallback) {
                testMonitor.statusCallback(data);
            }
            
            // If test is completed or has error, stop polling
            if (data.status === 'completed' || data.status === 'error') {
                console.log(`Test ${data.status}, stopping monitoring`);
                stopTestMonitoring();
            }
        })
        .catch(error => {
            console.error("Error polling test status:", error);
            
            // After consecutive errors, we might want to stop polling
            if (testMonitor.statusCallback) {
                testMonitor.statusCallback({
                    status: 'error',
                    message: `Error polling test status: ${error.message}`
                });
            }
        });
}

// Stop test monitoring
function stopTestMonitoring() {
    console.log("Stopping test monitoring");
    
    testMonitor.isPolling = false;
    
    if (testMonitor.pollingInterval) {
        clearInterval(testMonitor.pollingInterval);
        testMonitor.pollingInterval = null;
    }
}

// Manually trigger status check
function checkTestStatus(taskId, callback) {
    fetch(`/test_status/${taskId}`)
        .then(response => response.json())
        .then(data => {
            if (callback) callback(data);
        })
        .catch(error => {
            console.error("Error checking test status:", error);
            if (callback) callback({ status: 'error', message: error.message });
        });
}

// Export the helper functions
window.TestMonitor = {
    init: initTestMonitoring,
    stop: stopTestMonitoring,
    check: checkTestStatus
}; 