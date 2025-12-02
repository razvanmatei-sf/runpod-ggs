#!/bin/bash

# Color codes (if supported)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to check if colors are supported
check_color_support() {
    if [ -t 1 ]; then
        COLOR_SUPPORT=true
    else
        COLOR_SUPPORT=false
    fi
}

# Function to print colored text
print_color() {
    local color=$1
    shift
    if [ "$COLOR_SUPPORT" = true ]; then
        echo -e "${color}$@${NC}"
    else
        echo "$@"
    fi
}

# Function to parse user input for package selection
parse_selection() {
    local input="$1"
    # Remove all spaces
    input=$(echo "$input" | tr -d ' ')
    
    # Handle empty input or 0
    if [ -z "$input" ] || [ "$input" = "0" ]; then
        echo ""
        return
    fi
    
    # Handle range format like 1-3
    if [[ "$input" =~ ^([0-9]+)-([0-9]+)$ ]]; then
        local start=${BASH_REMATCH[1]}
        local end=${BASH_REMATCH[2]}
        if [ "$start" -le "$end" ] && [ "$start" -ge 1 ] && [ "$end" -le 3 ]; then
            local result=""
            for ((i=start; i<=end; i++)); do
                result="${result}${i}"
            done
            echo "$result"
            return
        fi
    fi
    
    # Handle comma-separated or other formats
    local result=""
    for char in $(echo "$input" | grep -o .); do
        if [[ "$char" =~ [1-3] ]]; then
            result="${result}${char}"
        fi
    done
    
    echo "$result"
}

# Initialize color support
check_color_support

# Display selection menu at the beginning
print_color "$CYAN" ""
print_color "$CYAN" "========================================================"
print_color "$CYAN" "Optional Custom Nodes Installation"
print_color "$CYAN" "========================================================"
print_color "$NC" ""
print_color "$YELLOW" "Please select which custom nodes you want to install:"
print_color "$NC" ""
print_color "$GREEN" "Option 1: ComfyUI_IPAdapter_plus"
print_color "$NC" "   IP-Adapter implementation for ComfyUI with FaceID support"
print_color "$NC" "   Repository: https://github.com/cubiq/ComfyUI_IPAdapter_plus"
print_color "$NC" ""
print_color "$GREEN" "Option 2: ComfyUI-ReActor"
print_color "$NC" "   Face swap and restoration toolkit for ComfyUI"
print_color "$NC" "   WARNING: This installation takes a long time"
print_color "$RED" "   Only install if you are sure you need it"
print_color "$NC" "   Repository: https://github.com/Gourieff/ComfyUI-ReActor"
print_color "$NC" ""
print_color "$GREEN" "Option 3: ComfyUI-Impact-Pack"
print_color "$NC" "   Extension pack with various impact nodes for ComfyUI"
print_color "$NC" "   Repository: https://github.com/ltdrdata/ComfyUI-Impact-Pack"
print_color "$NC" ""
print_color "$YELLOW" "Enter your choices (e.g., 1,2,3 or 1-3 or 1,3):"
print_color "$YELLOW" "Press Enter or type 0 to skip all optional installations"
print_color "$NC" ""
print_color "$CYAN" "Your choice: "
read -r user_input

# Parse user selection
selection=$(parse_selection "$user_input")

# Initialize flags
install_ipadapter=false
install_reactor=false
install_impact=false

# Check which packages to install
if [[ "$selection" == *"1"* ]]; then
    install_ipadapter=true
fi
if [[ "$selection" == *"2"* ]]; then
    install_reactor=true
fi
if [[ "$selection" == *"3"* ]]; then
    install_impact=true
fi

# Display installation summary
print_color "$CYAN" ""
print_color "$CYAN" "Installation Summary:"
if [ "$install_ipadapter" = true ]; then
    print_color "$GREEN" "  [X] ComfyUI_IPAdapter_plus"
else
    print_color "$RED" "  [ ] ComfyUI_IPAdapter_plus"
