# conzooming

*conzooming enables mosaic-like collages to be generated from many images.*


## **Getting Started:**

### *Download Python:*
Download the latest version for your system https://www.python.org/downloads/

##### Check the "Add python to environment variables" Box during the installation.

### *Install required Python-Libraries:*
Paste following separately into your commandline, and execute:

    python -m pip install -U Pillow
    python -m pip install -U numpy

# **Executing the mosaic generator:**

Open a commandline in your folder, containing the python script.
To execute the script type:

    python conzooming_generate_mosaic.py

You'll see, that you have to give some additional arguments for the program to run properly.
You can check these via:

    python conzooming_generate_mosaic.py --help

Or see the list of them here:

required arguments:

    --img       IMG      File-Name of the image to be created out of Images
    --dir       DIR      Directory Path containing all images (If you Path spaces, put it inside quotes: "../my path/foo/")

optional arguments:

    -h, --help           show this help message and exit
    --out       OUT      Output directory for the final image. Default is the directory as dir (If your Path contains spaces, put it quotes: "../my path/foo/")
    --scale     SCALE    Minimum count of images per row on the mapped image. Default is 100 (Might be automatically scaled up)
    --size      SIZE     Resolution of the output image. Default is 1 (Resolution = size^2 * Input-Image-Resolution)
    --crop      CROP     Crop images. Default is True
    --orig      ORIG     Should target image appear in smaller images. Default is False
    --wmark     WMARK    Should watermark be added. Default is False

### Examples could look like this:

    python conzooming_generate_mosaic.py --img "myimage.jpg" --dir "C:\Users\Max\Desktop\images\" 
    python conzooming_generate_mosaic.py --img "myimage.jpg" --dir "C:\Users\Max\Desktop\images\"  --size 3 --scale 100 --crop False --out "C:\Users\Max\Desktop\images_2\"
    python conzooming_generate_mosaic.py --img "myimage.jpg" --dir "C:\Users\Max\Desktop\images\" --out "C:\Users\Max\Desktop\images_2\"


# **MP4 generator:**

### **Requirements:** 
### *Install required Python-Libraries:*

Be sure you that you already installed all of the above.
Paste the following separately into your command line, and execute:

    python -m pip install -U imageio
    python -m pip install -U opencv-python
    
### **Executing the MP4-Generator:**

Open a command line in your folder, containing the python script.
To execute the script write:

    python conzooming_generate_mp4_from_mosaic.py

You'll see that you need to provide some additional arguments for the program to run properly
You can check these via:

    python conzooming_generate_mp4_from_mosaic.py --help

Or see the list of them here:

required arguments:

    --img       IMG      File-Name of the image to be created out of Images
    --resx      RESX     The resolution in width
    --resy      RESY     The resolution in height

optional arguments:

    -h, --help           show this help message and exit
    --fps       FPS      GIF Framerate. Default is 24
    --ztime     ZTIME    Length of zoom in seconds. Default is 5
    --zoom      ZOOM     Zoom stregth. equivalent to scale. Default is 20
    --prev      PREV     Add preview before and after. Default is 0 seconds
    --zrev      ZREV     Determines if zooming should be reversed. Default is False
    --out       OUT      Output directory for the final image. Default is the directory from the image (If your Path contains spaces, put it inside quotes: "../my path/foo/")
    --midx      MIDX     Select x value of the center point. Default is the middle of the width
    --midy      MIDY     Select y value of the center point. Default is the middle of the height
    



## Important: resx & resy should be in the same *format* as the source image

### Examples could look like this:


    python conzooming_generate_mp4_from_mosaic.py --img "C:\Users\peter\Desktop\images\mosaicimage.jpg" --resx 720 --resy 720
    python conzooming_generate_mp4_from_mosaic.py --img "C:\Users\peter\Desktop\images\mosaicimage.jpg" --resx 1000 --resy 1000 --zoom 20 --zrev True --ztime 10  --prev True



# **Instagram Picture Downloader:**

### **Requirements:** 
### *Install required Python-Libraries:*

Ensure you have already installed all of the above.
Paste following separately into your command line, and execute:

    python -m pip install -U instaloader
    
Open a command line in your folder, containing the python script.
To execute the script write:

    python conzooming_instaloader.py

You'll see, that you have to give some additional arguments for the program to run properly.
You can check these via:

    python conzooming_instaloader.py --help

Or see the list of them here:

required arguments:

    --user USER  username
    --dir DIR    Directory Path where folder with images should be created (If your Path contains spaces, put it inside quotes: "../my path/foo/")


optional arguments:

    -h, --help           show this help message and exit
    --max MAX    (Integer) Count of images, that should be downloaded. Default is 200

### Examples could look like this:

    python conzooming_instaloader.py --user Hans --max 10 --dir "C:\users\peter\Desktop"
