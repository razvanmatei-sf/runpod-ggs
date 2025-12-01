# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ComfyStudio is a containerized web application for running ComfyUI on RunPod cloud infrastructure. It provides a multi-user collaborative environment with per-user isolated output directories, admin mode for installations, session management via Flask, and Jupyter Lab integration.

## Build and Deployment

### Build Docker Image
```bash
cd server/
./build_server.sh
```
This builds and pushes to GitHub Container Registry as `ghcr.io/razvanmatei-sf/runpod-ggs:latest`.

### Local Docker Run
```bash
docker run -it --rm \
  -p 8080:8080 -p 8888:8888 -p 8188:8188 \
  -v /path/to/workspace:/workspace \
  ghcr.io/razvanmatei-sf/runpod-ggs:latest
```

### Download AI Models
```bash
export HUGGING_FACE_HUB_TOKEN=hf_your_token
export HF_HUB_ENABLE_HF_TRANSFER=1
export HF_XET_CHUNK_CACHE_SIZE_BYTES=90737418240
./download_flux_models.sh      # Flux diffusion models (~40-50 GB)
./download_qwen_all.sh         # All Qwen models (consolidated)
# See other download_*.sh scripts for additional models
```

## Architecture

### Service Ports
- **Port 8080**: ComfyStudio Flask UI (entry point)
- **Port 8675**: AI-Toolkit UI
- **Port 7861**: SwarmUI web interface
- **Port 3000**: LoRA-Tool dataset helper
- **Port 8188**: ComfyUI image generation interface
- **Port 8888**: Jupyter Lab notebook environment

### Multi-User Isolation
Each user session creates isolated output at `/workspace/ComfyUI/output/{user_name}/`. Same ComfyUI/Jupyter processes are shared, but outputs are separated.

### Key Paths on RunPod
- **ComfyUI Installation**: `/workspace/ComfyUI/`
- **Python Virtual Environment**: `/workspace/ComfyUI/venv/`
- **User Output Directories**: `/workspace/ComfyUI/output/{user_name}/`
- **Models Directory**: `/workspace/models/`
- **Cloned Repository**: `/workspace/runpod-ggs/`

### Key Files
- `server/server.py` - Core Flask app with embedded HTML frontend
- `server/Dockerfile` - Container definition (PyTorch 2.2.0, CUDA 12.1.1, Ubuntu 22.04)
- `server/build_server.sh` - Build and push to ghcr.io registry
- `server/start_server.sh` - Container entrypoint, clones/pulls repo, starts server
- `server/artist_names.sh` - Single source of truth for users and admins
- `setup/` - Installation and startup scripts for tools

### User Configuration (artist_names.sh)

All users are defined in `server/artist_names.sh` with a single `USERS` array:
```bash
USERS=(
    "Regular User"
    "Admin User:admin"    # :admin suffix grants admin mode access
)
```

The `:admin` suffix determines who can access the admin toggle in the UI. This is the **single source of truth** - no user/admin lists are hardcoded in server.py.

### Git Auto-Sync on Startup

The `start_server.sh` script automatically clones or pulls the latest code from GitHub on pod startup:
- Repository cloned to `/workspace/runpod-ggs/`
- If repo exists, performs `git fetch --all && git reset --hard origin/main && git pull`
- Admin Install/Update buttons execute scripts from the cloned repo

### Setup Script Naming Convention

Scripts in `setup/` folders follow this pattern:
- `setup/{tool}/install_{tool}.sh` - Installation script
- `setup/{tool}/start_{tool}.sh` - Startup script

Example: `setup/comfy/install_comfy.sh`, `setup/comfy/start_comfy.sh`

### RunPod Integration
- Pod ID from `$RUNPOD_POD_ID` environment variable
- Network volume mounted at `/workspace`
- Proxied URLs: `https://{pod_id}-{port}.proxy.runpod.net`
- Environment variables set: `HF_HOME=/workspace`, `HF_HUB_ENABLE_HF_TRANSFER=1`
- `REPO_DIR` environment variable points to cloned repo path

