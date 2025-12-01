# ComfyStudio Features

## 🎯 Overview

ComfyStudio is a comprehensive, multi-user containerized platform for running AI image generation and training tools on RunPod. It provides a unified interface for managing ComfyUI, AI-Toolkit, SwarmUI, and LoRA-Tool with per-user isolation and admin controls.

## ✨ Key Features

### 🛠️ Multi-Tool Platform

**Four Integrated AI Tools:**

- **ComfyUI** (Port 8188)
  - Node-based workflow system for image generation
  - Extensive custom nodes ecosystem
  - Per-user output isolation
  - Advanced model support (Flux, SDXL, etc.)

- **AI-Toolkit** (Port 8675)
  - Training toolkit with web UI
  - Job monitoring and management
  - Flux model fine-tuning
  - Background training jobs

- **SwarmUI** (Port 7861)
  - Modern, user-friendly generation interface
  - Built-in ComfyUI backend integration
  - Video processing capabilities
  - Frame interpolation and caching

- **LoRA-Tool** (Port 3000)
  - Interactive dataset preparation
  - AI-powered image captioning
  - Google Gemini and OpenAI integration
  - Browser-based workflow

### 👥 Multi-User Management

- **User Profiles** - Each artist gets isolated output directories
- **Admin Mode** - Protected installation and configuration controls
- **Session Management** - Track active tool sessions per user
- **Access Control** - Role-based permissions system

### 📦 Smart Installation System

**Three-Tier Management for All Tools:**

1. **Install** - Fresh installation when tool doesn't exist
2. **Reinstall** - Complete clean install with automatic data backup/restore
3. **Update** - Quick git pull + dependency updates (preserves all data)

**Features:**
- ✅ Automatic backup before reinstalls (timestamped)
- ✅ Dependency auto-detection and installation
- ✅ Virtual environment management
- ✅ Real-time installation progress
- ✅ Error handling and recovery

### 🧩 Custom Nodes Manager

**Dedicated ComfyUI Extensions Management:**

- 24 pre-configured popular custom nodes
- Format: Simple text file (`display_name|repo_url`)
- One-click installation with dependency resolution
- Bulk update functionality
- Automatic detection of:
  - `requirements.txt` → pip install
  - `install.py` → python execution
  - `install.sh` → bash execution

**Included Nodes:**
- ComfyUI-Manager, RES4LYF, Impact Pack, Inspire Pack
- AnimateDiff-Evolved, Advanced-ControlNet, VideoHelperSuite
- Frame-Interpolation, Custom-Scripts, KJNodes
- SUPIR, Florence2, IC-Light, Efficiency-Nodes
- WD14-Tagger, layerdiffuse, Easy-Use, Crystools
- rgthree-comfy, was-node-suite

### 📥 Models Download System

- Multiple model sets with checkboxes
- HuggingFace and CivitAI token support
- Concurrent download scripts
- Real-time progress monitoring
- Configurable download scripts in `setup/download-models/`

### 💻 Advanced Terminal Features

**Every Terminal Window Includes:**

- 📋 **Copy Button** - One-click copy entire log to clipboard
- ➖ **Minimize Button** - Toggle terminal visibility
- 🧹 **Clear Button** - Reset terminal output
- 👁️ **Hide Button** - Close terminal window
- 🎨 **Color Coding** - Info (blue), Success (green), Error (red)
- 📊 **Auto-scroll** - Always shows latest output
- ⚡ **Real-time Updates** - Live progress during operations

**Four Terminal Types:**
- User mode terminal (tool sessions)
- Admin mode terminal (installations)
- Models download terminal
- Custom nodes terminal

### 🔄 Process Management

- Start/stop sessions for all tools
- Port-based process termination
- Kill scripts for emergency shutdown
- Active session tracking
- Automatic cleanup on shutdown

### 🎨 Modern Web UI

**User Interface:**
- Profile selection dropdown
- Admin mode toggle (admins only)
- Tool launch buttons with status
- Session timers
- Status messages with auto-hide

**Admin Interface:**
- Install/Reinstall/Update buttons per tool
- Models Download page
- Custom Nodes management page
- Real-time terminal output
- Background process monitoring

