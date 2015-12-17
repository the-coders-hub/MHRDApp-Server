from django.contrib import admin
from .models import File, Tag


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['id', 'file', 'mime_type']
    exclude = ['mime_type']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'tag']
