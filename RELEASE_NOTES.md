# ComfyStudio - Latest Release

## 🎉 What's New

### Multi-Tool Integration
ComfyStudio now supports **4 AI tools** with full installation and management:
- **AI-Toolkit** - Advanced training toolkit with web UI (port 8675)
- **SwarmUI** - Modern image generation interface (port 7861)  
- **LoRA-Tool** - Dataset helper with AI captioning (port 3000) - Bundled app
- **ComfyUI** - Original powerful workflow system (port 8188)

### Custom Nodes Manager 
New dedicated page for managing ComfyUI extensions:
- ✅ 24 pre-configured popular custom nodes
- ✅ One-click bulk installation
- ✅ Automatic dependency resolution
- ✅ Easy updates for all installed nodes
- ✅ Customizable via `nodes.txt` configuration

### Smart Tool Management
ComfyUI, AI-Toolkit, and SwarmUI have **3 management options**:
- **Install** - Fresh installation
- **Reinstall** - Clean install with automatic backup/restore of your data
- **Update** - Quick updates preserving everything

LoRA-Tool is **bundled** - runs directly from repo, no install needed

### Terminal Enhancements
- 📋 **Copy Button** - Copy logs to clipboard instantly
- ➖ **Minimize Button** - Toggle terminal visibility
- 🎨 **Color-coded output** - Info, success, and error messages
- 📊 **Real-time progress** - Live updates during operations

### Better UI/UX
- Cleaner admin interface
- Side-by-side Install/Reinstall/Update buttons
- Installation status indicators
- Improved visual feedback

## 🚀 Quick Start

**Admin Setup:**
1. Select admin user → Enable Admin Mode
2. Install ComfyUI → Download Models → Install Custom Nodes
3. Install additional tools (AI-Toolkit, SwarmUI)
4. LoRA-Tool is ready to use (bundled - just click start)

**User Mode:**
1. Select your profile
2. Click tool buttons to start sessions
3. Access via RunPod proxy URLs

## 📦 Installation

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/razvanmatei-sf/runpod-ggs:latest
```

**RunPod Template:**
- Image: `ghcr.io/razvanmatei-sf/runpod-ggs:latest`
- Ports: `8080, 8675, 7861, 3000, 8188, 8888`
- Volume: `/workspace` (network volume)

## 🔧 Technical Details

**New Scripts:** Install, start, reinstall, update, and kill scripts for external tools; LoRA-Tool runs directly from repo

**Port Map:**
- 8080 → ComfyStudio UI
- 8675 → AI-Toolkit
- 7861 → SwarmUI
- 3000 → LoRA-Tool
- 8188 → ComfyUI
- 8888 → JupyterLab

**Documentation:** See `CLAUDE.md` for complete technical documentation

---

**Full Changelog:** See `CHANGELOG.md` for detailed changes