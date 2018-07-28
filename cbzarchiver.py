import os
import sys
import shutil

if os.name == "nt":
    SLASH = "\\"
else:
    SLASH = "/"

CWD = os.path.dirname(os.path.realpath(__file__)) + SLASH
os.chdir(CWD)

def list_folder():

    for directory in os.scandir(CWD):
        if os.path.isdir(directory):
            if not ".git" in str(directory) and not "pycache" in str(directory): 
                print(directory)
                makecbz(directory)
        os.chdir(CWD)

def makecbz(folder):
    folder = os.path.abspath(os.path.join(folder,  ""))
    print(os.path.exists(folder))
    os.chdir(folder)
    for directory in os.scandir(folder):
        if directory.is_dir():
            zipname = os.path.basename(os.path.abspath(directory.path))
            print(zipname)
            shutil.make_archive(zipname, 'zip', directory.path)
            zipname = zipname + ".zip"
            os.rename(zipname, zipname.replace(".zip", ".cbz"))
            #try cbz subfolders(chapters), create zip folder with all cbz files and then cbz everything

def __main__():
    list_folder()

if __name__ == "__main__":
    __main__()