### Process Management
- Port cleanup via `fuser -k` before service startup (8080, 8888, 8188)
- Graceful signal handling (SIGINT, SIGTERM)
- Background health monitoring thread for ComfyUI readiness (polls for 30s)
- Frontend status polling every 5s
- ComfyUI started with `--use-sage-attention` flag

## API Endpoints

- `GET /` - Render user selection UI
- `GET /debug` - Debug endpoint showing parsed USERS, ADMINS, current state
- `POST /start_session` - Start a tool session (ComfyUI, JupyterLab, etc.)
- `POST /stop_session` - Stop a running tool session
- `POST /set_artist` - Set current user
- `POST /set_admin_mode` - Toggle admin mode
- `POST /admin_action` - Run install/update scripts (admin only)
- `POST /download_models` - Download AI models with tokens
- `GET /logs` - Get terminal output logs (for polling)
- `POST /clear_logs` - Clear terminal output logs
- `GET /tool_status/<tool_id>` - Check if tool is installed/running

## JavaScript Template Gotchas

**IMPORTANT**: When writing JavaScript in the Python template string (`HTML_TEMPLATE`):

1. **Escape newlines**: Use `\\n` instead of `\n` in JavaScript strings
   ```python
   # WRONG - will break JavaScript
   appendToTerminal('Done\n', 'success');

   # CORRECT
   appendToTerminal('Done\\n', 'success');
   ```

2. **Avoid template literals**: Use string concatenation instead of backticks
   ```python
   # WRONG - can cause issues
   const url = `https://${host}`;

   # CORRECT
   var url = 'https://' + host;
   ```

3. **Use Jinja safely**: For JSON data, use `{{ var | tojson | safe }}`

4. **CSS visibility for toggle**: Use `visibility: hidden/visible` instead of `display: none/flex` for elements that need layout space reserved

## Tech Stack

- Python 3.10
- Flask 3.1.x (with blinker, click, itsdangerous, werkzeug)
- PyTorch 2.2.0
- CUDA 12.1.1
- Ubuntu 22.04
- HuggingFace Hub with transfer optimization
- Jupyter Lab (no auth, root allowed)

## GitHub Container Registry

Image: `ghcr.io/razvanmatei-sf/runpod-ggs:latest`

To make public for RunPod access:
1. Go to: https://github.com/users/razvanmatei-sf/packages/container/runpod-ggs/settings
2. Change visibility to Public

## Users

Users are defined in `server/artist_names.sh`. Add `:admin` suffix for admin access:
- Rosa Macak Cizmesija
- Karlo Vukovic
- Marko Kahlina
- Katarina Zidar
- Oleg Moskaljov
- Ivan Murat
- Matej Urukalo
- Ivor Strelar
- Ivan Prlic
- Josipa Filipcic Mazar
- Viktorija Samardzic
- Serhii Yashyn
- Razvan Matei (admin)

**Note**: User names with spaces are fully supported. The Flask app uses subprocess list args (not shell=True) and Python's os.makedirs(), both of which handle spaces correctly.

## First-Time RunPod Setup

1. Create template with image: `ghcr.io/razvanmatei-sf/runpod-ggs:latest`
2. Mount network volume at `/workspace`
3. Expose ports: 8080, 8675, 7861, 3000, 8888, 8188
4. Start pod - UI will be available on port 8080
5. Select admin user and enable Admin Mode
6. Use Install buttons to set up tools (ComfyUI, etc.)
7. Use Models Download page to download required models
8. Regular users can then select their profile and use the tools

## Debugging

Visit `/debug` endpoint to see:
- Parsed USERS and ADMINS arrays
- REPO_DIR path
- Current artist/admin state

Check browser console (F12) for JavaScript errors.
