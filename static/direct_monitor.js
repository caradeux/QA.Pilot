/**
 * Direct Monitoring Helper
 * This script allows manual monitoring of a test by task ID
 */

// Create UI elements for direct monitoring
function setupDirectMonitoring() {
    // Create container for the monitoring UI
    const container = document.createElement('div');
    container.id = 'direct-monitor';
    container.style.cssText = 'position: fixed; bottom: 10px; right: 10px; z-index: 9999; background: #212136; color: white; padding: 10px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.5); font-family: monospace;';
    
    container.innerHTML = `
        <h4></h4>
        <div>
            <input type="text" id="task-id-input" placeholder="Enter task ID..." style="width: 200px; padding: 5px;">
            <button id="monitor-btn" style="padding: 5px; background: #4a5feb; border: none; color: white; margin-left: 5px; cursor: pointer;">Monitor</button>
        </div>
        <div id="monitor-status" style="margin-top: 10px; font-size: 12px;"></div>
    `;
    
    document.body.appendChild(container);
    
    // Add event listener for the monitor button
    document.getElementById('monitor-btn').addEventListener('click', function() {
        const taskId = document.getElementById('task-id-input').value.trim();
        if (!taskId) {
            document.getElementById('monitor-status').textContent = 'Please enter a task ID';
            return;
        }
        
        document.getElementById('monitor-status').textContent = `Monitoring task: ${taskId}`;
        console.log("Manually monitoring task:", taskId);
        
        // Start monitoring with the TestMonitor helper
        if (window.TestMonitor) {
            TestMonitor.init(taskId, function(data) {
                console.log("Status update for manual monitoring:", data);
                document.getElementById('monitor-status').textContent = 
                    `Task: ${taskId}\nStatus: ${data.status}\nProgress: ${data.progress || '?'}%\nMessage: ${data.message || '-'}`;
            });
        } else {
            document.getElementById('monitor-status').textContent = 'TestMonitor not available';
        }
    });
    
    console.log("Direct monitoring UI added");
}

// Initialize once the page is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupDirectMonitoring);
} else {
    setupDirectMonitoring();
}

// Add a helper to decode task IDs from messages
window.extractTaskId = function(text) {
    // Look for common task ID patterns
    const patterns = [
        /task[_\s]?id[:\s]+([a-zA-Z0-9_]+)/i,
        /"task_id":\s*"([^"]+)"/,
        /task_id=([^&\s]+)/
    ];
    
    for (const pattern of patterns) {
        const match = text.match(pattern);
        if (match && match[1]) {
            return match[1];
        }
    }
    
    return null;
}; 