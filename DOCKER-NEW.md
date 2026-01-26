# Docker Image Optimization Plan

This document outlines the plan to migrate from the current RunPod base image to a minimal custom image.

## Current State

- **Base image:** `runpod/pytorch:1.0.3-cu1300-torch291-ubuntu2404`
- **Issues:** Bloated with unnecessary packages (multiple Python versions, extensive dev libraries, RunPod-specific tooling we don't use)
- **Estimated size:** ~5-8GB compressed

## Target State

- **Base image:** `nvidia/cuda:13.0.0-runtime-ubuntu24.04`
- **Goal:** Minimal image with only what SF AI Workbench actually needs
- **Estimated size:** ~1.5-2GB compressed

## Why Not Other Distros?

- **Alpine Linux:** Not viable. Uses musl libc instead of glibc, causing compatibility issues with CUDA binaries and PyTorch wheels.
- **Arch Linux:** Not viable. Rolling release = instability. No official NVIDIA CUDA images. PyTorch wheels target Ubuntu/Debian glibc versions.
- **Debian Slim:** Not viable. NVIDIA doesn't provide official CUDA images for Debian.

Ubuntu is the only practical choice for CUDA + PyTorch workloads.

## What We're Removing

- RunPod's nginx proxy system (we use Flask directly on port 8080)
- Multiple Python versions (3.9, 3.10, 3.11, 3.12, 3.13) - we only need 3.10
- Pre-installed PyTorch (each tool installs its own in venv)
- Extensive dev libraries from RunPod base

## What We're Keeping/Adding

### System Packages

| Package | Purpose | Size Impact |
|---------|---------|-------------|
| build-essential | DeepSpeed JIT compilation, custom nodes | ~150MB |
| openssh-server | SSH access to container | ~5MB |
| python3.10, python3.10-venv, python3.10-dev | Python runtime | ~50MB |
| git | Cloning repos | ~30MB |
| wget, curl, aria2 | Downloading models | ~10MB |
| ffmpeg | Video processing in ComfyUI | ~80MB |
| libgl1 | OpenCV/image processing | ~5MB |
| nodejs | AI-Toolkit and LoRA-Tool | ~100MB |
| htop, nvtop, tmux | Required by AI-Toolkit | ~10MB |
| unzip, psmisc | Utilities | ~5MB |

### Python Packages

| Package | Purpose |
|---------|---------|
| Flask, blinker, click, itsdangerous, werkzeug | Web server |
| jupyterlab, ipywidgets | Interactive Python environment |

## Dockerfile Draft

```dockerfile
# SF AI Workbench - Minimal Docker Image
FROM nvidia/cuda:13.0.0-runtime-ubuntu24.04

WORKDIR /workspace

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# System packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    openssh-server \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    python3-pip \
    git \
    wget \
    curl \
    aria2 \
    ffmpeg \
    libgl1 \
    htop \
    nvtop \
    tmux \
    unzip \
    psmisc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Node.js (for AI-Toolkit and LoRA-Tool)
RUN curl -fsSL https://deb.nodesource.com/setup_23.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Python packages
RUN pip install --no-cache-dir \
    Flask blinker click itsdangerous werkzeug \
    jupyterlab ipywidgets

# SSH setup
RUN mkdir -p /var/run/sshd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# Jupyter config
RUN mkdir -p /root/.jupyter && \
    echo "c.ServerApp.ip = '0.0.0.0'" >> /root/.jupyter/jupyter_lab_config.py && \
    echo "c.ServerApp.port = 8888" >> /root/.jupyter/jupyter_lab_config.py && \
    echo "c.ServerApp.token = ''" >> /root/.jupyter/jupyter_lab_config.py && \
    echo "c.ServerApp.password = ''" >> /root/.jupyter/jupyter_lab_config.py && \
    echo "c.ServerApp.allow_root = True" >> /root/.jupyter/jupyter_lab_config.py && \
    echo "c.ServerApp.allow_origin = '*'" >> /root/.jupyter/jupyter_lab_config.py && \
    echo "c.ServerApp.disable_check_xsrf = True" >> /root/.jupyter/jupyter_lab_config.py

# Environment variables
ENV PYTHONPATH=/workspace
ENV COMFYUI_PATH=/workspace/ComfyUI
ENV HF_HOME=/workspace
ENV HF_HUB_ENABLE_HF_TRANSFER=1
ENV TORCH_CUDA_ARCH_LIST="8.0 8.6 8.9 9.0 10.0 12.0"

# Copy server files
COPY start_server.sh /usr/local/bin/start_server.sh
COPY server.py /usr/local/bin/server.py
COPY user_management.py /usr/local/bin/user_management.py
COPY artist_names.sh /usr/local/bin/artist_names.sh
COPY templates /usr/local/bin/templates
COPY static /usr/local/bin/static

RUN chmod +x /usr/local/bin/start_server.sh /usr/local/bin/server.py /usr/local/bin/artist_names.sh

# Expose ports
EXPOSE 8080 8675 7861 3000 8188 8888

# Labels
LABEL runpod.port.8080="SF-AI-Workbench"
LABEL runpod.port.8675="AI-Toolkit"
LABEL runpod.port.7861="SwarmUI"
LABEL runpod.port.3000="LoRA-Tool"
LABEL runpod.port.8188="ComfyUI"
LABEL runpod.port.8888="JupyterLab"

CMD ["/usr/local/bin/start_server.sh"]
```

## Migration Steps

1. Build new image locally and test
2. Verify all install scripts still work (ComfyUI, AI-Toolkit, SwarmUI, LoRA-Tool)
3. Test tool startup/shutdown
4. Test model downloads
5. Compare image sizes (before/after)
6. Deploy to RunPod and validate

## Notes

- PyTorch is NOT included in the base image - each tool (ComfyUI, AI-Toolkit) installs its own version in a venv
- This means first-time tool installation takes longer, but the base image is much smaller
- SSH password needs to be set (either in Dockerfile or at runtime via environment variable)

## Open Questions

- Do we need cmake? (Currently not included - add if compilation fails)
- Should we pin Node.js version instead of using latest 23.x?
