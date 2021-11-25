from django.contrib import admin
from .models import Topic


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'creater', 'tenant', 'creater', 'created')
