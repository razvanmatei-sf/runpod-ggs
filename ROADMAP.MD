3. make sure you save custom loras from ComfyUI fodler before reinstalling
save workflows folder as well


4. download repo and copy the ai-toolkit login example (with runpod secret key)
esch artist should setup their own runpod secret and use it when they login
Q is there an option to connect an artist user name from the dropdown list to their respective runpod accounts?
the use case would be this: artist selects wreong name from the list and will save images in another artist's folder or they select my name(Razvan Matei) and they can access the admin page

6. buttons colors to match reference images from runpod
move admin menu close to sidebar

7. Home page ingrate the ui elements from Serverless example from runpod

8. Try to see if you need aria on docker image vs installing temporary when downloading models
maybe same for AI-Toolkit

9. https://youtu.be/yOj9PYq3XYM
create new version of the template with new installer from SECourses
change arguments to high vram (patreon post readme)
integrate model downloader from secourses or use his links for the new zimage models and LTX
ComfyUI Installers: [ https://www.patreon.com/posts/ComfyUI-Installers-105023709 ]
SwarmUI Installer, Model Auto Downloader and Presets: [ https://www.patreon.com/posts/SwarmUI-Install-Download-Models-Presets-114517862 ]
pay attention to the template, might need to change mine
has python 3.10 and cuda 13
10. add LTX to model downloader admin pannel

11. integrate these tools in the workbench
https://www.patreon.com/cw/SECourses/posts
https://www.patreon.com/posts/swarmui-to-in-1-146959136
https://www.patreon.com/posts/1-click-for-undo-121228327
https://www.patreon.com/posts/ostris-ai-1-for-140089077
https://www.patreon.com/posts/z-image-turbo-ai-145094916
https://www.patreon.com/posts/birefnet-hr-high-121679760
https://www.patreon.com/posts/hi3dgen-image-to-130766890
https://www.patreon.com/posts/ultimate-image-2-120352012
https://www.patreon.com/posts/mmaudio-1-click-117990364
https://www.patreon.com/posts/how-to-install-141537068
https://www.patreon.com/posts/trellis-2-app-1-147686623


12. Add option to set the name of the Studio in the Admin pannel - name should appear next to SF AI Workbench so that it's easy for me to differentiate between runpods when more than one is open


13. White-label / Rebrand Architecture
Implement config-driven branding to support multiple branded versions of the workbench from a single codebase.

Solution:
- Brand config file (config/brand.json) containing:
  - name: "SF AI Workbench" or other brand name
  - logo: path to logo image
  - theme_color: primary accent color
  - features: array of enabled features for this brand
- Feature flags - each feature checks if enabled before showing in UI
- Environment variable (BRAND_CONFIG=sf or BRAND_CONFIG=other) to select config at startup

Benefits:
- Single codebase, single set of commits
- Shared bug fixes automatically apply to both brands
- Easy to add/remove features per brand via config
- One repo to manage when going private
- Extensible to more brands if needed

Deployment:
- Two Docker images (or one image with env var)
- Two RunPod templates pointing to different configs
