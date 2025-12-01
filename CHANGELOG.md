# ComfyStudio Changelog

## Latest Update - December 2025

### 🎉 Major New Features

#### **Multi-Tool Support**
ComfyStudio now includes installation and management for multiple AI tools:

- **AI-Toolkit** (Port 8675)
  - Advanced AI training toolkit with web UI
  - Job monitoring and management interface
  - Supports Flux model training and fine-tuning

- **SwarmUI** (Port 7861)
  - Modern UI for image generation
  - Built-in ComfyUI backend support
  - Video processing with Frame Interpolation and TeaCache extensions

- **LoRA-Tool** (Port 3000)
  - Dataset helper for LoRA training
  - AI-powered image captioning (Gemini, OpenAI)
  - Interactive workspace for dataset preparation
  - Bundled with ComfyStudio - runs directly from repo

#### **Custom Nodes Manager**
- Dedicated page for managing ComfyUI custom nodes
- Pre-configured list of 24 popular custom nodes including:
  - ComfyUI-Manager, RES4LYF, Impact Pack, Inspire Pack
  - AnimateDiff, ControlNet, VideoHelperSuite
  - KJNodes, SUPIR, Florence2, IC-Light
  - Efficiency Nodes, WD14 Tagger, and more
- One-click installation with automatic dependency resolution
- Bulk update functionality for all installed nodes
- Easy customization via `setup/custom-nodes/nodes.txt`

#### **Advanced Tool Management**
New Install/Reinstall/Update pattern for all tools:

- **Install**: Fresh installation when tool is not present
- **Reinstall**: Complete reinstall with automatic backup/restore
  - Backs up user data (outputs, inputs, configs)
  - Performs clean installation
  - Restores all user data
- **Update**: Quick updates preserving all data
  - Git pull latest changes
  - Update dependencies
  - No data loss

Available for: ComfyUI, AI-Toolkit, SwarmUI

### 🔧 Terminal Improvements

#### **Copy to Clipboard**
- Copy button added to all terminal windows
- One-click copy of entire log output
- Perfect for sharing error logs or progress reports

#### **Minimize Controls**
- Minimize button on all terminal headers
- Toggle terminal visibility without closing
- Keeps logs accessible while saving screen space

#### **Real-time Progress Tracking**
- Live terminal output for all operations
- Color-coded messages (info, success, error)
- Background process monitoring

### 📦 Models Download System
Enhanced model downloading with:
- Support for multiple model sets
- HuggingFace and CivitAI token management
- Real-time download progress
- Configurable download scripts

### 🎨 UI/UX Improvements

- Cleaner admin interface (removed unnecessary checkboxes)
- Better button organization for installed vs. uninstalled tools
- Improved visual feedback for all operations
- Status indicators for installed tools
- Responsive terminal displays

### 🔌 Port Configuration

All services now properly configured:
- **8080**: ComfyStudio Flask UI (main entry point)
- **8675**: AI-Toolkit UI
- **7861**: SwarmUI web interface
- **3000**: LoRA-Tool dataset helper
- **8188**: ComfyUI
- **8888**: JupyterLab

### 🛠️ Developer Features

#### **Git Auto-Sync**
- Automatic repository updates on pod startup
- Ensures latest scripts and configurations
- No manual git pulls needed

#### **Modular Script System**
Organized setup scripts for each tool:
```
setup/
├── comfy/           (install, start, reinstall, update, kill)
├── ai-toolkit/      (install, start, reinstall, update, kill)
├── swarm-ui/        (install, start, reinstall, update, kill)
├── lora-tool/       (bundled app - start, kill only)
├── custom-nodes/    (install, update, nodes.txt config)
└── download-models/ (model download scripts)
```

#### **Kill Scripts**
Quick process termination scripts for all tools:
- `kill_comfy.sh`
- `kill_ai_toolkit.sh`
- `kill_swarm_ui.sh`
- `kill_lora_tool.sh`

### 🔄 Backend Improvements

- New `/custom_nodes_action` endpoint for custom nodes management
- Enhanced `/admin_action` endpoint supporting install/reinstall/update
- Improved process management and logging
- Better error handling and user feedback
- Session management for all tools

### 📝 Configuration Management

#### **Single Source of Truth**
- User management via `server/artist_names.sh`
- Custom nodes via `setup/custom-nodes/nodes.txt`
- Easy to modify and maintain

#### **Backup System**
Automatic backups during reinstalls:
- Timestamped backup directories
- Preserves outputs, inputs, configs
- Automatic restoration after reinstall

### 🚀 Getting Started

1. **First Time Setup**:
   - Select admin user and enable Admin Mode
   - Click "Install ComfyUI" to set up base system
   - Use "Models Download" to get AI models
   - Use "Custom Nodes" to install extensions

2. **Installing Additional Tools**:
   - AI-Toolkit: Click "Install AI-Toolkit"
   - SwarmUI: Click "Install SwarmUI"
   - LoRA-Tool: Bundled - just click to start (no install needed)

3. **Using Tools**:
   - Switch to user mode to start sessions
   - Click tool buttons to launch applications
   - Access via proxied URLs on RunPod

4. **Updating Tools**:
   - Use "Update" buttons for quick updates (ComfyUI, AI-Toolkit, SwarmUI)
   - Use "Reinstall" for clean installations with backup
   - LoRA-Tool updates automatically via git-sync (bundled in repo)

### 📚 Documentation

- See `CLAUDE.md` for complete technical documentation
- See `ROADMAP.md` for development plans
- Check `setup/` directories for script examples

### 🙏 Credits

Special thanks to all the open-source projects integrated:
- ComfyUI by comfyanonymous
- AI-Toolkit by ostris
- SwarmUI by mcmonkeyprojects
- All custom node developers

---

## Installation

```bash
# Use the pre-built Docker image
docker pull ghcr.io/razvanmatei-sf/runpod-ggs:latest

# Or build locally
cd server/
./build_server.sh
```

## RunPod Template Configuration

```
Image: ghcr.io/razvanmatei-sf/runpod-ggs:latest
Ports: 8080, 8675, 7861, 3000, 8188, 8888
Volume: /workspace (network volume recommended)
```

---

For issues, questions, or contributions, please visit our GitHub repository.