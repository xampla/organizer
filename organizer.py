import hashlib
import os
import shutil
import exiftool
from tqdm import tqdm
import datetime
from PIL import Image
import json
import argparse


def getMD5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def removeExif(file):
    with exiftool.ExifTool() as et:
        res = et.execute(os.fsencode("-all="), os.fsencode(file))

def detectFileType(path):
    photo_type = [".jpg",".png",".jpeg",".bmp"]
    other_media_type = [".flv",".f4v",".f4p",".f4a",".f4b",".3g2",".3gp",".m4v", \
    ".mpg",".mpeg",".m2v",".mp4",".m4v",".amv",".wmv",".mov",".qt",".avi",".ogv", \
    ".ogg",".flv",".mkv",".webm",".cda",".8svx",".wma",".wav",".tta",".rf64",".raw", \
    ".opus",".mogg",".oga",".nmf",".msv",".mpc",".mp3",".m4p",".m4b",".m4a",".flac", \
    ".dvf",".dss",".dct",".awb",".au",".ape",".amr",".alac",".aiff",".act",".aax",".aac",".aa",".3gp"]
    if path.lower().endswith(tuple(photo_type)):
        try:
            im = Image.open(path)
            width, height = im.size
            im.close()
            ratio = width/height
            if ratio<1:
                ratio = height/width

        except:
            failed_file = open("failed.txt","a+")
            failed_file.write("Unexpected error with file: " + path + "\r\n")
            ratio = 0

        if 1.3 <= ratio <= 1.4:
            return "camera/"
        elif 1.6 <= ratio <= 2.3:
            return "screenshots/"
        else:
            return "memes/"
    elif path.lower().endswith(tuple(other_media_type)):
        return "more_media/"
    else:
        return "others/"

def createDestFolders(path):
    os.mkdir(path+'camera')
    os.mkdir(path+'more_media')
    os.mkdir(path+'screenshots')
    os.mkdir(path+'memes')
    os.mkdir(path+'others')
    os.mkdir(path+'tmp')

def safeState(files_hashes,files_duplicates,file_path):
    with open('hash.json', 'w+') as fp:
        json.dump(files_hashes, fp, indent=4)
    with open('duplicates.json', 'w+') as fp:
        json.dump(files_duplicates, fp, indent=4)
    with open("status.txt", "w+") as status:
        status.write(file_path)

def main():

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description='Sort files into media, screenshots, memes and others, while deleting duplicates.')
    parser.add_argument('src_dir', type=str, help='Source directory')
    parser.add_argument('dest_dir', type=str, help='Destination directory (it MUST be empty)')
    parser.add_argument('-r', '--recursive', action='store_true', help='Search src_dir recursively')
    parser.add_argument('-n', '--new', action='store_true', help='If status.txt exists from a previous failed execution, force to start over again.')

    args = parser.parse_args()

    files_hashes = {}
    files_duplicates = {}
    source_dir = args.src_dir
    dest_dir = args.dest_dir
    tmp_dir = dest_dir+"tmp/"

    num_files = len([file for file in os.listdir(source_dir)
                                if os.path.isfile(os.path.join(source_dir, file))])
    if args.recursive:
        num_files = sum([len(files) for r, d, files in os.walk(source_dir)])

    last_file = ""
    recovery = False
    if not args.new and os.path.isfile('status.txt'):
        with open("status.txt","r") as s:
            recovery = True
            last_file = s.readline()
            with open("hash.json") as h:
                files_hashes = json.load(h)

    if not recovery:
        createDestFolders(dest_dir)
        if os.path.isfile('hash.json'):
            os.remove('hash.json')
        if os.path.isfile('duplicates.json'):
            os.remove('duplicates.json')

    with tqdm(total=num_files) as pbar:
        current = not recovery
        for currentpath, folders, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(currentpath, file)
                if (recovery and file_path == last_file) or current:
                    current = True
                    if not file.startswith('.'):
                        tmp_path = tmp_dir+file
                        shutil.copy(file_path, tmp_path)
                        removeExif(tmp_path)
                        hash = getMD5(tmp_path)
                        if hash not in files_hashes:
                            files_hashes[hash] = file_path
                            file_type = detectFileType(file_path)
                            if not os.path.exists(dest_dir+file_type+file):
                                final_path = dest_dir+file_type+file
                                shutil.copy2(file_path, final_path)
                            else:
                                now = str(str(datetime.datetime.now())[:19].replace(":","_"))
                                base, extension = os.path.splitext(file)
                                shutil.copy2(file_path, dest_dir+file_type+base+now+extension)
                        else:
                            original_path = files_hashes[hash]
                            if original_path in files_duplicates:
                                files_duplicates[original_path].append(file_path)
                            else:
                                files_duplicates[original_path] = [file_path]
                        safeState(files_hashes,files_duplicates,file_path)
                        shutil.rmtree(tmp_dir)
                        os.mkdir(tmp_dir)

                pbar.update(1)
            if not args.recursive:
                break
    shutil.rmtree(tmp_dir)
    os.remove("status.txt")


main()
