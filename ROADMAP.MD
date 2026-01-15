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


14. possible actions when you click on a card - two options - one is to open comfy and open that workflow - you have to find a way for comfy to accesss the file from /workspace/runpod-ggs/workflows
for second option we have to build an interface that will:
-have the option to load any of the workflows present on the use case/images/3d model/etc in a simplified interface
the idea behind it is that i want to, as an admin, be able to edit a particular workflow for his "simplified form"
this will open the API version of the workflow which is arranged in such a way that it can be utilised to, instead of opening the worjkflow in comfy ui, have a sort of interface that will:
allow me to select which of the nodes from a workflow (API version) i want to expose in the simplified interface
example:
let's say I have a workflow that has 20 nodes
i will save the normal version of the workflow, which can be opened in comfy ui (the running instance on runpod)
i will save the API version of the workflow in the interface editor which will allow me to select which one of the multitude of nodes present in the workflow I want to expose 
the goal is to create a super simplified version of the workflow that will allow non advanced users to use these workflows as a user and not as a workflow builder
i would use the same pop-up/modal interface that we already have for uplloading the workflow to github
I would have another tab called something like "simplified workflow - don't use this ad literam, i want you to come up with a proper name for this"
all of this will be avaiulable if I have uploaded the API version of the workflow (btw this is a json file with a slightly better organized structure in terms of order of execution i suppose)
in this tab, i want, based on the workflow that I am adding as a template/card to see the different nodes from the workflow as selectable options (think of it as checkboxes that I can select) that, if checked, will expose that parameter
the nodes will be, but not allways, prompt input fields, image input fields, that will allow the non experienced users to use the workflow without the fear of openiong a very complex workflow
the cards should, by default, open the simplified version
i want us to add another button somewhere on the card that will say something like "advanced" which will open that workflow in comfy ui, for the advanced users that want to modify the parameters of that workflow
i want you to plan this before and let me know if there are any unknowns for you
after clicking a card, the simplified interface should open as a full screen page, where the users will see the selectable parameters, input images, or any other nodes that I expose from the card edit menu
anything that is unclear about this?


15. logout/switch profile


16. I want to remove the home conf title from the page, which is redundant because you already see that on the left sidebar. 


17. add sf new nodes
