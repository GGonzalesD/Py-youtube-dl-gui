#!/usr/bin/python
import youtube_dl, sys, os
import urllib
from urllib import request
from PIL import Image as PIL_Image
from pathlib import Path
import threading, time

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
#import pyperclip2
#from gi.repository import GObject

DIRWORK = os.getcwd()
print(DIRWORK)
URL = "."
INFO = {}
FORM = "mp4"
PROG = 0

def GetPercent(d):
    global PROG
    if d["status"] == "finished":
        PROG = 1

    if d["status"] == "downloading":
        PROG = float(d["_percent_str"].replace("%","").replace(" ","")) / 100
    
    builder.get_object("LabProg").set_text(f"{int(PROG*100)}%")
    builder.get_object("BarProg").set_fraction(PROG)

def OnOff(boolean):
    builder.get_object("BtnPaste").set_sensitive(boolean)
    builder.get_object("EntryDownload").set_sensitive(boolean)
    builder.get_object("BtnDownload").set_sensitive(boolean)
    builder.get_object("EntName").set_sensitive(boolean)
    builder.get_object("Crl1").set_sensitive(boolean)
    builder.get_object("Crl2").set_sensitive(boolean)
    builder.get_object("Crl3").set_sensitive(boolean)


def downloadImage(url):
    name = DIRWORK + "/.py_download.jpg"

    with open(name,"wb") as f: # Descargar Imagen
        f.write(request.urlopen(url).read())

    img = PIL_Image.open(name)
    new_img = img.resize((200,120))
    new_img.save(name,'png')

    return name

def getInfo(v_):
    with youtube_dl.YoutubeDL() as ydl:
        try:
            info_dict = ydl.extract_info(v_, download=False)
        except youtube_dl.utils.DownloadError:
            return None
        return dict(info_dict)

def Download(v_,name,mode):
    OnOff(False)
    if mode == "mp3":
        outtmpl = name + '.%(ext)s'
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': outtmpl,
            'progress_hooks':[GetPercent],
            'postprocessors': [
                {'key': 'FFmpegExtractAudio','preferredcodec': 'mp3',
                'preferredquality': '192',
                },
                {'key': 'FFmpegMetadata'},
            ],
        }
    if mode == "mp4":
        outtmpl = name + '.%(ext)s'
        ydl_opts = {
            "format":"mp4",
            'outtmpl': outtmpl
        }
    if mode == "max":
        outtmpl = name + '.%(ext)s'
        ydl_opts = {
            "format":"bestvideo/best",
            'outtmpl': outtmpl
        }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            a = builder.get_object("EntDir").get_filename()
            os.chdir(str(Path.home()) + "/Desktop" if a == None else a)
            info_dict = ydl.extract_info(v_, download=True)
        except youtube_dl.utils.DownloadError:
            OnOff(True)
        OnOff(True)
        time.sleep(1)
        Gtk.main_quit()
        sys.exit()

    

# D = getInfo(video)
# Image = D["thumbnail"]
# downloadImage(Image)


builder = Gtk.Builder()
builder.add_from_file(DIRWORK + "/.glade_download.glade")

EntUrl = builder.get_object("EntryDownload")
EntName = builder.get_object("EntName")
ImgLogo = builder.get_object("ImgLogo")
LabExt = builder.get_object("LabExt")

def _SelectMp3(*argv):
    global FORM
    FORM = "mp3"
    LabExt.set_text(FORM)
def _SelectMp4(*argv):
    global FORM
    FORM = "mp4"
    LabExt.set_text(FORM)
def _SelectMax(*argv):
    global FORM
    FORM = "max"
    LabExt.set_text(FORM)

def _onDestroy(*argv):
    Gtk.main_quit()
    sys.exit()

def _ActionPaste(*argv):
    pass


def _ActionPasteBtn(*argv,**kargv):
    global INFO, URL

    if (not "Replace" in kargv) | ("Replace" in kargv and kargv["Replace"]==True):
        print(":: Consultando...")
        URL = EntUrl.get_text()
        OnOff(False)
        INFO = getInfo(URL)
        print(":: Consultado")

        EntName.set_text(INFO["title"])
        print(":: Obteniendo Miniatura")
        ImgLogo.set_from_file(downloadImage(INFO["thumbnail"]))
        print(":: Miniatura obtenida")
        OnOff(True)
    else:
        print(":: No Consultado")

def _ActionDownload(*argv):
    print(":: Preparando Consulta")
    _ActionPasteBtn(Replace=((URL == ".") or (URL != EntUrl.get_text())))
    print(":: Preparando Descarga...")
    A = threading.Thread(target=Download, args=(EntUrl.get_text(), EntName.get_text(),FORM))
    A.start()


Handle = {
    "onDestroy": _onDestroy,
    "Action-Download": _ActionDownload,
    "Action-Paste": _ActionPaste,
    "Action-Paste-Btn": _ActionPasteBtn,
    "Select-Mp3": _SelectMp3,
    "Select-Mp4": _SelectMp4,
    "Select-Max": _SelectMax
}

builder.connect_signals(Handle)

window = builder.get_object("Main")
window.show_all()


Gtk.main()
