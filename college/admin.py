from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import College


@admin.register(College)
class CollegeAdmin(SimpleHistoryAdmin):
    list_display = ['id', 'name', 'location', 'homepage']
