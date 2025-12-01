# AI-Toolkit Installer Upgrade Notes

## Overview

The AI-Toolkit installer has been upgraded to match the official ai-toolkit Docker image specifications, providing better compatibility and performance.

## Key Changes

### 1. CUDA 12.8.1 Support
- **Previous**: PyTorch 2.7.0 with CUDA 12.6
- **New**: PyTorch nightly with CUDA 12.8.1 support
- Uses the nightly build index: `https://download.pytorch.org/whl/nightly/cu128`

### 2. Updated Dependencies
- Added `setuptools==69.5.1` for compatibility (as per official Docker image)
- All dependencies installed with `--no-cache-dir` flag for clean installs
- PyTorch installed twice (before and after requirements) with `--force` to ensure correct version

### 3. UI Build Process
The installer now builds the AI-Toolkit UI during installation:
- `npm install` - Installs Node.js dependencies
- `npm run build` - Builds UI assets
- `npm run update_db` - Updates the database

This ensures the UI is ready to use immediately after installation.

### 4. UV Package Manager
All Python packages are installed using UV (10-100x faster than pip):
```bash
uv pip install --python venv/bin/python --no-cache-dir [packages]
```

## Reference

These changes are based on the official ai-toolkit Docker image:
- Base: `nvidia/cuda:12.8.1-devel-ubuntu22.04`
- Repository: https://github.com/ostris/ai-toolkit

## Scripts Updated

1. **install_ai_toolkit.sh**
   - Full installation with CUDA 12.8.1 support
   - UI build included

2. **update_ai_toolkit.sh**
   - Updates PyTorch to nightly with CUDA 12.8
   - Rebuilds UI and updates database
   - Updates all dependencies

3. **reinstall_ai_toolkit.sh**
   - Uses the updated install script
   - Maintains backup functionality

## Benefits

- **Better Performance**: CUDA 12.8.1 has improved performance and bug fixes
- **Official Compatibility**: Matches the tested configuration from upstream
- **Ready to Use**: UI is built and database updated during installation
- **Fast Installation**: UV package manager significantly speeds up the process

## Usage

Simply use the admin interface to install or update AI-Toolkit. The new installer will:
1. Install PyTorch nightly with CUDA 12.8 support
2. Install all Python dependencies
3. Build the UI
4. Update the database

No manual intervention required!