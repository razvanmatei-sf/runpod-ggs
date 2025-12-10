# ComfyStudio Docker Image
# Base image with PyTorch 2.2.0, Python 3.10, CUDA 12.1.1
FROM runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04

# Set working directory
WORKDIR /workspace

# Set noninteractive to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (includes AI-Toolkit requirements)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    curl \
    psmisc \
    python3-pip \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    python3-venv \
    python3-opencv \
    build-essential \
    cmake \
    ffmpeg \
    htop \
    nvtop \
    tmux \
    openssh-client \
    openssh-server \
    openssl \
    rsync \
    unzip \
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 23
RUN curl -sL https://deb.nodesource.com/setup_23.x -o /tmp/nodesource_setup.sh && \
    bash /tmp/nodesource_setup.sh && \
    apt-get update && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Flask for the server (ignore existing packages to avoid conflicts)
RUN pip install --ignore-installed --no-deps Flask blinker click itsdangerous werkzeug

# Set environment variables
ENV PYTHONPATH=/workspace
ENV COMFYUI_PATH=/workspace/ComfyUI
ENV HF_HOME=/workspace
ENV HF_HUB_ENABLE_HF_TRANSFER=1
ENV TORCH_CUDA_ARCH_LIST="8.0 8.6 8.9 9.0 10.0 12.0"

# Copy startup scripts and config
COPY start_server.sh /usr/local/bin/start_server.sh
COPY server.py /usr/local/bin/server.py
COPY user_management.py /usr/local/bin/user_management.py
COPY artist_names.sh /usr/local/bin/artist_names.sh
COPY templates /usr/local/bin/templates
COPY static /usr/local/bin/static
RUN chmod +x /usr/local/bin/start_server.sh
RUN chmod +x /usr/local/bin/server.py
RUN chmod +x /usr/local/bin/artist_names.sh

# Create jupyter config directory
RUN mkdir -p /root/.jupyter

# Configure Jupyter Lab
RUN jupyter lab --generate-config && \
    echo "c.ServerApp.ip = '0.0.0.0'" >> /root/.jupyter/jupyter_lab_config.py && \
    echo "c.ServerApp.port = 8888" >> /root/.jupyter/jupyter_lab_config.py && \
    echo "c.ServerApp.token = ''" >> /root/.jupyter/jupyter_lab_config.py && \
    echo "c.ServerApp.password = ''" >> /root/.jupyter/jupyter_lab_config.py && \
    echo "c.ServerApp.allow_root = True" >> /root/.jupyter/jupyter_lab_config.py && \
    echo "c.ServerApp.allow_origin = '*'" >> /root/.jupyter/jupyter_lab_config.py && \
    echo "c.ServerApp.disable_check_xsrf = True" >> /root/.jupyter/jupyter_lab_config.py

# Expose ports
EXPOSE 8080
EXPOSE 8675
EXPOSE 7861
EXPOSE 3000
EXPOSE 8188
EXPOSE 8888

# Labels for RunPod - using multiple formats for compatibility
LABEL runpod.port.8080="ComfyStudio"
LABEL runpod.port.8675="AI-Toolkit"
LABEL runpod.port.7861="SwarmUI"
LABEL runpod.port.3000="LoRA-Tool"
LABEL runpod.port.8188="ComfyUI"
LABEL runpod.port.8888="JupyterLab"

# Alternative label formats for RunPod
LABEL runpod.ports="8080/http:ComfyStudio,8675/http:AI-Toolkit,7861/http:SwarmUI,3000/http:LoRA-Tool,8188/http:ComfyUI,8888/http:JupyterLab"

# Standard Docker labels
LABEL org.opencontainers.image.ports="8080,8675,7861,3000,8188,8888"

# Default command
CMD ["/usr/local/bin/start_server.sh"]
