from django.contrib import admin
from .models import (
    Network, Port,
    Firewall, StaticRouting,
    Keypair, Image, Volume
)


@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    list_display = ('id', 'os_network_id', 'os_subnet_id', 'tenants',
                    'name', 'cidr', 'is_shared', 'created', 'modified')


@admin.register(Port)
class PortAdmin(admin.ModelAdmin):
    list_display = ('id', 'os_port_id',
                    'network', 'ip_address', 'is_external',
                    'created', 'modified')


@admin.register(Firewall)
class FirewallAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',
                    'source_tenant', 'destination_tenant',
                    'source_network', 'destination_network',
                    'creater', 'created')


@admin.register(StaticRouting)
class StaticRoutingAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',
                    'destination_subnet', 'ip_next_hop_address',
                    'cluster_code', 'tenant',
                    'creater', 'created')


@admin.register(Keypair)
class KeypairAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user_id',
                    'fingerprint', 'public_key',
                    'type_list', 'public_key')


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner',
                    'size', 'status',
                    'disk_format', 'container_format',
                    'visibility', 'os_type', 'created_at',
                    'updated_at', 'description', 'user_id')


@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'volume_type', 'size',
                    'status', 'is_bootable', 'attachments',
                    'created_at', 'user_name', 'user_id',
                    'volume_used', 'server_id', 'server_name',
                    'device', 'tenant_id', 'volume_used',
                    'tenant_name', 'updated_at')
