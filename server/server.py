#!/usr/bin/env python3

import os
import subprocess
import time
import threading
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
import signal
import sys

app = Flask(__name__)

# Admins - these users get the admin toggle
ADMINS = [
    "Razvan Matei",
]

def parse_artists_from_script():
    """Parse artist names from artist_names.sh"""
    script_paths = [
        "/usr/local/bin/artist_names.sh",  # Docker container path
        "/workspace/artist_names.sh",       # Workspace path
        os.path.join(os.path.dirname(__file__), "artist_names.sh"),  # Same directory
    ]

    artists = []
    for script_path in script_paths:
        if os.path.exists(script_path):
            try:
                with open(script_path, 'r') as f:
                    content = f.read()
                    # Extract names from ARTISTS=( ... ) block
                    import re
                    match = re.search(r'ARTISTS=\((.*?)\)', content, re.DOTALL)
                    if match:
                        block = match.group(1)
                        # Extract quoted strings
                        names = re.findall(r'"([^"]+)"', block)
                        artists = names
                        break
            except:
                pass

    return artists

# Tool configuration
TOOLS = {
    "ai-toolkit": {
        "name": "AI-Toolkit",
        "port": 7860,
        "install_path": "/workspace/AI-Toolkit",
        "admin_only": False,
    },
    "lora-tool": {
        "name": "LoRA-Tool",
        "port": 7861,
        "install_path": "/workspace/LoRA-Tool",
        "admin_only": False,
    },
    "swarm-ui": {
        "name": "SwarmUI",
        "port": 7801,
        "install_path": "/workspace/SwarmUI",
        "admin_only": False,
    },
    "comfy-ui": {
        "name": "ComfyUI",
        "port": 8188,
        "install_path": "/workspace/ComfyUI",
        "admin_only": False,
    },
    "jupyter-lab": {
        "name": "JupyterLab",
        "port": 8888,
        "install_path": None,  # Always available (part of base image)
        "admin_only": False,
        "user_only": True,  # Only show in user mode, not admin mode
    },
}