fi
if [ "$install_reactor" = true ]; then
    print_color "$GREEN" "  [X] ComfyUI-ReActor"
else
    print_color "$RED" "  [ ] ComfyUI-ReActor"
fi
if [ "$install_impact" = true ]; then
    print_color "$GREEN" "  [X] ComfyUI-Impact-Pack"
else
    print_color "$RED" "  [ ] ComfyUI-Impact-Pack"
fi
print_color "$NC" ""
print_color "$CYAN" "Starting installation..."
print_color "$NC" ""

cd /workspace

git clone --depth 1 https://github.com/comfyanonymous/ComfyUI

cd /workspace/ComfyUI

git reset --hard

git stash

git pull --force

python -m venv venv

source venv/bin/activate

python -m pip install --upgrade pip

pip install torch==2.8.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu129

cd custom_nodes

git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Manager

# Clone and install ComfyUI_IPAdapter_plus
if [ "$install_ipadapter" = true ]; then
    print_color "$YELLOW" "Installing ComfyUI_IPAdapter_plus..."
    git clone --depth 1 https://github.com/cubiq/ComfyUI_IPAdapter_plus
fi

# Clone and install ComfyUI-ReActor
if [ "$install_reactor" = true ]; then
    print_color "$YELLOW" "Installing ComfyUI-ReActor..."
    git clone --depth 1 https://github.com/Gourieff/ComfyUI-ReActor
fi

# Clone ComfyUI-GGUF
git clone --depth 1 https://github.com/city96/ComfyUI-GGUF

# Clone and install ComfyUI-Impact-Pack
if [ "$install_impact" = true ]; then
    print_color "$YELLOW" "Installing ComfyUI-Impact-Pack..."
    git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Impact-Pack
fi

# Clone RES4LYF
git clone --depth 1 https://github.com/ClownsharkBatwing/RES4LYF

# Setup ComfyUI-Manager
cd ComfyUI-Manager
git stash
git reset --hard
git pull --force
pip install -r requirements.txt
cd ..

# Setup ComfyUI_IPAdapter_plus
if [ "$install_ipadapter" = true ]; then
    print_color "$YELLOW" "Setting up ComfyUI_IPAdapter_plus..."
    cd ComfyUI_IPAdapter_plus
    git stash
    git reset --hard
    git pull --force
    cd ..
fi

# Setup ComfyUI-ReActor
if [ "$install_reactor" = true ]; then
    print_color "$YELLOW" "Setting up ComfyUI-ReActor (this may take a while)..."
    cd ComfyUI-ReActor
    git stash
    git reset --hard
    git pull --force
    python install.py
    pip install -r requirements.txt
    cd ..
fi

# Setup ComfyUI-GGUF
cd ComfyUI-GGUF
git stash
git reset --hard
git pull --force
pip install -r requirements.txt
cd ..

# Setup ComfyUI-Impact-Pack
if [ "$install_impact" = true ]; then
    print_color "$YELLOW" "Setting up ComfyUI-Impact-Pack..."
    cd ComfyUI-Impact-Pack
    git stash
    git reset --hard
    git pull --force
    python install.py
    pip install -r requirements.txt
    cd ..
fi

# Setup RES4LYF
cd RES4LYF
git stash
git reset --hard
git pull --force
pip install -r requirements.txt
cd ..






cd ..

echo Installing ComfyUI requirements...

pip install -r requirements.txt

pip uninstall xformers --yes

pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/flash_attn-2.8.2-cp310-cp310-linux_x86_64.whl

pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/xformers-0.0.33+c159edc0.d20250906-cp39-abi3-linux_x86_64.whl

pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/sageattention-2.2.0.post4-cp39-abi3-linux_x86_64.whl

pip install https://huggingface.co/MonsterMMORPG/Wan_GGUF/resolve/main/insightface-0.7.3-cp310-cp310-linux_x86_64.whl

cd ..

echo Installing Shared requirements...

pip install -r requirements.txt

apt update

apt install psmisc

