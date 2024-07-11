"""
@brief - usng a simple config file, change the background of desktop
         at a consistent interval. Can choose multiple wall paper folders
         at once to mix between, provided they are in same parent directory. 
            - ex) if you have a folder of space pictures and landscape pictures,
            you can configure it to only show one folder, or show a shuffle of both
        
        It also allows for setting different wallpapers to each monitor, such
        as space images on the left screen, and landscapes on the right. Again, 
        provided both folders are in the same parent directory
         - note, this relies on hydrapaper being installed
         
@version - 2.0, using classes to mainstream the code, and starting
           to use JSON as a config file instead of a plain text file.
           Note, a few things in the config file don't do anything yet, 
           such as gsettings_mode. Currently only uses zoom (span for hydrapaper)
           will make functionl in v3
           
"""


import os  # to delete old log file, and execute shell commands
from time import sleep  # to pause between switches
from random import shuffle # shuffle pictures to randomize display order
from datetime import datetime # to display in the log file the time last executed
import json # to read/write the config file
from PIL import Image # used to join pictures together manually


class ErrorLogger():
    """
            Create a log file for errors or blank out the old one
            Allows easy writing to the end of the file for logging errors
            
            Class Members:
                path : str - the full path to the log file
    """
    def __init__(self, directory : str):
        
        # determine the full file path for the log file
        self.path = directory + "errors.log"
        
        # overwrite old-log, or create a 
        # blank log file if it doesn't exist
        with open(self.path, 'w') as f:
            # write the datetime at the top for reference
            formatted_time = "Ran On: " + self.time_str()
            f.write(formatted_time + "\n")
            [f.write('-') for i in range(len(formatted_time))]
            f.write('\n\n')
  
        
    def log(self, log_message: str):
        with open(self.path, 'a') as f:
            f.write(log_message + "\n")
            
    def time_str(self) -> str:
        return datetime.now().strftime("%a %b %d @ %-I:%M:%S %p")
                    
