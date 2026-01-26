#!/usr/bin/env python3
# ABOUTME: Main Flask server for SF AI Workbench
# ABOUTME: Handles routes, tool management, and user profiles

import json
import os
import re
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from urllib.parse import urlencode

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    render_template_string,
    request,
    send_file,
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


def load_models_metadata():
    """Load models metadata from JSON file for size information."""
    metadata_path = os.path.join(REPO_DIR, "setup", "download-models", "models_metadata.json")
    try:
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading models metadata: {e}")
    return {}


def get_download_scripts():
    """
    Scan setup/download-models/ directory and return available download scripts.
    Returns list of dicts with 'id', 'name', 'path', 'installed', 'total', 'size_gb' for each script.
    """
    scripts = []
    download_dir = os.path.join(REPO_DIR, "setup", "download-models")

    if not os.path.exists(download_dir):
        return scripts

    # Load metadata for file sizes
    metadata = load_models_metadata()

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

                script_id = filename.replace(".sh", "")
                script_path = os.path.join(download_dir, filename)
                destinations = parse_model_destinations(script_path)
                installed, total = check_models_installed(destinations)

                # Get size from metadata if available
                size_gb = None
                if script_id in metadata:
                    size_gb = metadata[script_id].get("size_gb")

                scripts.append(
                    {
                        "id": script_id,
                        "name": name,
                        "filename": filename,
                        "path": script_path,
                        "installed": installed,
                        "total": total,
                        "size_gb": size_gb,
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
                        {% if script.size_gb %}
                            <span style="color: #9ca3af; font-size: 11px; margin-left: 4px;">({{ script.size_gb }}GB)</span>
                        {% endif %}
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


# Path for hero banner image
HERO_BANNER_PATH = "/workspace/hero_banner.jpg"

# Path for workflow templates
TEMPLATES_JSON_PATH = os.path.join(REPO_DIR, "workflows", "templates.json")
PREVIEWS_DIR = os.path.join(REPO_DIR, "workflows", "previews")
WORKFLOWS_DIR = os.path.join(REPO_DIR, "workflows")


def load_templates():
    """Load workflow templates from JSON file"""
    try:
        if os.path.exists(TEMPLATES_JSON_PATH):
            with open(TEMPLATES_JSON_PATH, "r") as f:
                data = json.load(f)
                return data.get("templates", [])
    except Exception as e:
        print(f"Error loading templates: {e}")
    return []


def save_templates(templates):
    """Save workflow templates to JSON file"""
    try:
        with open(TEMPLATES_JSON_PATH, "w") as f:
            json.dump({"templates": templates}, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving templates: {e}")
        return False


def sanitize_workflow_json(content):
    """Remove API keys and secrets from workflow JSON content.

    Patterns removed:
    - Anthropic API keys (sk-ant-...)
    - OpenAI API keys (sk-...)
    - HuggingFace tokens (hf_...)
    - Generic API key patterns
    """
    # Pattern for various API keys
    patterns = [
        # Anthropic API keys: sk-ant-... (various formats, be aggressive)
        (r"sk-ant-[a-zA-Z0-9_\-]{10,}", "[ANTHROPIC_API_KEY_REMOVED]"),
        # Anthropic broader pattern (catches sk-ant followed by anything inside quotes)
        (r'"sk-ant[^"]*"', '"[ANTHROPIC_API_KEY_REMOVED]"'),
        # OpenAI API keys: sk-... (but not sk-ant which is Anthropic)
        (r"sk-(?!ant)[a-zA-Z0-9]{20,}", "[OPENAI_API_KEY_REMOVED]"),
        # OpenAI project keys: sk-proj-...
        (r"sk-proj-[a-zA-Z0-9_\-]{20,}", "[OPENAI_PROJECT_KEY_REMOVED]"),
        # HuggingFace tokens: hf_...
        (r"hf_[a-zA-Z0-9]{10,}", "[HF_TOKEN_REMOVED]"),
        # Replicate API tokens
        (r"r8_[a-zA-Z0-9]{10,}", "[REPLICATE_TOKEN_REMOVED]"),
    ]

    sanitized = content
    removed_keys = []

    for pattern, replacement in patterns:
        matches = re.findall(pattern, sanitized, re.IGNORECASE)
        if matches:
            removed_keys.extend(
                matches if isinstance(matches[0], str) else [m[0] for m in matches]
            )
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    if removed_keys:
        print(f"Sanitized workflow: removed {len(removed_keys)} potential API key(s)")

    return sanitized


def strip_image_metadata(image_path):
    """Strip all metadata from an image file to remove embedded secrets.

    ComfyUI embeds workflow JSON (including API keys) into PNG metadata.
    This function removes all metadata to prevent secrets from leaking.
    """
    try:
        # Try using exiftool first (most thorough)
        result = subprocess.run(
            ["exiftool", "-all=", "-overwrite_original", image_path],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"Stripped metadata from {image_path} using exiftool")
            return True
    except FileNotFoundError:
        pass  # exiftool not installed, try PIL

    # Fallback to PIL - re-save image without metadata
    try:
        from PIL import Image

        img = Image.open(image_path)
        # Create a new image without metadata
        data = list(img.getdata())
        img_no_meta = Image.new(img.mode, img.size)
        img_no_meta.putdata(data)
        img_no_meta.save(image_path)
        print(f"Stripped metadata from {image_path} using PIL")
        return True
    except ImportError:
        print("Warning: Neither exiftool nor PIL available for metadata stripping")
        return False
    except Exception as e:
        print(f"Error stripping metadata with PIL: {e}")
        return False


def git_commit_and_push(message):
    """Commit changes to git and push to remote"""
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        return False, "GITHUB_TOKEN not configured"

    try:
        # Configure git user identity (use --global for root user)
        subprocess.run(
            ["git", "config", "--global", "user.email", "razvan.matei@stillfront.com"],
            cwd=REPO_DIR,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "--global", "user.name", "Razvan Matei"],
            cwd=REPO_DIR,
            check=True,
            capture_output=True,
        )

        # Configure git to use token for authentication
        repo_url = f"https://{github_token}@github.com/razvanmatei-sf/runpod-ggs.git"

        # Stage all changes in workflows directory
        subprocess.run(
            ["git", "add", "workflows/"],
            cwd=REPO_DIR,
            check=True,
            capture_output=True,
        )

        # Check if there are changes to commit
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_DIR,
            check=True,
            capture_output=True,
            text=True,
        )

        if not result.stdout.strip():
            return True, "No changes to commit"

        # Commit
        commit_result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
        )

        if commit_result.returncode != 0:
            error_msg = commit_result.stderr or commit_result.stdout
            if "nothing to commit" in error_msg.lower():
                return True, "No changes to commit"
            return False, f"Commit failed: {error_msg}"

        # Push using token auth
        push_result = subprocess.run(
            ["git", "push", repo_url, "feature/upgrade-setup-scripts"],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
        )

        if push_result.returncode != 0:
            return False, f"Push failed: {push_result.stderr or push_result.stdout}"

        return True, "Changes pushed successfully"
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if e.stderr else ""
        stdout = e.stdout.decode() if e.stdout else ""
        return False, f"Git error: {stderr or stdout or str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_hero_banner_url():
    """Get the hero banner URL if it exists"""
    if os.path.exists(HERO_BANNER_PATH):
        return "/hero_banner"
    return None


