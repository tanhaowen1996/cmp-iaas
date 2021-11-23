from django.conf import settings
from django.contrib.postgres.indexes import BrinIndex
from django.db import models
from django.utils.translation import gettext_lazy as _
from netfields import CidrAddressField, InetAddressField,\
    MACAddressField, NetManager
from .utils import OpenstackMixin
import uuid


class Network(models.Model, OpenstackMixin):
    IP_VERSION_V4 = 4
    CATEGORY_CLUSTER = 'cluster'
    CATEGORY_CONTAINER = 'container'
    CATEGORY_CHOICES = (
        (CATEGORY_CLUSTER, 'cluster'),
        (CATEGORY_CONTAINER, 'container'),
    )
    id = models.UUIDField(
        editable=False,
        primary_key=True,
        default=uuid.uuid1,
        verbose_name=_('network id'))
    os_network_id = models.UUIDField(
        editable=False)
    os_subnet_id = models.UUIDField(
        editable=False)
    tenants = models.JSONField(
        default=list,
        verbose_name=_('tenant obj list with id & name'))
    name = models.CharField(
        max_length=255,
        verbose_name=_('network name'))
    cidr = CidrAddressField()
    total_interface = models.PositiveIntegerField()
    vlan_id = models.PositiveSmallIntegerField(
        unique=True)
    category = models.CharField(
        choices=CATEGORY_CHOICES,
        max_length=255)
    is_shared = models.BooleanField()
    description = models.CharField(
        blank=True,
        max_length=255)
    creater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT)
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created time'))
    modified = models.DateTimeField(
        auto_now=True,
        verbose_name=_('updated time'))

    class Meta:
        indexes = (BrinIndex(fields=['modified', 'created']),)
        ordering = ('-modified',)

    def __str__(self):
        return self.name

    def create_os_network_subnet(self, os_conn):
        network = os_conn.network.create_network(
            name=self.name
        )
        subnet = os_conn.network.create_subnet(
            name=self.name,
            network_id=network.id,
            ip_version=self.IP_VERSION_V4,
            cidr=str(self.cidr)  # type IPv4Network is not JSON serializable
        )
        self.id = self.os_network_id = network.id
        self.os_subnet_id = subnet.id
        self.total_interface = self.cidr.num_addresses - 2

    def update_os_network_subnet(self, os_conn, name='', description='', **kwargs):
        os_conn.network.update_subnet(
            self.os_subnet_id, name=name, description=description)
        os_conn.network.update_network(
            self.os_network_id, name=name, description=description)

    def destroy_os_network_subnet(self, os_conn):
        os_conn.network.delete_subnet(self.os_subnet_id, ignore_missing=False)
        os_conn.network.delete_network(self.os_network_id, ignore_missing=False)

    def get_os_network_subnet(self, os_conn):
        network = os_conn.network.find_network(self.os_network_id)
        subnet = os_conn.network.find_subnet(self.os_subnet_id)
        return {
            'port_number': self.port_set.count(),
            'status': network.status,
            'mtu': network.mtu,
            'provider_physical_network': network.provider_physical_network,
            'creater': self.creater.get_full_name(),
            'provider_network_type': network.provider_network_type,
            'allocation_pools': subnet.allocation_pools
        }


class Port(models.Model, OpenstackMixin):
    id = models.UUIDField(
        editable=False,
        primary_key=True,
        default=uuid.uuid1,
        verbose_name=_('port id'))
    os_port_id = models.UUIDField(
        editable=False)
    network = models.ForeignKey(
        Network,
        on_delete=models.CASCADE)
    name = models.CharField(
        max_length=20,
        verbose_name=_('port name'))
    ip_address = InetAddressField()
    mac_address = MACAddressField(
        unique=True)
    is_external = models.BooleanField()
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created time'))
    modified = models.DateTimeField(
        auto_now=True,
        verbose_name=_('updated time'))
    objects = NetManager()

    class Meta:
        indexes = (BrinIndex(fields=['modified', 'created']),)
        ordering = ('-modified',)

    def __str__(self):
        return self.name

    def create_os_port(self, os_conn):
        fixed_ip = {'subnet_id': self.network.os_subnet_id}
        if self.ip_address:
            fixed_ip['ip_address'] = self.ip_address
            if not self.name:
                self.name = self.ip_address  # assign ip as name

        os_port = os_conn.network.create_port(
            network_id=self.network.os_network_id,
            fixed_ips=[fixed_ip],
            name=self.name,
        )
        self.id = self.os_port_id = os_port.id
        self.mac_address = os_port.mac_address
        self.ip_address = os_port.fixed_ips[0]['ip_address']
        if not self.name:
            self.name = self.ip_address

    def update_os_port(self, os_conn, name='', **kwargs):
        os_conn.network.update_port(self.os_port_id, name=name)
        self.name = name

    def destroy_os_port(self, os_conn):
        os_conn.network.delete_port(self.os_port_id, ignore_missing=False)


