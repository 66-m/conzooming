# Project: conzooming
# Author: Marcel Mauel
# Contributor: Daniil Vyazalov
# View GitHub-Repository: https://github.com/marcelmauel/conzooming
# Instagram: conzooming.github.io

"""
IDEA:

Goal of this program is to generate an in-/outzooming gif from an image.
"""

import numpy as np
import argparse
import imageio
import cv2
import os
import io
import warnings
from PIL import Image
from PIL import ExifTags
from os.path import isfile
Image.MAX_IMAGE_PIXELS = 300000000


# Params:
# image: a Pillow Image
# What?
# EXIF ist Meta information about an image. By reading it you can see how the image got recorded.
# Returns:
# A rotated Pilow Image


def correct_exif_orientation(img):
    if img._getexif():
        exif = dict((ExifTags.TAGS[k], v) for k, v in img._getexif().items() if k in ExifTags.TAGS)
        if 'Orientation' in exif.keys():
            if exif['Orientation'] == 3:
                img = img.rotate(180, expand=True)
            if exif['Orientation'] == 6:
                img = img.rotate(-90, expand=True)
            if exif['Orientation'] == 8:
                img = img.rotate(90, expand=True)
    return img


# Print iterations progress
def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end="\r"):
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
        print_end    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '─' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    # Print New Line on Complete
    if iteration == total:
        print()


