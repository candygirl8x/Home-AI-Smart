/* ============================================
   SMART HOME AI - COMPLETE JAVASCRIPT
   ============================================ */

// ---------- DOM READY ----------
document.addEventListener('DOMContentLoaded', function () {
    console.log('🏠 Smart Home AI initialized');

    // Initialize all components
    initTimeUpdate();
    initToggleSwitches();
    initDeviceControls();
    initVoiceCommands();
    initNotifications();
    initCharts();
    initFormValidation();
    initAutoRefresh();
});

// ---------- TIME UPDATE ----------
function initTimeUpdate() {
    const timeElement = document.getElementById('currentTime');
    if (timeElement) {
        setInterval(() => {
            const now = new Date();
            timeElement.textContent = now.toLocaleString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        }, 1000);
    }
}

// ---------- TOGGLE SWITCHES ----------
function initToggleSwitches() {
    document.querySelectorAll('.toggle-switch').forEach(toggle => {
        toggle.addEventListener('click', function (e) {
            e.stopPropagation();
            toggleSwitch(this);
        });
    });
}

function toggleSwitch(element) {
    if (!element) return;

    element.classList.toggle('active');
    const hiddenInput = element.parentElement.querySelector('input[type="hidden"]');
    if (hiddenInput) {
        hiddenInput.value = element.classList.contains('active') ? 'true' : 'false';
    }

    // Trigger change event for any listeners
    const event = new Event('change', { bubbles: true });
    if (hiddenInput) {
        hiddenInput.dispatchEvent(event);
    }

    // Update related UI
    const statusBadge = element.closest('.settings-card').querySelector('.card-badge');
    if (statusBadge) {
        const isActive = element.classList.contains('active');
        statusBadge.textContent = isActive ? 'Enabled' : 'Disabled';
        statusBadge.className = `card-badge ${isActive ? 'success' : 'warning'}`;
    }
}

// ---------- DEVICE CONTROLS ----------
function initDeviceControls() {
    // Device toggle buttons
    document.querySelectorAll('.status-toggle').forEach(toggle => {
        toggle.addEventListener('click', function () {
            const deviceId = this.dataset.deviceId;
            const isActive = this.classList.contains('active');
            const newStatus = isActive ? 'off' : 'on';

            toggleDevice(deviceId, newStatus);
        });
    });

    // Quick action buttons
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const action = this.dataset.action;
            executeQuickAction(action);
        });
    });
}

async function toggleDevice(deviceId, status) {
    try {
        const response = await fetch(`/api/devices/${deviceId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: status })
        });

        const data = await response.json();

        if (data.status === 'success') {
            // Update UI
            const toggle = document.querySelector(`.status-toggle[data-device-id="${deviceId}"]`);
            if (toggle) {
                toggle.classList.toggle('active');
                const slider = toggle.querySelector('.toggle-slider');
                if (slider) {
                    slider.style.left = toggle.classList.contains('active') ? '25px' : '3px';
                }
            }

            // Update status indicator
            const indicator = document.querySelector(`.status-indicator[data-device-id="${deviceId}"]`);
            if (indicator) {
                indicator.className = `status-indicator status-${status}`;
            }

            showNotification('Device updated successfully', 'success');
            refreshStats();
        } else {
            showNotification('Failed to update device', 'danger');
        }
    } catch (error) {
        console.error('Error toggling device:', error);
        showNotification('Error updating device', 'danger');
    }
}

function executeQuickAction(action) {
    switch (action) {
        case 'all-on':
            toggleAllDevices('on');
            break;
        case 'all-off':
            toggleAllDevices('off');
            break;
        case 'goodnight':
            goodnightMode();
            break;
        case 'goodmorning':
            goodMorningMode();
            break;
        default:
            console.log('Unknown quick action:', action);
    }
}

async function toggleAllDevices(status) {
    try {
        const response = await fetch('/api/devices/all', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: status })
        });

        const data = await response.json();
        if (data.status === 'success') {
            showNotification(`All devices turned ${status}`, 'success');
            location.reload();
        }
    } catch (error) {
        console.error('Error toggling all devices:', error);
        showNotification('Failed to control all devices', 'danger');
    }
}

async function goodnightMode() {
    try {
        const response = await fetch('/api/scenes/goodnight', {
            method: 'POST'
        });
        const data = await response.json();
        if (data.status === 'success') {
            showNotification('Goodnight mode activated! 🌙', 'success');
            location.reload();
        }
    } catch (error) {
        console.error('Error activating goodnight mode:', error);
        showNotification('Failed to activate goodnight mode', 'danger');
    }
}

async function goodMorningMode() {
    try {
        const response = await fetch('/api/scenes/goodmorning', {
            method: 'POST'
        });
        const data = await response.json();
        if (data.status === 'success') {
            showNotification('Good morning! ☀️', 'success');
            location.reload();
        }
    } catch (error) {
        console.error('Error activating good morning mode:', error);
        showNotification('Failed to activate good morning mode', 'danger');
    }
}

// ---------- VOICE COMMANDS ----------
function initVoiceCommands() {
    const voiceInput = document.getElementById('voiceCommand');
    const sendBtn = document.getElementById('sendCommandBtn');
    const micBtn = document.getElementById('micBtn');

    if (sendBtn && voiceInput) {
        sendBtn.addEventListener('click', function () {
            const command = voiceInput.value.trim();
            if (command) {
                sendVoiceCommand(command);
                voiceInput.value = '';
            }
        });

        voiceInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                sendBtn.click();
            }
        });
    }

    if (micBtn) {
        micBtn.addEventListener('click', toggleVoiceRecording);
    }
}

let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

async function toggleVoiceRecording() {
    const micBtn = document.getElementById('micBtn');

    if (isRecording) {
        // Stop recording
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
        }
        micBtn.classList.remove('recording');
        micBtn.innerHTML = '🎙️';
        isRecording = false;
        return;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            await processVoiceAudio(audioBlob);

            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        micBtn.classList.add('recording');
        micBtn.innerHTML = '⏹️';
        isRecording = true;

        const responseArea = document.getElementById('responseArea');
        if (responseArea) {
            responseArea.textContent = '🎤 Listening...';
        }

    } catch (error) {
        console.error('Error accessing microphone:', error);
        showNotification('Could not access microphone. Please allow microphone access.', 'danger');
    }
}

async function processVoiceAudio(audioBlob) {
    try {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');

        const response = await fetch('/api/voice/command', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        const responseArea = document.getElementById('responseArea');
        if (responseArea) {
            responseArea.textContent = data.response || 'Command processed successfully.';
        }

        if (data.action) {
            await handleVoiceAction(data.action);
        }

        refreshDevices();
        refreshStats();

    } catch (error) {
        console.error('Error processing voice:', error);
        showNotification('Error processing voice command', 'danger');

        const responseArea = document.getElementById('responseArea');
        if (responseArea) {
            responseArea.textContent = '❌ Error processing voice command';
        }
    }
}

async function sendVoiceCommand(command) {
    try {
        const response = await fetch('/api/voice/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: command })
        });

        const data = await response.json();

        const responseArea = document.getElementById('responseArea');
        if (responseArea) {
            responseArea.textContent = data.response || 'Command processed.';
        }

        if (data.action) {
            await handleVoiceAction(data.action);
        }

        refreshDevices();
        refreshStats();

    } catch (error) {
        console.error('Error sending voice command:', error);
        showNotification('Error sending voice command', 'danger');

        const responseArea = document.getElementById('responseArea');
        if (responseArea) {
            responseArea.textContent = '❌ Error sending voice command';
        }
    }
}
