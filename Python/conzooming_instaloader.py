import argparse
import instaloader
import datetime
import os

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", help="username", type=str, required=True)
    parser.add_argument("--dir",    help="Directory Path where folder with images should be created (If your Path contains spaces, put it inside quotes: \"../my path/foo/\")", action=readable_dir, required=True)
    parser.add_argument("--max", help="(Integer)  Count of images, that shuld be downloaded. Default is 200", type=int)


    args = parser.parse_args()
    user = args.user
    folder_path = str(args.dir)

    L = instaloader.Instaloader()

    posts=""
    try:
        print("Downloading images..")
        posts = [x for x in instaloader.Profile.from_username(context=L.context, username=user).get_posts()]
    except:
        raise Exception("User does not exist")

    max = len(posts)

    if max < 1:
        raise Exception('User is private or has no posts')


    if max > 200:
        max = 200

    if args.max != None:
        if args.max < 1:
            max = 1
        else:
            max = args.max


    if '/' in folder_path:
        if not folder_path.endswith('/'):
            folder_path += '/'
    elif '\\' in folder_path:
        if not folder_path.endswith('\\'):
            folder_path += '\\'


    folder_path += user + ''

    try:
        os.mkdir(folder_path)
    except OSError:
        raise Exception("Creation of the directory %s failed" % folder_path)



    if '/' in folder_path:
        if not folder_path.endswith('/'):
            folder_path += '/'
    elif '\\' in folder_path:
        if not folder_path.endswith('\\'):
            folder_path += '\\'


    cnt = 1
    for post in posts:
        if not post.is_video:
            L.download_pic(filename=folder_path+str(cnt)+user, url=post.url, mtime=datetime.datetime.now())
            cnt +=1
        if cnt == max+1:
            break

    print("Done")