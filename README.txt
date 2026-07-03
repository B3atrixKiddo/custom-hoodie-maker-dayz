CUSTOM HOODIE MAKER - By B3atrixKiddo
ONLINE VERSION: https://custom-hoodie-maker-dayz.onrender.com/
----------

1. Put your two transparent logos here:
       logos\back.png
       logos\front.png

2. Run:
       Custom_Hoodie_Maker.bat

3: Click
       Bake With Save Placement


4. Packing the generated folder:

       Yourname_Custom_Hoodie_Mod\ (CHANGE THIS IF YOU WANT -> THIS WILL BE THE PBO NAME)
Creates the texure paa files and is ready for DayZTools. Do these Steps: build the folder with ADDON BUILDER -> sign the pbos with DS UTIL -> then you can either copy the 2 .pbo's into your server pack and publish.


If you want it as a mod by it self then create the following folder structure with your 2 pbo's:
--------------------------------------------------
\Yourname_Custom_Hoodie_Mod
|
\Addons
	|  Yourname_Custom_Hoodie_Mod.pbo
	|  Yourname_Custom_Hoodie_Mod.bsigin.pbo
|\Keys
	|BeatrixKiddo.bikey

--------------------------------------------------
Then select this folder as the publisher folder to upload and you are done!

Depends, if you want to change the default logo placement then choose option Pick Placement + Bake All:


1. Pick the base as your reference texture, draw:
       RED   = back logo
       GREEN = front logo

2. After both boxes:
       Q / E       rotate BACK
       A / D       rotate FRONT
       Shift+key   rotate 5 degrees
       R           redraw both
       Enter       save and bake

3. Packing the generated folder, same way as section 4.
