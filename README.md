# ORGANIZER

This script *copies* files from the source folder to the destination one. It *removes* duplicates and organize the files in 5 different folders (based by the extension and aspect ratio, if needed): camera, memes, more_media, screenshots and others. To check the equality of 2 files it deletes the metadata and perform a md5 hash which stores it to make later checks.

## Getting Started

These instructions will help you to set up the environment to be able to run the script.

### Prerequisites

You will need python3 and as this script is using the ExifTool, it is necessary to be installed in you computer.
You can download it from the oficial website and follow the instructions based on you OS: 
https://exiftool.org/

### Installing

Once you have the prerequisites, you will need to install the requirements.

```
pip install -r requirements.txt
```

**Note** that if you are using Windows 10 you may need to replace the contents of `C:\Users\xavi\AppData\Local\Programs\Python\Python38-32\Lib\site-packages\exiftool` to the code from here:
https://raw.githubusercontent.com/smarnach/pyexiftool/8738ae963afc784fcef76de6bcebf277a58379ab/exiftool.py

## Running the script
When executing the script 3 files will be created: 
- hash.json: it contains the files and their corresponding hash.
- duplicates.json: it has file paths with the duplicate files, if any. If you are not sure the script has done its job well you can check which files has discard.
- status.txt: if something goes wrong this file avoids to have to start the whole process again. If the script ends correctly it will be deleted.

```
python3 organizer.py [-h] [-r] [-n] src_dir dest_dir

positional arguments:
  src_dir          Source directory
  dest_dir         Destination directory

optional arguments:
  -h, --help       Show this help message and exit
  -r, --recursive  Search src_dir recursively
  -n, --new        If status.txt exists from a previous failed execution, force to start over again.
```



## Authors

* **Xavier Marrugat** 
