from django.conf.urls import patterns, include, url
from django.views.static import *
from django.conf import settings
import z2_site.views, z2_site.ajax, z2_site.admin

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns("",
    url(r"^$", z2_site.views.index),
    url(r"^upload$", z2_site.views.upload),
    
    # Articles
    url(r"^article$", z2_site.views.article_directory),
    url(r"^article/(?P<id>[0-9]+)/(.*)$", z2_site.views.article_view),
    
    # Special Article Pages (those with urls besides /article/#/title)
    url(r"^about-zzt$", z2_site.views.article_view, {"id":1}),
    url(r"^ascii$", z2_site.views.article_view, {"id":3}),
    url(r"^clones$", z2_site.views.article_view, {"id":6}),
    url(r"^getting-started$", z2_site.views.article_view, {"id":5}),
    url(r"^mass$", z2_site.views.article_view, {"id":7}),
    url(r"^zzt$", z2_site.views.article_view, {"id":2}),
    
    # Featured Games
    url(r"^featured$", z2_site.views.featured_games),
    
    # Files
    url(r"^browse/(?P<letter>[a-z1])$", z2_site.views.browse),
    url(r"^file/(?P<letter>[a-z1!])/(?P<filename>.*)$", z2_site.views.file),
    url(r"^superzzt$", z2_site.views.browse, {"category":"Super ZZT"}),
    url(r"^zig$", z2_site.views.browse, {"category":"ZIG"}),
    url(r"^soundtracks$", z2_site.views.browse, {"category":"Soundtrack"}),
    url(r"^uploaded$", z2_site.views.browse, {"category":"Uploaded"}),
    url(r"^utilities$", z2_site.views.browse, {"category":"Utility"}),
    
    # Random ZZT World
    url(r"^random$", z2_site.views.random),
    
    # Reviews
    url(r"^review/(?P<letter>[a-z1])/(?P<filename>.*)$", z2_site.views.review),
    
    # Search
    url(r"^advanced-search$", z2_site.views.advanced_search),
    url(r"^search$", z2_site.views.search),
    
    # Uploads
    url(r"^upload$", z2_site.views.upload),
    
    
    ###########################################################################
    ###########################################################################
    
    # AJAX
    url(r"^ajax/get_zip_file$", z2_site.ajax.get_zip_file),
    
    # Admin
    url(r"^admin/file_management$", z2_site.admin.file_management),
    url(r"^admin/article_management$", z2_site.admin.article_management),
    
    # Debug
    url(r"^debug/save$", z2_site.views.debug_save),
    
    (r"^assets/(?P<path>.*)$", "django.views.static.serve", {"document_root": settings.STATIC_ROOT}),
    (r"^zgames/(?P<path>.*)$", "django.views.static.serve", {"document_root": "/var/projects/z2/zgames/"})
)
