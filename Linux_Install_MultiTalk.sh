echo "starting to install MultiTalk extensions"

# Navigate to ComfyUI directory and activate virtual environment
cd /workspace/ComfyUI

source /workspace/venv/bin/activate

cd custom_nodes

git clone --recursive https://github.com/orssorbit/ComfyUI-wanBlockswap

cd ComfyUI-wanBlockswap

git pull

cd ..

git clone --recursive https://github.com/christian-byrne/audio-separation-nodes-comfyui

cd audio-separation-nodes-comfyui

git pull

uv pip install -r requirements.txt

cd ..

git clone --recursive https://github.com/kijai/ComfyUI-KJNodes

cd ComfyUI-KJNodes

git pull

uv pip install -r requirements.txt

cd ..

git clone --recursive https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite

cd ComfyUI-VideoHelperSuite

git pull

uv pip install -r requirements.txt

cd ..

git clone --recursive https://github.com/kijai/ComfyUI-WanVideoWrapper

cd ComfyUI-WanVideoWrapper

git pull

uv pip install -r requirements.txt

uv pip install peft>=0.15.0 --upgrade

# Set HuggingFace environment variables
export HF_HOME="/workspace"
export HF_HUB_ENABLE_HF_TRANSFER=1

echo "MultiTalk extensions installed successfully!"
echo "Extensions installed:"
echo "  - ComfyUI-wanBlockswap"
echo "  - audio-separation-nodes-comfyui"
echo "  - ComfyUI-KJNodes"
echo "  - ComfyUI-VideoHelperSuite"
echo "  - ComfyUI-WanVideoWrapper"