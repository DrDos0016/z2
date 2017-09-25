import os
import subprocess
import zipfile

from datetime import datetime

from django.conf import settings
from django.db import models
from django.db.models import Avg

from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

try:
    import zookeeper
    HAS_ZOOKEEPER = True
except ImportError:
    HAS_ZOOKEEPER = False


ARTICLE_FORMATS = (
    ("text", "Plaintext"),
    ("md", "Markdown"),
    ("html", "HTML"),
    ("django", "Django"),
)


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
    ("ZZM", "ZZM Soundtrack"),
    ("GFX", "Modified Graphics"),
    ("MOD", "Modified Executables"),
    ("ETC", "Etc."),
    ("SZZT", "Super ZZT Worlds"),
    ("UTILITY", "Utilities"),
    ("ZZT", "ZZT Worlds"),
    ("ZIG", "ZIG World"),
    ("LOST", "Lost Worlds"),
    ("UPLOADED", "Uploaded Worlds"),
    ("REMOVED", "Removed Worlds"),
)

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

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Article(models.Model):
    """ Article object repesenting a page from an article

    Fields:
    title           -- Title of the article
    author          -- Author of the article
    category        -- Categorization of the article for the directory
    content         -- Body of the article
    css             -- Custom CSS for the article
    type            -- Whether the article is in text/md/html/django form
    date            -- Date the article was written
    published       -- If the article is available to the public
    page            -- Page # of the article
    parent          -- Article ID of the first page of the article
    summary         -- Summary for Opengraph
    preview         -- Path to preview image
    allow_comments  -- Allow user comments on the article
    """
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    content = models.TextField(default="")
    css = models.TextField(default="", blank=True)
    type = models.CharField(max_length=6, choices=ARTICLE_FORMATS)
    date = models.DateField(default="1970-01-01")
    published = models.BooleanField(default=False)
    page = models.IntegerField(default=1)
    parent = models.ForeignKey("Article", null=True, blank=True, default=None)
    summary = models.CharField(max_length=150, default="", blank=True)
    preview = models.CharField(max_length=80, default="", blank=True)
    #allow_comments = models.BooleanField(default=False)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        output = "[" + str(self.id) + "] " + self.title + " by " + self.author
        if self.page > 1:
            output += " (P{})".format(self.page)
        return output

    def url(self):
        return "/article/" + str(self.id) + "/" + slugify(self.title)

    def get_page_count(self):
        if self.parent_id == 0:
            page_count = 1 + Article.objects.filter(parent_id=self.id).count()
        else:
            page_count = 1 + Article.objects.filter(
                parent_id=self.parent_id
            ).count()
        return page_count


class Comment():
    """ Review object repesenting a comment on an article

    Fields:
    article         -- Link to Article object
    user            -- UserID who posted comment
    content         -- Body of comment
    date            -- Date review was written
    ip              -- IP address posting the review
    """
    article = models.ForeignKey("Article")
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.TextField()
    date = models.DateField()
    ip = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        x = ("[" + str(self.id) + "] Comment for " + str(self.article.title) + " by " + str(self.article.author))
        return x

    def from_request(self, request):
        if request.method != "POST":
            return False

        self.file_id = int(request.POST.get("file_id"))
        self.title = request.POST.get("title")
        self.author = request.POST.get("name")  # NAME not author
        self.email = request.POST.get("email")
        self.content = request.POST.get("content")
        self.rating = round(float(request.POST.get("rating")), 2)
        self.date = datetime.utcnow()
        self.ip = request.META["REMOTE_ADDR"]

        return True


