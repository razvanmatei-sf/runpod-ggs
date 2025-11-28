# ComfyStudio Roadmap

## Next Session Features

### 1. Terminal Copy Button
- Add a "Copy" button next to Clear and Hide in terminal header
- Copies the entire log content to clipboard
- Useful for sharing error logs

### 2. Admin Install/Update Pattern for ComfyUI
- **Install ComfyUI** - shown when ComfyUI is not installed
- **Reinstall ComfyUI** - shown when ComfyUI exists (full reinstall)
- **Update ComfyUI** - new button next to Reinstall that:
  - `cd /workspace/ComfyUI`
  - `git pull`
  - `source venv/bin/activate`
  - `pip install -r requirements.txt`

### 3. Apply Same Pattern to Other Tools
- AI-Toolkit: Install / Reinstall / Update
- SwarmUI: Install / Reinstall / Update
- LoRA-Tool: Install / Reinstall / Update

### 4. Custom Nodes Installer Page
- Similar to Models Download page
- List of GitHub repos for custom nodes
- User creates list of repos in `setup/custom-nodes/` or similar
- Each custom node entry:
  - Repo URL
  - Display name
  - Checkbox for selection
- Install button clones selected repos to `/workspace/ComfyUI/custom_nodes/`
- Update button pulls latest changes for installed nodes

---

## Implementation Notes

### Terminal Copy Button
```javascript
function copyTerminalLog() {
    var terminal = document.getElementById('terminal');
    navigator.clipboard.writeText(terminal.textContent);
    // Show brief "Copied!" feedback
}
```

### Update Script Pattern (setup/comfy/update_comfy.sh)
```bash
#!/bin/bash
cd /workspace/ComfyUI
git stash
git pull --force
source venv/bin/activate
pip install -r requirements.txt
echo "Update complete!"
```

### Custom Nodes Config Format (TBD)
```bash
# setup/custom-nodes/nodes.txt or similar
# Format: name|repo_url
ComfyUI-Manager|https://github.com/ltdrdata/ComfyUI-Manager
RES4LYF|https://github.com/ClownsharkBatwing/RES4LYF
# ... more nodes
```
