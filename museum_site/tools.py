import codecs
import grp
import os
import pwd
import shutil

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .common import *
from .constants import *
from zipfile import ZipFile
from .models import *

from internetarchive import upload

try:
    import zookeeper
    HAS_ZOOKEEPER = True
except ImportError:
    HAS_ZOOKEEPER = False


@staff_member_required
def add_livestream(request, pk):
    """ Returns page to add a livestream VOD article """
    data = {
        "title": "Tools",
        "file": File.objects.get(pk=pk),
        "today": str(datetime.now())[:10]
    }
    print(SITE_ROOT)

    if request.POST.get("action"):
        if request.POST.get("pk"):
            a = Article.objects.get(pk=int(request.POST["pk"]))
        else:
            a = Article()

        # Convert video URL
        url = request.POST.get("url")
        if request.POST.get("url").startswith("http"):
            url = url.replace("https://youtu.be/", "")
            url = url.replace("https://www.youtube.com/watch?v=", "")
            url = url.replace("https://studio.youtube.com/video/", "")
            url = url.replace("/edit", "")
            if "&" in url:
                url = url[:url.find("&")]
        data["video_id"] = url

        a.title = "Livestream - " + request.POST.get("title")
        a.author = request.POST.get("author")
        a.category = "Livestream"
        a.schema = "django"
        a.date = request.POST.get("date")
        a.published = PUBLISHED_ARTICLE
        a.summary = request.POST.get("summary")
        a.allow_comments = True

        # Open the template
        file_path = os.path.join(SITE_ROOT, "tools", "data", "youtube_template.html")
        with open(file_path) as fh:
            template = fh.read()

        # Process the description
        final_desc = request.POST.get("desc")
        final_desc = final_desc[:final_desc.find("Download:")]
        final_desc = "<p>" + final_desc.replace("\r\n", "</p>\n<p>")
        final_desc = final_desc[:-3]
        final_desc = final_desc.replace("<p></p>", "")

        a.content = template.format(video_id=data["video_id"], desc=final_desc)

        a.save()
        data["article_pk"] = str(a.id)

        # Upload the preview
        if request.FILES.get("preview"):
            # Save the file to the uploaded folder
            file_path = os.path.join(SITE_ROOT, "museum_site", "static", "images", "articles", "streams", (str(a.id) + ".png"))
            with open(file_path, 'wb+') as fh:
                for chunk in request.FILES["preview"].chunks():
                    fh.write(chunk)

            a.preview = "articles/streams/" + str(a.id) + ".png"
            a.save()

        # Associate the article with the relevant file
        data["file"].articles.add(a)
        data["file"].save()

    return render(request, "museum_site/tools/add_livestream.html", data)


@staff_member_required
def audit_zeta_config(request):
    data = {
        "title": "Zeta Config Audit",
    }
    data["special"] = File.objects.filter(details__in=[DETAIL_ZZT, DETAIL_SZZT]).exclude(zeta_config_id__in=[1, 4]).order_by("zeta_config")
    return render(request, "museum_site/tools/audit_zeta_config.html", data)


@staff_member_required
def calculate(request, field, pk):
    f = File.objects.get(pk=pk)
    data = {
        "title": "Calculate " + field.title(),
    }
    return render(request, "museum_site/tools/calculate.html", data)


