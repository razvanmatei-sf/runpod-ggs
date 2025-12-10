1.
Server UI Mods
we are going to design a new interface for the server
we will create a temp branch with these mods so that we don't break the existing working setup as we test designs
we will create a temporary 1-2-3 toggle for the designs that you provide so that we test them, improve, combine them into a new amazing professional looking design for our application
your goal is to act as a proffesional web and graphic designer working in an Games Dev Studio
the UI should reflect a proffessional gaming studio
keep in mind that this tool will be used in a webpage so it should be optimized for that rather than mobile (it seems to be like this for now)
explore different ways that we can approach this design
onw would be with the terminal button that opens whenever you rpess a button (opens under the button) but I feel like that would take up too much vertical space and not use the widescren format of most monitors nowadays.
so maybe consider something like a terminal window open at all times to the right side of the buttons. when opening jupyter, ai-toolkit, comfy etc open a new tab in that terminal window.
create 3  page/app designs first and let's figure how we can test them before writing all the code 
the new design will be pushed on a new git branch and we will merge it with the main one once we are happy with it
focus on creating a sleek minimalist proffessional design
think about the buttons design so that it works with the terminal being a part of it when pressed
I want the 3 options to be as different from eachtother as possible so that we can experiment with 
I want us to bounce a few ideas first and then to find a way to preview these changes without you having to code everything, so the user page with a button pressed and the terminal open to see how they connect would be enough for us to determine wheter we should pursue the design 
do you think that using Google Nano Banana Pro would give us a good design starting point? I coul d paste a screencap of the current design and use that as a base for getting a few concepts done before you start coding
I would like for you to give me a sumarize of the things I want to change so that I can copy-paste it into Google Gemini alongside the screencaps with the existing design.
Give it all the necessary details in order for it to have all the requirements and to start designing the 3 concepts. 
I will then bring the concepts back to you so that we can start thinkning about the implementation
after we decide about the direction, implement the inintal new layout, we will:
add some christmass flavour ot it (like snowflakes) once we are happy with one design
this will have to be in tune with the new design. it has to be subtle but effective, with great animation (wind, gravity, etc)
If there is an easy way for you to design this on the go and for me to preview it very fast, let's try that too

2.
Admin Page Mods
StudioAdmin page to select which studio will be displayed on front page
i will set this up for more than one studio and I would like for the logo that I select to be shown next to the ComfyStudio Title
clicking the CS temporary icon will take you to the StudioSetup page
in this page you have a dropdown list with studio that you can select
selecting one will automatically load it's respective logo
logo for each stored in github, select each based on studio
i want the option to add users/artists manually, one by one > empty field with grayed out Artist Name and Add button next to it. you add then a new row shows up
i want the option to paste multiple artists names on multiple lines and they all get added (eg 3 names on 3 rows will add 3 artists)
they will be added in a list similar to how the download models works.
i want to be able to select them, remove multiple, etc
i wat to be able to make some of them an admin - select 1, 3,etc and button for turn to admin
once admin you can see the admin page, and also add new admins but never remove Razvan Matei as admin
button to turn admin back to regular user/artist
page will have the option to select which studio is this being setup for (select from list from repo)
i will paste a list of names and you will create and keep the /workspace/ComfyUI/output folder in sync with the names added for the studio
Razvan Matei is always admin

3.
download repo and copy the ai-toolkit login example (with runpod secret key)
esch artist should setup their own runpod secret and use it when they login
Q is there an option to connect an artist user name from the dropdown list to their respective runpod accounts?
the use case would be this: artist selects wreong name from the list and will save images in another artist's folder or they select my name(Razvan Matei) and they can access the admin page



4.
search and remove for the blue info text from all the terminal windows


note to self:
use gemini-banana chatgpt to create mockup design first
create a good prompt from this description first

5. fix Updateing missplell in terminal and button
