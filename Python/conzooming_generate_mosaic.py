#Project: conzooming
#Author: CompilerStuck
#Contributor: Daniil Vyazalov
#View GitHub-Repository: https://github.com/CompilerStuck/conzooming
#Instagram: conzooming.github.io

import numpy as np
import argparse
import os
from PIL import Image
from PIL import ExifTags
from os import listdir
from os.path import isfile, join

#Params:
    #dir_name: A Directory name containing images
#Returns:
    #An Array containing all image paths
def get_file_names_from_dir(dir_name, image_name, orig):
    file_names = []
    for f in listdir(dir_name):
        if isfile(join(dir_name, f)) and (f.lower().endswith('.png') or f.lower().endswith('.jpg') or f.lower().endswith('.webp') or f.lower().endswith('.jpeg')):
            if orig or f.lower() != image_name.lower():
                file_names.append(dir_name + f)

    return file_names


#Params:
    #file_names: Array containing all image file names
    #scale: Scaling of the images
    #org_scale: Scale of the original image that is going to be mapped
#What?
    #Opens and scales all images that should map the main image
#Returns:
    #Array containing scaled rgb images as arrays
def get_scaled_images(file_names, scale, org_size, size_adjustment, auto_crop):
    scaled_images = []
    cnt = 0
    for file_name in file_names:
        img = correct_EXIF_orientation(Image.open(file_name)).convert('RGB')
        if auto_crop:
            if img.height != img.width:
                min_length = min(img.height, img.width)
                img = img.crop((img.width//2 - min_length//2, img.height//2 - min_length//2, img.width//2 + min_length//2, img.height//2 + min_length//2))
            scaled_images.append(np.asarray(img.resize((list(org_size)[0]//scale*size_adjustment, list(org_size)[0]//scale*size_adjustment))))
        elif img.size == org_size:
            scaled_images.append(np.asarray(img.resize((img.width//scale*size_adjustment, img.height//scale*size_adjustment))))
        cnt += 1
        printProgressBar(cnt, len(file_names), length = 50, prefix="Loading/Scaling Images:\t")
    return scaled_images


#Params:
    #image_array: An rgb image array
#Returns:
    #Average rgb color in the image
def get_avg_color_rgb(image_array):
    return image_array.mean(axis=1).mean(axis=0)


#Params:
    #original: scale factor
    #org_size: size of the image to be mapped
#Returns:
    #Scale that divides height and width without rest
def correct_scale(scale, org_size, auto_crop):
    new_scale = scale
    if auto_crop:
        while (min(org_size) > new_scale and (org_size[0] % new_scale != 0 or org_size[1] % (org_size[0]/(org_size[0]/new_scale) ) != 0)):
            new_scale += 1
    else:
        while (min(org_size) > new_scale and (org_size[0]%new_scale!=0 or org_size[1]%new_scale!=0)):
            new_scale += 1
    if min(org_size) <= new_scale:
        raise argparse.ArgumentTypeError("scale: " + str(scale) + " to high. Select a smaller one")
    print("► Corrected Scale to " + str(new_scale))
    return new_scale


#Params:
    #image: a Pillow Image
#What?
    #EXIF ist Meta information about an image. By reading it you can see how the image got recorded.
#Returns:
    #A rotated Pilow Image
def correct_EXIF_orientation(image):
    if image._getexif():
        exif=dict((ExifTags.TAGS[k], v) for k, v in image._getexif().items() if k in ExifTags.TAGS)
        if 'Orientation' in exif.keys():
            if exif['Orientation'] == 3:
                image=image.rotate(180, expand=True)
            if exif['Orientation'] == 6:
                image=image.rotate(-90, expand=True)
            if exif['Orientation'] == 8:
                image=image.rotate(90, expand=True)
    return image


#Params:
    #scaled_images: list of scaled images as numpy arrays
    #image: the target image als Pillow Image
    #scale: int discribing the size
    #color_func: function to evaluate the average color of an image
    #auto_crop: boolean
    #size_adjustment: int to scale up the image quality
#What?
    #Evalualtes all images and maps an image to each section where its avg. color is the same
#Returns:
    #An numpy array containing the mapped image
import time


def map_images(scaled_images, image, scale, color_func, auto_crop, size_adjustment):

    labeled_images = {}

    mapped_img = np.asarray(image.resize((image.width * size_adjustment, image.height * size_adjustment))).copy()
    image_arr = np.asarray(image).copy()

    img_height = len(mapped_img)
    img_width = len(mapped_img[0])

    width_step = len(mapped_img[0]) // scale
    height_step = len(mapped_img)//scale

    if auto_crop:
        height_step = width_step
    for img in scaled_images:
        label = color_func(img)

        known = False
        for x in labeled_images.keys():
            if np.sqrt(sum([a ** 2 for a in x - label])) < 10:
                labeled_images[tuple(x)].append(img)
                known = True
                break

        if not known:
            labeled_images[tuple(label)] = [img]

    cnt = 0
    mapped_labels = {}
    for row in range(height_step, img_height+1, height_step):
        for column in range(width_step, img_width+1, width_step):
            part = image_arr[row // size_adjustment - height_step // size_adjustment:row // size_adjustment, column // size_adjustment - width_step // size_adjustment:column // size_adjustment]

            part_label = color_func(part)

            best_label = tuple()
            known = False
            # for x in mapped_labels.keys():
            #     if np.sqrt(sum([a ** 2 for a in x - part_label])) < 10:
            #         best_label = mapped_labels[x]
            #         known = True
            #         break
            if not known:
                best_label = min(labeled_images, key=lambda x:np.sqrt(sum([x**2 for x in x-part_label])))
                mapped_labels[tuple(part_label)] = best_label


            mapped_img[row-height_step:row, column-width_step:column] = labeled_images[best_label][np.random.randint(len(labeled_images[best_label]))]
            cnt += 1
            printProgressBar(cnt, img_height//height_step*img_width//width_step, length=50, prefix="Mapping Target Image:\t")

    if cnt !=img_height // height_step * img_width // width_step:
        printProgressBar(img_height // height_step * img_width // width_step, img_height // height_step * img_width // width_step, length=50, prefix="Mapping Target Image:\t")

    return mapped_img



# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    FROM: https://stackoverflow.com/users/2206251/greenstick
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '─' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()

#Check if is dir
class readable_dir(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir=values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("dir: {0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace,self.dest,prospective_dir)
        else:
            raise argparse.ArgumentTypeError("dir: {0} is not a readable dir".format(prospective_dir))

#parse string to bool
def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--img",    help="File-Name of the image to be created out of Images", type = str, required=True)
    parser.add_argument("--dir",    help="Directory Path containing all images (If your Path contains spaces, put it inside quotes: \"../my path/foo/\")", action=readable_dir, required=True)
    parser.add_argument("--out",    help="Output directory for the final image. Default is the same directory as dir (If your Path contains spaces, put it inside quotes: \"../my path/foo/\")", action=readable_dir)
    parser.add_argument("--scale",  help="Minimum count of images per row on the mapped image. Default is 100 (Might be automatically scaled up) ", type=int)
    parser.add_argument("--size",   help="Resolution of the output image. Default is 1 (Output-Resolution = size^2 * Input-Image-Resolution)", type=int)
    parser.add_argument("--crop",   help="Crop images. Default is True", type=str2bool)
    parser.add_argument("--orig",   help="Should target image appear in smaller images. Default is False", type=str2bool)
    parser.add_argument("--wmark",   help="Should watermark be added. Default is True", type=str2bool)

    args = parser.parse_args()

    out_path = "placeholder"
    auto_crop = True
    orig = False
    wmark = True
    size_adjustment = 1
    scale = 100


    image_name = str(args.img)

    folder_path = str(args.dir)
    if '/' in folder_path:
        if not folder_path.endswith('/'):
            folder_path += '/'
    elif '\\' in folder_path:
        if not folder_path.endswith('\\'):
            folder_path += '\\'

    if args.out == None:
        out_path = folder_path
    else:
        out_path = str(args.out)
        if '/' in out_path:
            if not out_path.endswith('/'):
                out_path += '/'
        elif '\\' in out_path:
            if not out_path.endswith('\\'):
                out_path += '\\'

    if not isfile(join(folder_path, image_name)):
        raise argparse.ArgumentTypeError("\"" + str(join(folder_path, image_name)) + "\" is not a valid file")

    if args.crop != None:
        auto_crop = bool(args.crop)

    if args.orig != None:
        orig  = bool(args.orig)

    if args.wmark != None:
        wmark  = bool(args.wmark)

    if args.size != None:
        if args.size < 1:
            raise argparse.ArgumentTypeError("size: " + str(args.size) + " has to be > 0")
        else:
            size_adjustment = int(args.size)

    image = correct_EXIF_orientation(Image.open(folder_path + image_name)).convert('RGB')
    image = image.resize((image.width-int(image.width%10), image.height-int(image.height%10)))


    if args.scale != None:
        if args.scale < 1:
            raise argparse.ArgumentTypeError("scale: " + str(args.scale) + " has to be > 0")
        else:
            scale = correct_scale(args.scale, image.size, auto_crop)

    #IMG_20200111_150923
    print("► Target Image Height: " + str(image.height) + ", Width: " + str(image.width))


    scaled_images = get_scaled_images(get_file_names_from_dir(folder_path, image_name, orig), scale, image.size, size_adjustment, auto_crop)
    mapped_image = Image.fromarray(map_images(scaled_images, image, scale, get_avg_color_rgb, auto_crop, size_adjustment))

    if wmark:
        watermark_path = "../Media/Watermark/watermark-logo-transp.png"
        watermark = correct_EXIF_orientation(Image.open(watermark_path))
        watermark_width, watermark_height = watermark.size
        mapped_image_width, mapped_image_height = mapped_image.size
        watermark_scale = (mapped_image_width/4) / watermark_width
        watermark = watermark.resize((int(watermark_scale*watermark_width),int(watermark_scale*watermark_height)))
        mapped_image.paste(watermark, (0, mapped_image.height-watermark.height), watermark)


    cnt = 0
    out_name = "mapped-" + image_name.split('.')[-2] + "-sc" + str(scale) + "-sz" + str(size_adjustment) + "-nr" + str(cnt) + ".jpg"
    while (out_name.lower() in [x.lower() for x in listdir(out_path)]):
        cnt += 1
        out_name = "mapped-" + image_name.split('.')[-2] + "-sc" + str(scale) + "-sz" + str(size_adjustment) + "-nr" + str(cnt) + ".jpg"
    mapped_image.save(out_path + out_name)


