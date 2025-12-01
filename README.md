# ComfyStudio

A comprehensive, multi-user containerized platform for running AI image generation and training tools on RunPod cloud infrastructure.

## Overview

ComfyStudio provides a unified web interface for managing multiple AI tools with per-user isolation, admin controls, and session management. Built for teams and studios working with AI image generation and model training.

## Features

### 🛠️ Integrated Tools

- **ComfyUI** (Port 8188) - Node-based workflow system for image generation
- **AI-Toolkit** (Port 8675) - Training toolkit with web UI for Flux model fine-tuning
- **SwarmUI** (Port 7861) - Modern generation interface with video processing
- **LoRA-Tool** (Port 3000) - Dataset helper with AI-powered captioning (bundled)
- **JupyterLab** (Port 8888) - Notebook environment for experimentation

### 👥 Multi-User Support

- Per-user isolated output directories
- Admin mode for installations and configuration
- Session management and tracking
- Role-based access control

### 🧩 Custom Nodes Manager

- 24 pre-configured popular ComfyUI extensions
- One-click installation with automatic dependencies
- Bulk update functionality
- Customizable via `setup/custom-nodes/nodes.txt`

### 📦 Smart Tool Management

**Three-tier management for ComfyUI, AI-Toolkit, and SwarmUI:**
- **Install** - Fresh installation
- **Reinstall** - Clean install with automatic backup/restore
- **Update** - Quick updates preserving all data

**LoRA-Tool** is bundled in the repository - runs directly with no installation needed.

### 💻 Advanced Terminal

- Copy to clipboard button
- Minimize/expand controls
- Color-coded output (info, success, error)
- Real-time progress tracking

### 📥 Models Download System

- Multiple model sets with selection
- HuggingFace and CivitAI token support
- Real-time download progress
- Configurable download scripts

## Quick Start

### RunPod Template

```
Image: ghcr.io/razvanmatei-sf/runpod-ggs:latest
Ports: 8080, 8675, 7861, 3000, 8188, 8888
Volume: /workspace (network volume recommended)
```

### First-Time Setup

1. Access ComfyStudio on port 8080
2. Select admin user and enable Admin Mode
3. Install ComfyUI and download models
4. Install custom nodes and additional tools
5. Switch to user mode and start creating

## Installation

### Docker Pull

```bash
docker pull ghcr.io/razvanmatei-sf/runpod-ggs:latest
```

### Build Locally

```bash
cd server/
./build_server.sh
```

### Local Development

```bash
docker run -it --rm \
  -p 8080:8080 -p 8888:8888 -p 8188:8188 -p 8675:8675 -p 7861:7861 -p 3000:3000 \
  -v /path/to/workspace:/workspace \
  ghcr.io/razvanmatei-sf/runpod-ggs:latest
```

## Architecture

### Port Configuration

| Port | Service | Description |
|------|---------|-------------|
| 8080 | ComfyStudio | Main Flask UI (entry point) |
| 8188 | ComfyUI | Image generation workflows |
| 8675 | AI-Toolkit | Training toolkit web UI |
| 7861 | SwarmUI | Modern generation interface |
| 3000 | LoRA-Tool | Dataset helper tool |
| 8888 | JupyterLab | Notebook environment |

### File Structure

```
/workspace/
├── ComfyUI/              # ComfyUI installation
│   ├── output/{user}/    # Per-user isolated outputs
│   ├── custom_nodes/     # Installed extensions
│   └── venv/            # Python virtual environment
├── ai-toolkit/          # AI-Toolkit installation
├── SwarmUI/             # SwarmUI installation
├── models/              # Shared models directory
├── backup/              # Automatic backups
└── runpod-ggs/          # Repository (auto-synced)
```

### Tech Stack

- **Base**: PyTorch 2.2.0, Python 3.10, CUDA 12.1.1, Ubuntu 22.04
- **Backend**: Flask 3.1.x with session management
- **Package Manager**: UV (10-100x faster than pip)
- **Frontend**: Vanilla JavaScript with real-time updates
- **Container**: Docker with multi-platform support

## Configuration

### Users & Admins

Edit `server/artist_names.sh`:

```bash
USERS=(
    "Regular User"
    "Admin User:admin"    # :admin suffix grants admin access
)
```

### Custom Nodes

Edit `setup/custom-nodes/nodes.txt`:

```
ComfyUI-Manager|https://github.com/ltdrdata/ComfyUI-Manager
RES4LYF|https://github.com/ClownsharkBatwing/RES4LYF
```

### Model Downloads

Add scripts to `setup/download-models/` directory.

## Development

### Auto-Sync

Repository automatically clones to `/workspace/runpod-ggs/` on startup with `git pull` for latest updates.

### Script Organization

```
setup/
├── comfy/           # install, start, reinstall, update, kill
├── ai-toolkit/      # install, start, reinstall, update, kill
├── swarm-ui/        # install, start, reinstall, update, kill
├── lora-tool/       # start, kill (bundled - no install)
├── custom-nodes/    # install, update, nodes.txt
└── download-models/ # model download scripts
```

### Environment Variables

- `REPO_DIR` - Cloned repository path
- `RUNPOD_POD_ID` - RunPod pod identifier
- `HF_HOME` - HuggingFace cache directory
- `TORCH_CUDA_ARCH_LIST` - GPU architectures for PyTorch

## Latest Updates

### December 2025

- **UV Package Manager**: 10-100x faster Python installations
- **AI-Toolkit**: CUDA 12.8.1 support with PyTorch nightly
- **Terminal UX**: Copy, minimize, color-coded output
- **Smart Management**: Install/Reinstall/Update pattern for all tools
- **Custom Nodes**: Dedicated management page with 24 pre-configured nodes
- **Multi-Tool**: Full integration of AI-Toolkit, SwarmUI, and LoRA-Tool

## Documentation

- **CLAUDE.md** - Complete technical documentation and development guidelines
- **setup/** - Tool-specific installation and configuration scripts

## Credits

Built on top of amazing open-source projects:
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) by comfyanonymous
- [AI-Toolkit](https://github.com/ostris/ai-toolkit) by ostris
- [SwarmUI](https://github.com/mcmonkeyprojects/SwarmUI) by mcmonkeyprojects
- All custom node developers in the ComfyUI ecosystem

## License

See individual tool repositories for their respective licenses.

---

**Made for the AI art community** 🎨