class File(models.Model):
    """ File object repesenting an upload to the site

    Fields:
    letter          -- Letter the file can be found under via browse pages
    filename        -- Name of the (Zip) file (ex: Respite.zip)
    title           -- Name of the World (ex: Frost 1: Power)
    sort_title      -- Title used for natural sorting
    author          -- / sep. ABC list of authors (ex: Hercules/Nadir)
    size            -- Filesize in Kilobytes (ex: 42)
    genre           -- / sep. ABC list of genres (ex: Action/RPG)
    release_date    -- Best guess release date (ex: 2001-04-16)
    release_source  -- Source of release date (ex: ZZT file, News post, Text)
    screenshot      -- Filename of screenshot to display (ex: 3dtalk.png)
    company         -- / sep. ABC list of companies published (ex: ERI/IF)
    description     -- Description of file for utilities or featured games
    review_count    -- Number of reviews on this file
    rating          -- Average rating if any, from file's reviews
    details         -- Link to Detail objects
    articles        -- Link to Article objects
    article_count   -- Number of articles associated with this file
    checksum        -- md5 checksum of the zip file
    superceded      -- FK with File for the "definitive" version of a file
    playable_boards -- Number of boards in file that can be accessed in play
    total_boards    -- Number of boards in file that exist period
    """

    letter = models.CharField(max_length=1, db_index=True)
    filename = models.CharField(max_length=50)
    title = models.CharField(max_length=80)
    sort_title = models.CharField(
        max_length=100, db_index=True, default="", blank=True,
        help_text="Leave blank to set automatically"
    )
    author = models.CharField(max_length=80)
    size = models.IntegerField(default=0)
    genre = models.CharField(max_length=80, blank=True, default="")
    release_date = models.DateField(default=None, null=True, blank=True)
    release_source = models.CharField(
        max_length=20, null=True, default=None, blank=True
    )
    screenshot = models.CharField(
        max_length=80, blank=True, null=True, default=None
    )
    company = models.CharField(
        max_length=80, default="", blank=True, null=True
    )
    description = models.TextField(null=True, blank=True, default="")
    review_count = models.IntegerField(
        default=0, help_text="Set automatically. Do not adjust."
    )
    rating = models.FloatField(null=True, default=None, blank=True)
    details = models.ManyToManyField("Detail", default=None, blank=True)
    articles = models.ManyToManyField("Article", default=None, blank=True,
                                      limit_choices_to={'page': 1})
    article_count = models.IntegerField(
        default=0, help_text="Set automatically. Do not adjust."
    )
    checksum = models.CharField(max_length=32, null=True,
                                blank=True, default="")
    superceded = models.ForeignKey("File", db_column="superceded_id",
                                   null=True, blank=True, default=None)
    playable_boards = models.IntegerField(null=True, blank=True, default=None, help_text="Set automatically. Do not adjust.")
    total_boards = models.IntegerField(null=True, blank=True, default=None, help_text="Set automatically. Do not adjust.")

    class Meta:
        ordering = ["sort_title", "letter"]

    def __str__(self):
        return "[" + str(self.id) + "] " + self.title

    def save(self, *args, **kwargs):
        # Pre save
        # Force lowercase letter
        self.letter = self.letter.lower()

        # Sort genres
        temp_list = self.genre.split("/")
        temp_list.sort()
        sorted_str = "/".join(temp_list)

        self.genre = sorted_str

        # Create sorted title if not set
        if self.sort_title == "":
            self.sort_title = self.sorted_title()

        # Recalculate Article Count
        if self.id is not None:
            self.article_count = self.articles.all().filter(
                published=True
            ).count()

        # If the screenshot is blank and a file exists for it, set it
        if self.screenshot == "" and os.path.isfile(os.path.join(SITE_ROOT, "museum_site/static/images/screenshots/") + self.letter + "/" + self.filename[:-4] + ".png"):
            self.screenshot = self.filename[:-4] + ".png"

        # Recalculate Review Scores
        self.recalculate_reviews()

        # Update blank md5s
        if self.checksum == "":
            try:
                resp = subprocess.run(["md5sum", os.path.join(SITE_ROOT, "zgames/") + self.letter + "/" + self.filename], stdout=subprocess.PIPE)
                md5 = resp.stdout[:32].decode("utf-8")
                self.checksum = md5
            except:
                pass

        # Set board counts
        if not self.playable_boards or not self.total_boards and HAS_ZOOKEEPER:
            self.calculate_boards()

        # Actual save call
        super(File, self).save(*args, **kwargs)

    def sorted_title(self):
        # Handle titles that start with A/An/The
        sort_title = self.title.lower()

        if sort_title.startswith(("a ", "an ", "the ")):
            sort_title = sort_title[sort_title.find(" ") + 1:]

        # Expand numbers
        words = sort_title.split(" ")
        expanded = []
        for word in words:
            try:
                int(word)
                expanded.append(("0000" + word)[-4:])
            except ValueError:
                expanded.append(word)
        sort_title = " ".join(expanded)

        return sort_title

    def download_url(self):
        if self.is_uploaded():
            return "/zgames/uploaded/" + self.filename
        else:
            return "/zgames/" + self.letter + "/" + self.filename

    def play_url(self):
        return "/play/" + self.letter + "/" + self.filename

    def review_url(self):
        return "/review/" + self.letter + "/" + self.filename

    def file_url(self):
        return "/file/" + self.letter + "/" + self.filename

    def article_url(self):
        return "/article/" + self.letter + "/" + self.filename

    def wiki_url(self):
        return "http://zzt.org/zu/wiki/" + self.title

    def get_detail_ids(self):
        details = self.details.all()
        output = []
        for detail in details:
            output.append(int(detail.id))
        return output

    def author_list(self):
        return self.author.split("/")

    def genre_list(self):
        return self.genre.split("/")

    def is_lost(self):
        lost = self.details.all().values_list("id", flat=True)
        return True if DETAIL_LOST in lost else False

    def is_uploaded(self):
        uploaded = self.details.all().values_list("id", flat=True)
        return True if DETAIL_UPLOADED in uploaded else False

    def recalculate_reviews(self):
        # Recalculate Review Count
        if self.id is not None:
            self.review_count = Review.objects.filter(file_id=self.id).count()

        # Recalculate Rating
        if self.id is not None:
            ratings = Review.objects.filter(
                file_id=self.id, rating__gte=0
            ).aggregate(Avg("rating"))
            if ratings["rating__avg"] is not None:
                self.rating = round(ratings["rating__avg"], 2)

    def from_request(self, request):
        upload_directory = os.path.join(SITE_ROOT, "zgames/uploaded")

        if request.method != "POST":
            return False

        # First handle the easy stuff
        self.letter = request.POST.get("title", "1")[0].lower()
        if self.letter not in "abcdefghijklmnopqrstuvwxyz":
            self.letter = "1"
        self.filename = str(request.FILES.get("file"))
        self.title = request.POST.get("title")
        # sort_title handled by saving
        self.author = request.POST.get("author")
        self.size = int(request.FILES.get("file").size / 1024)
        self.release_date = request.POST.get("release_date")
        self.release_source = "User upload"
        self.company = request.POST.get("company", "")
        self.description = request.POST.get("desc", "")
        self.genre = "/".join(request.POST.getlist("genre"))

        # DEBUG -- REMOVE THIS FOR LAUNCH WHEN THIS FIELD IS REMOVED
        self.category = "ZZT"

        # SCREENSHOT -- Currently manual
        # DETAILS -- Currently manual

        # Check for a duplicate filename
        exists = File.objects.filter(filename=self.filename).exists()
        if exists:
            return {"status": "error",
                    "msg": "The chosen filename is already in use."}

        # Save the file to the uploaded folder
        file_path = os.path.join(upload_directory, self.filename)
        with open(file_path, 'wb+') as fh:
            for chunk in request.FILES["file"].chunks():
                fh.write(chunk)

        # md5 checksum
        resp = subprocess.run(["md5sum", file_path], stdout=subprocess.PIPE)
        md5 = resp.stdout[:32].decode("utf-8")
        self.checksum = md5

        # SITE META
        return {"status": "success"}

    def calculate_boards(self):
        temp_playable = 0
        temp_total = 0
        zip_path = os.path.join(SITE_ROOT, "zgames",self.letter, self.filename)
        temp_path = os.path.join(SITE_ROOT, "temp")

        try:
            zf = zipfile.ZipFile(zip_path)
        except (FileNotFoundError, zipfile.BadZipFile):
            print("\tSkipping due to bad zip")

        file_list = zf.namelist()

        for file in file_list:
            name, ext = os.path.splitext(file)
            ext = ext.upper()

            if ext == ".ZZT":  # ZZT File
                # Extract the file
                try:
                    zf.extract(file, path=temp_path)
                except:
                    print("Bad zip.")
            else:
                continue

            z = zookeeper.Zookeeper(
                os.path.join(temp_path, file)
            )

            # Since a ZZT world is being opened, initialize these for the first file only
            if self.playable_boards is None:
                self.playable_boards = 0
                self.total_boards = 0

            to_explore = []
            accessible = []

            # Start with the starting board
            to_explore.append(z.world.current_board)

            false_positives = 0
            for idx in to_explore:
                # Make sure the board idx exists in the file (in case of imported boards with passages)
                if idx >= len(z.boards):
                    false_positives += 1
                    continue

                #print(to_explore)
                # This board is clearly accessible
                accessible.append(idx)

                # Get the connected boards via edges
                if z.boards[idx].board_north != 0 and z.boards[idx].board_north not in to_explore:
                    to_explore.append(z.boards[idx].board_north)
                if z.boards[idx].board_south != 0 and z.boards[idx].board_south not in to_explore:
                    to_explore.append(z.boards[idx].board_south)
                if z.boards[idx].board_east != 0 and z.boards[idx].board_east not in to_explore:
                    to_explore.append(z.boards[idx].board_east)
                if z.boards[idx].board_west != 0 and z.boards[idx].board_west not in to_explore:
                    to_explore.append(z.boards[idx].board_west)

                # Get the connected boards via passages
                for stat in z.boards[idx].stat_data:
                    if z.boards[idx].get_element((stat.x, stat.y)).name == "Passage":
                        # print("Found a passage at", stat.x, stat.y)
                        if stat.param3 not in to_explore:
                            to_explore.append(stat.param3)

            # Title screen always counts (but don't count it twice)
            if 0 not in to_explore:
                to_explore.append(0)

            """
            for x in range(0, len(z.boards)):
                if x in to_explore:
                    print("[X]", z.boards[x].title)
                else:
                    print("[ ]", z.boards[x].title)
            """

            self.playable_boards += len(to_explore) - false_positives
            self.total_boards += len(z.boards)
        return True


