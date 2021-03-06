from django import VERSION
from django.http import Http404
from django.http import HttpResponse
from django.http import QueryDict
from django.template import RequestContext
from django.shortcuts import redirect, get_object_or_404
from django.db import connection
from django.db.models import Count, Avg, Sum, Q
from django.core.exceptions import ValidationError
# from django.utils.timezone import utc
# from django.contrib.auth import logout, authenticate, login as auth_login

from museum_site.models import *
from museum_site.constants import *
from datetime import datetime
from io import BytesIO
from random import randint, shuffle, seed
from time import time
import glob
import math
import os
import re
import subprocess
import sys
import urllib.parse
import zipfile

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_PATH = os.path.join(SITE_ROOT, "temp")
BASE_PATH = os.path.join(SITE_ROOT, "museum_site", "static", "data", "base")
STATIC_PATH = os.path.join(SITE_ROOT, "museum_site", "static")
CSS_INCLUDES = ["grid.css", "zzt.css", "low-res.css"]
TRACKING = True  # Analytics
DEBUG = True if os.path.isfile("/var/projects/DEV") else False
PAGE_SIZE = 25
LIST_PAGE_SIZE = 300
UPLOADS_ENABLED = True
UPLOAD_CAP = 1048576  # 1 Megabyte
YEAR = datetime.now().year
PYTHON_VERSION = sys.version
DJANGO_VERSION = VERSION
START_TIME = datetime.utcnow()
BOOT_TS = START_TIME.strftime("%m%d%H%M%S")
ARCHIVE_COLLECTION = "open_source_software" if not DEBUG else "test_collection"

FILE_VIEWER_TEXT_EXTENSIONS = (
    "", ".doc", ".txt", ".bat", ".cfg", ".nfo", ".dat", ".bas", ".deu", ".diz",
    ".c", ".ds_store", ".faq", ".frm", ".fyi", ".gud", ".h", ".hlp", ".lst",
    ".me", ".nfo", ".pas", ".reg", ".sol", ".zln", ".zml", ".zzl", ".zzm",
    ".135", ".1st", ".asm", ".bb", ".bin", ".chr", ".sdi", ".now", ".md",
    ".wri",
)
FILE_VIEWER_HEX_EXTENSIONS = (
    ".hi", ".zzt", ".brd", ".mh", ".sav", ".szt", ".mwz"
)

FILE_VIEWER_B64_EXTENSIONS = (
    ".jpg", ".jpeg", ".bmp", ".gif", ".png", ".ico", ".avi"
)

FILE_VIEWER_AUDIO_EXTENSIONS = (
    ".wav", ".mp3", ".ogg", ".mid", ".midi"
)

EMAIL_ADDRESS = "doctordos@gmail.com"

LETTERS = (
    "1", "a", "b", "c", "d", "e", "f", "g", "h",
    "i", "j", "k", "l", "m", "n", "o", "p", "q",
    "r", "s", "t", "u", "v", "w", "x", "y", "z"
)

DETAIL_LIST = (
    "Contest"
    "Etc."
    "Featured Game"
    "Modified Graphics"
    "Linux Compatible Program"
    "Modified Executable"
    "MS-DOS Compatible Program"
    "OSX Compatible"
    "Super ZZT World"
    "Utility"
    "Windows 16-bit"
    "Windows 32-bit"
    "Windows 64-bit"
    "ZZT World"
    "ZZM Audio"
    "ZIG World"
)

GENRE_LIST = (
    "24HoZZT", "Action", "Adventure", "Advertisement", "Arcade", "Art",
    "Beta", "BKZZT", "Bugfix", "Cameo", "Catalog", "Cinema", "Comedy", "Comic",
    "Compilation", "Contest", "Demo", "Dungeon", "Edutainment", "Engine",
    "Experimental", "Explicit", "Fangame", "Fantasy", "Fighting", "Font",
    "Help", "Horror", "Incomplete", "Ludum Dare", "Magazine", "Maze",
    "Minigame", "Multiplayer", "Music", "Mystery", "Non-English", "Official",
    "Other", "Parody", "Platformer", "Puzzle", "Racing", "Random", "Remake",
    "Registered", "Retro", "RPG", "Sci-Fi", "Shareware", "Shooter",
    "Simulation", "Space", "Sports", "Story", "Strategy", "Toolkit",
    "Trippy", "Trivia", "Update", "Utility", "WoZZT"
)

