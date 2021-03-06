import datetime

import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

from museum_site.models import *  # noqa: E402
from museum_site.constants import REMOVED_ARTICLE, DETAIL_REMOVED  # noqa: E402


def main():
    print("WARNING! THIS WILL PERMANENTLY REMOVE DATA FROM THIS DATABASE")
    print("Are you sure you wish to remove all non-public data?")
    confirm = input("Type 'yes' to confirm: ")

    if confirm == "yes":
        print("Deleting articles...")
        for a in Article.objects.filter(published=REMOVED_ARTICLE):
            print(a)
            a.delete()
        print("Done!")
        print("Deleting file objects...")
        for f in File.objects.filter(details__id=DETAIL_REMOVED):
            print(f)
            f.delete()
        print("Done!")
        print("Deleting sessions...")
        Session.objects.all().delete()
        print("Done!")
        print("Clearing accounts...")
        qs = User.objects.all()
        for u in qs:
            u.username = "USER #" + str(u.id)
            u.first_name = ""
            u.last_name= ""
            u.email = "test@example.com"
            u.password = u.set_password("password")
            u.is_staff = False
            u.is_superuser = False
            u.save()




        print("Private data has removed. Database can be publicly shared.")
        print("DONE.")
    else:
        print("ABORTED.")


if __name__ == '__main__':
    main()
