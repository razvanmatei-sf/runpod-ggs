# ComfyStudio Docker Image
# Base image with PyTorch 2.2.0, Python 3.10, CUDA 12.1.1
FROM runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04

# Set working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    psmisc \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install UV package installer (blazingly fast pip replacement)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Install Flask for the server (ignore existing packages to avoid conflicts)
RUN pip install --ignore-installed --no-deps Flask blinker click itsdangerous werkzeug

# Set environment variables
ENV PYTHONPATH=/workspace
ENV COMFYUI_PATH=/workspace/ComfyUI
ENV HF_HOME=/workspace
ENV HF_HUB_ENABLE_HF_TRANSFER=1

# Copy startup scripts and config
COPY start_server.sh /usr/local/bin/start_server.sh
COPY server.py /usr/local/bin/server.py
COPY artist_names.sh /usr/local/bin/artist_names.sh
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