@app.route("/hero_banner")
def hero_banner():
    """Serve the hero banner image"""
    if os.path.exists(HERO_BANNER_PATH):
        from flask import send_file

        return send_file(HERO_BANNER_PATH, mimetype="image/jpeg")
    return "", 404


@app.route("/upload_hero_banner", methods=["POST"])
def upload_hero_banner():
    """Upload a new hero banner image"""
    if not is_admin(current_artist):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "message": "No file selected"}), 400

    # Save the file
    file.save(HERO_BANNER_PATH)
    return jsonify({"success": True, "message": "Hero banner uploaded"})


@app.route("/home")
def home():
    if not current_artist:
        return redirect(url_for("login"))

    # Get filter type from query params
    active_filter = request.args.get("type", "image")
    filter_names = {
        "use-cases": "Use Cases",
        "image": "Image",
        "video": "Video",
        "audio": "Audio",
        "3d-model": "3D Model",
        "llm": "LLM",
    }
    active_filter_name = filter_names.get(active_filter, "Image")

    # Load templates and filter by category
    all_templates = load_templates()
    if active_filter and active_filter != "use-cases":
        templates = [
            t
            for t in all_templates
            if t.get("category") == active_filter and t.get("enabled", True)
        ]
    else:
        templates = [t for t in all_templates if t.get("enabled", True)]

    # Sort by order
    templates.sort(key=lambda x: x.get("order", 999))

    return render_template(
        "home.html",
        current_user=current_artist,
        is_admin=is_admin(current_artist),
        active_page="home",
        active_filter=active_filter,
        active_filter_name=active_filter_name,
        page_title="Home",
        runpod_id=get_runpod_id(),
        hero_banner_url=get_hero_banner_url(),
        templates=templates,
    )


@app.route("/api/templates", methods=["GET"])
def api_get_templates():
    """Get all workflow templates"""
    templates = load_templates()
    return jsonify({"success": True, "templates": templates})


@app.route("/api/templates", methods=["POST"])
def api_create_template():
    """Create a new workflow template"""
    if not is_admin(current_artist):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json()
    templates = load_templates()

    # Generate unique ID
    import re

    base_id = re.sub(r"[^a-z0-9]+", "-", data.get("title", "template").lower()).strip(
        "-"
    )
    template_id = base_id
    counter = 1
    existing_ids = {t.get("id") for t in templates}
    while template_id in existing_ids:
        template_id = f"{base_id}-{counter}"
        counter += 1

    new_template = {
        "id": template_id,
        "title": data.get("title", "New Template"),
        "description": data.get("description", ""),
        "category": data.get("category", "image"),
        "tags": data.get("tags", []),
        "workflow_file": None,
        "workflow_api_file": None,
        "preview_image_a": None,
        "preview_image_b": None,
        "logo_text": data.get("logo_text"),
        "exposed_nodes": data.get("exposed_nodes", []),
        "enabled": True,
        "order": len(templates) + 1,
    }

    templates.append(new_template)
    if save_templates(templates):
        return jsonify({"success": True, "template": new_template})
    return jsonify({"success": False, "message": "Failed to save template"}), 500


@app.route("/api/templates/<template_id>", methods=["PUT"])
def api_update_template(template_id):
    """Update a workflow template"""
    if not is_admin(current_artist):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json()
    templates = load_templates()

    for i, t in enumerate(templates):
        if t.get("id") == template_id:
            # Update fields
            templates[i]["title"] = data.get("title", t.get("title"))
            templates[i]["description"] = data.get("description", t.get("description"))
            templates[i]["category"] = data.get("category", t.get("category"))
            templates[i]["tags"] = data.get("tags", t.get("tags"))
            templates[i]["logo_text"] = data.get("logo_text", t.get("logo_text"))
            templates[i]["exposed_nodes"] = data.get(
                "exposed_nodes", t.get("exposed_nodes", [])
            )
            templates[i]["enabled"] = data.get("enabled", t.get("enabled", True))

            if save_templates(templates):
                return jsonify({"success": True, "template": templates[i]})
            return jsonify(
                {"success": False, "message": "Failed to save template"}
            ), 500

    return jsonify({"success": False, "message": "Template not found"}), 404


@app.route("/api/templates/<template_id>", methods=["DELETE"])
def api_delete_template(template_id):
    """Delete a workflow template and its associated files"""
    if not is_admin(current_artist):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    templates = load_templates()

    # Find the template to get file references before deleting
    template_to_delete = None
    for t in templates:
        if t.get("id") == template_id:
            template_to_delete = t
            break

    if template_to_delete:
        # Delete associated files
        files_to_delete = []

        if template_to_delete.get("workflow_file"):
            files_to_delete.append(
                os.path.join(WORKFLOWS_DIR, template_to_delete["workflow_file"])
            )

        if template_to_delete.get("workflow_api_file"):
            files_to_delete.append(
                os.path.join(WORKFLOWS_DIR, template_to_delete["workflow_api_file"])
            )

        if template_to_delete.get("preview_image_a"):
            files_to_delete.append(
                os.path.join(PREVIEWS_DIR, template_to_delete["preview_image_a"])
            )

        if template_to_delete.get("preview_image_b"):
            files_to_delete.append(
                os.path.join(PREVIEWS_DIR, template_to_delete["preview_image_b"])
            )

        for filepath in files_to_delete:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"Deleted file: {filepath}")
            except Exception as e:
                print(f"Error deleting file {filepath}: {e}")

    # Remove template from list
    templates = [t for t in templates if t.get("id") != template_id]

    if save_templates(templates):
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Failed to save templates"}), 500


@app.route("/api/templates/<template_id>/upload", methods=["POST"])
def api_upload_template_file(template_id):
    """Upload a file for a template (workflow, preview images)"""
    if not is_admin(current_artist):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    file_type = request.form.get("type")  # workflow, workflow_api, preview_a, preview_b
    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "message": "No file selected"}), 400

    templates = load_templates()
    template = None
    template_idx = None
    for i, t in enumerate(templates):
        if t.get("id") == template_id:
            template = t
            template_idx = i
            break

    if not template:
        return jsonify({"success": False, "message": "Template not found"}), 404

    # Determine save path based on file type
    if file_type == "workflow":
        filename = f"{template_id}.json"
        save_path = os.path.join(WORKFLOWS_DIR, filename)
        templates[template_idx]["workflow_file"] = filename
    elif file_type == "workflow_api":
        filename = f"{template_id}_api.json"
        save_path = os.path.join(WORKFLOWS_DIR, filename)
        templates[template_idx]["workflow_api_file"] = filename
    elif file_type == "preview_a":
        ext = os.path.splitext(file.filename)[1] or ".jpg"
        filename = f"{template_id}_a{ext}"
        save_path = os.path.join(PREVIEWS_DIR, filename)
        templates[template_idx]["preview_image_a"] = filename
    elif file_type == "preview_b":
        ext = os.path.splitext(file.filename)[1] or ".jpg"
        filename = f"{template_id}_b{ext}"
        save_path = os.path.join(PREVIEWS_DIR, filename)
        templates[template_idx]["preview_image_b"] = filename
    else:
        return jsonify({"success": False, "message": "Invalid file type"}), 400

    # Ensure directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Read file content
    file_content = file.read()

    # Try to sanitize all files (in case JSON was uploaded with wrong extension)
    try:
        # Try to decode as text and sanitize
        text_content = file_content.decode("utf-8")
        sanitized_content = sanitize_workflow_json(text_content)
        with open(save_path, "w") as f:
            f.write(sanitized_content)
    except UnicodeDecodeError:
        # Binary file (actual image), save directly
        with open(save_path, "wb") as f:
            f.write(file_content)
        # Strip metadata from images to remove embedded secrets (ComfyUI embeds workflow JSON)
        if file_type in ("preview_a", "preview_b"):
            strip_image_metadata(save_path)

    # Update templates.json
    if save_templates(templates):
        return jsonify({"success": True, "filename": filename})
    return jsonify({"success": False, "message": "Failed to update template"}), 500


