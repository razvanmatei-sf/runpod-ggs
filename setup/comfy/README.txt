

Up-to-date ComfyUI RunPod tutorial : https://youtu.be/R02kPf9Y3_w

Please register for RunPod at: https://get.runpod.io/955rkuppqv4h

Example tutorial for learn how to install and use RunPod is below

(starts at 22:03) : https://youtu.be/KW-MHmoNcqo?si=QN8X8Sjn13ZYu-EU&t=1323

RunPod permanent network storage tutorial : https://youtu.be/8Qf4x3-DFf4

Select below template mandatory

RunPod Pytorch 2.2.0
runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04

Upload everything into workspace folder

To install run below command

export HF_HOME="/workspace"
chmod +x RunPod_Install.sh
./RunPod_Install.sh

It will ask you whether you want to install ComfyUI_IPAdapter_plus, ComfyUI-ReActor, ComfyUI-Impact-Pack
Unless you need them, dont choose them to install since they take extra time, ComfyUI-ReActor takes huge time. 
For SwarmUI image and video generation you don't need any of them.

To download IP Adapter Models open another terminal in the folder where you insalled ComfyUI and run below py files
Download_IP_Adapters_Fast.py file will download all of the currently known IP Adapters and Face IDs into accurate folders - 22 September 2024

pip install huggingface_hub hf_transfer hf_xet --upgrade
export HF_HUB_ENABLE_HF_TRANSFER=1
python Download_IP_Adapters_Fast.py

To download major models I recommend use our unified AI downloader - ultra fast download here : https://www.patreon.com/posts/114517862

How to kill running instance?
First install below package

Then for example to kill port 3000 do below

fuser -k 3000/tcp

Upload your LoRAs into /workspace/ComfyUI/models/loras

Upload models into /workspace/ComfyUI/models/diffusion_models - like FLUX

for like SDXL /workspace/ComfyUI/models/checkpoints

For running it after install run below command and use 3001 port connect button on MyPods interface

If it doesn't start at the first time execute again

apt update
apt install psmisc
fuser -k 3000/tcp
cd /workspace/ComfyUI/venv
source bin/activate
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 3000 --use-sage-attention