class Keypair(models.Model, OpenstackMixin):
    id = models.UUIDField(
        editable=False,
        primary_key=True,
        default=uuid.uuid1,
        verbose_name=_('keypair id')
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('keypair name'))
    user_id = models.CharField(
        blank=True,
        max_length=255
    )
    user_name = models.CharField(
        null=True,
        max_length=255
    )
    tenant_id = models.CharField(
        null=True,
        max_length=255
    )
    tenant_name = models.CharField(
        null=True,
        max_length=255
    )
    project_id = models.UUIDField(
        blank=True
    )
    fingerprint = models.CharField(
        max_length=255,
        blank=True
    )
    public_key = models.TextField(
        null=True
    )
    ssh = 'ssh'
    x509 = 'x509'
    type_list = [
        (ssh, 'ssh'),
        (x509, 'x509')
    ]
    description = models.TextField(
        null=True
    )
    type = models.CharField(choices=type_list, default=ssh, max_length=255)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created time'))
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('updated time'))

    def __str__(self):
        return self.id

    class Meta:
        unique_together = ('name', 'project_id')
        indexes = (BrinIndex(fields=['updated_at', 'created_at']),)

    @classmethod
    def create_keypair(cls, os_conn, key_name, key_pub=None):
        if key_pub:
            ssh_key = os_conn.compute.create_keypair(name=key_name, public_key=key_pub)
        else:
            ssh_key = os_conn.compute.create_keypair(name=key_name)
        return ssh_key

    def destroy_keypair(self, os_conn):
        os_conn.compute.delete_keypair(self.name, ignore_missing=False)


class Image(models.Model, OpenstackMixin):
    os_type_t = (
        ('windows', 'windows'),
        ('ubuntu', 'ubuntu'),
        ('centos', 'centos'),
    )

    id = models.UUIDField(
        editable=False,
        primary_key=True,
        default=uuid.uuid1,
        verbose_name=_('image id'))

    owner = models.UUIDField(
        default=uuid.uuid1,
        verbose_name=_('image owner'))

    name = models.CharField(
        max_length=20,
        null=True,
        verbose_name=_('image name'))
    status = (
        ('active', 'active'),
        ('queued', 'queued'),
        ('saving', 'saving'),
    )

    size = models.IntegerField(null=True)

    status = models.CharField(
        max_length=45,
        choices=status,
        null=True)

    disk_format = models.CharField(
        max_length=20,
        null=True)

    container_format = models.CharField(
        max_length=45,
        null=True)

    visibility = models.CharField(
        max_length=45,
        null=True)

    os_type = models.CharField(
        max_length=45,
        choices=os_type_t,
        default="vmdk")

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created time'))
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('updated time'))

    description = models.TextField(
        null=True
    )

    user_id = models.CharField(
        null=True,
        max_length=255
    )
    user_name = models.CharField(
        null=True,
        max_length=255
    )
    tenant_id = models.CharField(
        null=True,
        max_length=255
    )
    tenant_name = models.CharField(
        null=True,
        max_length=255
    )

    class Meta:
        indexes = (BrinIndex(fields=['updated_at', 'created_at']),)

    @classmethod
    def upload_image(cls, os_conn, file, **kwargs):
        up_image = os_conn.image.upload_image(data=file, **kwargs)
        return up_image

    def update_image(self, os_conn, name='', description='', **kwargs):
        os_conn.image.update_image(str(self.id), name=name,
                                   description=description, **kwargs)

    def destroy_image(self, os_conn):
        os_conn.image.delete_image(self.id, ignore_missing=False)

    def get_image(self, os_conn):
        image = os_conn.image.get_image(self.id)
        return image


