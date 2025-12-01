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
- **Port 3000**: LoRA-Tool dataset helper (bundled app)
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
- **LoRA-Tool**: Runs directly from `/workspace/runpod-ggs/setup/lora-tool/`

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
- `setup/{tool}/install_{tool}.sh` - Installation script (for external tools)
- `setup/{tool}/start_{tool}.sh` - Startup script
- `setup/{tool}/reinstall_{tool}.sh` - Reinstall with backup
- `setup/{tool}/update_{tool}.sh` - Update script
- `setup/{tool}/kill_{tool}.sh` - Process termination

Example: `setup/comfy/install_comfy.sh`, `setup/comfy/start_comfy.sh`

**Note**: LoRA-Tool is bundled in the repo and runs directly - no install script needed

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

**CRITICAL**: The HTML_TEMPLATE must be a RAW STRING to prevent Python from interpreting backslashes!

```python
# CORRECT - Use raw string
HTML_TEMPLATE = r"""
<!DOCTYPE html>
...
```

**IMPORTANT**: When writing JavaScript in the Python template string (`HTML_TEMPLATE`):

1. **Use raw string (r""")**: This prevents Python from interpreting `\\n` as `\n` (which would become a literal newline in HTML, breaking JavaScript strings)
   ```python
   # With r""", you can use \\n which stays as \\n in the rendered HTML
   appendToTerminal('Done\\n', 'success');
   ```

2. **Escape Jinja variables**: Use `| e` filter for variables in JavaScript strings
   ```python
   var runpodId = '{{ runpod_id | e }}';
   ```

3. **Avoid template literals**: Use string concatenation instead of backticks
   ```python
   # WRONG - can cause issues
   const url = `https://${host}`;

   # CORRECT
   var url = 'https://' + host;
   ```

4. **Use Jinja safely**: For JSON data, use `{{ var | tojson | safe }}`

5. **CSS visibility for toggle**: Use `visibility: hidden/visible` instead of `display: none/flex` for elements that need layout space reserved

## Tech Stack

- Python 3.10
- Flask 3.1.x (with blinker, click, itsdangerous, werkzeug)
- PyTorch 2.2.0 (base image), PyTorch nightly cu128 (AI-Toolkit venv)
- CUDA 12.1.1 (base image) / CUDA 12.8 (for RTX 50-series in AI-Toolkit)
- Ubuntu 22.04
- UV package manager (10-100x faster than pip)
- Node.js 23 (for AI-Toolkit UI)
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
6. Use Install buttons to set up tools (ComfyUI, AI-Toolkit, SwarmUI)
7. Use Models Download page to download required models
8. LoRA-Tool is bundled - ready to use immediately (no install needed)
9. Regular users can then select their profile and use the tools

## Debugging

Visit `/debug` endpoint to see:
- Parsed USERS and ADMINS arrays
- REPO_DIR path
- Current artist/admin state

Check browser console (F12) for JavaScript errors.

## AI-Toolkit Installation

### Requirements
- RTX 50-series GPUs require PyTorch nightly with CUDA 12.8
- Installation takes 10-20 minutes (PyTorch, dependencies, UI build)
- Network volume at `/workspace` persists installations across pod restarts

### Installation Method
AI-Toolkit uses UV package manager for faster installation:
- Creates venv at `/workspace/ai-toolkit/venv/`
- Installs PyTorch nightly with CUDA 12.8 (RTX 50-series support)
- Installs all requirements.txt dependencies
- Builds UI with npm (includes Prisma client generation)

### Common Issues

**Install fails from admin panel but works in terminal:**
- Cause: Flask subprocess doesn't inherit full PATH
- Solution: Install script uses full paths (`/root/.cargo/bin/uv`)
- Fix: Export PATH at start of script

**Slow numpy/sympy installation:**
- Some packages build from source with PyTorch nightly cu128
- UV is still faster than pip even when building from source
- Trade-off necessary for RTX 50-series support

**Terminal closes before showing errors:**
- Fixed: Removed auto-reload after installation
- Terminal now stays open to show full error output
- User can copy logs and manually refresh when ready

### Starting AI-Toolkit
AI-Toolkit start script:
1. Checks for node_modules and installs if missing
2. Generates Prisma client if needed
3. Runs `npm run start` (starts worker + Next.js UI via concurrently)
4. UI available on port 8675

### Official AI-Toolkit Reference
- GitHub: https://github.com/ostris/ai-toolkit
- Their Docker uses similar approach but pre-builds everything
- Our approach: Install on-demand, updates via git pull

## Current Issues

### AI-Toolkit Install from Admin Panel
**Status**: Installation works in JupyterLab terminal but may fail from admin panel
**Symptoms**: Process starts but fails silently or with errors
**Debug**: Terminal now stays open to show errors (auto-reload removed)
**Next Steps**: Check logs in admin terminal for specific error messages

### Tools Status
- ✅ ComfyUI: Working with UV installer
- ✅ JupyterLab: Built-in, always available
- ✅ LoRA-Tool: Bundled, runs from repo
- 🔧 AI-Toolkit: Installation works in terminal, troubleshooting admin panel install
- ❓ SwarmUI: Not yet tested

## Latest Session Changes (Dec 2025)

1. **Fixed JavaScript template escaping** - Changed `HTML_TEMPLATE = """` to `HTML_TEMPLATE = r"""` (raw string)
2. **AI-Toolkit CUDA 12.8.1** - Upgraded to PyTorch nightly for RTX 50-series support
3. **UV package manager** - All tool installations use UV for 10-100x speed improvement
4. **UI improvements** - Always show tool name, timer indicates running status
5. **Terminal persistence** - Removed auto-reload to keep errors visible
6. **Path fixes** - Use full paths in install scripts for Flask subprocess compatibility
7. **Consolidated README** - Single comprehensive README.md for repository page