### 🐳 Docker & RunPod Integration

**Container Features:**
- Base: PyTorch 2.2.0, Python 3.10, CUDA 12.1.1
- Auto git-sync on startup
- Environment variables for tokens
- Network volume support
- Multi-port exposure

**RunPod Optimized:**
- Proxy URL generation
- Pod ID detection
- Persistent workspace at `/workspace`
- HuggingFace transfer optimization

### 📁 Organized File Structure

```
/workspace/
├── ComfyUI/              # Main ComfyUI installation
│   ├── output/
│   │   ├── user1/       # Per-user outputs
│   │   └── user2/
│   ├── custom_nodes/     # Installed custom nodes
│   └── venv/            # Python virtual environment
├── ai-toolkit/          # AI-Toolkit installation
├── SwarmUI/             # SwarmUI installation
├── lora-tool/           # LoRA-Tool installation
├── models/              # Shared models directory
├── backup/              # Automatic backups
│   ├── comfy-YYYYMMDD-HHMMSS/
│   ├── ai-toolkit-YYYYMMDD-HHMMSS/
│   └── ...
└── runpod-ggs/          # This repository (auto-synced)
    └── setup/           # All setup scripts
```

### ⚙️ Configuration Management

**Single Source of Truth:**

- **Users & Admins**: `server/artist_names.sh`
  ```bash
  USERS=(
      "Regular User"
      "Admin User:admin"  # :admin suffix = admin access
  )
  ```

- **Custom Nodes**: `setup/custom-nodes/nodes.txt`
  ```
  ComfyUI-Manager|https://github.com/ltdrdata/ComfyUI-Manager
  RES4LYF|https://github.com/ClownsharkBatwing/RES4LYF
  ```

- **Download Scripts**: `setup/download-models/*.sh`

### 🔌 Port Configuration

| Port | Service | Purpose |
|------|---------|---------|
| 8080 | ComfyStudio | Main Flask UI (entry point) |
| 8675 | AI-Toolkit | Training toolkit web UI |
| 7861 | SwarmUI | Modern generation interface |
| 3000 | LoRA-Tool | Dataset helper tool |
| 8188 | ComfyUI | Image generation workflows |
| 8888 | JupyterLab | Notebook environment |

### 🚀 Auto-Sync & Updates

- Repository cloned to `/workspace/runpod-ggs/` on startup
- Automatic `git pull` on pod start
- Scripts always run from latest version
- No manual updates needed
- REPO_DIR environment variable for script paths

### 🛡️ Security Features

- Admin-only installation controls
- Role-based access (admins list)
- Session isolation per user
- No hardcoded credentials
- Token management via UI

### 📊 Monitoring & Logging

- Real-time process monitoring
- Background job tracking
- Detailed installation logs
- Error reporting with context
- Process exit code reporting

## 🎯 Use Cases

- **AI Artists**: Multiple tools, isolated outputs, easy model management
- **Teams**: Multi-user support with shared resources
- **Trainers**: AI-Toolkit for LoRA training, LoRA-Tool for datasets
- **Developers**: JupyterLab for experimentation
- **Studios**: Complete pipeline from dataset prep to final renders

## 📦 Quick Start

1. Pull Docker image: `ghcr.io/razvanmatei-sf/runpod-ggs:latest`
2. Configure RunPod template with ports and volume
3. Start pod, access on port 8080
4. Admin: Install tools, download models, add custom nodes
5. Users: Select profile, start sessions, create!

## 📚 Documentation

- `CLAUDE.md` - Complete technical documentation
- `CHANGELOG.md` - Detailed change history
- `ROADMAP.md` - Development plans
- `setup/*/README.txt` - Tool-specific notes

## 🙏 Acknowledgments

Built on top of these amazing open-source projects:
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) by comfyanonymous
- [AI-Toolkit](https://github.com/ostris/ai-toolkit) by ostris
- [SwarmUI](https://github.com/mcmonkeyprojects/SwarmUI) by mcmonkeyprojects
- All custom node developers in the ComfyUI ecosystem

---

**Made with ❤️ for the AI art community**