#!/usr/bin/env python3
# ABOUTME: Main Flask server for SF AI Workbench
# ABOUTME: Handles routes, tool management, and user profiles

import json
import os
import signal
import socket
import subprocess
import sys
import threading
import time
from datetime import datetime

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    render_template_string,
    request,
    url_for,
)

# Get the directory where server.py is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(SCRIPT_DIR, "static"),
    template_folder=os.path.join(SCRIPT_DIR, "templates"),
)

# Repository path (set by start_server.sh)
REPO_DIR = os.environ.get("REPO_DIR", "/workspace/runpod-ggs")

# User process log file for streaming tool startup logs (legacy, kept for admin actions)
USER_LOG_FILE = "/tmp/comfystudio_user_log.txt"
user_process_running = False


def get_tool_log_file(tool_id):
    """Get the log file path for a specific tool"""
    return f"/tmp/comfystudio_{tool_id}.log"


# Import user management module
from user_management import (
    SUPERADMIN_NAME,
    add_users_bulk,
    delete_user,
    ensure_razvan_exists,
    get_admins_list,
    get_all_user_names,
    initialize_users,
    is_admin_check,
    load_users_from_file,
    save_users_to_file,
    set_user_admin,
)

# Paths for user management
USERS_JSON_PATH = "/workspace/users.json"
USERS_OUTPUT_DIR = "/workspace/ComfyUI/output"

# Initialize users and admins from JSON/folders
USERS_DATA, ADMINS = initialize_users(USERS_JSON_PATH, USERS_OUTPUT_DIR)


def is_admin(user_name):
    """Check if user is an admin (case-insensitive). Razvan is always admin."""
    return is_admin_check(user_name, ADMINS)


def reload_users():
    """Reload users and admins from storage"""
    global USERS_DATA, ADMINS
    USERS_DATA, ADMINS = initialize_users(USERS_JSON_PATH, USERS_OUTPUT_DIR)


def get_setup_script(tool_id, script_type):
    """Get path to setup script for a tool. script_type is 'install' or 'start'"""
    # Map tool IDs to setup folder names
    folder_map = {
        "ai-toolkit": "ai-toolkit",
        "lora-tool": "lora-tool",
        "swarm-ui": "swarm-ui",
        "comfy-ui": "comfy",
    }

    folder = folder_map.get(tool_id)
    if not folder:
        return None

    # Script naming: install_comfy.sh, start_comfy.sh, etc.
    # Replace hyphens with underscores for script names
    script_folder_name = folder.replace("-", "_")
    script_name = f"{script_type}_{script_folder_name}.sh"
    script_path = os.path.join(REPO_DIR, "setup", folder, script_name)
    if os.path.exists(script_path):
        return script_path
    return None


def parse_model_destinations(script_path):
    """
    Parse a download script to extract destination model filenames.
    Returns list of full destination file paths.
    """
    import re

    destinations = []
    try:
        with open(script_path, "r") as f:
            content = f.read()
            lines = content.splitlines()

        current_dir = None

        # Join continuation lines (backslash at end of line)
        joined_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            while line.rstrip().endswith("\\") and i + 1 < len(lines):
                line = line.rstrip()[:-1] + " " + lines[i + 1].strip()
                i += 1
            joined_lines.append(line)
            i += 1

        for line in joined_lines:
            line_stripped = line.strip()

            # Track cd commands to know current directory
            # Match: cd "$MODELS_DIR/subdir" or cd /workspace/models/subdir
            cd_match = re.match(r'cd\s+["\']?([^"\';\s]+)["\']?', line_stripped)
            if cd_match:
                cd_path = cd_match.group(1)
                # Expand $MODELS_DIR variable
                cd_path = cd_path.replace("$MODELS_DIR", "/workspace/models")
                cd_path = cd_path.replace("${MODELS_DIR}", "/workspace/models")
                current_dir = cd_path
                continue

            # Pattern 1: -O filename (wget) - just filename, need to combine with current_dir
            o_match = re.search(
                r"-[Oo]\s+([^\s\\]+\.(?:safetensors|gguf|bin|pt|pth|ckpt))",
                line_stripped,
            )
            if o_match:
                filename = o_match.group(1)
                if current_dir and not filename.startswith("/"):
                    destinations.append(os.path.join(current_dir, filename))
                else:
                    destinations.append(filename)
                continue

            # Pattern 2: download "url" "dest" function calls (full path in dest)
            dl_match = re.search(r'download\s+"[^"]+"\s+"([^"]+)"', line_stripped)
            if dl_match:
                dest = dl_match.group(1)
                if any(
                    ext in dest
                    for ext in [".safetensors", ".gguf", ".bin", ".pt", ".pth", ".ckpt"]
                ):
                    destinations.append(dest)

    except Exception as e:
        print(f"Error parsing script {script_path}: {e}")

    return destinations


def check_models_installed(destinations):
    """
    Check how many model files from a script are installed.
    Returns tuple of (installed_count, total_count).
    """
    if not destinations:
        return (0, 0)

    installed = 0
    for dest in destinations:
        # Normalize paths
        if dest.startswith("/"):
            full_path = dest
        elif dest.startswith("ComfyUI/"):
            full_path = os.path.join("/workspace", dest)
        else:
            full_path = os.path.join("/workspace", dest)

        if os.path.exists(full_path):
            installed += 1

    return (installed, len(destinations))


def get_download_scripts():
    """
    Scan setup/download-models/ directory and return available download scripts.
    Returns list of dicts with 'id', 'name', 'path', 'installed', 'total' for each script.
    """
    scripts = []
    download_dir = os.path.join(REPO_DIR, "setup", "download-models")

    if not os.path.exists(download_dir):
        return scripts

    try:
        for filename in os.listdir(download_dir):
            if filename.endswith(".sh"):
                # Convert filename to display name
                # e.g., "download_z_image_turbo.sh" -> "Z Image Turbo"
                # e.g., "download_flux_models.sh" -> "Flux Models"
                name = filename.replace(".sh", "")
                name = name.replace("download_", "")
                name = name.replace("_", " ")
                name = name.title()

                script_path = os.path.join(download_dir, filename)
                destinations = parse_model_destinations(script_path)
                installed, total = check_models_installed(destinations)

                scripts.append(
                    {
                        "id": filename.replace(".sh", ""),
                        "name": name,
                        "filename": filename,
                        "path": script_path,
                        "installed": installed,
                        "total": total,
                    }
                )
    except Exception as e:
        print(f"Error scanning download scripts: {e}")

    # Sort by name (case-insensitive)
    scripts.sort(key=lambda x: x["name"].lower())
    return scripts


def get_custom_nodes():
    """
    Parse custom nodes from nodes.txt configuration file.
    Returns list of dicts with 'name', 'repo_url', 'installed' for each node.
    """
    nodes = []
    nodes_config = os.path.join(REPO_DIR, "setup", "custom-nodes", "nodes.txt")
    custom_nodes_dir = "/workspace/ComfyUI/custom_nodes"

    if not os.path.exists(nodes_config):
        return nodes

    try:
        with open(nodes_config, "r") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue

                repo_url = line
                # Extract repo name from URL
                repo_name = os.path.basename(repo_url.replace(".git", ""))
                node_path = os.path.join(custom_nodes_dir, repo_name)

                nodes.append(
                    {
                        "name": repo_name,
                        "repo_url": repo_url,
                        "repo_name": repo_name,
                        "installed": os.path.isdir(node_path),
                    }
                )
    except Exception as e:
        print(f"Error parsing custom nodes config: {e}")

    # Sort nodes by name (case-insensitive)
    nodes.sort(key=lambda x: x["name"].lower())
    return nodes


