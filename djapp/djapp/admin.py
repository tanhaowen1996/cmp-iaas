from django.contrib import admin
from .models import Network, Port, Keypair, Image, Volume


@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    list_display = ('id', 'os_network_id', 'os_subnet_id',
                    'name', 'cidr', 'is_shared', 'created', 'modified')


@admin.register(Port)
class PortAdmin(admin.ModelAdmin):
    list_display = ('id', 'os_port_id',
                    'network', 'ip_address', 'is_external',
                    'created', 'modified')


@admin.register(Keypair)
class KeypairAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user_id',
                    'fingerprint', 'public_key',
                    'type_list', 'public_key')

@admin.register(Image)
class KeypairAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner',
                    'size', 'status',
                    'disk_format', 'container_format',
                    'checksum', 'min_disk',
                    'min_ram', 'protected', 'virtual_size',
                    'visibility', 'os_type', 'created_at',
                    'updated_at','description','user_id')


@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'volume_type', 'size',
                    'status', 'is_bootable', 'attachments',
                    'created_at', 'user_name', 'user_id',
                    'volume_used', 'server_id', 'server_name',
                    'device', 'tenant_id', 'volume_used',
                    'tenant_name', 'updated_at')
