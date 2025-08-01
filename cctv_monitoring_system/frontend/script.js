// Global variables
let websocket = null;
let detectionCanvas = null;
let detectionCtx = null;
let fpsCounter = 0;
let objectCounter = 0;
let lastFpsUpdate = 0;
let alerts = [];
let statistics = {
    'NO_HELMET': 0,
    'NO_VEST': 0,
    'FALL_DETECTED': 0,
    'FIRE': 0,
    'SMOKE': 0
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize canvas for detection overlays
    detectionCanvas = document.getElementById('detection-canvas');
    detectionCtx = detectionCanvas.getContext('2d');
    
    // Set canvas size
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Initialize WebSocket connection
    connectWebSocket();
    
    // Start time display
    updateTime();
    setInterval(updateTime, 1000);
    
    // Start FPS counter
    setInterval(updateFps, 1000);
    
    // Initialize event listeners
    initializeEventListeners();
    
    // Load initial statistics
    loadStatistics();
}

function resizeCanvas() {
    const videoFeed = document.getElementById('video-feed');
    const rect = videoFeed.getBoundingClientRect();
    detectionCanvas.width = rect.width;
    detectionCanvas.height = rect.height;
}

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    websocket = new WebSocket(wsUrl);
    
    websocket.onopen = function(event) {
        console.log('WebSocket connected');
        updateConnectionStatus(true);
    };
    
    websocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    websocket.onclose = function(event) {
        console.log('WebSocket disconnected');
        updateConnectionStatus(false);
        
        // Reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
    };
    
    websocket.onerror = function(error) {
        console.error('WebSocket error:', error);
        updateConnectionStatus(false);
    };
}

function handleWebSocketMessage(data) {
    switch(data.type) {
        case 'detection_update':
        case 'violation_update':
            handleDetectionUpdate(data);
            break;
        case 'statistics_update':
            updateStatistics(data.statistics);
            break;
        case 'emergency_alert':
            handleEmergencyAlert(data);
            break;
        default:
            console.log('Unknown message type:', data.type);
    }
}

function handleDetectionUpdate(data) {
    // Update violation counts
    if (data.violations) {
        data.violations.forEach(violation => {
            if (statistics[violation.type] !== undefined) {
                statistics[violation.type]++;
            }
        });
        
        // Update display
        updateStatisticsDisplay();
        
        // Draw detection boxes
        drawDetections(data.violations);
        
        // Check for emergency violations
        checkEmergencyViolations(data.violations);
    }
}

function drawDetections(violations) {
    if (!detectionCtx) return;
    
    // Clear canvas
    detectionCtx.clearRect(0, 0, detectionCanvas.width, detectionCanvas.height);
    
    violations.forEach(violation => {
        const bbox = violation.bbox;
        const [x1, y1, x2, y2] = bbox;
        
        // Calculate scaled coordinates
        const scaleX = detectionCanvas.width / 640; // Assuming 640x480 input
        const scaleY = detectionCanvas.height / 480;
        
        const scaledX1 = x1 * scaleX;
        const scaledY1 = y1 * scaleY;
        const scaledX2 = x2 * scaleX;
        const scaledY2 = y2 * scaleY;
        
        // Set color based on violation type
        let color = '#667eea';
        let lineWidth = 2;
        
        switch(violation.type) {
            case 'FALL_DETECTED':
                color = '#ff6b6b';
                lineWidth = 4;
                break;
            case 'FIRE':
                color = '#ff8c00';
                lineWidth = 4;
                break;
            case 'SMOKE':
                color = '#8b4513';
                lineWidth = 3;
                break;
            case 'NO_HELMET':
                color = '#ffd700';
                lineWidth = 2;
                break;
            case 'NO_VEST':
                color = '#ff69b4';
                lineWidth = 2;
                break;
        }
        
        // Draw bounding box
        detectionCtx.strokeStyle = color;
        detectionCtx.lineWidth = lineWidth;
        detectionCtx.strokeRect(scaledX1, scaledY1, scaledX2 - scaledX1, scaledY2 - scaledY1);
        
        // Draw label
        detectionCtx.fillStyle = color;
        detectionCtx.font = '14px Arial';
        detectionCtx.fillText(violation.type, scaledX1, scaledY1 - 5);
        
        // Draw confidence
        detectionCtx.fillStyle = 'white';
        detectionCtx.font = '12px Arial';
        detectionCtx.fillText(`${(violation.confidence * 100).toFixed(1)}%`, scaledX1, scaledY1 + 15);
    });
    
    // Update object counter
    objectCounter = violations.length;
    document.getElementById('object-counter').textContent = objectCounter;
}