class Volume(models.Model, OpenstackMixin):
    id = models.UUIDField(
        primary_key=True
    )
    name = models.CharField(
        max_length=255,
        null=True
    )
    description = models.TextField(
        null=True,
        max_length=255
    )
    project_id = models.UUIDField(
        null=True
    )
    user_id = models.CharField(
        null=True,
        max_length=255
    )
    user_name = models.CharField(
        null=True,
        max_length=255
    )
    tenant_id = models.CharField(
        null=True,
        max_length=255
    )
    tenant_name = models.CharField(
        null=True,
        max_length=255
    )
    volume_used = models.FloatField(
        null=True,
        default=0
    )
    is_bootable = models.BooleanField(
        null=True
    )
    volume_type = models.CharField(
        null=True,
        max_length=255,
        default='__DEFAULT__'
    )
    size = models.IntegerField(
        null=True
    )
    device = models.CharField(
        null=True,
        max_length=255
    )
    status = models.CharField(
        null=True,
        max_length=255
    )
    attach_status = models.CharField(
        null=True,
        max_length=255,
        default="detached"
    )
    attachments = models.JSONField(
        null=True
    )
    cluster_name = models.CharField(
        null=True,
        max_length=255
    )
    server_id = models.UUIDField(
        null=True
    )
    server_name = models.CharField(
        null=True,
        max_length=255
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created time'))
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('updated time'))

    class Meta:
        indexes = (BrinIndex(fields=['updated_at', 'created_at']),)

    def get_volume(self, os_conn):
        volume = os_conn.volume.get_volume(self.id)
        return volume

    def get_server(self, os_conn, server_id):
        server = os_conn.compute.get_server(server_id)
        return server

    def get_volume_list_status(self):
        os_conn = self.get_conn()
        volumes = os_conn.volume.list_volumes()
        return volumes

    @classmethod
    def create_volume(cls, os_conn, size, name=None, volume_type=None):
        volume = os_conn.volume.create_volume(size=size, name=name, volume_type=volume_type)
        return volume

    def destroy_volume(self, os_conn):
        os_conn.volume.delete_volume(self.id, ignore_missing=False)

    def update_volume(self, os_conn, name):
        update_volume = os_conn.update_volume(self.id, name=name)
        return update_volume

    def attached_volume(self, os_conn, server_id):
        server = os_conn.compute.get_server(server_id)
        volume = os_conn.get_volume(self.id)
        attached = os_conn.attach_volume(server=server, volume=volume)
        return attached

    def detached_volume(self, os_conn, server_id):
        server = os_conn.compute.get_server(server_id)
        volume = os_conn.get_volume(self.id)
        os_conn.detach_volume(server=server, volume=volume)

    def extend_volume(self, os_conn, new_size):
        volume = os_conn.get_volume(self.id)
        os_conn.volume.extend_volume(volume, size=new_size)


class VolumeType(models.Model, OpenstackMixin):
    id = models.UUIDField(
        primary_key=True
    )
    name = models.CharField(
        max_length=255
    )
    is_public = models.BooleanField(
        null=True
    )
    description = models.CharField(
        null=True,
        max_length=255
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created time'))
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('updated time'))

    class Meta:
        indexes = (BrinIndex(fields=['updated_at', 'created_at']),)


class Instance(models.Model, OpenstackMixin):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    flavor = models.CharField(max_length=255, blank=True, null=True)
    flavor_id = models.CharField(max_length=255, blank=True, null=True)
    ip_intranet = models.CharField(max_length=255, blank=True, null=True)
    ip_internet = models.CharField(max_length=255, blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    deleted = models.SmallIntegerField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    updater_id = models.CharField(max_length=255, blank=True, null=True)
    updater_name = models.CharField(max_length=255, blank=True, null=True)
    tenant_id = models.CharField(max_length=255, blank=True, null=True)
    tenant_name = models.CharField(max_length=255, blank=True, null=True)
    admin_password = models.CharField(max_length=255, blank=True, null=True)
    keypair_id = models.CharField(max_length=255, blank=True, null=True)
    keypair_name = models.CharField(max_length=255, blank=True, null=True)
    project_id = models.CharField(max_length=255, blank=True, null=True)
    os_type = models.CharField(max_length=255, blank=True, null=True)
    creator_id = models.CharField(max_length=255, blank=True, null=True)
    creator_name = models.CharField(max_length=255, blank=True, null=True)
    image_id = models.UUIDField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'cvm_instance'


class Flavor(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    memory = models.BigIntegerField(blank=True, null=True)
    cpu = models.IntegerField(blank=True, null=True)
    disk = models.BigIntegerField(blank=True, null=True)
    creator_id = models.CharField(max_length=255, blank=True, null=True)
    deleted = models.SmallIntegerField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'cvm_flavor'


class InstancePort(models.Model):
    id = models.UUIDField(primary_key=True)
    server_id = models.UUIDField(blank=True, null=True)
    port_id = models.UUIDField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    modified = models.DateTimeField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'cvm_port'