# Global state
active_sessions = {}  # {tool_id: {"process": proc, "start_time": datetime, "artist": name}}
current_artist = None
admin_mode = False

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ComfyStudio</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: white;
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            max-width: 450px;
            width: 100%;
        }

        .header {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            margin-bottom: 1.5rem;
        }

        .logo {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 18px;
        }

        h1 {
            color: #333;
            font-size: 1.8rem;
            font-weight: 600;
        }

        .profile-row {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 1.5rem;
        }

        .profile-select {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 15px;
            background: white;
            cursor: pointer;
            transition: border-color 0.2s;
        }

        .profile-select:focus {
            outline: none;
            border-color: #667eea;
        }

        .admin-toggle {
            display: none;
            align-items: center;
            gap: 8px;
        }

        .admin-toggle.visible {
            display: flex;
        }

        .toggle-switch {
            position: relative;
            width: 44px;
            height: 24px;
        }

        .toggle-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .toggle-slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: 0.3s;
            border-radius: 24px;
        }

        .toggle-slider:before {
            position: absolute;
            content: "";
            height: 18px;
            width: 18px;
            left: 3px;
            bottom: 3px;
            background-color: white;
            transition: 0.3s;
            border-radius: 50%;
        }

        input:checked + .toggle-slider {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        input:checked + .toggle-slider:before {
            transform: translateX(20px);
        }

        .tools-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .tool-btn {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 18px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            background: white;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 15px;
            font-weight: 500;
            color: #333;
        }

        .tool-btn:hover {
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        }

        .tool-btn.active {
            background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
            border-color: #22c55e;
            color: white;
        }

        .tool-btn.disabled {
            opacity: 0.5;
            cursor: not-allowed;
            pointer-events: none;
        }

        .tool-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .tool-timer {
            font-size: 13px;
            opacity: 0.9;
        }

        .tool-stop {
            width: 24px;
            height: 24px;
            border-radius: 6px;
            background: rgba(255,255,255,0.3);
            border: none;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            transition: background 0.2s;
        }

        .tool-stop:hover {
            background: rgba(255,255,255,0.5);
        }

        .admin-tool-row {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .admin-tool-btn {
            flex: 1;
            padding: 14px 18px;
            border: 2px solid #f59e0b;
            border-radius: 10px;
            background: #fffbeb;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 15px;
            font-weight: 500;
            color: #92400e;
        }

        .admin-tool-btn:hover {
            background: #fef3c7;
            transform: translateY(-2px);
        }

        .admin-tool-btn.update {
            border-color: #667eea;
            background: #eef2ff;
            color: #4338ca;
        }

        .admin-tool-btn.update:hover {
            background: #e0e7ff;
        }

        .admin-checkbox {
            width: 22px;
            height: 22px;
            cursor: pointer;
            accent-color: #667eea;
        }

        .models-btn {
            width: 100%;
            padding: 14px 18px;
            border: 2px solid #667eea;
            border-radius: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 15px;
            font-weight: 600;
            margin-top: 10px;
        }

        .models-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        /* Models Download Page */
        .models-page {
            display: none;
        }

        .models-page.visible {
            display: block;
        }

        .back-btn {
            display: flex;
            align-items: center;
            gap: 6px;
            background: none;
            border: none;
            color: #667eea;
            cursor: pointer;
            font-size: 14px;
            margin-bottom: 1rem;
            padding: 0;
        }

        .back-btn:hover {
            text-decoration: underline;
        }

        .token-input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            margin-bottom: 10px;
            transition: border-color 0.2s;
        }

        .token-input:focus {
            outline: none;
            border-color: #667eea;
        }

        .model-checkboxes {
            margin: 1rem 0;
        }

        .model-option {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }

        .model-option:last-child {
            border-bottom: none;
        }

        .model-checkbox {
            width: 20px;
            height: 20px;
            accent-color: #667eea;
            cursor: pointer;
        }

        .model-label {
            font-size: 15px;
            color: #333;
            cursor: pointer;
        }

        .done-btn {
            width: 100%;
            padding: 14px 18px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
            color: white;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 15px;
            font-weight: 600;
            margin-top: 1rem;
        }

        .done-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(34, 197, 94, 0.4);
        }

        .hidden {
            display: none !important;
        }

        .main-page {
            display: block;
        }

        .status-message {
            text-align: center;
            padding: 10px;
            margin-top: 10px;
            border-radius: 8px;
            font-size: 14px;
        }

        .status-message.success {
            background: #f0fdf4;
            color: #166534;
        }

        .status-message.error {
            background: #fef2f2;
            color: #991b1b;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Main Page -->
        <div id="mainPage" class="main-page">
            <div class="header">
                <div class="logo">CS</div>
                <h1>ComfyStudio</h1>
            </div>

            <div class="profile-row">
                <select class="profile-select" id="profileSelect">
                    <option value="">Choose Profile</option>
                    {% for artist in artists %}
                    <option value="{{ artist }}" {% if artist == current_artist %}selected{% endif %}>{{ artist }}</option>
                    {% endfor %}
                </select>

                <div class="admin-toggle" id="adminToggle">
                    <label class="toggle-switch">
                        <input type="checkbox" id="adminSwitch" {% if admin_mode %}checked{% endif %}>
                        <span class="toggle-slider"></span>
                    </label>
                </div>
            </div>

            <!-- User Mode Tools -->
            <div class="tools-list" id="userTools">
                {% for tool_id, tool in tools.items() %}
                {% if not tool.get('user_only', False) or not admin_mode %}
                <button class="tool-btn {% if tool_id in active_sessions %}active{% endif %}"
                        data-tool="{{ tool_id }}"
                        onclick="handleToolClick('{{ tool_id }}')">
                    <span class="tool-info">
                        <span class="tool-name">{{ tool.name }}</span>
                        {% if tool_id in active_sessions %}
                        <span class="tool-timer" data-start="{{ active_sessions[tool_id].start_time }}">00:00</span>
                        {% endif %}
                    </span>
                    {% if tool_id in active_sessions %}
                    <button class="tool-stop" onclick="event.stopPropagation(); stopSession('{{ tool_id }}')">✕</button>
                    {% endif %}
                </button>
                {% endif %}
                {% endfor %}
            </div>

            <!-- Admin Mode Tools -->
            <div class="tools-list hidden" id="adminTools">
                {% for tool_id, tool in tools.items() %}
                {% if not tool.get('user_only', False) %}
                <div class="admin-tool-row">
                    <button class="admin-tool-btn {% if tool.install_path and is_installed(tool.install_path) %}update{% endif %}"
                            data-tool="{{ tool_id }}"
                            onclick="handleAdminToolClick('{{ tool_id }}')">
                        {% if tool.install_path %}
                            {% if is_installed(tool.install_path) %}
                            Update {{ tool.name }}
                            {% else %}
                            Install {{ tool.name }}
                            {% endif %}
                        {% else %}
                        {{ tool.name }} (Built-in)
                        {% endif %}
                    </button>
                    <input type="checkbox" class="admin-checkbox" data-tool="{{ tool_id }}">
                </div>
                {% endif %}
                {% endfor %}

                <button class="models-btn" onclick="showModelsPage()">
                    Models Download
                </button>
            </div>

            <div id="statusMessage" class="status-message hidden"></div>
        </div>

        <!-- Models Download Page -->
        <div id="modelsPage" class="models-page">
            <button class="back-btn" onclick="hideModelsPage()">
                ← Back
            </button>

            <div class="header">
                <div class="logo">CS</div>
                <h1>ComfyStudio</h1>
            </div>

            <div class="profile-row">
                <select class="profile-select" disabled>
                    <option>{{ current_artist or 'Choose Profile' }}</option>
                </select>
                <div class="admin-toggle visible">
                    <label class="toggle-switch">
                        <input type="checkbox" checked disabled>
                        <span class="toggle-slider"></span>
                    </label>
                </div>
            </div>

            <input type="text" class="token-input" id="hfToken" placeholder="HuggingFace Token">
            <input type="text" class="token-input" id="civitToken" placeholder="CivitAI Token">

            <div class="model-checkboxes">
                <div class="model-option">
                    <input type="checkbox" class="model-checkbox" id="modelQwen" value="qwen">
                    <label class="model-label" for="modelQwen">Qwen</label>
                </div>
                <div class="model-option">
                    <input type="checkbox" class="model-checkbox" id="modelFlux" value="flux">
                    <label class="model-label" for="modelFlux">Flux</label>
                </div>
                <div class="model-option">
                    <input type="checkbox" class="model-checkbox" id="modelKrita" value="krita">
                    <label class="model-label" for="modelKrita">Krita Diffusion</label>
                </div>
                <div class="model-option">
                    <input type="checkbox" class="model-checkbox" id="modelWan" value="wan">
                    <label class="model-label" for="modelWan">Wan 2.2</label>
                </div>
            </div>

            <button class="done-btn" onclick="downloadModels()">
                Done
            </button>

            <div id="modelsStatusMessage" class="status-message hidden"></div>
        </div>
    </div>

    <script>
        const admins = {{ admins | tojson }};
        let currentArtist = '{{ current_artist or "" }}';
        let adminMode = {{ 'true' if admin_mode else 'false' }};
        let sessionTimers = {};

        // Initialize on load
        document.addEventListener('DOMContentLoaded', function() {
            updateUI();
            startTimers();
        });

        // Profile selection change
        document.getElementById('profileSelect').addEventListener('change', function() {
            currentArtist = this.value;

            // Update server with new artist
            fetch('/set_artist', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ artist: currentArtist })
            });

            updateUI();
        });

        // Admin toggle change
        document.getElementById('adminSwitch').addEventListener('change', function() {
            adminMode = this.checked;

            fetch('/set_admin_mode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ admin_mode: adminMode })
            });

            updateUI();
        });

        function updateUI() {
            const adminToggle = document.getElementById('adminToggle');
            const userTools = document.getElementById('userTools');
            const adminTools = document.getElementById('adminTools');

            // Show admin toggle only for admins
            if (currentArtist && admins.includes(currentArtist)) {
                adminToggle.classList.add('visible');
            } else {
                adminToggle.classList.remove('visible');
                adminMode = false;
                document.getElementById('adminSwitch').checked = false;
            }

            // Toggle between user and admin tools
            if (adminMode) {
                userTools.classList.add('hidden');
                adminTools.classList.remove('hidden');
            } else {
                userTools.classList.remove('hidden');
                adminTools.classList.add('hidden');
            }
        }

        function handleToolClick(toolId) {
            if (!currentArtist) {
                showStatus('Please select a profile first', 'error');
                return;
            }

            const btn = document.querySelector(`[data-tool="${toolId}"]`);
            if (btn.classList.contains('active')) {
                // Tool is running - open it in new tab
                const runpodId = '{{ runpod_id }}';
                const tool = {{ tools | tojson }}[toolId];
                const url = `https://${runpodId}-${tool.port}.proxy.runpod.net`;
                window.open(url, '_blank');
            } else {
                // Start the tool
                startSession(toolId);
            }
        }

        function startSession(toolId) {
            fetch('/start_session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tool_id: toolId, artist: currentArtist })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showStatus(`${data.tool_name} started`, 'success');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showStatus(data.message, 'error');
                }
            });
        }

        function stopSession(toolId) {
            fetch('/stop_session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tool_id: toolId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showStatus(`${data.tool_name} stopped`, 'success');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showStatus(data.message, 'error');
                }
            });
        }

        function handleAdminToolClick(toolId) {
            // Placeholder for install/update functionality
            showStatus(`Install/Update for ${toolId} - Coming soon`, 'success');
        }

        function showModelsPage() {
            document.getElementById('mainPage').classList.add('hidden');
            document.getElementById('modelsPage').classList.add('visible');
        }

        function hideModelsPage() {
            document.getElementById('modelsPage').classList.remove('visible');
            document.getElementById('mainPage').classList.remove('hidden');
        }

        function downloadModels() {
            const hfToken = document.getElementById('hfToken').value;
            const civitToken = document.getElementById('civitToken').value;

            const selectedModels = [];
            document.querySelectorAll('.model-checkbox:checked').forEach(cb => {
                selectedModels.push(cb.value);
            });

            if (selectedModels.length === 0) {
                showModelsStatus('Please select at least one model set', 'error');
                return;
            }

            // Placeholder for download functionality
            showModelsStatus(`Download started for: ${selectedModels.join(', ')}`, 'success');
        }

        function showStatus(message, type) {
            const el = document.getElementById('statusMessage');
            el.textContent = message;
            el.className = `status-message ${type}`;
            el.classList.remove('hidden');
            setTimeout(() => el.classList.add('hidden'), 3000);
        }

        function showModelsStatus(message, type) {
            const el = document.getElementById('modelsStatusMessage');
            el.textContent = message;
            el.className = `status-message ${type}`;
            el.classList.remove('hidden');
            setTimeout(() => el.classList.add('hidden'), 3000);
        }

        function startTimers() {
            document.querySelectorAll('.tool-timer').forEach(timer => {
                const startTime = new Date(timer.dataset.start);
                setInterval(() => {
                    const elapsed = Math.floor((new Date() - startTime) / 1000);
                    const minutes = Math.floor(elapsed / 60);
                    const seconds = elapsed % 60;
                    timer.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                }, 1000);
            });
        }
    </script>