SORT_CODES = {
    "title": ["sort_title"],
    "author": ["author", "sort_title"],
    "company": ["company", "sort_title"],
    "id": ["-id"],
    "rating": ["-rating", "sort_title"],
    "release": ["release_date", "sort_title"],
    "published": ["-publish_date", "-id"],
    "roulette": ["?"],
    "uploaded": ["-upload_date", "-id"],
}

ADV_SEARCH_DEFAULTS = [
    str(DETAIL_ZZT),
    str(DETAIL_SZZT),
    str(DETAIL_UTILITY),
]

PACKAGE_PROFILES = (
    {
        "name": "ZZT v3.2 Registered",
        "directory": "ZZT32-REG",
        "use_cfg": True,
        "registered": True,
        "prefix": "zzt_",
        "executable": "ZZT.EXE",
        "engine": "ZZT",
        "auto_desc": "World created using the ZZT engine.",
    },
    {
        "name": "Super ZZT Registered",
        "directory": "SZZT-REG",
        "use_cfg": False,
        "registered": True,
        "prefix": "superzzt_",
        "executable": "SUPERZ.EXE",
        "engine": "Super ZZT",
        "auto_desc": "World created using the Super ZZT engine.",
    },
    {
        "name": "CleanZZT",
        "directory": "CLEANZZT",
        "use_cfg": True,
        "registered": True,
        "prefix": "cleanzzt_",
        "executable": "CLEANZZT.EXE",
        "engine": "ZZT",
        "auto_desc": "World created using the ZZT engine, and running under Clean ZZT, a customized ZZT executable that removes certain default sound effects and messages",
    },
    {
        "name": "Super ZZT v4.0",
        "directory": "SZZT40",
        "use_cfg": False,
        "registered": True,
        "prefix": "superzzt40_",
        "executable": "s.bat",
        "engine": "Super ZZT",
        "auto_desc": "World created using the Super ZZT engine, and running under Super ZZT 4.0, a customized Super ZZT executable to increase certain memory limitations",
    },
    {
        "name": "ZZT v2.0 Shareware",
        "directory": "ZZT20-SW",
        "use_cfg": True,
        "registered": False,
        "prefix": "zzt20sw_",
        "executable": "ZZT.EXE",
        "engine": "ZZT",
        "auto_desc": "World created using the ZZT engine, and running under ZZT 2.0 Shareware edition.",
    },
    {
        "name": "ZZT v3.1 Shareware",
        "directory": "ZZT31-SW",
        "use_cfg": True,
        "registered": False,
        "prefix": "zzt31sw_",
        "executable": "ZZT.EXE",
        "engine": "ZZT",
        "auto_desc": "World created using the ZZT engine, and running under ZZT 3.1 Shareware edition.",
    },
    {
        "name": "ZZT v3.2 Shareware",
        "directory": "ZZT32-SW",
        "use_cfg": True,
        "registered": False,
        "prefix": "zztsw_",
        "executable": "ZZT.EXE",
        "engine": "ZZT",
        "auto_desc": "World created using the ZZT engine, and running under ZZT 3.2 Shareware edition.",
    },
    {
        "name": "ZZT v4.0",
        "directory": "ZZT40",
        "use_cfg": True,
        "registered": True,
        "prefix": "zzt40_",
        "executable": "zzt.EXE",
        "engine": "ZZT",
        "auto_desc": "World created using the ZZT engine, and running under ZZT 4.0, a customized ZZT executable to increase certain memory limitations and fix bugs with the original program.",
    },
    {
        "name": "ZZT v4.0 - No MSG",
        "directory": "ZZT40",
        "use_cfg": True,
        "registered": True,
        "prefix": "zzt40nomsg_",
        "executable": "zztnomsg.EXE",
        "engine": "ZZT",
        "auto_desc": "World created using the ZZT engine, and running under ZZT 4.0 No MSG, a customized ZZT executable to increase certain memory limitations, fix bugs with the original program, and remove certain default sounds and messages.",
    },
    {
        "name": "ZZT v4.1",
        "directory": "ZZT41",
        "use_cfg": True,
        "registered": True,
        "prefix": "zzt41_",
        "executable": "zzt41.exe",
        "engine": "ZZT",
        "auto_desc": "World created using the ZZT engine, and running under ZZT 4.1 No MSG, a customized ZZT executable to increase certain memory limitations, fix bugs with the original program, and remove certain default sounds and messages.",
    },
    {
        "name": "ZZT Music Player v2.0",
        "directory": "ZZTMP20",
        "prefix": "zztmp20_",
        "executable": "ZZTMPLAY.EXE",
        "engine": "ZZM",
        "auto_desc": "ZZM files being played using ZZT Music Player v2.0, a program to play ZZM music, a format designed to play ZZT's PC speaker sounds in a more traditional audio player. Note that ZZM files do not sound identical to the same sounds produced in ZZT. (If both formats are available, ZZT is the superior choice for playback accuracy.)",
    }
)

