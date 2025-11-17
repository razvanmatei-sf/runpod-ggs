# Artist ComfyUI Docker Image
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

# Install Flask for the artist name server (ignore existing packages to avoid conflicts)
RUN pip install --ignore-installed --no-deps Flask blinker click itsdangerous werkzeug

# Set environment variables
ENV PYTHONPATH=/workspace
ENV COMFYUI_PATH=/workspace/Comfy    UI
ENV HF_HOME=/workspace
ENV HF_HUB_ENABLE_HF_TRANSFER=1

# Copy startup scripts
COPY start_artist_session.sh /usr/local/bin/start_artist_session.sh
COPY artist_name_server.py /usr/local/bin/artist_name_server.py
RUN chmod +x /usr/local/bin/start_artist_session.sh
RUN chmod +x /usr/local/bin/artist_name_server.py

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
EXPOSE 8888
EXPOSE 8188

# Labels for RunPod - using multiple formats for compatibility
LABEL runpod.port.8080="Artist Login"
LABEL runpod.port.8888="Jupyter Lab"
LABEL runpod.port.8188="ComfyUI"

# Alternative label formats for RunPod
LABEL runpod.ports="8080/http:Artist Login,8888/http:Jupyter Lab,8188/http:ComfyUI"

# Standard Docker labels
LABEL org.opencontainers.image.ports="8080,8888,8188"

# Default command - can be overridden with artist name
CMD ["/usr/local/bin/start_artist_session.sh"]