</body>
</html>
"""

def get_runpod_id():
    """Get RunPod instance ID from environment"""
    return os.environ.get('RUNPOD_POD_ID', 'localhost')

def is_installed(path):
    """Check if a tool is installed by checking directory existence"""
    if path is None:
        return True
    return os.path.isdir(path)

def get_existing_artists():
    """Get list of existing artist folders, fallback to artist_names.sh"""
    output_dir = "/workspace/ComfyUI/output"
    artists = []
    try:
        if os.path.exists(output_dir):
            for item in os.listdir(output_dir):
                item_path = os.path.join(output_dir, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    artists.append(item)
            artists.sort()
    except:
        pass

    # If no artists found, parse from artist_names.sh
    if not artists:
        artists = parse_artists_from_script()

    return artists

@app.route('/')
def index():
    artists = get_existing_artists()
    return render_template_string(
        HTML_TEMPLATE,
        artists=artists,
        admins=ADMINS,
        tools=TOOLS,
        current_artist=current_artist,
        admin_mode=admin_mode,
        active_sessions={k: {"start_time": v["start_time"].isoformat()} for k, v in active_sessions.items()},
        runpod_id=get_runpod_id(),
        is_installed=is_installed
    )

@app.route('/set_artist', methods=['POST'])
def set_artist():
    global current_artist, admin_mode
    data = request.get_json()
    current_artist = data.get('artist', '')

    # Reset admin mode if not an admin
    if current_artist not in ADMINS:
        admin_mode = False

    return jsonify({'success': True})

@app.route('/set_admin_mode', methods=['POST'])
def set_admin_mode():
    global admin_mode
    data = request.get_json()

    # Only allow admin mode for admins
    if current_artist in ADMINS:
        admin_mode = data.get('admin_mode', False)

    return jsonify({'success': True})

@app.route('/start_session', methods=['POST'])
def start_session():
    global active_sessions

    data = request.get_json()
    tool_id = data.get('tool_id')
    artist = data.get('artist')

    if not tool_id or tool_id not in TOOLS:
        return jsonify({'success': False, 'message': 'Invalid tool'})

    if not artist:
        return jsonify({'success': False, 'message': 'No artist selected'})

    tool = TOOLS[tool_id]

    # Create artist output directory if ComfyUI
    if tool_id == 'comfy-ui':
        output_dir = f"/workspace/ComfyUI/output/{artist}"
        os.makedirs(output_dir, exist_ok=True)

    # Placeholder: In the future, this will actually start the tool
    # For now, just track the session
    active_sessions[tool_id] = {
        "process": None,
        "start_time": datetime.now(),
        "artist": artist
    }

    return jsonify({
        'success': True,
        'tool_name': tool['name'],
        'message': f'{tool["name"]} session started'
    })

@app.route('/stop_session', methods=['POST'])
def stop_session():
    global active_sessions

    data = request.get_json()
    tool_id = data.get('tool_id')

    if not tool_id or tool_id not in TOOLS:
        return jsonify({'success': False, 'message': 'Invalid tool'})

    tool = TOOLS[tool_id]

    # Kill the process if running
    if tool_id in active_sessions:
        session = active_sessions[tool_id]
        if session.get("process"):
            session["process"].terminate()

        # Kill by port
        port = tool['port']
        subprocess.run(['fuser', '-k', f'{port}/tcp'], capture_output=True)

        del active_sessions[tool_id]

    return jsonify({
        'success': True,
        'tool_name': tool['name'],
        'message': f'{tool["name"]} stopped'
    })

@app.route('/tool_status/<tool_id>')
def tool_status(tool_id):
    if tool_id not in TOOLS:
        return jsonify({'error': 'Invalid tool'})

    tool = TOOLS[tool_id]
    is_running = tool_id in active_sessions

    return jsonify({
        'tool_id': tool_id,
        'name': tool['name'],
        'running': is_running,
        'installed': is_installed(tool.get('install_path'))
    })

def cleanup_sessions():
    """Cleanup all active sessions"""
    for tool_id, session in active_sessions.items():
        if session.get("process"):
            session["process"].terminate()
        tool = TOOLS.get(tool_id)
        if tool:
            subprocess.run(['fuser', '-k', f'{tool["port"]}/tcp'], capture_output=True)

def signal_handler(sig, frame):
    cleanup_sessions()
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("Starting ComfyStudio on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=False)