class ConfigReader():
    def __init__(self, logger : ErrorLogger, directory : str):
        
        # determine the full file path for the config file
        self.path = directory + "config.json"
        
        # check if it exists, if not, make a default one
        if (not os.path.isfile(self.path)):
            self.create_default_config_file()
            
        # track last time config file modified
        self.last_modified = os.stat(self.path).st_ctime
            
        # var to track config data, to be filled in validate
        # config
        self.config_data = None 
            
        # validate the data to make sure they have good values.
        self.critical_error = False
        self.logger = logger
        self.validate_config()
    
    def check_config_updated(self) -> bool:
        modified = os.stat(self.path).st_ctime
        if self.last_modified != modified:
            self.last_modified = modified
            self.logger.log(f"\nConfig File Updated - {self.logger.time_str()}")
            
            # update all the config variables
            self.critical_error = False # assume no error until read
            self.validate_config()
            return True # was updated
        else:
            return False # was not updated
            

        
    def validate_config(self):
        """ 
            Check the config data to make sure they are allowed values
            ie, bools are true false, ints dont contain strings, etc.
            
            If errors are found, they will be logged. If possible, 
            default values will be assigned
        """
        # read in all the data
        with open(self.path, 'r') as file:
            self.config_data = json.load(file)
        
        # check the service, this is a critical check
        service = None
        try:
            service = self.config_data['service']
            if (service != 'gsettings' and service != 'hydrapaper'):
                self.logger.log("CRITICAL ERROR: 'service' should be either 'gsettings' or 'hydrapaper'")
                self.critical_error = True
        except KeyError:
            self.critical_error = True
            self.logger.log("CRITICAL ERROR: 'service' field is missing")
            self.logger.log("To make a new config file, delete the existing one\nand a default one will be automatically generated")
            return
            
            
        # check gsettings-specific config stuff (don't bother if not gsettings)
        if (service == 'gsettings'):
            # check color theme - non-critical, default 'dark'
            try:
                if (self.config_data['gnome_color_theme'] == 'light'):
                    self.config_data['gnome_color_theme'] == "picture-uri"
                elif (self.config_data['gnome_color_theme'] == 'dark'):
                    self.config_data['gnome_color_theme'] = "picture-uri-dark"
                else:
                    self.logger.log("ERROR: 'gnome_color_theme' should be either 'light' or 'dark'")
                    self.logger.log("Using default 'dark'")
                    self.config_data['gnome_color_theme'] = 'picture-uri-dark'
                
                    
            except KeyError:
                self.logger.log("ERROR: 'gnome_color_theme' field is missing")
                self.logger.log("Using default 'dark'")
                self.logger.log("To make a new config file, delete the existing one\nand a default one will be automatically generated")
                self.config_data['gnome_color_theme'] = 'picture-uri-dark'
                
            # check gsettings_mode - non-critical, default 'zoom'
            try:
                acceptable_values = ['spanned', 'wallpaper', 'zoom', 'none', 'centered', 'scaled', 'stretched']
                if (self.config_data['gsettings_mode'] not in acceptable_values):
                    self.logger.log(f"ERROR: 'gsettings_mode' should be one of the following: {acceptable_values}")
                    self.logger.log("Using default 'zoom'")
                    self.config_data['gsettings_mode'] = 'zoom'
            
            except KeyError:
                self.logger.log("ERROR: 'gsettings_mode' field is missing")
                self.logger.log("Using default 'zoom'")
                self.logger.log("To make a new config file, delete the existing one\nand a default one will be automatically generated")
                self.config_data['gsettings_mode'] = 'zoom'
        
        # check hydrapaper-specific config stuff
        elif (service == 'hydrapaper'):
            
            # hydrapaper_stagger - validate and make a bool
            try:
                if (self.config_data['hydrapaper_stagger'] != 'true' and
                    self.config_data['hydrapaper_stagger'] != 'false'):
                    self.logger.log(f"ERROR: 'gsettings_mode' should be ether 'true' or 'false'")
                    self.logger.log("Using default 'false'")
                    self.config_data['hydrapaper_stagger'] = False
                
                # change from string to bool if valid
                else:
                    if (self.config_data['hydrapaper_stagger'] == 'true'):
                        self.config_data['hydrapaper_stagger'] = True
                    else:
                        self.config_data['hydrapaper_stagger'] = False

            # catch error if field is missing
            except KeyError:
                self.logger.log("ERROR: 'hydrapaper_stagger' field is missing")
                self.logger.log("Using default 'false'")
                self.logger.log("To make a new config file, delete the existing one\nand a default one will be automatically generated")
                self.config_data['hydrapaper_stagger'] = False
        

        # check time delay - noncritical, default 60
        try:
            time = int(self.config_data['switch_time'])
            if (time < 5):
                self.logger.log("ERROR: 'switch_time' must be a minimum of 5")
                self.logger.log("Using minimum 5")
                time = 5
            self.config_data['switch_time'] = time
        
        except ValueError:
            self.logger.log("ERROR: 'switch_time' should be a integer, at least 5. ")
            self.logger.log("Using default 60")
            self.config_data['switch_time'] = 60
        except KeyError:
            self.logger.log("ERROR; 'switch_time' field is missing")
            self.logger.log("Using default 60")
            self.logger.log("To make a new config file, delete the existing one\nand a default one will be automatically generated")
            self.config_data['switch_time'] = 60
            
            
        # check parent directory - critical
        parent_path = None
        try:
            parent_path = self.config_data['image_parent_directory']
            if not os.path.isdir(os.path.expanduser(parent_path)):
                self.critical_error = True
                self.logger.log(f"CRITICAL ERROR: invalid parent folder '{parent_path}'")
        
        except KeyError:
            self.critical_error = True
            self.logger.log(f"CRITICAL ERROR: 'image_parent_directory' field is missing")
            self.logger.log("To make a new config file, delete the existing one\nand a default one will be automatically generated")
            
        # check child directories and validate files within,
        # here, check only they were in json, check files in different function
        if (not self.critical_error):
            try:
                image_folders = self.config_data['image_folders']
                
                # validate single image folder
                if (service == 'gsettings'):
                    try:
                        self.config_data['image_folders']['one_monitor'] = self.validate_img_folders(image_folders['one_monitor'])
                        
                        # check at least one valid image file
                        if not self.config_data['image_folders']['one_monitor']:
                            self.logger.log("CRITICAL ERROR: no valid images in one monitor folders")
                            self.critical_error = True
                    # single image field doesn't exist
                    except KeyError:
                        self.logger.log("CRITICAL ERROR: 'one_monitor' list is missing")
                        self.logger.log("To make a new config file, delete the existing one\nand a default one will be automatically generated")
                        self.critical_error = True
                        
                # validate left/right monitor folders if hydrapaper
                else:
                    try:
                        # turn into list of image file paths
                        self.config_data['image_folders']['left_monitor'] = self.validate_img_folders(image_folders['left_monitor'])
                        self.config_data['image_folders']['right_monitor'] = self.validate_img_folders(image_folders['right_monitor'])
                        
                        # check that at least one valid image for each monitor to display
                        if not self.config_data['image_folders']['left_monitor']:
                            self.logger.log("CRITICAL ERROR: no valid images in left monitor folders")
                            self.critical_error = True
                        if not self.config_data['image_folders']['right_monitor']:
                            self.logger.log("CRITICAL ERROR: no valid images in right monitor folders")
                            self.critical_error = True
                        
                    except KeyError:
                        self.logger.log("CRITICAL ERROR: 'left_monitor' or 'right_monitor' list(s) missing")
                        self.logger.log("To make a new config file, delete the existing one\nand a default one will be automatically generated")
                        self.critical_error = True
                        
                        
            # image folder sub-dictionary doesn't exist.
            except KeyError:
                self.critical_error = True
                self.logger.log("CRITICAL ERROR: 'image_folders' sub dictionary is missing")
                self.logger.log("To make a new config file, delete the existing one\nand a default one will be automatically generated")
                                
                
    def validate_img_folders(self, folders: list[str]) -> list[str]:
        """ Given a list of sub-folders, return a list of all valid 
        image files within each sub-folder. If no valid image folders, returns empty list"""
        # track valid sub-folders with at least 1 image file
        valid_files = []
        
        valid_file_extensions = [".webp", ".svg", ".png", ".jpeg", ".jpg"]
        
        folders = [os.path.join(self.config_data['image_parent_directory'], f) for f in folders]
        for folder in folders:
            folder = os.path.expanduser(folder)
            if not os.path.isdir(folder):
                self.logger.log(f"ERROR invalid folder path '{folder}'")
                continue
            
            files = [f.path for f in list(os.scandir(folder))]
            
            for file in files:
                if any(file.lower().endswith(ext) for ext in valid_file_extensions):
                    valid_files.append(file)
                else:
                    self.logger.log(f"ERROR: Invalid image file: {file}")
                    
        return valid_files
 
                        
    def create_default_config_file(self):
        
        with open(self.path, 'w') as f:
            contents = """{
    "service" : "gsettings",

    "gsettings_mode" : "zoom",
    "gnome_color_theme" : "dark",

    "hydrapaper_stagger" : "true",

    "switch_time" : "60",

    "image_parent_directory" : "/usr/share/backgrounds/",
    "image_folders" : 
    {
        "one_monitor" :
            [
                "gnome"
            ]
        ,
        "left_monitor"  : 
            [
                "folder1", "folder2"
            ]
        ,
        "right_monitor" : 
            [
                "folder1", "folder2"
            ]
    }

}"""
            f.write(contents)      
        
