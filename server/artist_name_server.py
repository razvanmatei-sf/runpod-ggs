#!/usr/bin/env python3

import os
import subprocess
import time
import threading
import requests
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
import signal
import sys

app = Flask(__name__)

# Global variables
artist_name = None
comfyui_process = None
jupyter_process = None
session_start_time = None
comfyui_ready = False

# Clean single-page interface template
ARTIST_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>ComfyUI Artist Studio</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #333;
        }
        
        .container { 
            background: white;
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 600px;
            width: 90%;
            text-align: center;
            min-height: 500px;
        }
        
        h1 { 
            color: #333;
            margin-bottom: 0.5rem;
            font-size: 2.5rem;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 2rem;
            font-size: 1.1rem;
        }
        
        select, button { 
            width: 100%;
            padding: 15px 20px;
            margin: 10px 0;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        select {
            border: 2px solid #e0e0e0;
            background: white;
            cursor: pointer;
        }
        
        select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        button { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            cursor: pointer;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        #status {
            margin-top: 1rem;
            min-height: 20px;
        }
        
        .session-section {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 2rem;
            margin-top: 2rem;
        }
        
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .info-row:last-child {
            border-bottom: none;
        }
        
        .info-label {
            color: #666;
            font-weight: 500;
        }
        
        .info-value {
            color: #333;
            font-weight: 600;
        }
        
        .service-links {
            display: grid;
            gap: 1rem;
            margin-top: 1.5rem;
        }
        
        .service-link {
            display: block;
            padding: 1rem;
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            text-decoration: none;
            color: #333;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .service-link:hover:not(.inactive) {
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .service-link.ready {
            border-color: #4caf50;
            background: #f1f8e9;
        }
        
        .service-link.waiting {
            border-color: #ff9800;
            background: #fff3e0;
        }
        
        .service-link.inactive {
            background: #f5f5f5;
            color: #999;
            cursor: not-allowed;
            opacity: 0.7;
        }
        
        .terminate-btn {
            background: #f44336;
            margin-top: 2rem;
        }
        
        .terminate-btn:hover:not(:disabled) {
            box-shadow: 0 5px 15px rgba(244, 67, 54, 0.4);
        }
        
        
        .copy-feedback {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #4caf50;
            color: white;
            padding: 1rem 2rem;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 1000;
        }
        
        .copy-feedback.show {
            opacity: 1;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 ComfyUI Artist Studio - StillFront</h1>
        <p class="subtitle">Select your artist profile to begin</p>
        
        <form id="artistForm">
            <select id="artistSelect">
                <option value="">-- Choose your name --</option>
                {% for artist in artists %}
                <option value="{{ artist }}">{{ artist }}</option>
                {% endfor %}
            </select>
        </form>
        
        <div id="status"></div>
        
        <div class="session-section">
            <div class="info-row">
                <span class="info-label">Active Artist:</span>
                <span class="info-value" id="activeArtist">Not Selected</span>
            </div>
            <div class="info-row">
                <span class="info-label">Session Time:</span>
                <span class="info-value" id="sessionTime">--:--</span>
            </div>
            
            <div class="service-links">
                <a href="#" class="service-link inactive" id="comfyLink" onclick="handleComfyClick(event)">
                    <strong>ComfyUI</strong>
                    <span id="comfyStatus"> - Select artist first</span>
                </a>
                <a href="#" class="service-link inactive" id="jupyterLink" onclick="return false;">
                    <strong>Jupyter Lab</strong>
                    <span id="jupyterStatus"> - Select artist first</span>
                </a>
            </div>
            
            <button id="startBtn" style="visibility: hidden;" onclick="startSession()">
                Start My Session
            </button>
            
            <button class="terminate-btn" onclick="terminateRunPod()">
                Terminate RunPod Instance
            </button>
        </div>
    </div>
    
    <div class="copy-feedback" id="copyFeedback">
        ComfyUI link copied to clipboard!
    </div>
    
    <script>
        let sessionStartTime = null;
        let timerInterval = null;
        let checkInterval = null;
        let sessionActive = false;
        
        // Handle artist selection
        document.getElementById('artistSelect').addEventListener('change', function() {
            const artistName = this.value;
            if (artistName) {
                document.getElementById('activeArtist').textContent = artistName;
                document.getElementById('startBtn').style.visibility = 'visible';
                document.getElementById('status').innerHTML = '';
            } else {
                document.getElementById('activeArtist').textContent = 'Not Selected';
                document.getElementById('startBtn').style.visibility = 'hidden';
                resetSession();
            }
        });
        
        async function startSession() {
            const artistName = document.getElementById('artistSelect').value;
            if (!artistName) {
                document.getElementById('status').innerHTML = '<p style="color: #f44336;">Please select your name</p>';
                return;
            }
            
            // Disable form and button
            document.getElementById('artistSelect').disabled = true;
            document.getElementById('startBtn').disabled = true;
            document.getElementById('startBtn').textContent = 'Starting...';
            
            document.getElementById('status').innerHTML = '<p style="color: #667eea;">Starting your session...</p>';
            
            const response = await fetch('/start_session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ artist_name: artistName })
            });
            
            const result = await response.json();
            if (result.success) {
                sessionActive = true;
                sessionStartTime = new Date();
                
                // Update UI
                document.getElementById('startBtn').style.visibility = 'hidden';
                document.getElementById('status').innerHTML = '';
                
                // Enable Jupyter immediately
                const runpodId = '{{ runpod_id }}';
                const jupyterUrl = `https://${runpodId}-8888.proxy.runpod.net`;
                document.getElementById('jupyterLink').href = jupyterUrl;
                document.getElementById('jupyterLink').classList.remove('inactive');
                document.getElementById('jupyterLink').classList.add('ready');
                document.getElementById('jupyterLink').onclick = null;
                document.getElementById('jupyterLink').target = '_blank';
                document.getElementById('jupyterStatus').textContent = ' - Ready';
                
                // Show ComfyUI as waiting
                document.getElementById('comfyLink').classList.remove('inactive');
                document.getElementById('comfyLink').classList.add('waiting');
                document.getElementById('comfyStatus').textContent = ' - Starting...';
                
                // Start checking ComfyUI status
                checkComfyUIStatus();
                
                // Start session timer
                startSessionTimer();
            } else {
                document.getElementById('status').innerHTML = '<p style="color: #f44336;">Error: ' + result.message + '</p>';
                document.getElementById('artistSelect').disabled = false;
                document.getElementById('startBtn').disabled = false;
                document.getElementById('startBtn').textContent = 'Start My Session';
            }
        }
        
        function checkComfyUIStatus() {
            checkInterval = setInterval(async () => {
                try {
                    const response = await fetch('/comfyui_status');
                    const result = await response.json();
                    
                    if (result.ready) {
                        const runpodId = '{{ runpod_id }}';
                        const comfyUrl = `https://${runpodId}-8188.proxy.runpod.net`;
                        document.getElementById('comfyLink').href = comfyUrl;
                        document.getElementById('comfyLink').classList.remove('waiting');
                        document.getElementById('comfyLink').classList.add('ready');
                        document.getElementById('comfyLink').innerHTML = '<strong>Open ComfyUI</strong>';
                        clearInterval(checkInterval);
                    }
                } catch (e) {
                    console.error('Status check failed:', e);
                }
            }, 5000);
        }
        
        function handleComfyClick(event) {
            const link = document.getElementById('comfyLink');
            
            // If not ready, prevent default
            if (link.classList.contains('inactive')) {
                event.preventDefault();
                return false;
            }
            
            // If ready, copy to clipboard and open
            if (link.classList.contains('ready')) {
                event.preventDefault();
                const url = link.href;
                
                // Copy to clipboard
                navigator.clipboard.writeText(url).then(() => {
                    // Show feedback
                    const feedback = document.getElementById('copyFeedback');
                    feedback.classList.add('show');
                    setTimeout(() => {
                        feedback.classList.remove('show');
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy:', err);
                });
                
                // Open in new tab
                window.open(url, '_blank');
            }
        }
        
        function startSessionTimer() {
            timerInterval = setInterval(() => {
                if (sessionStartTime) {
                    const elapsed = Math.floor((new Date() - sessionStartTime) / 1000);
                    const hours = Math.floor(elapsed / 3600);
                    const minutes = Math.floor((elapsed % 3600) / 60);
                    const seconds = elapsed % 60;
                    
                    let timeStr = '';
                    if (hours > 0) {
                        timeStr = `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                    } else {
                        timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;
                    }
                    
                    document.getElementById('sessionTime').textContent = timeStr;
                }
            }, 1000);
        }
        
        function resetSession() {
            sessionActive = false;
            sessionStartTime = null;
            
            // Clear intervals
            if (timerInterval) clearInterval(timerInterval);
            if (checkInterval) clearInterval(checkInterval);
            
            // Reset timer
            document.getElementById('sessionTime').textContent = '--:--';
            
            // Reset service links
            document.getElementById('comfyLink').href = '#';
            document.getElementById('comfyLink').classList.remove('ready', 'waiting');
            document.getElementById('comfyLink').classList.add('inactive');
            document.getElementById('comfyStatus').textContent = ' - Select artist first';
            
            document.getElementById('jupyterLink').href = '#';
            document.getElementById('jupyterLink').classList.remove('ready');
            document.getElementById('jupyterLink').classList.add('inactive');
            document.getElementById('jupyterLink').onclick = function() { return false; };
            document.getElementById('jupyterLink').target = '';
            document.getElementById('jupyterStatus').textContent = ' - Select artist first';
        }
        
        async function terminateRunPod() {
            if (confirm('Are you sure you want to terminate this RunPod instance? All unsaved work will be lost.')) {
                const btn = event.target;
                btn.disabled = true;
                btn.textContent = 'Terminating...';
                
                try {
                    const response = await fetch('/terminate', {
                        method: 'POST'
                    });
                    const result = await response.json();
                    
                    if (result.success) {
                        alert('Processes terminated. Redirecting to RunPod console in 5 seconds...');
                        setTimeout(() => {
                            window.location.href = 'https://console.runpod.io/pods';
                        }, 5000);
                    } else {
                        alert('Failed to terminate: ' + result.message);
                        btn.disabled = false;
                        btn.textContent = 'Terminate RunPod Instance';
                    }
                } catch (e) {
                    alert('Error: ' + e.message);
                    btn.disabled = false;
                    btn.textContent = 'Terminate RunPod Instance';
                }
            }
        }
    </script>
</body>
</html>
"""

def get_existing_artists():
    """Get list of existing artist folders"""
    output_dir = "/workspace/output"
    artists = []
    try:
        if os.path.exists(output_dir):
            for item in os.listdir(output_dir):
                if os.path.isdir(os.path.join(output_dir, item)):
                    # Filter out system/hidden folders
                    if not item.startswith('.') and item != '.ipynb_checkpoints':
                        artists.append(item)
            artists.sort()
    except:
        pass
    return artists

def get_runpod_id():
    """Get RunPod instance ID from environment"""
    return os.environ.get('RUNPOD_POD_ID', 'localhost')

def check_comfyui_ready():
    """Check if ComfyUI is responding"""
    global comfyui_ready
    try:
        response = requests.get('http://localhost:8188/api/prompt', timeout=2)
        comfyui_ready = response.status_code == 200
    except:
        comfyui_ready = False
    return comfyui_ready

@app.route('/')
def index():
    existing_artists = get_existing_artists()
    runpod_id = get_runpod_id()
    return render_template_string(ARTIST_HTML, artists=existing_artists, runpod_id=runpod_id)

@app.route('/start_session', methods=['POST'])
def start_session():
    global artist_name, comfyui_process, jupyter_process, session_start_time, comfyui_ready
    
    try:
        data = request.get_json()
        name = data.get('artist_name', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'Artist name required'})
        
        artist_name = name
        session_start_time = datetime.now()
        comfyui_ready = False
        
        # Create output directory
        output_dir = f"/workspace/output/{artist_name}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Start Jupyter Lab
        if not jupyter_process or jupyter_process.poll() is not None:
            jupyter_process = subprocess.Popen([
                'jupyter', 'lab',
                '--ip=0.0.0.0',
                '--port=8888',
                '--no-browser',
                '--allow-root',
                '--NotebookApp.token=',
                '--NotebookApp.password='
            ], cwd='/workspace')
        
        # Start ComfyUI
        if not comfyui_process or comfyui_process.poll() is not None:
            subprocess.run(['fuser', '-k', '8188/tcp'], capture_output=True)
            time.sleep(1)
            
            # Activate virtual environment and start ComfyUI
            env = os.environ.copy()
            env['HF_HOME'] = '/workspace'
            env['HF_HUB_ENABLE_HF_TRANSFER'] = '1'
            
            # Set the artist-specific output directory
            artist_output_dir = f"/workspace/output/{artist_name}"
            
            # Start ComfyUI with correct parameters
            comfyui_process = subprocess.Popen([
                '/workspace/venv/bin/python',
                'main.py',
                '--listen', '0.0.0.0',
                '--port', '8188',
                '--use-sage-attention',
                '--output-directory', artist_output_dir
            ], cwd='/workspace/ComfyUI', env=env)
            
            # Start a thread to monitor ComfyUI readiness
            def monitor_comfyui():
                time.sleep(5)  # Give it time to start
                for _ in range(30):  # Check for up to 30 seconds
                    if check_comfyui_ready():
                        break
                    time.sleep(1)
            
            threading.Thread(target=monitor_comfyui, daemon=True).start()
        
        return jsonify({'success': True, 'message': f'Session started for {artist_name}'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/comfyui_status')
def comfyui_status():
    """Check if ComfyUI is ready"""
    return jsonify({'ready': check_comfyui_ready()})

@app.route('/terminate', methods=['POST'])
def terminate():
    """Kill processes on ports and prepare for redirect"""
    try:
        # Kill processes on port 8188 (ComfyUI)
        subprocess.run(['fuser', '-k', '8188/tcp'], capture_output=True)
        
        # Kill processes on port 8888 (Jupyter)
        subprocess.run(['fuser', '-k', '8888/tcp'], capture_output=True)
        
        # Also cleanup our tracked processes
        cleanup_processes()
        
        # Return success - the client will handle the redirect
        return jsonify({'success': True, 'message': 'Processes terminated successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

def cleanup_processes():
    global comfyui_process, jupyter_process
    if comfyui_process:
        comfyui_process.terminate()
    if jupyter_process:
        jupyter_process.terminate()

def signal_handler(sig, frame):
    cleanup_processes()
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Starting Artist Name Selection Server on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=False)