class Detail(models.Model):
    detail = models.CharField(max_length=20)

    class Meta:
        ordering = ["detail"]

    def __str__(self):
        return "[" + str(self.id) + "] " + self.detail


class Review(models.Model):
    """ Review object repesenting an review to a file

    Fields:
    file            -- Link to File object
    title           -- Title of the review
    author          -- Author of the review
    email           -- Author's email (hide this? Optional?)
    content         -- Body of review
    rating          -- Rating given to file from 0.0 - 5.0
    date            -- Date review was written
    ip              -- IP address posting the review
    """
    file = models.ForeignKey("File")
    title = models.CharField(max_length=50)
    author = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    content = models.TextField()
    rating = models.FloatField(default=5.0)
    date = models.DateField()
    ip = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        x = ("[" + str(self.id) + "] Review for " + str(self.file.title) + " [" +
             str(self.file.filename) + "] by " + str(self.author)
             )
        return x

    def from_request(self, request):
        if request.method != "POST":
            return False

        self.file_id = int(request.POST.get("file_id"))
        self.title = request.POST.get("title")
        self.author = request.POST.get("name")  # NAME not author
        self.email = request.POST.get("email")
        self.content = request.POST.get("content")
        self.rating = round(float(request.POST.get("rating")), 2)
        self.date = datetime.utcnow()
        self.ip = request.META["REMOTE_ADDR"]

        return True