class ReadableDir(argparse.Action):
    def __call__(self, args_parser, namespace, values, option_string=None):
        prospective_dir = values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("dir: {0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError("dir: {0} is not a readable dir".format(prospective_dir))


# parse string to bool
def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_bytes_from_image(img):
    image_bytes_arr = io.BytesIO()
    img.save(image_bytes_arr, 'jpeg')
    image_byte_arr = image_bytes_arr.getvalue()
    bytes = imageio.imread(image_byte_arr)

    return bytes


def get_image(img_name):
    im = Image.open(img_name)
    im = correct_exif_orientation(im)

    return im


def generate_video(img, frames_per_second, zoom_time, zoom_strength, res_x, res_y, reverse, preview, mid_xx, mid_yy, writer):

    video_writer = writer

    frame_cnt = zoom_time * frames_per_second
    img_width, img_height = img.size
    img_midx = mid_xx
    img_midy = mid_yy
    if mid_xx == -187 or mid_yy == -187:
        img_midx = img_width / 2
        img_midy = img_height / 2
    zoomx = img_width / zoom_strength
    zoomy = img_height / zoom_strength
    xstep = (img_width / 2 - zoomx/2) / frame_cnt
    ystep = (img_height / 2 - zoomy/2) / frame_cnt
    middiffx = ((img_midx - (img_width / 2)) / frame_cnt)
    middiffy = ((img_midy - (img_height / 2)) / frame_cnt)

    x1, x2, y1, y2 = 0, 0, 0, 0

    size = tuple((res_x, res_y))

    if not reverse:
        x1 = 0
        y1 = 0
        x2 = img_width
        y2 = img_height
    else:
        x1 = img_midx - zoomx/2
        y1 = img_midy - zoomy/2
        x2 = img_midx + zoomx/2
        y2 = img_midy + zoomy/2

    if preview > 0:
        frame = img.crop((x1, y1, x2, y2))
        frame_bytes = get_bytes_from_image(frame.resize(size))
        for i in range(0, frames_per_second * preview):
            video_writer.write(cv2.cvtColor(np.array(frame_bytes), cv2.COLOR_RGB2BGR))

    for i in range(0, frame_cnt, 1):

        frame = img.crop((x1, y1, x2, y2))
        frame_bytes = get_bytes_from_image(frame.resize(size))
        video_writer.write(cv2.cvtColor(np.array(frame_bytes), cv2.COLOR_RGB2BGR))

        if not reverse:
            factor = (frame_cnt * 1.75 - (i)*1.5) / frame_cnt + 1 / (frame_cnt)
            x1 += int((xstep + middiffx) * factor)
            y1 += int((ystep + middiffy) * factor)
            x2 -= int((xstep - middiffx) * factor)
            y2 -= int((ystep - middiffy) * factor)
        else:
            factor = (frame_cnt / 4 + (i)*1.5) / frame_cnt + 1 / (frame_cnt)
            x1 -= int((xstep + middiffx) * factor)
            y1 -= int((ystep + middiffy) * factor)
            x2 += int((xstep - middiffx) * factor)
            y2 += int((ystep - middiffy) * factor)

        print_progress_bar(i, frame_cnt, length=50, prefix="Cropping/Resizing images:\t")

    if preview > 0:
        frame = img.crop((x1, y1, x2, y2))
        frame_bytes = get_bytes_from_image(frame.resize(size, Image.ANTIALIAS))
        for i in range(0, frames_per_second * preview):
            video_writer.write(cv2.cvtColor(np.array(frame_bytes), cv2.COLOR_RGB2BGR))

    print_progress_bar(frame_cnt, frame_cnt, length=50, prefix="Cropping/Resizing images:\t")

    cv2.destroyAllWindows()
    return video_writer


if __name__ == "__main__":
    warnings.filterwarnings("ignore")

    parser = argparse.ArgumentParser()
    parser.add_argument("--img", help="File-Name of the image to be created out of Images", type=str, required=True)
    parser.add_argument("--fps", help="GIF Framerate. Default is 24", type=int, default=24)
    parser.add_argument("--ztime", help="Length of zoom in seconds. Default is 5", type=int, default=5)
    parser.add_argument("--zoom", help="Zoom stregth. Aquivalent to scale. Default is 20", type=int, default=20)
    parser.add_argument("--resx", help="The resolution in width. Default is 1000", type=int, default=1000)
    parser.add_argument("--resy", help="The resolution in height. Default is 1000", type=int, default=1000)
    parser.add_argument("--midx", help="Select x value of the center point. Default is the middle of the width",
                        type=int, default=-187)
    parser.add_argument("--midy", help="Select x value of the center point. Default is the middle of the height",
                        type=int, default=-187)
    parser.add_argument("--prev", help="Add preview before and after. Default is 0 seconds", type=int)
    parser.add_argument("--zrev", help="Determines if zooming should be reversed. Default is False", type=str2bool)
    parser.add_argument("--out",
                        help="Output directory for the final image. Default is the directory from the image (If your Path contains spaces, put it inside quotes: \"../my path/foo/\")",
                        action=ReadableDir)

    zrev = False
    prev = 0

    args = parser.parse_args()

    fps = int(args.fps)
    resx = int(args.resx)
    resy = int(args.resy)
    midx = int(args.midx)
    midy = int(args.midy)
    ztime = int(args.ztime)
    zoom = int(args.zoom)

    if not (midx == -187 and midy == -187):
        if midy < 1 or midx < 1:
            raise Exception('--midx and --midy has to be greater that zero')

    image_name = str(args.img)
    if not isfile(image_name):
        raise argparse.ArgumentTypeError("\"" + str(image_name) + "\" is not a valid file")

    if args.zrev != None:
        zrev = bool(args.zrev)

    if args.prev != None:
        prev = args.prev
        if prev < 0:
            prev = 0

    image = get_image(image_name)

    mp4_path = ''
    out_path = ''
    format = '.mp4'
    cnt = 0

    out_path = image_name
    if '/' in out_path:
        out_path = '/'.join(image_name.split('/')[:-1]) + '/'
        image_name = image_name.split('/')[-1]
    elif '\\' in out_path:
        out_path = '\\'.join(image_name.split('\\')[:-1]) + '\\'
        image_name = image_name.split('\\')[-1]

    if args.out != None:
        out_path = str(args.out)
        if '/' in out_path:
            if not out_path.endswith('/'):
                out_path += '/'
        elif '\\' in out_path:
            if not out_path.endswith('\\'):
                out_path += '\\'

    mp4_path = out_path + '.'.join(image_name.replace('mapped','zoom').split('.')[:-1]) + str(cnt) + '.mp4'

    while (('.'.join(image_name.replace('mapped','zoom').split('.')[:-1]) + str(cnt) + '.mp4').lower() in [x.lower() for x in os.listdir(out_path)]):
        cnt += 1
        mp4_path = out_path + '.'.join(image_name.replace('mapped','zoom').split('.')[:-1]) + str(cnt) + '.mp4'




    fourcc = cv2.VideoWriter_fourcc(*'avc1')

    generate_video(image, fps, ztime, zoom, resx, resy, zrev, prev, midx, midy, cv2.VideoWriter(mp4_path, fourcc, fps, (resx, resy))).release()