class WallPaperSwitcher():
    def __init__(self):
        
        self.directory = __file__
        while (self.directory):
            self.directory = self.directory[:-1]
            if (self.directory[-1] == '/'):
                break
        
        self.logger = ErrorLogger(self.directory)
        # get config file info
        self.config = ConfigReader(self.logger, self.directory)
        self.keyboard_interupt = False
        
    def use_gsettings(self):
        """ Use gsettings to display to one image"""
        print("In gsettings")
        
        
        try:
            while True:
                # set gsettings mode once before displaying all images
                os.system(f"gsettings set org.gnome.desktop.background picture-options {self.config.config_data['gsettings_mode']}")
                shuffle(self.config.config_data['image_folders']['one_monitor'])
                
                for f in self.config.config_data['image_folders']['one_monitor']:
                    os.system(f"gsettings set org.gnome.desktop.background {self.config.config_data['gnome_color_theme']} file://{f}")
                    sleep(self.config.config_data['switch_time'])
                    
                    # check if config file updated
                    if self.config.check_config_updated():
                        return # may not be using gsettings or invalid config
                                                        
        except KeyboardInterrupt:
            self.logger.log("Keyboard interrupt detected, terminating program...")
            self.keyboard_interupt = True
            
           
    def use_hydrapaper(self):
        print("in hydrapaper")
        
        try:
            
            left_files = self.config.config_data['image_folders']['left_monitor']
            right_files = self.config.config_data['image_folders']['right_monitor']
            
            # use ints to index lists
            left_index = 0
            right_index = 0
            
            shuffle(left_files)
            shuffle(right_files)
            
            rights_turn = True  #flag for use when staggered, not used otherwise

            while True:
                
                # if index is too large, set to 0 and reshuffle
                if left_index > len(left_files) - 1:
                    left_index = 0
                    shuffle(left_files)
                if right_index > len(right_files) - 1:
                    right_index = 0
                    shuffle(right_files)
                    
                os.system(f"flatpak run org.gabmus.hydrapaper -c {left_files[left_index]} {right_files[right_index]}")
                self.join_images([left_files[left_index], right_files[right_index]])
                
                if not self.config.config_data['hydrapaper_stagger']:
                    left_index += 1
                    right_index += 1
                    
                    sleep(self.config.config_data['switch_time'])
                    
                else:
                    if rights_turn:
                        right_index += 1
                    else:
                        left_index += 1
                        
                    sleep(self.config.config_data['switch_time'] / 2)
                    rights_turn = not rights_turn
                    
                
                # check if config file updated
                if self.config.check_config_updated():
                    return # may not be using gsettings or invalid config
                                                        
        except KeyboardInterrupt:
            self.logger.log("Keyboard interrupt detected, terminating program...")
            self.keyboard_interupt = True
    
    
    def join_images(self, image_paths):
        
        # target size for each screen assume 1920x1080
        target_width, target_height = 1920,1080
        
        # open and resize images
        images = [Image.open(x).resize((target_width, target_height), Image.LANCZOS) for x in image_paths]
        
        # calculate dimensions for new image
        total_width = target_width * len(images)
        max_height = target_height

        # create new image of combined width and height
        new_im = Image.new('RGB', (total_width, max_height))

        # 'paste' images onto larger image
        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset,0))
            x_offset += im.size[0]

        # save in the current directory
        new_im.save(self.directory + "/.joined_file.jpg")
            
        
    
        
        
if __name__ == "__main__":
    switcher = WallPaperSwitcher()
    
    while not switcher.keyboard_interupt:
        print("in main")
        if (not switcher.config.critical_error):
            if (switcher.config.config_data['service'] == 'gsettings'):
                switcher.use_gsettings()
            else:
                switcher.use_hydrapaper()
        
        # check if updates. causes a second check if 
        # update caused it to leave one of the display loops, 
        # but allows program to keep running if config is messed up 
        # until it is fixed, without needing to find and run this script
        switcher.config.check_config_updated()
            
