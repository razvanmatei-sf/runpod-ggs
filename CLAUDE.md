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
This builds and pushes to GitHub Container Registry as `ghcr.io/razvanmatei-sf/runpod-nanobit:latest`.

### Local Docker Run
```bash
docker run -it --rm \
  -p 8080:8080 -p 8888:8888 -p 8188:8188 \
  -v /path/to/workspace:/workspace \
  ghcr.io/razvanmatei-sf/runpod-nanobit:latest
```

### Download AI Models
```bash
export HUGGING_FACE_HUB_TOKEN=hf_your_token
./download_flux_models.sh      # Flux diffusion models
./download_qwen_models.sh      # Qwen image models
./download_uso_models.sh       # USO models
# See other download_*.sh scripts for additional models
```

## Architecture

### Three-Service Model
- **Port 8080**: Flask artist selection UI (entry point)
- **Port 8188**: ComfyUI image generation interface
- **Port 8888**: Jupyter Lab notebook environment

### Multi-Artist Isolation
Each artist session creates isolated output at `/workspace/output/{artist_name}/`. Same ComfyUI/Jupyter processes are shared, but outputs are separated.

### Key Files
- `server/artist_name_server.py` - Core Flask app with embedded HTML frontend (613 lines)
- `server/Dockerfile` - Container definition (PyTorch 2.2.0, CUDA 12.1.1, Ubuntu 22.04)
- `server/build_artist_image.sh` - Build and push to registry
- `server/start_artist_session.sh` - Container entrypoint

### RunPod Integration
- Pod ID from `$RUNPOD_POD_ID` environment variable
- Network volume mounted at `/workspace`
- Proxied URLs: `{pod_id}-{port}.proxy.runpod.net`

### Process Management
- Port cleanup via `fuser` before service startup
- Graceful signal handling (SIGINT, SIGTERM)
- Background health monitoring thread for ComfyUI readiness (30s timeout)
- Status polling every 5s from frontend

## API Endpoints

- `GET /` - Render artist selection UI
- `POST /start_session` - Initialize session with artist name
- `GET /comfyui_status` - Check ComfyUI service readiness
- `POST /terminate` - Kill all managed processes

## Workspace Requirements

RunPod network volume must contain:
- `/workspace/ComfyUI/` - ComfyUI installation
- `/workspace/venv/` - Python virtual environment
- `/workspace/start_comfyui.sh` - ComfyUI startup script

## Tech Stack

Python 3.10, Flask 2.x, PyTorch 2.2.0, CUDA 12.1.1, Ubuntu 22.04, HuggingFace Hub