@app.route("/api/templates/<template_id>/workflow-api")
def api_get_workflow_api(template_id):
    """Get the API workflow JSON for a template (for QuickGen parsing)"""
    if not current_artist:
        return jsonify({"error": "Not authenticated"}), 401

    templates = load_templates()
    template = None
    for t in templates:
        if t.get("id") == template_id:
            template = t
            break

    if not template:
        return jsonify({"error": "Template not found"}), 404

    if not template.get("workflow_api_file"):
        return jsonify({"error": "No API workflow file"}), 404

    workflow_path = os.path.join(WORKFLOWS_DIR, template["workflow_api_file"])
    if not os.path.exists(workflow_path):
        return jsonify({"error": "Workflow file not found"}), 404

    try:
        with open(workflow_path, "r") as f:
            workflow_data = json.load(f)
        return jsonify(workflow_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/templates/commit", methods=["POST"])
def api_commit_templates():
    """Commit and push template changes to git"""
    if not is_admin(current_artist):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json() or {}
    message = data.get("message", "Update workflow templates")

    success, result_message = git_commit_and_push(message)
    return jsonify({"success": success, "message": result_message})


@app.route("/workflow/preview/<filename>")
def serve_workflow_preview(filename):
    """Serve workflow preview images"""
    from flask import send_file

    filepath = os.path.join(PREVIEWS_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath)
    return "", 404


# =============================================================================
# QuickGen Routes - Simplified workflow generation interface
# =============================================================================

COMFYUI_API_URL = "http://127.0.0.1:8188"

# Cache for ComfyUI object_info (node definitions)
_object_info_cache = {"data": None, "timestamp": 0}
OBJECT_INFO_CACHE_TTL = 300  # 5 minutes


def get_comfyui_object_info():
    """Fetch and cache ComfyUI's object_info (node definitions)"""
    import time

    current_time = time.time()

    # Return cached data if still valid
    if (
        _object_info_cache["data"]
        and current_time - _object_info_cache["timestamp"] < OBJECT_INFO_CACHE_TTL
    ):
        return _object_info_cache["data"]

    try:
        req = urllib.request.Request(f"{COMFYUI_API_URL}/object_info", method="GET")
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            _object_info_cache["data"] = data
            _object_info_cache["timestamp"] = current_time
            print(f"QuickGen: Cached object_info with {len(data)} node types")
            return data
    except Exception as e:
        print(f"QuickGen: Failed to fetch object_info: {e}")
        return _object_info_cache["data"]  # Return stale cache if available


def resolve_anywhere_connections(workflow, object_info):
    """
    Resolve 'Anything Everywhere' and 'Prompts Everywhere' node connections.

    These nodes broadcast outputs to matching inputs throughout the workflow.
    This function makes those implicit connections explicit in the workflow JSON.
    """
    if not object_info:
        print("QuickGen: No object_info available, skipping Anywhere resolution")
        return workflow

    # Make a deep copy to avoid modifying the original
    import copy

    workflow = copy.deepcopy(workflow)

    # Step 1: Find all broadcasts from Anywhere nodes
    # broadcasts_by_type: {output_type: (source_node_id, output_index)}
    # broadcasts_by_name: {input_name: (source_node_id, output_index, output_type)}
    broadcasts_by_type = {}
    broadcasts_by_name = {}

    anywhere_node_ids = set()

    for node_id, node_data in workflow.items():
        class_type = node_data.get("class_type", "")

        # Detect Anywhere/Everywhere nodes (various naming conventions)
        is_anywhere_node = any(
            keyword in class_type.lower() for keyword in ["anywhere", "everywhere"]
        )

        if not is_anywhere_node:
            continue

        anywhere_node_ids.add(node_id)
        is_prompts_node = "prompt" in class_type.lower()

        # Look at what's connected to this Anywhere node
        for input_name, input_value in node_data.get("inputs", {}).items():
            # Check if it's a connection [node_id, output_index]
            if not isinstance(input_value, list) or len(input_value) != 2:
                continue

            source_node_id = str(input_value[0])
            output_idx = int(input_value[1])

            source_node = workflow.get(source_node_id, {})
            source_class = source_node.get("class_type", "")

            if source_class not in object_info:
                continue

            # Get the output type from object_info
            outputs = object_info[source_class].get("output", [])
            if output_idx >= len(outputs):
                continue

            output_type = outputs[output_idx]

            # For Prompts Everywhere, match by name (positive/negative)
            if is_prompts_node and input_name in ["positive", "negative"]:
                broadcasts_by_name[input_name] = (
                    source_node_id,
                    output_idx,
                    output_type,
                )
            else:
                # For regular Anything Everywhere, match by type
                broadcasts_by_type[output_type] = (source_node_id, output_idx)

    if not broadcasts_by_type and not broadcasts_by_name:
        return workflow  # Nothing to resolve

    print(
        f"QuickGen: Found broadcasts - by_type: {list(broadcasts_by_type.keys())}, by_name: {list(broadcasts_by_name.keys())}"
    )

    # Step 2: Find missing connections and fill them
    connections_made = 0

    for node_id, node_data in workflow.items():
        if node_id in anywhere_node_ids:
            continue  # Skip the Anywhere nodes themselves

        class_type = node_data.get("class_type", "")
        if class_type not in object_info:
            continue

        node_info = object_info[class_type]
        required_inputs = node_info.get("input", {}).get("required", {})
        optional_inputs = node_info.get("input", {}).get("optional", {})

        all_inputs = {**required_inputs, **optional_inputs}

        for input_name, input_spec in all_inputs.items():
            # Get current value in workflow
            current_value = node_data.get("inputs", {}).get(input_name)

            # Skip if already connected (is a [node_id, index] array)
            if isinstance(current_value, list) and len(current_value) == 2:
                # Check if first element looks like a node reference
                if isinstance(current_value[0], (str, int)):
                    continue

            # Determine expected type for this input
            expected_type = None
            if isinstance(input_spec, list) and len(input_spec) > 0:
                first_elem = input_spec[0]
                # If it's a string, it's a type name (e.g., "VAE", "MODEL")
                # If it's a list, it's dropdown options - skip those
                if isinstance(first_elem, str):
                    expected_type = first_elem

            if not expected_type:
                continue

            # Try to find a matching broadcast
            connected = False

            # First, try name-based matching (for positive/negative conditioning)
            if input_name in broadcasts_by_name:
                source_node_id, output_idx, broadcast_type = broadcasts_by_name[
                    input_name
                ]
                if broadcast_type == expected_type:
                    if "inputs" not in workflow[node_id]:
                        workflow[node_id]["inputs"] = {}
                    workflow[node_id]["inputs"][input_name] = [
                        source_node_id,
                        output_idx,
                    ]
                    connections_made += 1
                    connected = True
                    print(
                        f"QuickGen: Connected {node_id}.{input_name} <- {source_node_id} (by name, type={expected_type})"
                    )

            # Then, try type-based matching
            if not connected and expected_type in broadcasts_by_type:
                source_node_id, output_idx = broadcasts_by_type[expected_type]
                if "inputs" not in workflow[node_id]:
                    workflow[node_id]["inputs"] = {}
                workflow[node_id]["inputs"][input_name] = [source_node_id, output_idx]
                connections_made += 1
                print(
                    f"QuickGen: Connected {node_id}.{input_name} <- {source_node_id} (by type={expected_type})"
                )

    print(f"QuickGen: Resolved {connections_made} Anywhere connections")
    return workflow


@app.route("/quickgen/<template_id>")
def quickgen_page(template_id):
    """Render the QuickGen page for a template"""
    if not current_artist:
        return redirect(url_for("login"))

    templates = load_templates()
    template = None
    for t in templates:
        if t.get("id") == template_id:
            template = t
            break

    if not template:
        return redirect(url_for("home"))

    # Get exposed nodes with their default values from the API workflow
    exposed_nodes = template.get("exposed_nodes", [])

    # Make a copy to avoid modifying the original template data
    import copy

    exposed_nodes = copy.deepcopy(exposed_nodes)

    # Load API workflow to get default values
    workflow_data = {}
    if template.get("workflow_api_file"):
        workflow_path = os.path.join(WORKFLOWS_DIR, template["workflow_api_file"])
        if os.path.exists(workflow_path):
            try:
                with open(workflow_path, "r") as f:
                    workflow_data = json.load(f)

                # Enrich exposed nodes with default values
                for node in exposed_nodes:
                    node_id = node.get("node_id")
                    input_name = node.get("input_name")
                    if node_id in workflow_data:
                        node_data = workflow_data[node_id]
                        inputs = node_data.get("inputs", {})
                        if input_name in inputs:
                            value = inputs[input_name]
                            # Only set default if it's not a link (list means connection)
                            if not isinstance(value, list):
                                node["default_value"] = value
            except Exception as e:
                print(f"Error loading workflow for QuickGen: {e}")

    # Fetch object_info to get dropdown options for combo inputs
    object_info = get_comfyui_object_info()
    if object_info:
        for node in exposed_nodes:
            class_type = node.get("class_type")
            input_name = node.get("input_name")

            # Skip COMBO detection for nodes that should use special input types
            # LoadImage should use IMAGE type (file upload), not COMBO (dropdown of existing files)
            if class_type == "LoadImage" and input_name == "image":
                node["input_type"] = "IMAGE"
                continue

            if class_type and class_type in object_info:
                node_info = object_info[class_type]
                # Check required inputs
                required_inputs = node_info.get("input", {}).get("required", {})
                # Check optional inputs
                optional_inputs = node_info.get("input", {}).get("optional", {})
                all_inputs = {**required_inputs, **optional_inputs}

                if input_name in all_inputs:
                    input_spec = all_inputs[input_name]
                    # input_spec is like: [["option1", "option2", ...], {"default": "option1"}]
                    # or for types: ["STRING", {"default": ""}]
                    if isinstance(input_spec, list) and len(input_spec) > 0:
                        first_elem = input_spec[0]
                        # If first element is a list, it's dropdown options
                        if isinstance(first_elem, list):
                            node["options"] = first_elem
                            node["input_type"] = "COMBO"
                            print(
                                f"QuickGen: Found dropdown options for {class_type}.{input_name}: {len(first_elem)} options"
                            )

    return render_template(
        "quickgen.html",
        current_user=current_artist,
        is_admin=is_admin(current_artist),
        active_page="home",
        page_title=f"QuickGen - {template.get('title', 'Generate')}",
        runpod_id=get_runpod_id(),
        template=template,
        exposed_nodes=exposed_nodes,
    )


@app.route("/api/quickgen/submit", methods=["POST"])
def api_quickgen_submit():
    """Submit a QuickGen prompt to ComfyUI"""
    if not current_artist:
        return jsonify({"success": False, "error": "Not authenticated"}), 401

    data = request.get_json()
    template_id = data.get("template_id")
    inputs = data.get("inputs", {})

    # Load template
    templates = load_templates()
    template = None
    for t in templates:
        if t.get("id") == template_id:
            template = t
            break

    if not template:
        return jsonify({"success": False, "error": "Template not found"}), 404

    if not template.get("workflow_api_file"):
        return jsonify(
            {"success": False, "error": "No API workflow for this template"}
        ), 400

    # Load the API workflow
    workflow_path = os.path.join(WORKFLOWS_DIR, template["workflow_api_file"])
    if not os.path.exists(workflow_path):
        return jsonify({"success": False, "error": "Workflow file not found"}), 404

    try:
        with open(workflow_path, "r") as f:
            workflow = json.load(f)
    except Exception as e:
        return jsonify(
            {"success": False, "error": f"Failed to load workflow: {e}"}
        ), 500

    # Apply user inputs to the workflow
    for key, value in inputs.items():
        if ":" in key:
            node_id, input_name = key.split(":", 1)
            if node_id in workflow and "inputs" in workflow[node_id]:
                # Convert value to appropriate type
                current_value = workflow[node_id]["inputs"].get(input_name)
                if isinstance(current_value, int):
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        pass
                elif isinstance(current_value, float):
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        pass
                elif isinstance(current_value, bool) or value in [
                    True,
                    False,
                    "true",
                    "false",
                ]:
                    value = value in [True, "true", "on", "1"]

                workflow[node_id]["inputs"][input_name] = value

    # Generate a unique client ID for this request
    client_id = str(uuid.uuid4())

    # Debug: log the workflow being submitted
    print(f"QuickGen: Submitting workflow for template {template_id}")
    print(f"QuickGen: Applied inputs: {inputs}")
    print(f"QuickGen: Workflow node IDs: {list(workflow.keys())}")

    # Resolve Anything Everywhere connections
    object_info = get_comfyui_object_info()
    if object_info:
        workflow = resolve_anywhere_connections(workflow, object_info)

    # Submit to ComfyUI
    try:
        prompt_data = {"prompt": workflow, "client_id": client_id}

        req = urllib.request.Request(
            f"{COMFYUI_API_URL}/prompt",
            data=json.dumps(prompt_data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            prompt_id = result.get("prompt_id")

            if prompt_id:
                return jsonify(
                    {"success": True, "prompt_id": prompt_id, "client_id": client_id}
                )
            else:
                return jsonify(
                    {"success": False, "error": "No prompt_id returned"}
                ), 500

    except urllib.error.HTTPError as e:
        # Read the error response body for more details
        error_body = ""
        try:
            error_body = e.read().decode("utf-8")
            error_json = json.loads(error_body)

            # Build a user-friendly error message
            error_parts = []

            # Main error message
            main_error = error_json.get("error", {})
            if isinstance(main_error, dict):
                main_msg = main_error.get("message", "")
                if main_msg:
                    error_parts.append(main_msg)
            elif isinstance(main_error, str):
                error_parts.append(main_error)

            # Node-specific errors (validation failures)
            node_errors = error_json.get("node_errors", {})
            for node_id, node_error in node_errors.items():
                node_type = node_error.get("class_type", "Unknown")
                errors = node_error.get("errors", [])
                for err in errors:
                    err_msg = err.get("message", "Unknown error")
                    details = err.get("details", "")
                    if details:
                        error_parts.append(
                            f"Node {node_id} ({node_type}): {err_msg} - {details}"
                        )
                    else:
                        error_parts.append(f"Node {node_id} ({node_type}): {err_msg}")

            error_msg = "\n".join(error_parts) if error_parts else str(e)

        except Exception:
            error_msg = f"{e}: {error_body}" if error_body else str(e)

        print(f"ComfyUI HTTP Error: {error_msg}")
        return jsonify({"success": False, "error": error_msg}), 400
    except urllib.error.URLError as e:
        return jsonify({"success": False, "error": f"ComfyUI not reachable: {e}"}), 503
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/quickgen/status/<prompt_id>")
def api_quickgen_status(prompt_id):
    """Check the status of a QuickGen generation"""
    if not current_artist:
        return jsonify({"error": "Not authenticated"}), 401

    try:
        # Check history for completed prompts
        req = urllib.request.Request(
            f"{COMFYUI_API_URL}/history/{prompt_id}", method="GET"
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            history = json.loads(response.read().decode("utf-8"))

            if prompt_id in history:
                prompt_data = history[prompt_id]

                # Check for execution errors first
                status_data = prompt_data.get("status", {})
                if status_data.get("status_str") == "error":
                    # Extract error messages
                    error_messages = []
                    messages = status_data.get("messages", [])
                    for msg in messages:
                        if isinstance(msg, list) and len(msg) >= 2:
                            msg_type, msg_data = msg[0], msg[1]
                            if msg_type == "execution_error":
                                error_messages.append(
                                    f"Node {msg_data.get('node_id', '?')} ({msg_data.get('node_type', '?')}): {msg_data.get('exception_message', 'Unknown error')}"
                                )
                            elif msg_type == "execution_interrupted":
                                error_messages.append("Execution was interrupted")

                    # Also check for node_errors in prompt validation
                    if not error_messages:
                        error_messages.append("Workflow execution failed")

                    return jsonify(
                        {"status": "error", "error": "\n".join(error_messages)}
                    )

                outputs = prompt_data.get("outputs", {})

                # Find all output images
                images = []
                for node_id, node_output in outputs.items():
                    if "images" in node_output:
                        for img in node_output["images"]:
                            filename = img.get("filename")
                            subfolder = img.get("subfolder", "")
                            img_type = img.get("type", "output")

                            # Build URL to fetch image from ComfyUI
                            img_url = f"/api/quickgen/image?filename={filename}"
                            if subfolder:
                                img_url += f"&subfolder={subfolder}"
                            img_url += f"&type={img_type}"

                            images.append({"url": img_url, "filename": filename})

                if images:
                    return jsonify({"status": "completed", "images": images})

                # Prompt is in history but no images - check if it completed without output
                if status_data.get("completed", False):
                    return jsonify(
                        {
                            "status": "error",
                            "error": "Workflow completed but produced no images. Check if SaveImage node is connected.",
                        }
                    )

        # Check queue for pending prompts
        req = urllib.request.Request(f"{COMFYUI_API_URL}/queue", method="GET")

        with urllib.request.urlopen(req, timeout=10) as response:
            queue = json.loads(response.read().decode("utf-8"))

            # Check running queue
            running = queue.get("queue_running", [])
            for item in running:
                if len(item) > 1 and item[1] == prompt_id:
                    return jsonify({"status": "processing", "progress": "Running..."})

            # Check pending queue
            pending = queue.get("queue_pending", [])
            for i, item in enumerate(pending):
                if len(item) > 1 and item[1] == prompt_id:
                    return jsonify({"status": "queued", "queue_position": i + 1})

        # Not found in history or queue - might still be processing
        return jsonify({"status": "processing", "progress": "Processing..."})

    except urllib.error.URLError as e:
        return jsonify({"status": "error", "error": f"ComfyUI not reachable: {e}"}), 503
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/api/quickgen/image")
def api_quickgen_image():
    """Proxy image from ComfyUI to client"""
    if not current_artist:
        return "", 401

    filename = request.args.get("filename")
    subfolder = request.args.get("subfolder", "")
    img_type = request.args.get("type", "output")

    if not filename:
        return "", 400

    try:
        params = {"filename": filename, "subfolder": subfolder, "type": img_type}

        url = f"{COMFYUI_API_URL}/view?{urlencode(params)}"
        req = urllib.request.Request(url, method="GET")

        with urllib.request.urlopen(req, timeout=30) as response:
            image_data = response.read()
            content_type = response.headers.get("Content-Type", "image/png")

            from flask import Response

            return Response(image_data, mimetype=content_type)

    except Exception as e:
        print(f"Error fetching image from ComfyUI: {e}")
        return "", 500


@app.route("/api/quickgen/upload-image", methods=["POST"])
def api_quickgen_upload_image():
    """Upload an image to ComfyUI's input folder"""
    if not current_artist:
        return jsonify({"success": False, "error": "Not authenticated"}), 401

    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image provided"}), 400

    file = request.files["image"]
    if not file.filename:
        return jsonify({"success": False, "error": "No file selected"}), 400

    try:
        from io import BytesIO

        # Read file content
        file_content = file.read()

        # Create multipart form data manually
        boundary = "----WebKitFormBoundary" + str(uuid.uuid4()).replace("-", "")[:16]

        body = BytesIO()
        body.write(f"--{boundary}\r\n".encode())
        body.write(
            f'Content-Disposition: form-data; name="image"; filename="{file.filename}"\r\n'.encode()
        )
        body.write(f"Content-Type: {file.content_type or 'image/png'}\r\n\r\n".encode())
        body.write(file_content)
        body.write(f"\r\n--{boundary}--\r\n".encode())

        req = urllib.request.Request(
            f"{COMFYUI_API_URL}/upload/image",
            data=body.getvalue(),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
            return jsonify(
                {
                    "success": True,
                    "filename": result.get("name"),
                    "subfolder": result.get("subfolder", ""),
                }
            )

    except urllib.error.URLError as e:
        return jsonify({"success": False, "error": f"ComfyUI not reachable: {e}"}), 503
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =============================================================================
# Assets Browser Routes
# =============================================================================

WORKSPACE_ROOT = "/workspace"


def get_user_allowed_roots(user):
    """Get the allowed root paths for a user's assets.
    Admins get full workspace access, regular users get their personal folders."""
    # user can be a string (artist name) or None
    username = user if isinstance(user, str) else ""

    # Admins get access to entire workspace
    if is_admin(username):
        return [""]  # Empty string = workspace root

    return [
        f"ComfyUI/output/{username}",
        f"ComfyUI/input/{username}",
    ]


def is_path_allowed(path, user):
    """Check if the given path is within the user's allowed directories.
    Admins can access any path under /workspace."""
    # Admins have full access
    if is_admin(user):
        # Still prevent path traversal attacks
        normalized = os.path.normpath(path).lstrip("/")
        # Block any path that tries to escape workspace
        if ".." in normalized:
            return False
        return True

    allowed_roots = get_user_allowed_roots(user)
    # Normalize path to prevent traversal attacks
    normalized = os.path.normpath(path).lstrip("/")
    for root in allowed_roots:
        if normalized == root or normalized.startswith(root + "/"):
            return True
    return False


def get_file_type(filename):
    """Determine file type based on extension"""
    ext = filename.lower().split(".")[-1] if "." in filename else ""
    image_exts = {"png", "jpg", "jpeg", "gif", "webp", "svg", "bmp", "tiff"}
    video_exts = {"mp4", "webm", "mov", "avi", "mkv", "m4v"}
    audio_exts = {"mp3", "wav", "ogg", "flac", "aac", "m4a"}

    if ext in image_exts:
        return "image"
    elif ext in video_exts:
        return "video"
    elif ext in audio_exts:
        return "audio"
    elif ext == "pdf":
        return "pdf"
    elif ext in {"py", "js", "ts", "json", "html", "css", "sh", "yaml", "yml", "xml"}:
        return "code"
    else:
        return "file"


def format_file_size(size_bytes):
    """Format file size in human-readable format"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


@app.route("/assets")
@app.route("/assets/")
def assets():
    """Assets landing page - show user's root folders.
    Admins see all workspace folders, regular users see their personal folders."""
    if not current_artist:
        return redirect(url_for("login"))

    folders = []
    user_is_admin = is_admin(current_artist)

    if user_is_admin:
        # Admins see all top-level folders in /workspace
        try:
            for name in os.listdir(WORKSPACE_ROOT):
                item_path = os.path.join(WORKSPACE_ROOT, name)
                if os.path.isdir(item_path):
                    folders.append(
                        {
                            "name": name,
                            "path": name,
                            "type": "folder",
                        }
                    )
            folders.sort(key=lambda x: x["name"].lower())
        except PermissionError:
            pass
    else:
        # Regular users see their personal folders
        allowed_roots = get_user_allowed_roots(current_artist)
        for root in allowed_roots:
            full_path = os.path.join(WORKSPACE_ROOT, root)
            # Create directory if it doesn't exist
            if not os.path.exists(full_path):
                os.makedirs(full_path, exist_ok=True)

            # Determine folder display name
            if "output" in root:
                display_name = "My Outputs"
                folder_type = "output"
            else:
                display_name = "My Inputs"
                folder_type = "input"

            folders.append(
                {
                    "name": display_name,
                    "path": root,
                    "type": folder_type,
                }
            )

    return render_template(
        "assets.html",
        current_user=current_artist,
        is_admin=user_is_admin,
        active_page="assets",
        page_title="Assets",
        runpod_id=get_runpod_id(),
        folders=folders,
        files=[],
        current_path="",
        breadcrumb=[],
        parent_path="",
        is_root=True,
        is_admin_view=user_is_admin,
    )


@app.route("/assets/browse/<path:subpath>")
def assets_browse(subpath):
    """Browse a specific directory.
    Admins can browse any folder, regular users only their personal folders."""
    if not current_artist:
        return redirect(url_for("login"))

    user_is_admin = is_admin(current_artist)

    # Security check
    if not is_path_allowed(subpath, current_artist):
        return "Access denied", 403

    full_path = os.path.join(WORKSPACE_ROOT, subpath)

    if not os.path.exists(full_path):
        return "Path not found", 404

    if not os.path.isdir(full_path):
        return "Not a directory", 400

    # List directory contents
    folders = []
    files = []

    try:
        for name in os.listdir(full_path):
            item_path = os.path.join(full_path, name)

            if os.path.isdir(item_path):
                folders.append(
                    {
                        "name": name,
                        "path": os.path.join(subpath, name),
                    }
                )
            else:
                stat = os.stat(item_path)
                files.append(
                    {
                        "name": name,
                        "path": os.path.join(subpath, name),
                        "size": stat.st_size,
                        "size_formatted": format_file_size(stat.st_size),
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime(
                            "%Y-%m-%d %H:%M"
                        ),
                        "type": get_file_type(name),
                    }
                )

        # Sort folders and files alphabetically
        folders.sort(key=lambda x: x["name"].lower())
        files.sort(key=lambda x: x["name"].lower())

    except PermissionError:
        return "Permission denied", 403

    # Build breadcrumb based on user type
    parts = subpath.split("/")
    breadcrumb = []
    current_crumb_path = ""

    if user_is_admin:
        # Admins see full path breadcrumbs
        for part in parts:
            if part:
                current_crumb_path = (
                    os.path.join(current_crumb_path, part)
                    if current_crumb_path
                    else part
                )
                breadcrumb.append(
                    {
                        "name": part,
                        "path": current_crumb_path,
                    }
                )

        # Determine parent path for back button
        if len(breadcrumb) > 1:
            parent_path = breadcrumb[-2]["path"]
        elif len(breadcrumb) == 1:
            parent_path = ""
        else:
            parent_path = ""

        # Page title is the current folder name or "Assets"
        page_title = parts[-1] if parts else "Assets"

    else:
        # Regular users: show "My Outputs/Inputs" then subfolders (skip username folder)

        # Find the index of "output" or "input" in the path
        root_index = -1
        root_type = None
        for i, part in enumerate(parts):
            if part == "output":
                root_index = i
                root_type = "output"
                break
            elif part == "input":
                root_index = i
                root_type = "input"
                break

        # Build breadcrumb: "My Outputs/Inputs" first, then subfolders after username
        # Skip the username folder (root_index + 1) from display
        username_index = root_index + 1 if root_index >= 0 else -1

        # Build path as we iterate
        for i, part in enumerate(parts):
            if part:
                current_crumb_path = (
                    os.path.join(current_crumb_path, part)
                    if current_crumb_path
                    else part
                )

                # At username folder level, add "My Outputs" or "My Inputs" with THIS path
                # (the user's actual root folder path, not the output/input folder)
                if i == username_index and username_index >= 0:
                    display_name = (
                        "My Outputs" if root_type == "output" else "My Inputs"
                    )
                    breadcrumb.append(
                        {
                            "name": display_name,
                            "path": current_crumb_path,
                        }
                    )
                # Add subfolders after username folder
                elif i > username_index and username_index >= 0:
                    breadcrumb.append(
                        {
                            "name": part,
                            "path": current_crumb_path,
                        }
                    )

        # Determine parent path for back button
        if len(breadcrumb) > 1:
            parent_path = breadcrumb[-2]["path"]
        elif len(breadcrumb) == 1:
            parent_path = ""
        else:
            parent_path = ""

        # Determine page title from path
        if "output" in subpath:
            page_title = "My Outputs"
        elif "input" in subpath:
            page_title = "My Inputs"
        else:
            page_title = "Assets"

    return render_template(
        "assets.html",
        current_user=current_artist,
        is_admin=user_is_admin,
        active_page="assets",
        page_title=page_title,
        runpod_id=get_runpod_id(),
        folders=folders,
        files=files,
        current_path=subpath,
        breadcrumb=breadcrumb,
        parent_path=parent_path,
        is_root=False,
        is_admin_view=user_is_admin,
    )


@app.route("/assets/download/<path:filepath>")
def assets_download(filepath):
    """Download a file"""
    if not current_artist:
        return jsonify({"error": "Not authenticated"}), 401

    if not is_path_allowed(filepath, current_artist):
        return jsonify({"error": "Access denied"}), 403

    full_path = os.path.join(WORKSPACE_ROOT, filepath)

    if not os.path.exists(full_path):
        return jsonify({"error": "File not found"}), 404

    if not os.path.isfile(full_path):
        return jsonify({"error": "Not a file"}), 400

    return send_file(full_path, as_attachment=True)


@app.route("/assets/preview/<path:filepath>")
def assets_preview(filepath):
    """Preview/stream a file (for images and videos)"""
    if not current_artist:
        return "", 401

    if not is_path_allowed(filepath, current_artist):
        return "", 403

    full_path = os.path.join(WORKSPACE_ROOT, filepath)

    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return "", 404

    # Determine MIME type
    ext = filepath.lower().split(".")[-1] if "." in filepath else ""
    mime_types = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "webp": "image/webp",
        "svg": "image/svg+xml",
        "mp4": "video/mp4",
        "webm": "video/webm",
        "mov": "video/quicktime",
        "avi": "video/x-msvideo",
        "pdf": "application/pdf",
    }
    mimetype = mime_types.get(ext, "application/octet-stream")

    return send_file(full_path, mimetype=mimetype)


@app.route("/assets/delete/<path:filepath>", methods=["POST"])
def assets_delete(filepath):
    """Delete a file"""
    if not current_artist:
        return jsonify({"success": False, "error": "Not authenticated"}), 401

    if not is_path_allowed(filepath, current_artist):
        return jsonify({"success": False, "error": "Access denied"}), 403

    full_path = os.path.join(WORKSPACE_ROOT, filepath)

    if not os.path.exists(full_path):
        return jsonify({"success": False, "error": "File not found"}), 404

    if not os.path.isfile(full_path):
        return jsonify({"success": False, "error": "Not a file"}), 400

    try:
        os.remove(full_path)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/assets/download-folder/<path:folderpath>")
def assets_download_folder(folderpath):
    """Download a folder as a zip file"""
    import tempfile
    import zipfile

    if not current_artist:
        return jsonify({"error": "Not authenticated"}), 401

    if not is_path_allowed(folderpath, current_artist):
        return jsonify({"error": "Access denied"}), 403

    full_path = os.path.join(WORKSPACE_ROOT, folderpath)

    if not os.path.exists(full_path):
        return jsonify({"error": "Folder not found"}), 404

    if not os.path.isdir(full_path):
        return jsonify({"error": "Not a folder"}), 400

    folder_name = os.path.basename(folderpath)

    # Create a temporary zip file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    try:
        with zipfile.ZipFile(temp_file.name, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(full_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, full_path)
                    zipf.write(file_path, os.path.join(folder_name, arcname))

        return send_file(
            temp_file.name,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{folder_name}.zip",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/assets/delete-folder/<path:folderpath>", methods=["POST"])
def assets_delete_folder(folderpath):
    """Delete a folder and all its contents"""
    import shutil

    if not current_artist:
        return jsonify({"success": False, "error": "Not authenticated"}), 401

    if not is_path_allowed(folderpath, current_artist):
        return jsonify({"success": False, "error": "Access denied"}), 403

    full_path = os.path.join(WORKSPACE_ROOT, folderpath)

    if not os.path.exists(full_path):
        return jsonify({"success": False, "error": "Folder not found"}), 404

    if not os.path.isdir(full_path):
        return jsonify({"success": False, "error": "Not a folder"}), 400

    # Prevent deleting the user's root folder
    parts = folderpath.split("/")
    # Path structure: ComfyUI/output/username or ComfyUI/input/username
    # Don't allow deleting at depth <= 3 (the username folder level)
    if len(parts) <= 3:
        return jsonify(
            {"success": False, "error": "Cannot delete root user folder"}
        ), 403

    try:
        shutil.rmtree(full_path)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/assets/api/list/<path:subpath>")
@app.route("/assets/api/list/")
@app.route("/assets/api/list")
def assets_api_list(subpath=""):
    """API endpoint to list directory contents as JSON.
    Admins see all workspace folders, regular users see their personal folders."""
    if not current_artist:
        return jsonify({"error": "Not authenticated"}), 401

    user_is_admin = is_admin(current_artist)

    # Handle root listing
    if not subpath:
        folders = []

        if user_is_admin:
            # Admins see all top-level folders in /workspace
            try:
                for name in os.listdir(WORKSPACE_ROOT):
                    item_path = os.path.join(WORKSPACE_ROOT, name)
                    if os.path.isdir(item_path):
                        folders.append(
                            {
                                "name": name,
                                "path": name,
                                "is_dir": True,
                            }
                        )
                folders.sort(key=lambda x: x["name"].lower())
            except PermissionError:
                pass
        else:
            # Regular users see their personal folders
            allowed_roots = get_user_allowed_roots(current_artist)
            for root in allowed_roots:
                full_path = os.path.join(WORKSPACE_ROOT, root)
                if not os.path.exists(full_path):
                    os.makedirs(full_path, exist_ok=True)

                if "output" in root:
                    display_name = "My Outputs"
                else:
                    display_name = "My Inputs"

                folders.append(
                    {
                        "name": display_name,
                        "path": root,
                        "is_dir": True,
                    }
                )

        return jsonify({"folders": folders, "files": []})

    if not is_path_allowed(subpath, current_artist):
        return jsonify({"error": "Access denied"}), 403

    full_path = os.path.join(WORKSPACE_ROOT, subpath)

    if not os.path.exists(full_path) or not os.path.isdir(full_path):
        return jsonify({"error": "Path not found"}), 404

    folders = []
    files = []

    try:
        for name in os.listdir(full_path):
            item_path = os.path.join(full_path, name)

            if os.path.isdir(item_path):
                folders.append(
                    {
                        "name": name,
                        "path": os.path.join(subpath, name),
                        "is_dir": True,
                    }
                )
            else:
                stat = os.stat(item_path)
                files.append(
                    {
                        "name": name,
                        "path": os.path.join(subpath, name),
                        "size": stat.st_size,
                        "size_formatted": format_file_size(stat.st_size),
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime(
                            "%Y-%m-%d %H:%M"
                        ),
                        "type": get_file_type(name),
                        "is_dir": False,
                    }
                )

        folders.sort(key=lambda x: x["name"].lower())
        files.sort(key=lambda x: x["name"].lower())

    except PermissionError:
        return jsonify({"error": "Permission denied"}), 403

    return jsonify({"folders": folders, "files": files})


# Store last move operation for undo functionality
last_move_operation = {"sources": [], "destinations": [], "timestamp": None}


@app.route("/assets/copy", methods=["POST"])
def assets_copy():
    """Copy files/folders to a destination"""
    import shutil

    if not current_artist:
        return jsonify({"success": False, "error": "Not authenticated"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    sources = data.get("sources", [])
    destination = data.get("destination", "")

    if not sources:
        return jsonify({"success": False, "error": "No source files specified"}), 400

    if not destination:
        return jsonify({"success": False, "error": "No destination specified"}), 400

    # Check permissions for destination
    if not is_path_allowed(destination, current_artist):
        return jsonify({"success": False, "error": "Access denied to destination"}), 403

    dest_full = os.path.join(WORKSPACE_ROOT, destination)
    if not os.path.exists(dest_full) or not os.path.isdir(dest_full):
        return jsonify({"success": False, "error": "Destination folder not found"}), 404

    results = []
    for source in sources:
        source_path = source.get("path", "")
        if not source_path:
            continue

        # Check permissions for source
        if not is_path_allowed(source_path, current_artist):
            results.append(
                {"path": source_path, "success": False, "error": "Access denied"}
            )
            continue

        source_full = os.path.join(WORKSPACE_ROOT, source_path)
        if not os.path.exists(source_full):
            results.append(
                {"path": source_path, "success": False, "error": "Not found"}
            )
            continue

        source_name = os.path.basename(source_path)
        dest_item = os.path.join(dest_full, source_name)

        try:
            if os.path.isdir(source_full):
                shutil.copytree(source_full, dest_item)
            else:
                shutil.copy2(source_full, dest_item)
            results.append({"path": source_path, "success": True})
        except Exception as e:
            results.append({"path": source_path, "success": False, "error": str(e)})

    success_count = sum(1 for r in results if r["success"])
    return jsonify(
        {
            "success": success_count > 0,
            "results": results,
            "copied": success_count,
            "total": len(results),
        }
    )


@app.route("/assets/move", methods=["POST"])
def assets_move():
    """Move files/folders to a destination"""
    global last_move_operation
    import shutil

    if not current_artist:
        return jsonify({"success": False, "error": "Not authenticated"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    sources = data.get("sources", [])
    destination = data.get("destination", "")

    if not sources:
        return jsonify({"success": False, "error": "No source files specified"}), 400

    if not destination:
        return jsonify({"success": False, "error": "No destination specified"}), 400

    # Check permissions for destination
    if not is_path_allowed(destination, current_artist):
        return jsonify({"success": False, "error": "Access denied to destination"}), 403

    dest_full = os.path.join(WORKSPACE_ROOT, destination)
    if not os.path.exists(dest_full) or not os.path.isdir(dest_full):
        return jsonify({"success": False, "error": "Destination folder not found"}), 404

    results = []
    moved_sources = []
    moved_destinations = []

    for source in sources:
        source_path = source.get("path", "")
        if not source_path:
            continue

        # Check permissions for source
        if not is_path_allowed(source_path, current_artist):
            results.append(
                {"path": source_path, "success": False, "error": "Access denied"}
            )
            continue

        source_full = os.path.join(WORKSPACE_ROOT, source_path)
        if not os.path.exists(source_full):
            results.append(
                {"path": source_path, "success": False, "error": "Not found"}
            )
            continue

        source_name = os.path.basename(source_path)
        dest_item = os.path.join(dest_full, source_name)
        dest_relative = os.path.join(destination, source_name)

        try:
            shutil.move(source_full, dest_item)
            results.append(
                {"path": source_path, "success": True, "new_path": dest_relative}
            )
            moved_sources.append(source_path)
            moved_destinations.append(dest_relative)
        except Exception as e:
            results.append({"path": source_path, "success": False, "error": str(e)})

    # Store for undo
    if moved_sources:
        last_move_operation = {
            "sources": moved_sources,
            "destinations": moved_destinations,
            "timestamp": datetime.now().isoformat(),
        }

    success_count = sum(1 for r in results if r["success"])
    return jsonify(
        {
            "success": success_count > 0,
            "results": results,
            "moved": success_count,
            "total": len(results),
            "can_undo": len(moved_sources) > 0,
        }
    )


@app.route("/assets/undo-move", methods=["POST"])
def assets_undo_move():
    """Undo the last move operation"""
    global last_move_operation
    import shutil

    if not current_artist:
        return jsonify({"success": False, "error": "Not authenticated"}), 401

    if not last_move_operation["sources"]:
        return jsonify({"success": False, "error": "Nothing to undo"}), 400

    # Check timestamp - only allow undo within 30 seconds
    if last_move_operation["timestamp"]:
        move_time = datetime.fromisoformat(last_move_operation["timestamp"])
        if (datetime.now() - move_time).total_seconds() > 30:
            last_move_operation = {"sources": [], "destinations": [], "timestamp": None}
            return jsonify({"success": False, "error": "Undo window expired"}), 400

    results = []
    for i, dest_path in enumerate(last_move_operation["destinations"]):
        source_path = last_move_operation["sources"][i]

        # Check permissions
        if not is_path_allowed(dest_path, current_artist):
            results.append(
                {"path": dest_path, "success": False, "error": "Access denied"}
            )
            continue

        dest_full = os.path.join(WORKSPACE_ROOT, dest_path)
        source_full = os.path.join(WORKSPACE_ROOT, source_path)

        if not os.path.exists(dest_full):
            results.append(
                {"path": dest_path, "success": False, "error": "File no longer exists"}
            )
            continue

        # Ensure parent directory exists
        source_parent = os.path.dirname(source_full)
        if not os.path.exists(source_parent):
            os.makedirs(source_parent, exist_ok=True)

        try:
            shutil.move(dest_full, source_full)
            results.append(
                {"path": dest_path, "success": True, "restored_to": source_path}
            )
        except Exception as e:
            results.append({"path": dest_path, "success": False, "error": str(e)})

    # Clear undo state
    last_move_operation = {"sources": [], "destinations": [], "timestamp": None}

    success_count = sum(1 for r in results if r["success"])
    return jsonify(
        {
            "success": success_count > 0,
            "results": results,
            "restored": success_count,
            "total": len(results),
        }
    )


@app.route("/assets/check-exists", methods=["POST"])
def assets_check_exists():
    """Check if files/folders already exist at destination"""
    if not current_artist:
        return jsonify({"success": False, "error": "Not authenticated"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    sources = data.get("sources", [])
    destination = data.get("destination", "")

    if not destination:
        return jsonify({"success": False, "error": "No destination specified"}), 400

    if not is_path_allowed(destination, current_artist):
        return jsonify({"success": False, "error": "Access denied"}), 403

    dest_full = os.path.join(WORKSPACE_ROOT, destination)
    if not os.path.exists(dest_full):
        return jsonify({"success": False, "error": "Destination not found"}), 404

    conflicts = []
    for source in sources:
        source_path = source.get("path", "")
        if not source_path:
            continue

        source_name = os.path.basename(source_path)
        dest_item = os.path.join(dest_full, source_name)

        if os.path.exists(dest_item):
            conflicts.append(
                {
                    "name": source_name,
                    "source_path": source_path,
                    "is_dir": os.path.isdir(dest_item),
                }
            )

    return jsonify(
        {"success": True, "has_conflicts": len(conflicts) > 0, "conflicts": conflicts}
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
        autostart_comfyui = data.get("autostart_comfyui", False)
    else:
        current_artist = request.form.get("artist", "")
        autostart_comfyui = request.form.get("autostart_comfyui") == "on"

    # Reset admin mode if not an admin
    if not is_admin(current_artist):
        admin_mode = False

    # Auto-start ComfyUI if requested
    if autostart_comfyui and current_artist:
        # Start ComfyUI in background thread to not block the redirect
        def start_comfyui_background():
            start_session_internal("comfy-ui", current_artist)

        thread = threading.Thread(target=start_comfyui_background)
        thread.daemon = True
        thread.start()

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