function checkEmergencyViolations(violations) {
    const emergencyTypes = ['FALL_DETECTED', 'FIRE', 'SMOKE'];
    
    violations.forEach(violation => {
        if (emergencyTypes.includes(violation.type)) {
            showEmergencyAlert(violation);
            playEmergencySound(violation.type);
        }
    });
}

function showEmergencyAlert(violation) {
    const modal = document.getElementById('emergency-modal');
    const title = document.getElementById('emergency-title');
    const icon = document.getElementById('emergency-icon');
    const message = document.getElementById('emergency-message');
    const location = document.getElementById('emergency-location');
    const time = document.getElementById('emergency-time');
    
    // Set alert content
    title.textContent = `🚨 ${violation.type.replace('_', ' ')}`;
    message.textContent = `Emergency: ${violation.type.replace('_', ' ')} detected!`;
    location.textContent = `Camera: Main (${violation.bbox.join(', ')})`;
    time.textContent = new Date().toLocaleTimeString();
    
    // Set icon
    switch(violation.type) {
        case 'FALL_DETECTED':
            icon.className = 'fas fa-exclamation-triangle';
            break;
        case 'FIRE':
            icon.className = 'fas fa-fire';
            break;
        case 'SMOKE':
            icon.className = 'fas fa-smog';
            break;
    }
    
    // Show modal
    modal.classList.add('show');
    
    // Add to alerts list
    addAlert(violation);
}

function playEmergencySound(violationType) {
    if (!document.getElementById('sound-alerts').checked) return;
    
    let audioElement = null;
    
    switch(violationType) {
        case 'FALL_DETECTED':
            audioElement = document.getElementById('medical-siren');
            break;
        case 'FIRE':
        case 'SMOKE':
            audioElement = document.getElementById('evacuation-alarm');
            break;
        case 'NO_HELMET':
        case 'NO_VEST':
            audioElement = document.getElementById('light-warning');
            break;
    }
    
    if (audioElement) {
        audioElement.currentTime = 0;
        audioElement.play().catch(e => console.log('Audio play failed:', e));
    }
}

function addAlert(violation) {
    const alertsContainer = document.getElementById('alerts-container');
    
    // Remove "no alerts" message if present
    const noAlerts = alertsContainer.querySelector('.no-alerts');
    if (noAlerts) {
        noAlerts.remove();
    }
    
    // Create alert element
    const alertElement = document.createElement('div');
    alertElement.className = `alert-item ${isEmergencyViolation(violation.type) ? 'emergency' : ''}`;
    
    const time = new Date().toLocaleTimeString();
    alertElement.innerHTML = `
        <div class="alert-header">
            <span class="alert-type">${violation.type.replace('_', ' ')}</span>
            <span class="alert-time">${time}</span>
        </div>
        <div class="alert-location">Location: ${violation.bbox.join(', ')}</div>
    `;
    
    // Add to beginning of alerts
    alertsContainer.insertBefore(alertElement, alertsContainer.firstChild);
    
    // Keep only last 10 alerts
    const alerts = alertsContainer.querySelectorAll('.alert-item');
    if (alerts.length > 10) {
        alerts[alerts.length - 1].remove();
    }
}

function isEmergencyViolation(type) {
    return ['FALL_DETECTED', 'FIRE', 'SMOKE'].includes(type);
}

function updateConnectionStatus(connected) {
    const statusDot = document.getElementById('connection-status');
    const statusText = document.getElementById('status-text');
    
    if (connected) {
        statusDot.classList.add('connected');
        statusText.textContent = 'Connected';
    } else {
        statusDot.classList.remove('connected');
        statusText.textContent = 'Disconnected';
    }
}

function updateTime() {
    const timeDisplay = document.getElementById('current-time');
    const now = new Date();
    timeDisplay.textContent = now.toLocaleTimeString();
}

function updateFps() {
    const fpsElement = document.getElementById('fps-counter');
    fpsElement.textContent = fpsCounter;
    fpsCounter = 0;
}

function updateStatisticsDisplay() {
    document.getElementById('no-helmet-count').textContent = statistics['NO_HELMET'];
    document.getElementById('no-vest-count').textContent = statistics['NO_VEST'];
    document.getElementById('fall-count').textContent = statistics['FALL_DETECTED'];
    document.getElementById('fire-count').textContent = statistics['FIRE'];
    document.getElementById('smoke-count').textContent = statistics['SMOKE'];
    
    // Add emergency animation to emergency stats
    const emergencyStats = ['fall-stat', 'fire-stat', 'smoke-stat'];
    emergencyStats.forEach(statId => {
        const statCard = document.getElementById(statId);
        if (statistics[statId.replace('-stat', '').toUpperCase().replace('-', '_')] > 0) {
            statCard.classList.add('emergency');
        } else {
            statCard.classList.remove('emergency');
        }
    });
}

