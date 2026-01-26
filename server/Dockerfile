# SF AI Workbench - Minimal Docker Image
# Base image: NVIDIA CUDA 13.0 runtime on Ubuntu 24.04
FROM nvidia/cuda:13.0.0-runtime-ubuntu24.04

WORKDIR /workspace

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# System packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    build-essential \
    openssh-server \
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

# Install Python 3.10 from deadsnakes PPA
RUN add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 && \
    ln -sf /usr/bin/python3.10 /usr/bin/python

# Node.js (for AI-Toolkit and LoRA-Tool)
RUN curl -fsSL https://deb.nodesource.com/setup_23.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Python packages (use --ignore-installed to avoid conflicts with system packages)
RUN pip install --no-cache-dir --break-system-packages --ignore-installed \
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

# Labels for RunPod
LABEL runpod.port.8080="SF-AI-Workbench"
LABEL runpod.port.8675="AI-Toolkit"
LABEL runpod.port.7861="SwarmUI"
LABEL runpod.port.3000="LoRA-Tool"
LABEL runpod.port.8188="ComfyUI"
LABEL runpod.port.8888="JupyterLab"
LABEL runpod.ports="8080/http:SF-AI-Workbench,8675/http:AI-Toolkit,7861/http:SwarmUI,3000/http:LoRA-Tool,8188/http:ComfyUI,8888/http:JupyterLab"
LABEL org.opencontainers.image.ports="8080,8675,7861,3000,8188,8888"

CMD ["/usr/local/bin/start_server.sh"]
