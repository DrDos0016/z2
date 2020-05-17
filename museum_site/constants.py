import glob
import os

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Patron Locked Content
try:
    from museum_site.patron_secrets import PASSWORD2DOLLARS, PASSWORD5DOLLARS
except ModuleNotFoundError:
    print("PATRON_SECRETS.PY NOT FOUND. USING DEV VALUES")
    PASSWORD2DOLLARS = "test2dollars"
    PASSWORD5DOLLARS = "test5dollars"

# Article publish states
PUBLISHED_ARTICLE = 1
UPCOMING_ARTICLE = 2
UNPUBLISHED_ARTICLE = 3
REMOVED_ARTICLE = 0

# File details
DETAIL_DOS = 1
DETAIL_WIN16 = 2
DETAIL_WIN32 = 3
DETAIL_WIN64 = 4
DETAIL_LINUX = 5
DETAIL_OSX = 6
DETAIL_FEATURED = 7
DETAIL_CONTEST = 8
DETAIL_ZZM = 9
DETAIL_GFX = 10
DETAIL_MOD = 11
DETAIL_ETC = 12
DETAIL_SZZT = 13
DETAIL_UTILITY = 14
DETAIL_ZZT = 15
DETAIL_ZIG = 16
DETAIL_LOST = 17
DETAIL_UPLOADED = 18
DETAIL_REMOVED = 19

# Front Page
FP_ARTICLES_SHOWN = 10
FP_FILES_SHOWN = 12
FP_REVIEWS_SHOWN = 10

# File categories
CATEGORY_LIST = (
    ("?", "?"),
    ("MS-DOS", "MS-DOS Programs"),
    ("WIN16", "16-Bit Windows Programs"),
    ("WIN32", "32-Bit Windows Programs"),
    ("WIN64", "64-Bit Windows Programs"),
    ("LINUX", "Linux Programs"),
    ("OSX", "OSX Programs"),
    ("FEATURED", "Featured Worlds"),
    ("UNUSED-8", "UNUSED Contest Entries"),
    ("ZZM", "ZZM Soundtracks"),
    ("GFX", "Modified Graphics"),
    ("MOD", "Modified Executables"),
    ("ETC", "Etc."),
    ("SZZT", "Super ZZT Worlds"),
    ("UTILITY", "Utilities"),
    ("ZZT", "ZZT Worlds"),
    ("ZIG", "ZIG Worlds"),
    ("LOST", "Lost Worlds"),
    ("UPLOADED", "Uploaded Worlds"),
    ("REMOVED", "Removed Worlds"),
)

# Character Sets
CHARSETS = [
    {
        "id": 0,
        "filename": "cp437.png",
        "name": "Code Page 437",
        "engine": "ZZT",
    },
    {
        "id": 0,
        "filename": "szzt-cp437.png",
        "name": "Code Page 437 (SZZT)",
        "engine": "SZZT",
    }
]
CUSTOM_CHARSETS = []

pngs = sorted(glob.glob(
    os.path.join(
        SITE_ROOT, "museum_site", "static", "images", "charsets", "*.png"
    )
))
for png in pngs:
    filename = os.path.basename(png)
    if filename.find("cp437") != -1:  # Skip non-custom fonts
        continue

    if filename.startswith("szzt"):
        charset_id = int(filename.split("-")[1])
    else:
        charset_id = int(filename.split("-")[0])

    name = filename.split("-")[-1][:-4]
    engine = "ZZT" if "szzt" not in filename else "SZZT"
    CUSTOM_CHARSETS.append({
        "id": charset_id,
        "filename": filename,
        "name": name,
        "engine": engine,
    })

CUSTOM_CHARSETS.sort(key=lambda charset: charset["name"].lower())

exe_names = {
    "szzt.zip": "Super ZZT v2.0 (Registered)",
    "wozzt356.zip": "Worlds of ZZT v3.56",
    "zzt.zip": "ZZT v3.2 (Registered)",
    "zzt20.zip": "ZZT v2.0",
    "zzt30.zip": "ZZT v3.0",
    "zzt31.zip": "ZZT v3.1",
    "zzt32sw.zip": "ZZT v3.2 (Shareware)",

}
ZETA_EXECUTABLES = []
exes = sorted(glob.glob(
    os.path.join(
        SITE_ROOT, "museum_site", "static", "data", "zeta86_engines", "*.zip"
    )
))
for exe in exes:
    filename = os.path.basename(exe)
    ZETA_EXECUTABLES.append({
        "filename": filename,
        "name": exe_names.get(filename, filename)
    })

ZETA_EXECUTABLES.sort(key=lambda executable: executable["name"].lower())