function loadStatistics() {
    fetch('/api/statistics')
        .then(response => response.json())
        .then(data => {
            if (data.today_violations) {
                Object.keys(data.today_violations).forEach(key => {
                    if (statistics[key] !== undefined) {
                        statistics[key] = data.today_violations[key];
                    }
                });
                updateStatisticsDisplay();
            }
        })
        .catch(error => console.error('Error loading statistics:', error));
}

// Camera Control Functions
function controlCamera(action, value = 0) {
    const data = {
        action: action,
        pan: 0,
        tilt: 0,
        zoom: 1
    };
    
    switch(action) {
        case 'pan':
            data.pan = value;
            break;
        case 'tilt':
            data.tilt = value;
            break;
        case 'zoom':
            data.zoom = value;
            break;
    }
    
    fetch('/api/camera/control', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('Camera control successful:', data.result);
        } else {
            console.error('Camera control failed:', data.error);
        }
    })
    .catch(error => console.error('Error controlling camera:', error));
}

// Notification Functions
function testNotification() {
    fetch('/api/notifications/test', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification('Test notification sent successfully!', 'success');
        } else {
            showNotification('Test notification failed!', 'error');
        }
    })
    .catch(error => {
        console.error('Error testing notification:', error);
        showNotification('Test notification failed!', 'error');
    });
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Report Generation Functions
function generateReport(type) {
    const url = `/api/reports/generate?report_type=${type}`;
    
    // Show loading state
    showNotification('Generating report...', 'info');
    
    // Download the report
    const link = document.createElement('a');
    link.href = url;
    link.download = `ppe_compliance_report_${type}_${new Date().toISOString().split('T')[0]}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showNotification('Report generated successfully!', 'success');
}

// Video Control Functions
function toggleFullscreen() {
    const videoFeed = document.getElementById('video-feed');
    
    if (!document.fullscreenElement) {
        videoFeed.requestFullscreen().catch(err => {
            console.error('Error entering fullscreen:', err);
        });
    } else {
        document.exitFullscreen();
    }
}

function captureSnapshot() {
    // This would capture the current video frame
    showNotification('Snapshot captured!', 'success');
}

// Modal Functions
function closeEmergencyModal() {
    const modal = document.getElementById('emergency-modal');
    modal.classList.remove('show');
}

function acknowledgeEmergency() {
    closeEmergencyModal();
    showNotification('Emergency acknowledged!', 'success');
}

function closeSettingsModal() {
    const modal = document.getElementById('settings-modal');
    modal.classList.remove('show');
}

function saveSettings() {
    // Get settings values
    const cameraIp = document.getElementById('camera-ip').value;
    const cameraUsername = document.getElementById('camera-username').value;
    const cameraPassword = document.getElementById('camera-password').value;
    const notificationEmail = document.getElementById('notification-email').value;
    const whatsappNumber = document.getElementById('whatsapp-number').value;
    
    // Save settings (in a real app, this would be sent to the server)
    localStorage.setItem('cameraIp', cameraIp);
    localStorage.setItem('cameraUsername', cameraUsername);
    localStorage.setItem('cameraPassword', cameraPassword);
    localStorage.setItem('notificationEmail', notificationEmail);
    localStorage.setItem('whatsappNumber', whatsappNumber);
    
    showNotification('Settings saved successfully!', 'success');
    closeSettingsModal();
}

// Event Listeners
function initializeEventListeners() {
    // Settings button (if you add one)
    // document.getElementById('settings-btn').addEventListener('click', () => {
    //     document.getElementById('settings-modal').classList.add('show');
    // });
    
    // Close modals when clicking outside
    window.addEventListener('click', (event) => {
        const emergencyModal = document.getElementById('emergency-modal');
        const settingsModal = document.getElementById('settings-modal');
        
        if (event.target === emergencyModal) {
            closeEmergencyModal();
        }
        if (event.target === settingsModal) {
            closeSettingsModal();
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeEmergencyModal();
            closeSettingsModal();
        }
    });
}

// Utility Functions
function formatTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString();
}

function formatDate(timestamp) {
    return new Date(timestamp).toLocaleDateString();
}

// Export functions for HTML onclick handlers
window.controlCamera = controlCamera;
window.testNotification = testNotification;
window.generateReport = generateReport;
window.toggleFullscreen = toggleFullscreen;
window.captureSnapshot = captureSnapshot;
window.closeEmergencyModal = closeEmergencyModal;
window.acknowledgeEmergency = acknowledgeEmergency;
window.closeSettingsModal = closeSettingsModal;
window.saveSettings = saveSettings;