# Tool configuration
TOOLS = {
    "ai-toolkit": {
        "name": "AI-Toolkit",
        "port": 8675,
        "install_path": "/workspace/ai-toolkit",
        "admin_only": False,
    },
    "lora-tool": {
        "name": "LoRA-Tool",
        "port": 3000,
        "install_path": None,  # Runs directly from repo, no install needed
        "admin_only": False,
    },
    "swarm-ui": {
        "name": "SwarmUI",
        "port": 7861,
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
LOG_FILE = "/tmp/comfystudio.log"
running_process = None  # Track the currently running admin process

# HTML Template
HTML_TEMPLATE = r"""
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
            min-width: 0;
            max-width: calc(100% - 60px);
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
            display: flex;
            align-items: center;
            gap: 8px;
            visibility: hidden;
            flex-shrink: 0;
        }

        .admin-toggle.visible {
            visibility: visible;
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

        .tool-row {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .tool-btn {
            flex: 1;
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
            cursor: pointer;
        }

        .tool-btn.starting {
            background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
            border-color: #f59e0b;
            color: white;
            cursor: not-allowed;
            pointer-events: none;
        }

        .tool-btn:disabled {
            cursor: not-allowed;
            opacity: 0.8;
        }

        .tool-btn.active:hover {
            border-color: #16a34a;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
        }

        .tool-btn.starting:hover {
            transform: none;
            box-shadow: none;
        }

        .tool-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .tool-timer {
            font-size: 13px;
            opacity: 0.9;
            font-family: monospace;
        }

        .tool-stop-btn {
            padding: 10px 20px;
            border: 2px solid #ef4444;
            border-radius: 10px;
            background: white;
            color: #ef4444;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
        }

        .tool-stop-btn:hover {
            background: #ef4444;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
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

        .admin-tool-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .admin-tool-btn:disabled:hover {
            background: #fffbeb;
            transform: none;
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
            justify-content: center;
            background: none;
            border: none;
            color: #667eea;
            cursor: pointer;
            padding: 8px;
            border-radius: 8px;
            transition: background-color 0.2s;
        }

        .back-btn:hover {
            background-color: rgba(102, 126, 234, 0.1);
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

        /* Terminal styles */
        .terminal-container {
            display: none;
            margin-top: 15px;
        }

        .terminal-container.visible {
            display: block;
        }

        .terminal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #1e1e1e;
            padding: 8px 12px;
            border-radius: 8px 8px 0 0;
        }

        .terminal-title {
            color: #4ade80;
            font-size: 12px;
            font-weight: 600;
        }

        .terminal-timer {
            color: #fbbf24;
            font-size: 12px;
            font-weight: 600;
            font-family: monospace;
            margin-left: 10px;
        }

        .tool-status {
            color: #888;
            font-size: 11px;
            font-style: italic;
        }

        .tool-btn.disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .terminal-controls {
            display: flex;
            gap: 8px;
        }

        .terminal-btn {
            background: #333;
            border: none;
            color: #888;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
        }

        .terminal-btn:hover {
            background: #444;
            color: #fff;
        }

        .terminal {
            background: #1e1e1e;
            color: #d4d4d4;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 12px;
            line-height: 1.5;
            padding: 12px;
            border-radius: 0 0 8px 8px;
            height: 250px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .terminal::-webkit-scrollbar {
            width: 8px;
        }

        .terminal::-webkit-scrollbar-track {
            background: #1e1e1e;
        }

        .terminal::-webkit-scrollbar-thumb {
            background: #444;
            border-radius: 4px;
        }

        .terminal .error {
            color: #f87171;
        }

        .terminal .success {
            color: #4ade80;
        }

        .terminal .info {
            color: #60a5fa;
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
                <div class="tool-row">
                    {% set installed = is_installed(tool.get('install_path')) %}
                    <button class="tool-btn {% if tool_id in active_sessions %}active{% endif %}{% if not installed %} disabled{% endif %}"
                            data-tool="{{ tool_id }}"
                            onclick="handleToolClick('{{ tool_id }}')"
                            {% if not installed %}disabled{% endif %}>
                        <span class="tool-info">
                            <span class="tool-name">{{ tool.name }}</span>
                            {% if not installed %}
                            <span class="tool-status">Not Installed</span>
                            {% elif tool_id in active_sessions %}
                            <span class="tool-timer" data-start="{{ active_sessions[tool_id].start_time }}">00:00</span>
                            {% endif %}
                        </span>
                    </button>
                    {% if tool_id in active_sessions %}
                    <button class="tool-stop-btn" onclick="stopToolSession('{{ tool_id }}')">Stop</button>
                    {% endif %}
                </div>
                {% endif %}
                {% endfor %}

                <!-- Terminal output for user mode -->
                <div class="terminal-container" id="userTerminalContainer">
                    <div class="terminal-header">
                        <div style="display: flex; align-items: center; gap: 10px; margin-right: auto;">
                            <button class="terminal-btn" onclick="minimizeUserTerminal()">−</button>
                            <span class="terminal-title">Starting...</span>
                        </div>
                        <div class="terminal-controls">
                            <button class="terminal-btn" onclick="copyUserTerminal()">Copy</button>
                            <button class="terminal-btn" onclick="clearUserTerminal()">Clear</button>
                        </div>
                    </div>
                    <div class="terminal" id="userTerminal"></div>
                </div>
            </div>

            <!-- Admin Mode Tools -->
            <div class="tools-list hidden" id="adminTools">
                {% for tool_id, tool in tools.items() %}
                {% if not tool.get('user_only', False) %}
                <div class="admin-tool-row">
                    {% if tool.install_path %}
                        {% if is_installed(tool.install_path) %}
                        <!-- Tool is installed - show Reinstall and Update buttons -->
                        <button class="admin-tool-btn"
                                id="reinstall-btn-{{ tool_id }}"
                                data-tool="{{ tool_id }}"
                                data-action="reinstall"
                                onclick="handleAdminAction('{{ tool_id }}', 'reinstall')">
                            Reinstall {{ tool.name }}
                        </button>
                        <button class="admin-tool-btn update"
                                id="update-btn-{{ tool_id }}"
                                data-tool="{{ tool_id }}"
                                data-action="update"
                                onclick="handleAdminAction('{{ tool_id }}', 'update')">
                            Update {{ tool.name }}
                        </button>
                        {% else %}
                        <!-- Tool is not installed - show Install button -->
                        <button class="admin-tool-btn"
                                id="install-btn-{{ tool_id }}"
                                data-tool="{{ tool_id }}"
                                data-action="install"
                                onclick="handleAdminAction('{{ tool_id }}', 'install')">
                            Install {{ tool.name }}
                        </button>
                        {% endif %}
                    {% else %}
                        <!-- Built-in tool (like JupyterLab) -->
                        <button class="admin-tool-btn" disabled>
                            {{ tool.name }} (Built-in)
                        </button>
                    {% endif %}
                </div>
                {% endif %}
                {% endfor %}

                <button class="models-btn" onclick="showModelsPage()">
                    Models Download
                </button>

                <button class="models-btn" onclick="showCustomNodesPage()">
                    Custom Nodes
                </button>

                <!-- Terminal output -->
                <div class="terminal-container" id="terminalContainer">
                    <div class="terminal-header">
                        <div style="display: flex; align-items: center; gap: 10px; margin-right: auto;">
                            <button class="terminal-btn" onclick="minimizeTerminal()">−</button>
                            <span class="terminal-title">Terminal Output</span>
                            <span class="terminal-timer" id="terminalTimer"></span>
                        </div>
                        <div class="terminal-controls">
                            <button class="terminal-btn" onclick="copyTerminal()">Copy</button>
                            <button class="terminal-btn" onclick="clearTerminal()">Clear</button>
                        </div>
                    </div>
                    <div class="terminal" id="terminal"></div>
                </div>
            </div>

            <div id="statusMessage" class="status-message hidden"></div>
        </div>

        <!-- Models Download Page -->
        <div id="modelsPage" class="models-page">
            <div class="header" style="position: relative;">
                <button class="back-btn" onclick="hideModelsPage()" style="position: absolute; left: 0; top: 50%; transform: translateY(-50%);">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M19 12H5M12 19l-7-7 7-7"/>
                    </svg>
                </button>
                <div class="logo">CS</div>
                <h1>ComfyStudio</h1>
            </div>

            <input type="text" class="token-input" id="hfToken" placeholder="HuggingFace Token">
            <input type="text" class="token-input" id="civitToken" placeholder="CivitAI Token">

            <div class="model-checkboxes">
                <div class="model-option" style="border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; margin-bottom: 10px;">
                    <input type="checkbox" class="model-checkbox" id="downloadAllModels" onchange="toggleAllModels(this)">
                    <label class="model-label" for="downloadAllModels" style="font-weight: bold;">
                        Download All
                    </label>
                </div>
                {% for script in download_scripts %}
                <div class="model-option">
                    <input type="checkbox" class="model-checkbox" id="model_{{ script.id }}" value="{{ script.filename }}">
                    <label class="model-label" for="model_{{ script.id }}">
                        {{ script.name }}
                        {% if script.total > 0 %}
                            {% if script.installed == script.total %}
                                <span style="color: #10b981; font-size: 12px;"> ✓ Installed</span>
                            {% elif script.installed > 0 %}
                                <span style="color: #f59e0b; font-size: 12px;"> ({{ script.installed }}/{{ script.total }})</span>
                            {% else %}
                                <span style="color: #6b7280; font-size: 12px;"> (new)</span>
                            {% endif %}
                        {% endif %}
                    </label>
                </div>
                {% endfor %}
            </div>

            <button class="done-btn" onclick="downloadModels()" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                Download
            </button>

            <div id="modelsStatusMessage" class="status-message hidden"></div>

            <!-- Terminal output for models page -->
            <div class="terminal-container" id="modelsTerminalContainer">
                <div class="terminal-header">
                    <div style="display: flex; align-items: center; gap: 10px; margin-right: auto;">
                        <button class="terminal-btn" onclick="minimizeModelsTerminal()">−</button>
                        <span class="terminal-title">Download Progress</span>
                        <span class="terminal-timer" id="modelsTerminalTimer"></span>
                    </div>
                    <div class="terminal-controls">
                        <button class="terminal-btn" onclick="copyModelsTerminal()">Copy</button>
                        <button class="terminal-btn" onclick="clearModelsTerminal()">Clear</button>
                    </div>
                </div>
                <div class="terminal" id="modelsTerminal"></div>
            </div>
        </div>

        <!-- Custom Nodes Page -->
        <div id="customNodesPage" class="models-page">
            <div class="header" style="position: relative;">
                <button class="back-btn" onclick="hideCustomNodesPage()" style="position: absolute; left: 0; top: 50%; transform: translateY(-50%);">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M19 12H5M12 19l-7-7 7-7"/>
                    </svg>
                </button>
                <div class="logo">CS</div>
                <h1>ComfyStudio</h1>
            </div>

            <div class="model-checkboxes">
                <div class="model-option" style="border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; margin-bottom: 10px;">
                    <input type="checkbox" class="model-checkbox" id="installAllNodes" onchange="toggleAllNodes(this)">
                    <label class="model-label" for="installAllNodes" style="font-weight: bold;">
                        Install All
                    </label>
                </div>
                {% for node in custom_nodes %}
                <div class="model-option">
                    <input type="checkbox" class="model-checkbox" id="node_{{ loop.index }}" value="{{ node.repo_name }}" {% if node.installed %}checked{% endif %}>
                    <label class="model-label" for="node_{{ loop.index }}">
                        {{ node.name }}
                        {% if node.installed %}<span style="color: #10b981; font-size: 12px;"> ✓ Installed</span>{% endif %}
                    </label>
                </div>
                {% endfor %}
            </div>

            <div style="display: flex; gap: 10px; max-width: 600px; margin: 20px auto;">
                <button class="done-btn" onclick="installCustomNodes()" style="flex: 1;">
                    Install Selected
                </button>
                <button class="done-btn" onclick="updateCustomNodes()" style="flex: 1; background: #667eea;">
                    Update Installed
                </button>
            </div>

            <div id="customNodesStatusMessage" class="status-message hidden"></div>

            <!-- Terminal output for custom nodes page -->
            <div class="terminal-container" id="customNodesTerminalContainer">
                <div class="terminal-header">
                    <div style="display: flex; align-items: center; gap: 10px; margin-right: auto;">
                        <button class="terminal-btn" onclick="minimizeCustomNodesTerminal()">−</button>
                        <span class="terminal-title">Installation Progress</span>
                        <span class="terminal-timer" id="customNodesTerminalTimer"></span>
                    </div>
                    <div class="terminal-controls">
                        <button class="terminal-btn" onclick="copyCustomNodesTerminal()">Copy</button>
                        <button class="terminal-btn" onclick="clearCustomNodesTerminal()">Clear</button>
                    </div>
                </div>
                <div class="terminal" id="customNodesTerminal"></div>
            </div>
        </div>
    </div>

    <script>
        var admins = {{ admins | tojson | safe }};
        var currentArtist = "{{ current_artist | default('', true) | e }}";
        var adminMode = {% if admin_mode %}true{% else %}false{% endif %};
        var sessionTimers = {};

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

            // Check if current user is admin (with safety checks)
            let isAdmin = false;
            if (currentArtist && Array.isArray(admins) && admins.length > 0) {
                const currentLower = currentArtist.trim().toLowerCase();
                isAdmin = admins.some(function(admin) {
                    return admin && admin.trim().toLowerCase() === currentLower;
                });
            }

            if (isAdmin) {
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

            var btn = document.querySelector('[data-tool="' + toolId + '"]');
            if (btn.classList.contains('active')) {
                // Tool is running - open it in new tab
                var runpodId = '{{ runpod_id | e }}';
                var tool = {{ tools | tojson }}[toolId];
                var url = 'https://' + runpodId + '-' + tool.port + '.proxy.runpod.net';
                window.open(url, '_blank');
            } else if (!btn.classList.contains('starting')) {
                // Start the tool (only if not already starting)
                btn.classList.add('starting');
                // Update button text to show starting state
                var toolNameSpan = btn.querySelector('.tool-name');
                if (toolNameSpan) {
                    toolNameSpan.setAttribute('data-original-text', toolNameSpan.textContent);
                    toolNameSpan.textContent = 'Starting ' + toolNameSpan.textContent + '...';
                }
                startSession(toolId, btn);
            }
        }

        function startSession(toolId, btn) {
            var tools = {{ tools | tojson }};
            var toolName = tools[toolId] ? tools[toolId].name : toolId;

            // Show terminal
            clearUserTerminal();
            showUserTerminal(toolName);

            fetch('/start_session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tool_id: toolId, artist: currentArtist })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Start polling for ready status and logs
                    startPollingUserLogs(toolId, toolName);
                } else {
                    showStatus(data.message, 'error');
                    // Reset button state on error
                    if (btn) {
                        btn.classList.remove('starting');
                        var toolNameSpan = btn.querySelector('.tool-name');
                        if (toolNameSpan && toolNameSpan.getAttribute('data-original-text')) {
                            toolNameSpan.textContent = toolNameSpan.getAttribute('data-original-text');
                        }
                    }
                }
            })
            .catch(function(error) {
                showStatus('Error: ' + error, 'error');
                // Reset button state on error
                if (btn) {
                    btn.classList.remove('starting');
                    var toolNameSpan = btn.querySelector('.tool-name');
                    if (toolNameSpan && toolNameSpan.getAttribute('data-original-text')) {
                        toolNameSpan.textContent = toolNameSpan.getAttribute('data-original-text');
                    }
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
                    showStatus(data.tool_name + ' stopped', 'success');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showStatus(data.message, 'error');
                }
            });
        }

        function handleAdminAction(toolId, action) {
            // Get the button and disable it
            var btnId = action + '-btn-' + toolId;
            var btn = document.getElementById(btnId);
            // Get tool name from tools object
            var tools = {{ tools | tojson | safe }};
            var toolName = tools[toolId] ? tools[toolId].name : toolId;

            if (btn) {
                btn.disabled = true;
                btn.textContent = action.charAt(0).toUpperCase() + action.slice(1) + 'ing ' + toolName + '...';
                // Track active button globally so we can re-enable it when done
                activeAdminButton = btn;
                activeAdminAction = action;
                activeAdminToolId = toolId;
            }

            // Update terminal title based on action
            var terminalTitle = document.querySelector('#terminalContainer .terminal-title');
            if (terminalTitle) {
                var actionText = action.charAt(0).toUpperCase() + action.slice(1) + 'ing';
                terminalTitle.textContent = actionText + ' ' + toolName;
            }

            // Clear and show terminal, start timer
            clearTerminal();
            showTerminal();
            startTerminalTimer('terminalTimer');

            fetch('/admin_action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tool_id: toolId, action: action })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showStatus(data.message, 'success');
                    // Start polling for logs
                    startPollingLogs();
                } else {
                    showStatus(data.message, 'error');
                    appendToTerminal('Error: ' + data.message + '\n', 'error');
                    // Re-enable button on error
                    if (btn) {
                        btn.disabled = false;
                        btn.textContent = action.charAt(0).toUpperCase() + action.slice(1) + ' ' + toolId;
                    }
                }
            });
        }

        function stopToolSession(toolId) {
            fetch('/stop_session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tool_id: toolId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showStatus(data.message, 'success');
                    // Reload page to update UI
                    setTimeout(function() {
                        location.reload();
                    }, 1000);
                } else {
                    showStatus(data.message, 'error');
                }
            });
        }

        function showModelsPage() {
            document.getElementById('mainPage').classList.add('hidden');
            document.getElementById('modelsPage').classList.add('visible');
        }

        function hideModelsPage() {
            document.getElementById('modelsPage').classList.remove('visible');
            document.getElementById('mainPage').classList.remove('hidden');
        }

        function showCustomNodesPage() {
            document.getElementById('mainPage').classList.add('hidden');
            document.getElementById('customNodesPage').classList.add('visible');

            // Reset custom nodes terminal title
            var terminalTitle = document.querySelector('#customNodesTerminalContainer .terminal-title');
            if (terminalTitle) {
                terminalTitle.textContent = 'Installation Progress';
            }
        }

        function hideCustomNodesPage() {
            document.getElementById('customNodesPage').classList.remove('visible');
            document.getElementById('mainPage').classList.remove('hidden');
        }

        function toggleAllModels(checkbox) {
            var modelCheckboxes = document.querySelectorAll('#modelsPage .model-checkbox:not(#downloadAllModels)');
            modelCheckboxes.forEach(function(cb) {
                cb.checked = checkbox.checked;
            });
        }

        function toggleAllNodes(checkbox) {
            var nodeCheckboxes = document.querySelectorAll('#customNodesPage .model-checkbox:not(#installAllNodes)');
            nodeCheckboxes.forEach(function(cb) {
                cb.checked = checkbox.checked;
            });
        }

        function installCustomNodes() {
            // Update terminal title and start timer
            var terminalTitle = document.querySelector('#customNodesTerminalContainer .terminal-title');
            if (terminalTitle) {
                terminalTitle.textContent = 'Installing Custom Nodes';
            }
            startTerminalTimer('customNodesTerminalTimer');

            clearCustomNodesTerminal();
            showCustomNodesTerminal();
            appendToCustomNodesTerminal('Starting custom nodes installation...\\n', 'info');

            fetch('/custom_nodes_action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'install' })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showCustomNodesStatus(data.message, 'success');
                    startPollingCustomNodesLogs();
                } else {
                    showCustomNodesStatus(data.message, 'error');
                    appendToCustomNodesTerminal('Error: ' + data.message + '\\n', 'error');
                }
            });
        }

        function updateCustomNodes() {
            // Update terminal title and start timer
            var terminalTitle = document.querySelector('#customNodesTerminalContainer .terminal-title');
            if (terminalTitle) {
                terminalTitle.textContent = 'Updating Custom Nodes';
            }
            startTerminalTimer('customNodesTerminalTimer');

            clearCustomNodesTerminal();
            showCustomNodesTerminal();
            appendToCustomNodesTerminal('Starting custom nodes update...\\n', 'info');

            fetch('/custom_nodes_action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'update' })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showCustomNodesStatus(data.message, 'success');
                    startPollingCustomNodesLogs();
                } else {
                    showCustomNodesStatus(data.message, 'error');
                    appendToCustomNodesTerminal('Error: ' + data.message + '\\n', 'error');
                }
            });
        }

        function showCustomNodesStatus(message, type) {
            var statusDiv = document.getElementById('customNodesStatusMessage');
            statusDiv.textContent = message;
            statusDiv.className = 'status-message ' + type;
            statusDiv.classList.remove('hidden');
            setTimeout(function() {
                statusDiv.classList.add('hidden');
            }, 5000);
        }

        function showCustomNodesTerminal() {
            document.getElementById('customNodesTerminalContainer').style.display = 'block';
        }

        function minimizeCustomNodesTerminal() {
            var terminal = document.getElementById('customNodesTerminal');
            if (terminal.style.display === 'none') {
                terminal.style.display = 'block';
            } else {
                terminal.style.display = 'none';
            }
        }

        function copyCustomNodesTerminal() {
            var terminal = document.getElementById('customNodesTerminal');
            navigator.clipboard.writeText(terminal.textContent).then(function() {
                showCustomNodesStatus('Terminal content copied to clipboard', 'success');
            }).catch(function(err) {
                showCustomNodesStatus('Failed to copy: ' + err, 'error');
            });
        }

        function clearCustomNodesTerminal() {
            document.getElementById('customNodesTerminal').textContent = '';
        }

        function appendToCustomNodesTerminal(text, type) {
            var terminal = document.getElementById('customNodesTerminal');
            var span = document.createElement('span');
            span.textContent = text;
            if (type === 'error') {
                span.style.color = '#ef4444';
            } else if (type === 'success') {
                span.style.color = '#10b981';
            } else if (type === 'info') {
                span.style.color = '#3b82f6';
            }
            terminal.appendChild(span);
            terminal.scrollTop = terminal.scrollHeight;
        }

        function startPollingCustomNodesLogs() {
            var pollInterval = setInterval(function() {
                fetch('/logs')
                    .then(response => response.json())
                    .then(data => {
                        if (data.content) {
                            document.getElementById('customNodesTerminal').textContent = data.content;
                            var terminal = document.getElementById('customNodesTerminal');
                            terminal.scrollTop = terminal.scrollHeight;
                        }
                        if (!data.running) {
                            clearInterval(pollInterval);
                            appendToCustomNodesTerminal('\\n=== Process completed ===\\n', 'success');
                            stopTerminalTimer();
                        }
                    });
            }, 1000);
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

            // Update terminal title and start timer
            var terminalTitle = document.querySelector('#modelsTerminalContainer .terminal-title');
            if (terminalTitle) {
                terminalTitle.textContent = 'Downloading Models';
            }
            startTerminalTimer('modelsTerminalTimer');

            // Clear and show terminal
            clearModelsTerminal();
            showModelsTerminal();
            appendToModelsTerminal('Starting download for: ' + selectedModels.join(', ') + '...\\n', 'info');

            fetch('/download_models', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    models: selectedModels,
                    hf_token: hfToken,
                    civit_token: civitToken
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showModelsStatus(data.message, 'success');
                    // Start polling for logs
                    startPollingModelsLogs();
                } else {
                    showModelsStatus(data.message, 'error');
                    appendToModelsTerminal('Error: ' + data.message + '\\n', 'error');
                }
            });
        }

        // Models page terminal functions
        function showModelsTerminal() {
            document.getElementById('modelsTerminalContainer').classList.add('visible');
        }

        function minimizeModelsTerminal() {
            var terminal = document.getElementById('modelsTerminal');
            if (terminal.style.display === 'none') {
                terminal.style.display = 'block';
            } else {
                terminal.style.display = 'none';
            }
        }

        function copyModelsTerminal() {
            var terminal = document.getElementById('modelsTerminal');
            navigator.clipboard.writeText(terminal.textContent).then(function() {
                showModelsStatus('Terminal content copied to clipboard', 'success');
            }).catch(function(err) {
                showModelsStatus('Failed to copy: ' + err, 'error');
            });
        }

        function clearModelsTerminal() {
            document.getElementById('modelsTerminal').innerHTML = '';
            lastLogLength = 0;
            fetch('/clear_logs', { method: 'POST' });
        }

        function minimizeTerminal() {
            var terminal = document.getElementById('terminal');
            if (terminal.style.display === 'none') {
                terminal.style.display = 'block';
            } else {
                terminal.style.display = 'none';
            }
        }

        function copyTerminal() {
            var terminal = document.getElementById('terminal');
            navigator.clipboard.writeText(terminal.textContent).then(function() {
                showStatus('Terminal content copied to clipboard', 'success');
            }).catch(function(err) {
                showStatus('Failed to copy: ' + err, 'error');
            });
        }

        function clearTerminal() {
            document.getElementById('terminal').innerHTML = '';
            lastLogLength = 0;
        }

        function appendToModelsTerminal(text, className) {
            const terminal = document.getElementById('modelsTerminal');
            const span = document.createElement('span');
            if (className) span.className = className;
            span.textContent = text;
            terminal.appendChild(span);
            terminal.scrollTop = terminal.scrollHeight;
        }

        function pollModelsLogs() {
            fetch('/logs')
                .then(response => response.json())
                .then(data => {
                    if (data.content && data.content.length > lastLogLength) {
                        const newContent = data.content.substring(lastLogLength);
                        appendToModelsTerminal(newContent);
                        lastLogLength = data.content.length;
                    }
                    if (data.running === false && logPollingInterval) {
                        appendToModelsTerminal('\\n--- Download completed ---\\n', 'success');
                        stopTerminalTimer();
                        stopPollingLogs();
                    }
                })
                .catch(err => console.error('Error polling logs:', err));
        }

        function startPollingModelsLogs() {
            lastLogLength = 0;
            if (logPollingInterval) clearInterval(logPollingInterval);
            logPollingInterval = setInterval(pollModelsLogs, 1000);
            pollModelsLogs(); // Initial poll
        }

        function showStatus(message, type) {
            const el = document.getElementById('statusMessage');
            el.textContent = message;
            el.className = 'status-message ' + type;
            el.classList.remove('hidden');
            setTimeout(() => el.classList.add('hidden'), 3000);
        }

        function showModelsStatus(message, type) {
            const el = document.getElementById('modelsStatusMessage');
            el.textContent = message;
            el.className = 'status-message ' + type;
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
                    timer.textContent = minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0');
                }, 1000);
            });
        }

        // Terminal functions
        var logPollingInterval = null;
        var lastLogLength = 0;
        var activeAdminButton = null;
        var activeAdminAction = null;
        var activeAdminToolId = null;

        function showTerminal() {
            document.getElementById('terminalContainer').classList.add('visible');
        }

        function minimizeTerminal() {
            var terminal = document.getElementById('terminal');
            if (terminal.style.display === 'none') {
                terminal.style.display = 'block';
            } else {
                terminal.style.display = 'none';
            }
        }

        function clearTerminal() {
            document.getElementById('terminal').innerHTML = '';
            lastLogLength = 0;
            // Also clear server-side log
            fetch('/clear_logs', { method: 'POST' });
        }

        function appendToTerminal(text, className) {
            const terminal = document.getElementById('terminal');
            const span = document.createElement('span');
            if (className) span.className = className;
            span.textContent = text;
            terminal.appendChild(span);
            terminal.scrollTop = terminal.scrollHeight;
        }

        function pollLogs() {
            fetch('/logs')
                .then(response => response.json())
                .then(data => {
                    if (data.content && data.content.length > lastLogLength) {
                        const newContent = data.content.substring(lastLogLength);
                        appendToTerminal(newContent);
                        lastLogLength = data.content.length;
                    }
                    if (data.running === false && logPollingInterval) {
                        appendToTerminal('\n--- Process completed ---\n', 'success');
                        stopPollingLogs();
                        // Re-enable the admin button
                        resetAdminButton();
                        // Don't auto-reload - let user see any errors
                    }
                })
                .catch(err => console.error('Error polling logs:', err));
        }

        function startPollingLogs() {
            lastLogLength = 0;
            if (logPollingInterval) clearInterval(logPollingInterval);
            logPollingInterval = setInterval(pollLogs, 1000);
            pollLogs(); // Initial poll
        }

        function stopPollingLogs() {
            if (logPollingInterval) {
                clearInterval(logPollingInterval);
                logPollingInterval = null;
            }
            stopTerminalTimer();
        }

        // Terminal timer functions
        var terminalTimerInterval = null;
        var terminalTimerStart = null;

        function startTerminalTimer(timerId) {
            stopTerminalTimer();
            terminalTimerStart = Date.now();
            var timerElement = document.getElementById(timerId || 'terminalTimer');
            if (timerElement) {
                timerElement.textContent = '0:00';
                terminalTimerInterval = setInterval(function() {
                    var elapsed = Math.floor((Date.now() - terminalTimerStart) / 1000);
                    var minutes = Math.floor(elapsed / 60);
                    var seconds = elapsed % 60;
                    timerElement.textContent = minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
                }, 1000);
            }
        }

        function stopTerminalTimer() {
            if (terminalTimerInterval) {
                clearInterval(terminalTimerInterval);
                terminalTimerInterval = null;
            }
        }

        function resetAdminButton() {
            if (activeAdminButton && activeAdminAction && activeAdminToolId) {
                activeAdminButton.disabled = false;
                activeAdminButton.textContent = activeAdminAction.charAt(0).toUpperCase() + activeAdminAction.slice(1);
                activeAdminButton = null;
                activeAdminAction = null;
                activeAdminToolId = null;
            }
        }

        // User terminal functions
        var userLogPollingInterval = null;

        function showUserTerminal(toolName) {
            var container = document.getElementById('userTerminalContainer');
            var title = container.querySelector('.terminal-title');
            title.textContent = 'Starting ' + (toolName || '...');
            container.classList.add('visible');
        }

        function minimizeUserTerminal() {
            var terminal = document.getElementById('userTerminal');
            if (terminal.style.display === 'none') {
                terminal.style.display = 'block';
            } else {
                terminal.style.display = 'none';
            }
        }

        function copyUserTerminal() {
            var terminal = document.getElementById('userTerminal');
            navigator.clipboard.writeText(terminal.textContent).then(function() {
                showStatus('Terminal content copied to clipboard', 'success');
            }).catch(function(err) {
                showStatus('Failed to copy: ' + err, 'error');
            });
        }

        function clearUserTerminal() {
            document.getElementById('userTerminal').innerHTML = '';
        }

        function appendToUserTerminal(text, className) {
            var terminal = document.getElementById('userTerminal');
            var span = document.createElement('span');
            if (className) span.className = className;
            // Handle literal backslash-n from raw Python strings (\\\\n becomes \\n in JS regex)
            span.innerHTML = text.replace(/\\\\n/g, '<br>').replace(/\n/g, '<br>');
            terminal.appendChild(span);
            terminal.scrollTop = terminal.scrollHeight;
        }

        function startPollingUserLogs(toolId, toolName) {
            var tools = {{ tools | tojson }};
            var tool = tools[toolId];
            var port = tool ? tool.port : null;
            var checkCount = 0;
            var maxChecks = 300; // 300 seconds timeout (5 minutes)
            var lastLogLength = 0;
            var processExited = false;

            if (userLogPollingInterval) clearInterval(userLogPollingInterval);

            userLogPollingInterval = setInterval(function() {
                checkCount++;

                // Fetch actual logs from the process
                fetch('/user_logs')
                    .then(function(response) { return response.json(); })
                    .then(function(logData) {
                        // Show new log content
                        if (logData.content && logData.content.length > lastLogLength) {
                            var newContent = logData.content.substring(lastLogLength);
                            appendToUserTerminal(newContent);
                            lastLogLength = logData.content.length;

                            // Auto-scroll
                            var terminal = document.getElementById('userTerminal');
                            terminal.scrollTop = terminal.scrollHeight;
                        }

                        // Check if process exited (look for exit message in logs)
                        if (logData.content && logData.content.includes('=== Process exited with code:')) {
                            processExited = true;
                        }
                    });

                // Check if service is ready by polling tool_status
                fetch('/tool_status/' + toolId)
                    .then(function(response) { return response.json(); })
                    .then(function(data) {
                        if (data.running && data.port_ready) {
                            stopPollingUserLogs();
                            // Open the tool
                            var runpodId = '{{ runpod_id | e }}';
                            var url = 'https://' + runpodId + '-' + port + '.proxy.runpod.net';
                            window.open(url, '_blank');
                            setTimeout(function() { location.reload(); }, 1000);
                        } else if (processExited) {
                            stopPollingUserLogs();
                            showStatus(toolName + ' process exited unexpectedly', 'error');
                        } else if (checkCount >= maxChecks) {
                            stopPollingUserLogs();
                            showStatus('Timeout waiting for ' + toolName + ' to start', 'error');
                        }
                    })
                    .catch(function(err) {
                        console.error('Error checking status:', err);
                    });
            }, 1000);
        }

        function stopPollingUserLogs() {
            if (userLogPollingInterval) {
                clearInterval(userLogPollingInterval);
                userLogPollingInterval = null;
            }
        }
    </script>
</body>
</html>
"""


def get_runpod_id():
    """Get RunPod instance ID from environment"""
    return os.environ.get("RUNPOD_POD_ID", "localhost")


def is_installed(path):
    """Check if a tool is installed by checking directory existence"""
    if path is None:
        return True
    return os.path.isdir(path)


def get_all_users():
    """Get list of users for dropdown from users.json"""
    return get_all_user_names(USERS_JSON_PATH)


@app.route("/debug")
def debug():
    """Debug endpoint to check parsed users and admins"""
    return jsonify(
        {
            "USERS_DATA": USERS_DATA,
            "ADMINS": ADMINS,
            "USERS_JSON_PATH": USERS_JSON_PATH,
            "REPO_DIR": REPO_DIR,
            "current_artist": current_artist,
            "is_current_admin": is_admin(current_artist) if current_artist else None,
        }
    )


@app.route("/")
def index():
    # Redirect to login if no user selected, otherwise show home
    if not current_artist:
        return redirect(url_for("login"))
    return redirect(url_for("home"))


@app.route("/login")
def login():
    artists = get_all_users()
    return render_template("login.html", artists=artists)


@app.route("/home")
def home():
    if not current_artist:
        return redirect(url_for("login"))
    return render_template(
        "home.html",
        current_user=current_artist,
        is_admin=is_admin(current_artist),
        active_page="home",
        page_title="Home",
        runpod_id=get_runpod_id(),
    )


@app.route("/assets")
def assets():
    if not current_artist:
        return redirect(url_for("login"))
    return render_template(
        "assets.html",
        current_user=current_artist,
        is_admin=is_admin(current_artist),
        active_page="assets",
        page_title="Assets",
        runpod_id=get_runpod_id(),
    )


@app.route("/tool/<tool_id>")
def tool_page(tool_id):
    if not current_artist:
        return redirect(url_for("login"))

    if tool_id not in TOOLS:
        return redirect(url_for("home"))

    tool = TOOLS[tool_id]

    # Get tool status
    status = "stopped"
    if tool_id in active_sessions:
        if check_port_open(tool["port"]):
            status = "running"
        else:
            status = "starting"

    # Get logs for this tool
    logs = ""
    tool_log_file = get_tool_log_file(tool_id)
    if os.path.exists(tool_log_file):
        try:
            with open(tool_log_file, "r") as f:
                logs = f.read()
        except:
            pass

    # Use special template for LoRA Tool (no terminal)
    if tool_id == "lora-tool":
        return render_template(
            "lora_tool.html",
            current_user=current_artist,
            is_admin=is_admin(current_artist),
            active_page=tool_id,
            page_title=tool["name"],
            tool=tool,
            tool_id=tool_id,
            tool_status=status,
            runpod_id=get_runpod_id(),
        )

    return render_template(
        "tool.html",
        current_user=current_artist,
        is_admin=is_admin(current_artist),
        active_page=tool_id,
        page_title=tool["name"],
        tool=tool,
        tool_id=tool_id,
        tool_status=status,
        logs=logs,
        runpod_id=get_runpod_id(),
    )


@app.route("/admin")
def admin():
    if not current_artist:
        return redirect(url_for("login"))
    if not is_admin(current_artist):
        return redirect(url_for("home"))

    # Get tool installation status
    admin_tools = {
        "comfy-ui": {
            "name": "ComfyUI",
            "installed": is_installed(TOOLS["comfy-ui"]["install_path"]),
        },
        "swarm-ui": {
            "name": "SwarmUI",
            "installed": is_installed(TOOLS["swarm-ui"]["install_path"]),
        },
        "ai-toolkit": {
            "name": "AI-Toolkit",
            "installed": is_installed(TOOLS["ai-toolkit"]["install_path"]),
        },
    }

    # Get current admin logs and running status
    admin_logs = ""
    admin_process_running = False
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                admin_logs = f.read()
        except:
            pass
    if running_process is not None:
        admin_process_running = running_process.poll() is None

    return render_template(
        "admin.html",
        current_user=current_artist,
        is_admin=True,
        active_page="admin",
        page_title="Settings",
        runpod_id=get_runpod_id(),
        admin_tools=admin_tools,
        download_scripts=get_download_scripts(),
        custom_nodes=get_custom_nodes(),
        users_data=USERS_DATA,
        superadmin_name=SUPERADMIN_NAME,
        admin_logs=admin_logs,
        admin_process_running=admin_process_running,
    )


@app.route("/api/users", methods=["GET"])
def api_get_users():
    """Get all users with admin status"""
    if not is_admin(current_artist):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    reload_users()
    return jsonify({"success": True, "users": USERS_DATA})


@app.route("/api/users", methods=["POST"])
def api_add_users():
    """Add users from text (one name per line)"""
    global USERS_DATA, ADMINS

    if not is_admin(current_artist):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json()
    names_text = data.get("names", "")

    if not names_text.strip():
        return jsonify({"success": False, "message": "No names provided"})

    USERS_DATA = add_users_bulk(names_text, USERS_JSON_PATH, USERS_OUTPUT_DIR)
    ADMINS = get_admins_list(USERS_DATA)

    return jsonify({"success": True, "users": USERS_DATA})


@app.route("/api/users/<path:user_name>/admin", methods=["POST"])
def api_set_user_admin(user_name):
    """Set admin status for a user"""
    global USERS_DATA, ADMINS

    if not is_admin(current_artist):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json()
    is_admin_status = data.get("is_admin", False)

    USERS_DATA = set_user_admin(user_name, is_admin_status, USERS_JSON_PATH)
    ADMINS = get_admins_list(USERS_DATA)

    return jsonify({"success": True, "users": USERS_DATA})


@app.route("/api/users/<path:user_name>", methods=["DELETE"])
def api_delete_user(user_name):
    """Delete a user (cannot delete superadmin)"""
    global USERS_DATA, ADMINS

    if not is_admin(current_artist):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    if user_name.strip().lower() == SUPERADMIN_NAME.lower():
        return jsonify({"success": False, "message": "Cannot delete superadmin"})

    data = request.get_json() or {}
    delete_folder = data.get("delete_folder", False)

    USERS_DATA = delete_user(
        user_name, USERS_JSON_PATH, delete_folder, USERS_OUTPUT_DIR
    )
    ADMINS = get_admins_list(USERS_DATA)

    return jsonify({"success": True, "users": USERS_DATA})


@app.route("/old")
def old_index():
    """Legacy UI - keep for reference during migration"""
    artists = get_all_users()
    return render_template_string(
        HTML_TEMPLATE,
        artists=artists,
        admins=ADMINS,
        tools=TOOLS,
        current_artist=current_artist,
        admin_mode=admin_mode,
        active_sessions={
            k: {"start_time": v["start_time"].isoformat() + "Z"}
            for k, v in active_sessions.items()
        },
        runpod_id=get_runpod_id(),
        is_installed=is_installed,
        download_scripts=get_download_scripts(),
        custom_nodes=get_custom_nodes(),
    )


@app.route("/set_artist", methods=["POST"])
def set_artist():
    global current_artist, admin_mode

    # Handle both form submission and JSON
    if request.is_json:
        data = request.get_json()
        current_artist = data.get("artist", "")
    else:
        current_artist = request.form.get("artist", "")

    # Reset admin mode if not an admin
    if not is_admin(current_artist):
        admin_mode = False

    # If form submission, redirect to home
    if not request.is_json:
        return redirect(url_for("home"))

    return jsonify({"success": True})


@app.route("/set_admin_mode", methods=["POST"])
def set_admin_mode():
    global admin_mode
    data = request.get_json()

    # Only allow admin mode for admins
    if is_admin(current_artist):
        admin_mode = data.get("admin_mode", False)

    return jsonify({"success": True})


def start_session_internal(tool_id, artist):
    """Internal function to start a tool session"""
    global active_sessions, user_process_running

    if not tool_id or tool_id not in TOOLS:
        return {"status": "error", "message": "Invalid tool"}

    if not artist:
        return {"status": "error", "message": "No artist selected"}

    tool = TOOLS[tool_id]
    process = None

    # Create artist output directory if ComfyUI
    if tool_id == "comfy-ui":
        output_dir = f"/workspace/ComfyUI/output/{artist}"
        os.makedirs(output_dir, exist_ok=True)

    # Start the actual service
    try:
        if tool_id == "jupyter-lab":
            # Kill any existing jupyter on the port
            subprocess.run(["fuser", "-k", "8888/tcp"], capture_output=True)
            time.sleep(1)

            # Setup log capture
            tool_log_file = get_tool_log_file(tool_id)
            user_process_running = True
            with open(tool_log_file, "w") as f:
                f.write(f"=== Starting JupyterLab ===\n")
                f.write(f"Started at: {datetime.utcnow().isoformat()}Z\n")
                f.write("=" * 40 + "\n\n")

            log_file = open(tool_log_file, "a")
            process = subprocess.Popen(
                [
                    "jupyter",
                    "lab",
                    "--ip=0.0.0.0",
                    "--port=8888",
                    "--no-browser",
                    "--allow-root",
                    "--NotebookApp.token=",
                    "--NotebookApp.password=",
                ],
                cwd="/workspace",
                stdout=log_file,
                stderr=log_file,
            )

            def monitor_process():
                global user_process_running
                process.wait()
                with open(tool_log_file, "a") as f:
                    f.write(
                        f"\n=== Process exited with code: {process.returncode} ===\n"
                    )
                user_process_running = False

            threading.Thread(target=monitor_process, daemon=True).start()

        elif tool_id == "comfy-ui":
            # Start ComfyUI using start script
            start_script = get_setup_script("comfy-ui", "start")
            if start_script:
                # Setup log capture
                tool_log_file = get_tool_log_file(tool_id)
                user_process_running = True
                with open(tool_log_file, "w") as f:
                    f.write(f"=== Starting ComfyUI ===\n")
                    f.write(f"Script: {start_script}\n")
                    f.write(f"Started at: {datetime.utcnow().isoformat()}Z\n")
                    f.write("=" * 40 + "\n\n")

                log_file = open(tool_log_file, "a")
                env = os.environ.copy()
                env["HF_HOME"] = "/workspace"
                env["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
                env["COMFY_OUTPUT_DIR"] = f"/workspace/ComfyUI/output/{artist}"
                process = subprocess.Popen(
                    ["bash", start_script],
                    cwd="/workspace/ComfyUI",
                    env=env,
                    stdout=log_file,
                    stderr=log_file,
                )

                def monitor_process():
                    global user_process_running
                    process.wait()
                    with open(tool_log_file, "a") as f:
                        f.write(
                            f"\n=== Process exited with code: {process.returncode} ===\n"
                        )
                    user_process_running = False

                threading.Thread(target=monitor_process, daemon=True).start()
            else:
                return {"status": "error", "message": "ComfyUI start script not found"}

        elif tool_id == "ai-toolkit":
            # Kill any existing ai-toolkit on the port
            subprocess.run(["fuser", "-k", "8675/tcp"], capture_output=True)
            time.sleep(1)
            # Start AI-Toolkit using start script with log capture
            start_script = get_setup_script("ai-toolkit", "start")
            if start_script:
                # Clear and open log file
                tool_log_file = get_tool_log_file(tool_id)
                user_process_running = True
                with open(tool_log_file, "w") as f:
                    f.write(f"=== Starting AI-Toolkit ===\n")
                    f.write(f"Script: {start_script}\n")
                    f.write(f"Started at: {datetime.utcnow().isoformat()}Z\n")
                    f.write("=" * 40 + "\n\n")

                log_file = open(tool_log_file, "a")
                process = subprocess.Popen(
                    ["bash", start_script],
                    cwd="/workspace/ai-toolkit",
                    stdout=log_file,
                    stderr=log_file,
                )

                # Monitor process in background thread
                def monitor_process():
                    global user_process_running
                    process.wait()
                    with open(tool_log_file, "a") as f:
                        f.write(
                            f"\n=== Process exited with code: {process.returncode} ===\n"
                        )
                    user_process_running = False

                threading.Thread(target=monitor_process, daemon=True).start()
            else:
                raise Exception("AI-Toolkit start script not found")

        elif tool_id == "swarm-ui":
            # Kill any existing swarm-ui on the port
            subprocess.run(["fuser", "-k", "7861/tcp"], capture_output=True)
            time.sleep(1)
            # Start SwarmUI using start script with log capture
            start_script = get_setup_script("swarm-ui", "start")
            if start_script:
                # Clear and open log file
                tool_log_file = get_tool_log_file(tool_id)
                user_process_running = True
                with open(tool_log_file, "w") as f:
                    f.write(f"=== Starting SwarmUI ===\n")
                    f.write(f"Script: {start_script}\n")
                    f.write(f"Started at: {datetime.utcnow().isoformat()}Z\n")
                    f.write("=" * 40 + "\n\n")

                log_file = open(tool_log_file, "a")
                process = subprocess.Popen(
                    ["bash", start_script],
                    cwd="/workspace/SwarmUI",
                    stdout=log_file,
                    stderr=log_file,
                )

                # Monitor process in background thread
                def monitor_process():
                    global user_process_running
                    process.wait()
                    with open(tool_log_file, "a") as f:
                        f.write(
                            f"\n=== Process exited with code: {process.returncode} ===\n"
                        )
                    user_process_running = False

                threading.Thread(target=monitor_process, daemon=True).start()
            else:
                raise Exception("SwarmUI start script not found")

        elif tool_id == "lora-tool":
            # Kill any existing lora-tool on the port
            subprocess.run(["fuser", "-k", "3000/tcp"], capture_output=True)
            time.sleep(1)
            # Start LoRA-Tool using start script (runs from repo directory)
            start_script = get_setup_script("lora-tool", "start")
            if start_script:
                process = subprocess.Popen(
                    ["bash", start_script],
                    cwd=os.path.join(REPO_DIR, "setup", "lora-tool"),
                )
            else:
                raise Exception("LoRA-Tool start script not found")

    except Exception as e:
        return {"status": "error", "message": f"Failed to start: {str(e)}"}

    active_sessions[tool_id] = {
        "process": process,
        "start_time": datetime.utcnow(),
        "artist": artist,
    }

    return {"status": "started", "tool_name": tool["name"]}


@app.route("/start_session", methods=["POST"])
def start_session():
    global active_sessions, user_process_running

    data = request.get_json()
    tool_id = data.get("tool_id")
    artist = data.get("artist")

    result = start_session_internal(tool_id, artist)

    # Convert to old format for compatibility
    if result.get("status") == "started":
        return jsonify(
            {
                "success": True,
                "tool_name": result.get("tool_name"),
                "message": f"{result.get('tool_name')} session started",
            }
        )
    else:
        return jsonify(
            {"success": False, "message": result.get("message", "Unknown error")}
        )


@app.route("/stop_session", methods=["POST"])
def stop_session():
    global active_sessions

    data = request.get_json()
    tool_id = data.get("tool_id")

    if not tool_id or tool_id not in TOOLS:
        return jsonify({"success": False, "message": "Invalid tool"})

    tool = TOOLS[tool_id]

    # Kill the process if running
    if tool_id in active_sessions:
        session = active_sessions[tool_id]
        if session.get("process"):
            session["process"].terminate()

        # Kill by port
        port = tool["port"]
        subprocess.run(["fuser", "-k", f"{port}/tcp"], capture_output=True)

        del active_sessions[tool_id]

    return jsonify(
        {
            "success": True,
            "tool_name": tool["name"],
            "message": f"{tool['name']} stopped",
        }
    )


@app.route("/user_logs")
def user_logs():
    """Get user process logs for streaming to terminal"""
    try:
        if os.path.exists(USER_LOG_FILE):
            with open(USER_LOG_FILE, "r") as f:
                content = f.read()
        else:
            content = ""
        return jsonify({"content": content, "running": user_process_running})
    except Exception as e:
        return jsonify({"content": f"Error reading logs: {str(e)}", "running": False})


def check_port_open(port, timeout=1):
    """Check if a port is actually responding"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex(("127.0.0.1", port))
        sock.close()
        return result == 0
    except:
        return False


@app.route("/start/<tool_id>", methods=["POST"])
def start_tool(tool_id):
    """Simplified start endpoint for new UI"""
    global active_sessions, user_process_running

    if tool_id not in TOOLS:
        return jsonify({"status": "error", "message": "Invalid tool"})

    if tool_id in active_sessions:
        return jsonify({"status": "already_running"})

    # Use existing start_session logic
    data = {"tool_id": tool_id, "artist": current_artist}

    # Simulate the request
    with app.test_request_context(json=data):
        from flask import request as req

        result = start_session_internal(tool_id, current_artist)
        return jsonify(result)


@app.route("/stop/<tool_id>", methods=["POST"])
def stop_tool(tool_id):
    """Simplified stop endpoint for new UI"""
    global active_sessions

    if tool_id not in TOOLS:
        return jsonify({"status": "error", "message": "Invalid tool"})

    tool = TOOLS[tool_id]

    # Kill the process if running
    if tool_id in active_sessions:
        session = active_sessions[tool_id]
        if session.get("process"):
            session["process"].terminate()

        # Kill by port
        port = tool["port"]
        subprocess.run(["fuser", "-k", f"{port}/tcp"], capture_output=True)

        del active_sessions[tool_id]

    return jsonify({"status": "stopped"})


@app.route("/logs/<tool_id>")
def get_tool_logs(tool_id):
    """Get logs for a specific tool"""
    logs = ""
    tool_log_file = get_tool_log_file(tool_id)
    if os.path.exists(tool_log_file):
        try:
            with open(tool_log_file, "r") as f:
                logs = f.read()
        except:
            pass
    return jsonify({"logs": logs})


@app.route("/clear_logs/<tool_id>", methods=["POST"])
def clear_tool_logs(tool_id):
    """Clear logs for a specific tool"""
    tool_log_file = get_tool_log_file(tool_id)
    try:
        with open(tool_log_file, "w") as f:
            f.write("")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/tool_status/<tool_id>")
def tool_status(tool_id):
    if tool_id not in TOOLS:
        return jsonify({"error": "Invalid tool"})

    tool = TOOLS[tool_id]
    is_running = tool_id in active_sessions

    # Also check if port is actually responding (service is ready)
    port_ready = False
    if is_running and tool.get("port"):
        port_ready = check_port_open(tool["port"])

    # Determine status string for frontend
    if is_running:
        if port_ready:
            status = "running"
        else:
            status = "starting"
    else:
        status = "stopped"

    return jsonify(
        {
            "tool_id": tool_id,
            "name": tool["name"],
            "status": status,
            "running": is_running,
            "port_ready": port_ready,
            "installed": is_installed(tool.get("install_path")),
        }
    )


@app.route("/logs")
def get_logs():
    """Get current log file contents"""
    global running_process

    content = ""
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                content = f.read()
        except:
            pass

    # Check if process is still running
    process_running = False
    if running_process is not None:
        poll_result = running_process.poll()
        process_running = poll_result is None
        if not process_running:
            running_process = None

    return jsonify({"content": content, "running": process_running})


@app.route("/clear_logs", methods=["POST"])
def clear_logs():
    """Clear the log file"""
    try:
        with open(LOG_FILE, "w") as f:
            f.write("")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/admin_action", methods=["POST"])
def admin_action():
    """Handle admin install/update actions"""
    global current_artist

    # Check if user is admin
    if not is_admin(current_artist):
        return jsonify({"success": False, "message": "Unauthorized"})

    data = request.get_json()
    tool_id = data.get("tool_id")
    action = data.get("action")  # 'install', 'reinstall', or 'update'

    if not tool_id or tool_id not in TOOLS:
        return jsonify({"success": False, "message": "Invalid tool"})

    if action not in ["install", "reinstall", "update"]:
        return jsonify({"success": False, "message": "Invalid action"})

    tool = TOOLS[tool_id]

    # Determine which script to use based on action
    if action == "install":
        script_type = "install"
    elif action == "reinstall":
        script_type = "reinstall"
    else:  # update
        script_type = "update"

    # Get the appropriate script path
    script_path = get_setup_script(tool_id, script_type)

    if not script_path:
        return jsonify(
            {
                "success": False,
                "message": f"No {script_type} script found for {tool['name']}. Create setup/{tool_id}/{script_type}_{tool_id}.sh",
            }
        )

    try:
        global running_process

        # Clear log file first
        with open(LOG_FILE, "w") as f:
            f.write(f"=== {action.capitalize()} {tool['name']} ===\n")
            f.write(f"Script: {script_path}\n")
            f.write(f"Started at: {datetime.utcnow().isoformat()}Z\n")
            f.write("=" * 40 + "\n\n")

        # Open log file for appending
        log_file = open(LOG_FILE, "a")

        # Run the install script with output to log file
        running_process = subprocess.Popen(
            ["bash", script_path],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            cwd="/workspace",
            bufsize=1,  # Line buffered
        )

        # Start a thread to close the log file when process completes
        def wait_and_close():
            running_process.wait()
            log_file.write(
                f"\n=== Process completed with exit code: {running_process.returncode} ===\n"
            )
            log_file.close()

        thread = threading.Thread(target=wait_and_close, daemon=True)
        thread.start()

        # Return immediately - script runs in background
        return jsonify(
            {
                "success": True,
                "tool_name": tool["name"],
                "message": f"{action.capitalize()} started for {tool['name']}. Check terminal for progress.",
                "script": script_path,
            }
        )

    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to run script: {str(e)}"})


@app.route("/download_models", methods=["POST"])
def download_models():
    """Handle model download requests"""
    global current_artist

    # Check if user is admin
    if not is_admin(current_artist):
        return jsonify({"success": False, "message": "Unauthorized"})

    data = request.get_json()
    scripts = data.get(
        "models", []
    )  # Now contains script filenames like "download_flux_models.sh"
    hf_token = data.get("hf_token", "")
    civit_token = data.get("civit_token", "")

    if not scripts:
        return jsonify({"success": False, "message": "No models selected"})

    download_dir = os.path.join(REPO_DIR, "setup", "download-models")
    scripts_to_run = []
    script_names = []

    for script_filename in scripts:
        # Security: ensure filename doesn't contain path traversal
        if "/" in script_filename or "\\" in script_filename or ".." in script_filename:
            continue
        script_path = os.path.join(download_dir, script_filename)
        if os.path.exists(script_path) and script_filename.endswith(".sh"):
            scripts_to_run.append(script_path)
            # Clean name for display
            name = (
                script_filename.replace(".sh", "")
                .replace("download_", "")
                .replace("_", " ")
                .title()
            )
            script_names.append(name)

    if not scripts_to_run:
        return jsonify({"success": False, "message": "No valid model scripts found"})

    try:
        global running_process

        # Set environment variables
        env = os.environ.copy()
        if hf_token:
            env["HUGGING_FACE_HUB_TOKEN"] = hf_token
            env["HF_TOKEN"] = hf_token
        if civit_token:
            env["CIVITAI_API_TOKEN"] = civit_token
        env["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

        # Clear log file first
        with open(LOG_FILE, "w") as f:
            f.write(f"=== Downloading Models: {', '.join(script_names)} ===\n")
            f.write(f"Started at: {datetime.utcnow().isoformat()}Z\n")
            f.write("=" * 40 + "\n\n")

        # Create a combined script to run all downloads sequentially
        combined_script = "#!/bin/bash\nset -e\n"
        for script_path in scripts_to_run:
            combined_script += (
                f'\necho "\\n=== Running {os.path.basename(script_path)} ===\\n"\n'
            )
            combined_script += f'bash "{script_path}"\n'
        combined_script += '\necho "\\n=== All downloads completed ===\\n"\n'

        # Open log file for appending
        log_file = open(LOG_FILE, "a")

        # Run the combined script
        running_process = subprocess.Popen(
            ["bash", "-c", combined_script],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            cwd="/workspace",
            env=env,
            bufsize=1,
        )

        # Start a thread to close the log file when process completes
        def wait_and_close():
            running_process.wait()
            log_file.write(
                f"\n=== Process completed with exit code: {running_process.returncode} ===\n"
            )
            log_file.close()

        thread = threading.Thread(target=wait_and_close, daemon=True)
        thread.start()

        return jsonify(
            {
                "success": True,
                "message": f"Download started for: {', '.join(script_names)}. Check terminal for progress.",
                "scripts": scripts_to_run,
            }
        )

    except Exception as e:
        return jsonify(
            {"success": False, "message": f"Failed to start downloads: {str(e)}"}
        )


@app.route("/custom_nodes_action", methods=["POST"])
def custom_nodes_action():
    """Handle custom nodes install/update actions"""
    global current_artist

    # Check if user is admin
    if not is_admin(current_artist):
        return jsonify({"success": False, "message": "Unauthorized"})

    data = request.get_json()
    action = data.get("action")  # 'install' or 'update'

    if action not in ["install", "update"]:
        return jsonify({"success": False, "message": "Invalid action"})

    # Get the appropriate script path
    script_name = f"{action}_custom_nodes.sh"
    script_path = os.path.join(REPO_DIR, "setup", "custom-nodes", script_name)

    if not os.path.exists(script_path):
        return jsonify(
            {
                "success": False,
                "message": f"Script not found: {script_path}",
            }
        )

    try:
        global running_process

        # Clear log file first
        with open(LOG_FILE, "w") as f:
            f.write(f"=== {action.capitalize()} Custom Nodes ===\n")
            f.write(f"Script: {script_path}\n")
            f.write(f"Started at: {datetime.utcnow().isoformat()}Z\n")
            f.write("=" * 40 + "\n\n")

        # Open log file for appending
        log_file = open(LOG_FILE, "a")

        # Run the script with output to log file
        running_process = subprocess.Popen(
            ["bash", script_path],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            cwd="/workspace",
            bufsize=1,  # Line buffered
        )

        # Start a thread to close the log file when process completes
        def wait_and_close():
            running_process.wait()
            log_file.write(
                f"\n=== Process completed with exit code: {running_process.returncode} ===\n"
            )
            log_file.close()

        thread = threading.Thread(target=wait_and_close, daemon=True)
        thread.start()

        # Return immediately - script runs in background
        return jsonify(
            {
                "success": True,
                "message": f"{action.capitalize()} started for custom nodes. Check terminal for progress.",
                "script": script_path,
            }
        )

    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to run script: {str(e)}"})


def cleanup_sessions():
    """Cleanup all active sessions"""
    for tool_id, session in active_sessions.items():
        if session.get("process"):
            session["process"].terminate()
        tool = TOOLS.get(tool_id)
        if tool:
            subprocess.run(["fuser", "-k", f"{tool['port']}/tcp"], capture_output=True)


def signal_handler(sig, frame):
    cleanup_sessions()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("Starting ComfyStudio on port 8080...")
    app.run(host="0.0.0.0", port=8080, debug=False)
