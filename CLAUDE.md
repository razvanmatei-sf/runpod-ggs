# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RunPod NanoBit is a containerized web application for running ComfyUI on RunPod cloud infrastructure. It provides a multi-artist collaborative environment with per-artist isolated output directories, session management via Flask, and Jupyter Lab integration.

## Build and Deployment

### Build Docker Image
```bash
cd server/
./build_artist_image.sh
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

### Three-Service Model
- **Port 8080**: Flask artist selection UI (entry point)
- **Port 8188**: ComfyUI image generation interface
- **Port 8888**: Jupyter Lab notebook environment

### Multi-Artist Isolation
Each artist session creates isolated output at `/workspace/ComfyUI/output/{artist_name}/`. Same ComfyUI/Jupyter processes are shared, but outputs are separated.

### Key Paths on RunPod
- **ComfyUI Installation**: `/workspace/ComfyUI/`
- **Python Virtual Environment**: `/workspace/ComfyUI/venv/`
- **Artist Output Directories**: `/workspace/ComfyUI/output/{artist_name}/`
- **Models Directory**: `/workspace/models/`

### Key Files
- `server/artist_name_server.py` - Core Flask app with embedded HTML frontend
- `server/Dockerfile` - Container definition (PyTorch 2.2.0, CUDA 12.1.1, Ubuntu 22.04)
- `server/build_artist_image.sh` - Build and push to ghcr.io registry
- `server/start_artist_session.sh` - Container entrypoint, validates workspace structure
- `download_flux_models.sh` - Downloads Flux models with skip-if-exists logic
- `download_qwen_all.sh` - Consolidated Qwen model downloads with HF optimizations

### RunPod Integration
- Pod ID from `$RUNPOD_POD_ID` environment variable
- Network volume mounted at `/workspace`
- Proxied URLs: `https://{pod_id}-{port}.proxy.runpod.net`
- Environment variables set: `HF_HOME=/workspace`, `HF_HUB_ENABLE_HF_TRANSFER=1`

### Process Management
- Port cleanup via `fuser -k` before service startup (8080, 8888, 8188)
- Graceful signal handling (SIGINT, SIGTERM)
- Background health monitoring thread for ComfyUI readiness (polls for 30s)
- Frontend status polling every 5s
- ComfyUI started with `--use-sage-attention` flag

## API Endpoints

- `GET /` - Render artist selection UI (reads existing artist folders)
- `POST /start_session` - Initialize session with artist name, starts ComfyUI and Jupyter
- `GET /comfyui_status` - Check ComfyUI service readiness via localhost:8188/api/prompt
- `POST /terminate` - Kill all managed processes on ports 8188 and 8888

## Workspace Requirements

RunPod network volume must contain:
- `/workspace/ComfyUI/` - ComfyUI installation
- `/workspace/ComfyUI/venv/` - Python virtual environment with ComfyUI dependencies
- `/workspace/ComfyUI/output/` - Base output directory (artist subfolders created automatically)
- `/workspace/models/` - AI models (diffusion_models, clip, vae, controlnet, etc.)

Optional scripts on workspace:
- `/workspace/start_comfyui.sh` - Manual ComfyUI startup script

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

## Artists

Create artist folders by running `./artist_names.sh` on RunPod workspace:
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
- Razvan Matei
- Serhii Yashyn

**Note**: Artist names with spaces are fully supported. The Flask app uses subprocess list args (not shell=True) and Python's os.makedirs(), both of which handle spaces correctly.

## First-Time RunPod Setup

1. Create template with image: `ghcr.io/razvanmatei-sf/runpod-ggs:latest`
2. Mount network volume at `/workspace`
3. Expose ports: 8080, 8888, 8188
4. Start pod and connect to Jupyter (port 8888)
5. Upload and run `artist_names.sh` to create artist folders
6. Upload and run model download scripts as needed (flux, qwen, etc.)
7. Install ComfyUI at `/workspace/ComfyUI/` with venv at `/workspace/ComfyUI/venv/`
8. Restart pod - artist selection UI will be available on port 8080
