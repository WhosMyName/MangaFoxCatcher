"""Script to Download Mangas from MangaFox"""

import os
import subprocess
import multiprocessing
import threading
import tempfile
import time
import requests

#SEARCH FOR # TO FIND ALL COMMENTS

CURRTHREADS = multiprocessing.Value("i", 0)
LIMIT = 5
HEADERS = requests.utils.default_headers()
HEADERS.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",})

if os.name == "nt":
    SLASH = "\\"
else:
    SLASH = "/"

def get_file(srcfile, srcurl, counter=0, ftype=0):#ftype indicates if picture or not
    """Function to Downloadad and verify downloaded Files"""
    time.sleep(5)
    if not os.path.isfile(srcfile):
        print("Downloading", srcurl, "as", srcfile)
        counter = counter + 1
        with open(srcfile, "wb") as fifo:#open in binary write mode
            response = requests.get(srcurl, headers=HEADERS)#get request
            fifo.write(response.content)#write to file
        if int(str(os.path.getsize(srcfile)).strip("L")) < 1000000 and ftype: #Assumes Error in Download and redownlads File
            print("Redownloading", srcurl, "as", srcfile)
            autocleanse(srcfile)
            return get_file(srcfile, srcurl, counter)
        else: #Assume correct Filedownload
            return 0
    else:
        if int(str(os.path.getsize(srcfile)).strip("L")) < 1000000 and ftype: #Assumes Error in Download and redownlads File
            print(srcfile, "was already downloaded but the filesize does not seem to fit -> Redownl0ading")
            autocleanse(srcfile)
            return get_file(srcfile, srcurl, 0)
        else: #Assume correct Filedownload
            return 0

def autocleanse(cleansefile):
    """ Function for safer deleting of files """
    if os.path.exists(cleansefile):
        os.remove(cleansefile)
        return
    else:
        print("File", cleansefile, "not deleted, due to File not existing")
        return

def init_preps():
    """Function to initiate the Download Process"""
    cwd = os.path.dirname(os.path.realpath(__file__)) + SLASH
    os.chdir(cwd)
    print("Recommended URL-Format would be: http://mangafox.me/manga/the_gentleman_s_armchair/\n")
    inputurl = str(input("Please enter the URL of the Manga you want to download: "))
    #inputurl = "http://mangafox.me/manga/the_gentleman_s_armchair/"
    firstvolume = int(float(input("Please enter the Number of the first Volume you want: ") or "1"))
    lastvolume = int(float(input("Please enter the Number of the last Volume you want: ") or "1"))

    indexfile = cwd + "indexfile.html"
    manganame = inputurl.split("/")[4].replace("_s_", "s_").replace("_", " ").title()
    mangadir = cwd + manganame + SLASH
    chapterlist = []
    volumelist = [] 
    involume = False
    if not os.path.exists(mangadir):
        os.mkdir(mangadir)

    get_file(indexfile, inputurl)
    with open(indexfile, "r") as inde:
        for line in inde:
            line = str(line)
            if "<h3 class=\"volume\">Volume" in line:
                print("Found a Volume")
                volume = str(line.split("<h3 class=\"volume\">Volume")[1].split("<span>")[0].replace(" 0", " ").replace(" ", ""))
                involume = True
                print(volume)
                voldir = mangadir + volume + SLASH
                print("Created Volumefolder")
            if "<a href=" in line and "title=" in line and involume:
                print("Found a Chapter")
                chapternum = line.split("class=\"tips\">")[1].split("</a>")[0]
                chapternum = chapternum.split(" ")[len(chapternum.split(" ")) - 1]
                chapterlink = line.split("<a href=\"")[1].split("\"")[0]
                print(chapterlink)
                chapterlist.append([chapterlink, chapternum])
                print("It was Chapter", chapternum)
            if "</ul>" in line and involume:
                print("Lets do this")
                volumelist.append([volume, chapterlist, voldir])
                chapterlist = []
                involume = False

    autocleanse(indexfile)
    if len(volumelist) == 1:
        if not os.path.exists(volumelist[0][2]):
                    os.mkdir(volumelist[0][2])
        retrieve_chapter(volumelist[0][1], volumelist[0][2], CURRTHREADS)
        return
    else:
        volumelist.reverse()
        for volume in volumelist:
            volume[0] = int(volume[0])
            print(volume[0])
            if volume[0] >= firstvolume and volume[0] <= lastvolume:
                voldir = mangadir + "Volume " + str(volume[0]) + SLASH
                if not os.path.exists(voldir):
                    os.mkdir(voldir)
                CURRTHREADS.value = CURRTHREADS.value + 1
                print("Chapterlist:", volume[1])
                print("Voldir:", voldir)
                worker = multiprocessing.Process(target=retrieve_chapter, args=(volume[1], voldir, CURRTHREADS), daemon=False)
                worker.start()
                time.sleep(5)
                while CURRTHREADS.value == LIMIT:
                    time.sleep(1)
    return

def retrieve_chapter(chapterlist, voldir, CURRTHREADS):
    print("Yo, Process Nr.", CURRTHREADS.value, "here")
    imglist = []
    chapterlist.reverse()
    for chapter in chapterlist:
        chapterdir = voldir + "Chapter " + str(chapter[1]) + SLASH
        if not os.path.exists(chapterdir):
                os.mkdir(chapterdir)
        chapterfile = chapterdir + str(chapter[1]) + ".html"
        get_file(chapterfile,chapter[0])
        maxpages = 0
        with open(chapterfile, "r") as chap:
            for line in chap:
                if "<option value=\"" in line:
                    options = line.split(" >")
                    for option in options:
                        option = option.split("</")[0]
                        if not "Comments" in option and not "selected" in option:
                            option = int(option)
                            if option > maxpages:
                                maxpages = option
        
        srcurl = chapter[0].split("1.html")[0]
        for x in range(1, maxpages):
            time.sleep(1)
            pageurl = srcurl + str(x) + ".html"
            pagefile = chapterdir + str(x) + ".html"
            get_file(pagefile, pageurl)
            imgbool = False
            with open(pagefile, "r") as pgf:
                for line in pgf:
                    if "read_img" in line:
                        imgbool = True
                    if "<img src=\"" in line and "id=\"image\" alt=\"" in line and imgbool:
                        imgurl = line.split("\"")[1]
                        print(imgurl)
                        imgfile = chapterdir + "Page " + str(x) + ".jpg"
                        get_file(imgfile, imgurl)

            autocleanse(pagefile)
            pageurl = ""
            pagefile = ""
        autocleanse(chapterfile)
    return



def main():
    """MAIN"""
    os.umask(0)
    init_preps()
main()