from django.contrib import admin
from .models import Article, FSJob, FSImage, FSFilteredImage

# Register your models here.

admin.site.register(Article)
admin.site.register(FSJob)
admin.site.register(FSImage)
admin.site.register(FSFilteredImage)