PLAY_METHODS = {
    "archive": {"name":"Archive.org - DosBox Embed"},
    "zeta": {"name":"Zeta"},
}

def populate_collection_params(data):
    params = "?"
    keys = ["mode", "rng_seed", "author", "year", "genre", "company", "letter", "page", "sort"]
    for k in keys:
        if data.get(k):
            params += k + "=" + str(data[k]) + "&"
    params = params[:-1]
    return params


def get_view_format(request):
    """ Returns Detailed/List/Gallery based on selected View type """
    if request.GET.get("view"):
        return request.GET["view"]
    elif request.COOKIES.get("view"):
        return request.COOKIES["view"]
    else:
        return "detailed"


def qs_sans(params, key):
    """ Returns a query string with a key removed """
    qs = params.copy()

    if key in qs:
        qs_nokey = qs.copy()
        qs_nokey.pop(key)
    else:
        qs_nokey = qs

    return qs_nokey.urlencode()


def serve_file(file_path="", named=""):
    """ Returns an HTTPResponse containing the given file with an optional name """
    if not named:
        named = os.path.basename(file_path)

    if not os.path.isfile(file_path):
        raise Http404("Source file not found")

    response = HttpResponse(content_type="application/octet-stream")
    response["Content-Disposition"] = "attachment; filename={}".format(named)
    with open(file_path, "rb") as fh:
        response.write(fh.read())
    return response


def slash_separated_sort(orig):
    temp_list = orig.split("/")
    temp_list.sort()
    output = "/".join(temp_list)
    return output

def env_from_host(host):
    if host in ["beta.museumofzzt.com"]:
        return "BETA"
    elif host in ["museumofzzt.com"]:
        return "PROD"
    else:
        return "DEV"


def set_captcha_seed(request):
    request.session["captcha-seed"] = str(datetime.now()).replace("-", "").replace(":", "").replace(".", "").replace(" ", "")


# Decorators
def dev_only(func, *args, **kwargs):
    def inner(*args, **kwargs):
        request = kwargs.get("request", args[0])

        # Check host
        host = request.get_host()
        if env_from_host(host) != "DEV":
            raise Http404
        else:
            return func(*args, **kwargs)
    return inner


def non_production(func, *args, **kwargs):
    def inner(*args, **kwargs):
        request = kwargs.get("request", args[0])

        # Check host
        host = request.get_host()
        if env_from_host(host) not in ["DEV", "BETA"]:
            raise Http404
        else:
            return func(*args, **kwargs)
    return inner


def prod_only(func, *args, **kwargs):
    def inner(*args, **kwargs):
        request = kwargs.get("request", args[0])

        # Check host
        host = request.get_host()
        if env_from_host(host) != "PROD":
            raise Http404
        else:
            return func(*args, **kwargs)
    return inner
