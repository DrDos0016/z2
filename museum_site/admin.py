from django.contrib import admin

# Register your models here.
from .alias import Alias
from .article import Article
from .comment import Comment
from .file import File
from .detail import Detail
from .review import Review
from .zeta_config import Zeta_Config

admin.site.register(File)
admin.site.register(Article)
admin.site.register(Detail)
admin.site.register(Review)
admin.site.register(Alias)
admin.site.register(Zeta_Config)