@staff_member_required
def mirror(request, pk):
    """ Returns page to publish file on Archive.org """
    f = File.objects.get(pk=pk)
    data = {
        "title": "Archive.org Mirror",
        "file": f,
        "ret": None,
        "packages": PACKAGE_PROFILES,
        "collection": ARCHIVE_COLLECTION,
    }

    package = int(request.GET.get("package", 0))
    data["package"] = PACKAGE_PROFILES[package]
    data["split"] = math.ceil(len(data["packages"]) // 2)

    zip_file = zipfile.ZipFile(os.path.join(SITE_ROOT, f.download_url()[1:]))

    file_list = zip_file.namelist()
    file_list.sort(key=str.lower)
    data["file_list"] = file_list

    # Mirror the file
    if request.POST.get("mirror"):
        if request.POST.get("package") != "NONE":
            package = PACKAGE_PROFILES[int(request.POST.get("package", 0))]

            # Advanced settings
            zip_name = package["prefix"] + f.filename

            if request.POST.get("upload_name"):
                upload_name = request.POST["upload_name"]
            else:
                upload_name = zip_name[:-4]

            # Copy the base package zip
            shutil.copy(
                SITE_ROOT + f.download_url(),
                os.path.join(TEMP_PATH, zip_name)
            )

        # Handle alternative Zip upload
        if request.FILES.get("alt_src"):
            with open(os.path.join(TEMP_PATH, zip_name), "wb") as fh:
                fh.write(request.FILES["alt_src"].read())

        temp_zip = os.path.join(TEMP_PATH, zip_name)

        # Open the WIP zip
        with ZipFile(temp_zip, "a") as z:
            # Insert the base files
            to_add = glob.glob(
                os.path.join(BASE_PATH, package["directory"], "*")
            )
            for a in to_add:
                z.write(a, arcname=os.path.basename(a))

            # Create ZZT.CFG if needed
            if package.get("use_cfg"):
                config_content = request.POST.get("launch")[:-4].upper()  # Remove .ZZT extension
                if package["registered"]:
                    config_content += "\r\nREGISTERED"
                z.writestr("ZZT.CFG", config_content)

        # Create description
        description = "{}\n\n{}".format(package["auto_desc"], request.POST.get("description", ""))

        # Determine the launch command
        if request.POST.get("alt_launch"):
            launch_command = request.POST["alt_launch"]
        else:
            launch_command = package["executable"] + " " + request.POST.get("launch", "").upper()

        # Zip file is completed, prepare the upload
        meta = {
            "title": request.POST.get("title"),
            "mediatype": "software",
            "collection": ARCHIVE_COLLECTION,
            "emulator": "dosbox",
            "emulator_ext": "zip",
            "emulator_start": launch_command,
            "year": str(f.release_date)[:4],
            "subject": [package["engine"]] + f.genre.split("/"),
            "creator": f.author.split("/"),
            "description": description
        }

        if DEBUG:
            upload_name = "test-" + upload_name

        print("I'm gonna upload:", os.path.join(TEMP_PATH, zip_name))
        file_path = os.path.join(TEMP_PATH, zip_name)

        r = upload(
            upload_name,
            files=[file_path],
            metadata=meta,
            access_key=IA_ACCESS,
            secret_key=IA_SECRET,
        )

        if r[0].status_code == 200:
            data["status"] = "SUCCESS"
            f.archive_name = upload_name
            f.save()
            os.remove(os.path.join(TEMP_PATH, zip_name))
        else:
            data["status"] = "FAILURE"

        data["archive_resp"] = r

    return render(request, "museum_site/tools/mirror.html", data)

@staff_member_required
def publish(request, pk):
    """ Returns page to publish a file marked as uploaded """
    data = {
        "title": "Publish",
        "file": File.objects.get(pk=pk),
        "file_list": []
    }

    if request.POST.get("publish"):
        # Move the file
        src = SITE_ROOT + data["file"].download_url()
        dst = SITE_ROOT + "/zgames/" + data["file"].letter + "/" + data["file"].filename
        shutil.move(src, dst)

        # Adjust the details
        data["file"].details.remove(Detail.objects.get(pk=DETAIL_UPLOADED))
        for detail in request.POST.getlist("details"):
            data["file"].details.add(Detail.objects.get(pk=detail))

        # Save
        data["file"].publish_date = datetime.now()
        data["file"].save()

        # Redirect
        return redirect("tool_list", pk=pk)

    with ZipFile(SITE_ROOT + data["file"].download_url(), "r") as zf:
        data["file_list"] = zf.namelist()
    data["file_list"].sort()
    data["extension_list"] = []

    for f in data["file_list"]:
        data["extension_list"].append(f.split(".")[-1].upper())

    return render(request, "museum_site/tools/publish.html", data)


@staff_member_required
def replace_zip(request, pk):
    """ Returns page with latest Museum scan results"""
    data = {"title": "Replace Zip"}
    data["file"] = File.objects.get(pk=pk)

    # Original file info
    data["stat"] = os.stat(data["file"].phys_path())
    data["mtime"] = datetime.fromtimestamp(data["stat"].st_mtime)
    data["file_user"] = pwd.getpwuid(data["stat"].st_uid)
    data["file_group"] = grp.getgrgid(data["stat"].st_gid)

    if request.POST.get("action") == "replace-zip":
        file_path = data["file"].phys_path()
        print(request.FILES)
        with open(file_path, 'wb+') as fh:
            for chunk in request.FILES["replacement"].chunks():
                fh.write(chunk)

        data["new_file"] = File.objects.get(pk=pk)

        # Update checksum
        if request.POST.get("update-checksum"):
            data["new_file"].calculate_checksum()
        if request.POST.get("update-board-count"):
            data["new_file"].calculate_boards()
        if request.POST.get("update-size"):
            data["new_file"].calculate_size()
        data["new_file"].save()

        data["new_stat"] = os.stat(data["file"].phys_path())
        data["new_mtime"] = datetime.fromtimestamp(data["stat"].st_mtime)
        data["new_file_user"] = pwd.getpwuid(data["stat"].st_uid)
        data["new_file_group"] = grp.getgrgid(data["stat"].st_gid)

    return render(request, "museum_site/tools/replace_zip.html", data)



@staff_member_required
def scan(request):
    """ Returns page with latest Museum scan results"""
    data = {"title": "Museum Scan"}
    try:
        with codecs.open(os.path.join(STATIC_PATH, "data", "scan.log"), "r", "utf-8") as fh:
            data["scan"] = fh.read()
    except FileNotFoundError:
        data["scan"] = ""
    return render(request, "museum_site/tools/scan.html", data)


@staff_member_required
def tool_index(request):
    data = {"title": "Tool Index"}
    data["file"] = {"id": 1}
    return render(request, "museum_site/tools/tool_index.html", data)


@staff_member_required
def tool_list(request, pk):
    """ Returns page listing tools available for a file and file information """
    data = {
        "title": "Tools",
        "file": File.objects.get(pk=pk)
    }

    # Simple validation tools
    data["valid_letter"] = True if data["file"].letter in LETTERS else False
    data["valid_filename"] = True if data["file"].phys_path() else False

    if request.GET.get("recalculate"):
        field = request.GET["recalculate"]
        if field == "sort-title":
            data["file"].sorted_title()
            data["new"] = data["file"].sort_title
        elif field == "size":
            data["file"].calculate_size()
            data["new"] =  data["file"].size
        elif field == "reviews":
            data["file"].calculate_reviews()
            data["new"] =  "{}/{}".format(data["file"].review_count, data["file"].rating)
        elif field == "articles":
            data["file"].calculate_article_count()
            data["new"] =  data["file"].article_count
        elif field == "checksum":
            data["file"].calculate_checksum()
            data["new"] = data["file"].checksum
        elif field == "boards":
            data["file"].calculate_boards()
            data["new"] = "{}/{}".format(data["file"].playable_boards, data["file"].total_boards)

        data["file"].basic_save()

    return render(request, "museum_site/tools/list.html", data)


@staff_member_required
def set_screenshot(request, pk):
    """ Returns page to generate and set a file's screenshot """
    data = {
        "title": "Set Screenshot",
    }
    file = File.objects.get(pk=pk)
    data["file"] = file
    data["file_list"] = []

    if not HAS_ZOOKEEPER:
        return HttpResponse("Zookeeper library not found.")

    with ZipFile(SITE_ROOT + file.download_url(), "r") as zf:
        all_files = zf.namelist()
        for f in all_files:
            if f.lower().endswith(".zzt"):
                data["file_list"].append(f)
    data["file_list"].sort()

    if request.GET.get("file"):
        with ZipFile(SITE_ROOT + file.download_url(), "r") as zf:
            zf.extract(request.GET["file"], path=SITE_ROOT + "/museum_site/static/data/")

        z = zookeeper.Zookeeper(SITE_ROOT + "/museum_site/static/data/" + request.GET["file"])
        data["board_list"] = []
        for board in z.boards:
            print(board.title)
            data["board_list"].append(board.title)

    if request.GET.get("board"):
        data["board_num"] = int(request.GET["board"])

        if data["board_num"] != 0:
            z.boards[data["board_num"]].screenshot(SITE_ROOT + "/museum_site/static/data/temp")
        else:
            z.boards[data["board_num"]].screenshot(SITE_ROOT + "/museum_site/static/data/temp", title_screen=True)
        data["show_preview"] = True

    if request.POST.get("save"):
        src = SITE_ROOT + "/museum_site/static/data/temp.png"
        dst = SITE_ROOT + "/museum_site/static/images/screenshots/" + file.letter + "/" + file.filename[:-4] + ".png"
        shutil.copyfile(src, dst)

        file.screenshot = file.filename[:-4] + ".png"
        file.save()
    elif request.POST.get("b64img"):
        raw = request.POST.get("b64img").replace("data:image/png;base64,", "", 1)
        from PIL import Image
        from io import BytesIO
        import base64

        image = Image.open(BytesIO(base64.b64decode(raw)))
        image = image.crop((0, 0, 480, 350))
        image.save(SITE_ROOT + "/museum_site/static/images/screenshots/" + file.letter + "/" + file.filename[:-4] + ".png")


    if os.path.isfile(SITE_ROOT + "/museum_site/static/data/" + request.GET.get("file", "")):
        os.remove(SITE_ROOT + "/museum_site/static/data/" + request.GET["file"])
    return render(request, "museum_site/tools/set_screenshot.html", data)
