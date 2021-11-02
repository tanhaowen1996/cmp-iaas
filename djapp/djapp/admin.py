from django.contrib import admin
from .models import Network


@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    list_display = ('id', 'os_network_id', 'os_subnet_id',
                    'name', 'cidr', 'is_shared', 'created', 'modified')
