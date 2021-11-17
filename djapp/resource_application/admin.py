from django.contrib import admin
from .models import ResourceApplication


@admin.register(ResourceApplication)
class ResourceApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'creater', 'status', 'created')
