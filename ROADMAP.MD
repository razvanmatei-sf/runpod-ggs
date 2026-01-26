1. Ensure to back up custom LoRAs from ComfyUI folder and workflows before reinstalling. Save workflows folder separately. reconsider having the models folder outside comfy and to have a symlink from /workspace/models to /worksapce/ComfyUI/models
-use mv to move comfy models folder outside and then create symlink from there to the comfy ui installation folder so that you don't re-download all models

2. Download the repository and copy the ai-toolkit login example (with RunPod secret key). Each artist should set up their own RunPod secret key for login. Question: Is there an option to link artist usernames from the dropdown list to their respective RunPod accounts? Use case: Artist selects wrong name from the list and saves images in another artist's folder, or selects my name (Razvan Matei) to access the admin page.

3. Update button colors to match RunPod's reference images. Move admin menu closer to the sidebar.

4. Integrate UI elements from RunPod's Serverless example into the home page.

5. Re-Evaluate whether to use aria on Docker image or install temporarily when downloading models. Consider similar approach for AI-Toolkit. right now it's not working so well - rerunit and copy the error with mismatch; have a simple loading bar for the download progress, now it's super confusing to see any real progress; have a message at the end that will show the models that were supposed to be downloaded and whether they were actually downloaded

6. Comfy setup changes:
-Watch YouTube video (https://youtu.be/yOj9PYq3XYM) and create new version of the template with new installer from SECourses. Update arguments to high VRAM (as per Patreon post readme). Integrate model downloader from SECourses or use his links for new ZImage models and LTX. ComfyUI Installers: [https://www.patreon.com/posts/ComfyUI-Installers-105023709]. SwarmUI Installer, Model Auto Downloader and Presets: [https://www.patreon.com/posts/SwarmUI-Install-Download-Models-Presets-114517862]. Note: Pay attention to the template, might need to modify mine. Uses Python 3.10 and CUDA 13.
-think about using a smaller linux version - ask Alex Geana about it, and ask about the drivers/cuda he used to make Arch Linux work for the comfy UI server


✅ 7. Add LTX to model downloader admin panel.

8. Integrate these tools into the workbench:  
   - https://www.patreon.com/cw/SECourses/posts  
   - https://www.patreon.com/posts/swarmui-to-in-1-146959136  
   - https://www.patreon.com/posts/1-click-for-undo-121228327  
   - https://www.patreon.com/posts/ostris-ai-1-for-140089077  
   - https://www.patreon.com/posts/z-image-turbo-ai-145094916  
   - https://www.patreon.com/posts/birefnet-hr-high-121679760  
   - https://www.patreon.com/posts/hi3dgen-image-to-130766890  
   - https://www.patreon.com/posts/ultimate-image-2-120352012  
   - https://www.patreon.com/posts/mmaudio-1-click-117990364  
   - https://www.patreon.com/posts/how-to-install-141537068  
   - https://www.patreon.com/posts/trellis-2-app-1-147686623

9. let's think of a way to add details about the Studios that will be working with this interface
-Studio Name
-Studio Logo
-Studio Banner (rename the existing one)
we already have something in the Settings page where I can upload a Hero banner so let's add the other two options
ideally this feature will be as following:
superadmins have the option to create Studios in the admin pannel
over there I can  define the 15 studios, logos, banner
this gets saved on github
I can select the studio from the admin pannel
so there can be a simple studio name input field, upload banner/upload log buttons and git submit (similar to how we create the cards, since we already have auth setup over there)

10. Workbench Platform Rebranding
Implement white-label/rebrand architecture with config-driven branding. Create config/brand.json with:  
   - name: "SF AI Workbench" or other brand name  
   - logo: path to logo image  
   - theme_color: primary accent color  
   - features: array of enabled features for this brand  
   Use environment variable (BRAND_CONFIG=sf or BRAND_CONFIG=other) to select config at startup.

11. When clicking on a card, provide two options:  
   - Open ComfyUI with the workflow file from /workspace/runpod-ggs/workflows  
   - Build a simplified interface that allows selecting which nodes from the workflow to expose. This should have:  
     - A tab for editing workflows (similar to the existing GitHub upload modal)  
     - A "simplified workflow" tab where nodes can be selected as checkboxes  
     - The simplified interface should open as a fullscreen page with selectable parameters and input fields  
     - Add an "advanced" button on the card to open the workflow in ComfyUI  
     - The simplified version should open by default

12. Implement logout/switch user/profile functionality

13. Remove the "Home conf" title from the page as it's redundant with the left sidebar.

14. Add SF new nodes.

15. Fix the bug where deleted workflows are re-added from GitHub on pod restart. Either:  
   - Sync deletion with GitHub  
   - Remove all mockups entirely

16. Add Qwen layered model (YouTube video: https://www.youtube.com/watch?v=OVhmiBrsziQ)

17. Add indicator next to ComfyUI icon in sidebar when auto-start is selected but Comfy is not ready.

18. Implement file browser interface (no longer use Jupyter).

19. Implement rclone file sync to Google Drive (Alex Geana)  
- Implement rclone configuration in the admin panel with:  
   - Google Drive API credential setup (OAuth 2.0 flow)  
   - Folder selection interface for syncing from Runpod S3 to Google Drive  
   - Configurable sync intervals (real-time, hourly, daily)  
- Add "Gdrive Sync" section to admin panel with:  
   - Google Drive account selection (multiple accounts support)  
   - Runpod S3 bucket/folder selection  
   - Sync status monitoring dashboard  
- Ensure secure storage of Google Drive API keys using:  
   - Environment variables in studio-specific templates (as per item 25)  
   - Automatic rotation of credentials  
- Test S3 sync functionality when pod is powered off using Runpod's S3 capabilities  
- Add "Sync Now" button for manual triggering  
- Display sync logs in admin panel with error tracking

20. Add Gemma model from DeepMind: https://deepmind.google/models/gemma/gemma-3/

21. Add warning dialog when closing a new card template with unsaved changes.

22. **Simplified Workflow Interface** 
-create a catchy name for the simplified interface, suggestive yet fun and memorable
-in the add new card/edit card modal, i want to have a dropdown that will display the custom nodes contained by the API version of the workflow: if the card has an API workflow uploaded, the Edit Simplified Interface will appear as a collapsed menu, that if clicked it will expand to show all the custom nodes 
-all the custom nodes inside the workflow will appear as selectable checkboxes
-i will select the ones that i want to expose, then click save
-when clicking the card, the default action will be to open the simplified interface that we create with the exposed custom nodes, effectively creating an easier to use interface
-the card should have an "open in comfy" option so that advanced users can modify settings if they so want to
-the simplified interface of the opened workflow should run in a new tab under the current category (image, etc) 

23. remove the app title from the top bar, move all UI higher to create more working space

24. Think about how we can integrate the workbench workflows into comfy UI

25. add API keys in the environment variables of each studio's Template, for easy use withouth the fear of sharing API keys
they will add the keys themselves if possible so that nodes like SF LLM, SF Wavespeed, etc pick the API key automatically without the need to have it in the workflow as a string

26. ask Serhii about his version of the runpod server (interface with start-stop pods, file browser, etc)
file browser
terminate pods interface

27. URGENT - Update Models - Qwen latest image and edit, LTX if anything, Flux 

28. Add request form into the workbench so ideally a user or an artist that is part of a studio will have the option to create a workflow request or a template request. What I want to get out of this is to give them the option to show me a use case from their work where they have trouble getting something done or they want to speed up part of the process. They will have a button on the request page that when they press it, they will have the option to add a few images so that I see exactly what they are trying to achieve. Also, to have some sort of description where they describe their problem so that whenever we start this and we do tutorials, I don't have to ask for files, ask for permission to access resources that are needed in order for me to help them.
Ideally, this request will also contain the name of the user that's created it so we can take that from the login info. So basically, if they select one name from the list and they log in, this should be a part of the name of the request that I have to look at.

29. 




++++++++++++++

Deepseek priority plan:
### **Phase 1: Critical Foundation Work (High Priority)**
**Goals**: Ensure data integrity, improve core functionality, and stabilize infrastructure.

1. **Backup & Symlink Strategy**  
- *Symlinks for critical directories with studio-specific paths:*  
     - Source: `/workspace/outputs` → Destination: `/workspace/ComfyUI/outputs`  
     - Source: `/workspace/models` → Destination: `/workspace/ComfyUI/models`  
     - Source: `/workspace/inputs` → Destination: `/workspace/ComfyUI/inputs`  
     - Source: `/workspace/workflows_<STUDIO_NAME>` → Destination: `/workspace/ComfyUI/user/default/workflows`  
   - *Why*: Prevent data loss during reinstalls, save time on model re-downloads  
   - *Implementation Details*:  
     - Use dynamic symlink creation with studio name interpolation  
     - Store original workflows in `/workspace/workflows_<STUDIO_NAME>`  
     - Ensure symlink paths are validated during startup  
     - Add fallback mechanism if symlink breaks
     - implement step in the initial setup/comfy installer so that you add the studio ticker (GGS, ERP, ART, etc)
- *Implement rclone configuration in the admin panel with:*
   - Google Drive API credential setup (OAuth 2.0 flow)  
   - Folder selection interface for syncing from Runpod S3 to Google Drive  
   - Configurable sync intervals (real-time, hourly, daily)  
- Add "Gdrive Sync" section to admin panel with:  
   - Google Drive account selection (multiple accounts support)  
   - Runpod S3 bucket/folder selection  
   - Sync status monitoring dashboard  
- Ensure secure storage of Google Drive API keys using:  
   - Environment variables in studio-specific templates (as per item 25)  
   - Automatic rotation of credentials  
- Test S3 sync functionality when pod is powered off using Runpod's S3 capabilities  
- Add "Sync Now" button for manual triggering  
- Display sync logs in admin panel with error tracking

3. **RunPod Secret Key Integration (Item 2)**  
   - Implement per-artist RunPod key setup  
   - Investigate username-to-account linking mechanism  
   - *Why*: Security and prevent workflow folder contamination

4. **Workflow Sync Bug Fix (Item 15)**  
   - Implement GitHub sync for workflow deletions  
   - *Why*: Prevent data corruption on pod restarts

---

### **Phase 2: Usability & UX Improvements (Medium Priority)**
**Goals**: Enhance platform usability and consistency with RunPod's design language.

5. **UI/UX Overhaul (Items 3, 13, 23)**  
   - Update button colors to match RunPod  
   - Move admin menu closer to sidebar  
   - Remove redundant "Home conf" title  
   - Increase vertical workspace by removing top bar title  
   - *Why*: Improve visual consistency and user efficiency

6. **Simplified Workflow Interface (Item 22)**  
   - Develop a "Studio Mode" interface with checkbox-based node exposure  
   - Add "Open in ComfyUI" fallback for advanced users  
   - *Why*: Key differentiator for non-technical users

7. **Logout/Profile Switching (Item 12)**  
   - Implement secure session management  
   - *Why*: Essential for multi-user environments

---

### **Phase 3: Feature Expansion & Integration (Long-Term)**
**Goals**: Add new capabilities, integrations, and rebranding.

8. **ComfyUI Rebuild (Item 6)**  
   - Update to SECourses' installer with high VRAM support  
   - Explore smaller Linux distro options (consult Alex Geana)  
   - *Why*: Ensure platform stays up-to-date with latest tools

9. **Studio Management System (Item 9)**  
   - Superadmin studio creation interface  
   - GitHub storage for studio configs  
   - *Why*: Enables multi-studio deployment

10. **Rebranding Architecture (Item 10)**  
    - Implement `config/brand.json` with theme, logo, and feature toggles  
    - *Why*: Enables white-labeling for different clients

11. **API Key Management (Item 25)**  
    - Store API keys in studio-specific environment variables  
    - *Why*: Enhances security for LLM/audio nodes

12. **Advanced Tool Integrations (Items 8, 16, 20)**  
    - Add Gemma, Qwen, and other models  
    - Integrate SECourses' tools  
    - *Why*: Expands platform capabilities




Serhii call

S3 browser -

