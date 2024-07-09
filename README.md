# wall_paper_switcher

## Brief
Consistently switch the background wallpaper on a given interval, with images in a given directory. Made to work with 2 monitors

It uses a JSON config file to setup what directories of images to use, what gsettings mode to use, how long to 
switch between images, and others. The way it is set up, it requires a parent directory with subdirectories containing images, 
such as ~/Pictures/WallPapers/, with sub-directories filled with images like ~/Pictures/WallPapers/Space/ or ~/Pictures/WallPapers/Landscapes/
This allows you to configure it to only use one folder, like only using space images or only uses landscapes, mix both of them together, 
or, when using two monitors, put one folder on the left monitor and a different on the right monitor, like space on the left and 
landscapes on the right.

When working with one monitor, or with two when displaying the same image to both or spanning an image across both, 
the gsettings service is used. 

To work with two monitors, other than when spanning one image across both, it utilizes a third-party application
called Hydrapaper. As I continue to devlop this, this dependancy will hopefully be eliminated. Currently, it is used
to merge the two wallpapers into one larger image, then use gsettings to display that larger image spanned across both screens, 
which appropriately splits each image onto each monitor.

## Dependancies
hydrapaper 
gnome-tweaks

both can be installed by sudo apt install _ 
however, the flatpak version of hydrapaper is recommended

## All Config Fields 
Below is an example config file:


{
    "service" : "gsettings",

    "gsettings_mode" : "zoom",
    "gnome_color_theme" : "dark",

    "hydrapaper_stagger" : "true",

    "switch_time" : "5",

    "image_parent_directory" : "~/Pictures/WallPapers",
    "image_folders" : 
    {
        "one_monitor" :
            [
                "space", "landscapes"
            ]
        ,
        "left_monitor"  : 
            [
                "space"
            ]
        ,
        "right_monitor" : 
            [
                "landscapes"
            ]
    }

}

"service" - if the program should use gsettings or hydrapaper.
          - "gsettings" is for one image on each monitor, working with only one monitor, or spanning images across both
          - "hydrapaper" is for having a different image on each monitor
          
           
"gsettings_mode" - only checked when "service" is "gsettings"
                 - determines the gsettings mode, such as spanned, zoom, centered, etc. for displaying image
                 - forced to "spanned" when using hydrapaper

"gnome_color_theme" - "light" or "dark"
                    - only checked when "service" is "gsettings" (hydrapaper likely knows how to retrieve this without needing to ask)
                    - needs to know the system theme, to determine if the gsettings command should include "picture-uri-dark" or "picture-uri"

"hydrapaper_stagger" - "true" or "false"
                     - only checked when "service" is "hydrapaper"
                     - when displaying two separate images, if they should stagger when they change. 
                     - if "false", both images change at the same time
                     - if "true", right screen picture is offset by half the switch time, so they alternate when they change
                     - both images changed every "switch_time" seconds, but the command to change the wallpaper is run 
                       every "switch_time"/2 seconds, which may lead to more performance issues
                       
"switch_time" - the time in seconds before the wallpaper switches
              - minimum of 5 second

"image_parent_directory" - the parent directory containing all sub-folders with images

"one_monitor" - only checked when "service" is "gsettings"
              - also used with two monitors when same image on both, or spanned across both
              - lists all subdirectories of images to display
              - in the example, a mix of space and landscapes will be displayed

"left_monitor" - only checked when "service" is "hydrapaper"
               - lists all subdirectories of images to display to the left monitor
               - in the example, only space images will be displayed to the monitor
               - listing more directories will mix more images into the pool to be displayed


"right_monitor" - only checked when "service" is "hydrapaper"
               - lists all subdirectories of images to display to the right monitor
               - in the example, only landscape images will be displayed to the monitor
               - listing more directories will mix more images into the pool to be displayed
