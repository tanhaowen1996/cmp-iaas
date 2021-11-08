from django.contrib.postgres.indexes import BrinIndex
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from netfields import CidrAddressField, InetAddressField, MACAddressField, NetManager
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
    name = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('network name'))
    cidr = CidrAddressField(
        unique=True)
    total_interface = models.PositiveIntegerField()
    vlan_id = models.PositiveSmallIntegerField(
        unique=True)
    category = models.CharField(
        choices=CATEGORY_CHOICES,
        max_length=20)
    is_shared = models.BooleanField()
    description = models.CharField(
        blank=True,
        max_length=50)
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created time'))
    modified = models.DateTimeField(
        auto_now=True,
        verbose_name=_('updated time'))

    class Meta:
        indexes = (BrinIndex(fields=['modified', 'created']),)

    @classmethod
    def create_os_network_subnet(cls, name, cidr, **kwargs):
        os_conn = cls.get_conn()
        network = os_conn.network.create_network(
            name=name
        )

        subnet = os_conn.network.create_subnet(
            name=name,
            network_id=network.id,
            ip_version=cls.IP_VERSION_V4,
            cidr=cidr
        )
        return network.id, subnet.id

    def update_os_network_subnet(self, name='', description='', **kwargs):
        os_conn = self.get_conn()
        os_conn.network.update_subnet(
            self.os_subnet_id, name=name, description=description)
        os_conn.network.update_network(
            self.os_network_id, name=name, description=description)

    def destroy_os_network_subnet(self):
        os_conn = self.get_conn()
        os_conn.network.delete_subnet(self.os_subnet_id, ignore_missing=False)
        os_conn.network.delete_network(self.os_network_id, ignore_missing=False)


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
        unique=True,
        verbose_name=_('port name'))
    ip_address = InetAddressField(
        unique=True)
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

    def create_os_port(self):
        os_conn = self.get_conn()
        fixed_ip = {'subnet_id': self.network.os_subnet_id}
        if self.ip_address:
            fixed_ip['ip_address'] = self.ip_address

        os_port = os_conn.network.create_port(
            network_id=self.network.os_network_id,
            fixed_ips=[fixed_ip],
            name=self.name,
        )
        return os_port

    def update_os_port(self):
        os_conn = self.get_conn()
        os_conn.network.update_port(self.os_port_id, name=self.name)

    def destroy_os_port(self):
        os_conn = self.get_conn()
        os_conn.network.delete_port(self.os_port_id, ignore_missing=False)


@receiver(pre_save, sender=Port)
def create_or_update_os_port(sender, instance=None, **kwargs):
    if not instance.created:
        os_port = instance.create_os_port()
        instance.ip_address = os_port.fixed_ips[0]['ip_address']
        instance.os_port_id = os_port.id
        instance.mac_address = os_port.mac_address
        if not instance.name:
            instance.name = instance.ip_address

    else:
        instance.update_os_port()


class Keypair(models.Model, OpenstackMixin):
    id = models.UUIDField(
        editable=False,
        primary_key=True,
        default=uuid.uuid1,
        verbose_name=_('keypair id')
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('keypair name'))
    user_id = models.UUIDField(
        blank=True
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
        indexes = (BrinIndex(fields=['updated_at', 'created_at']),)

    @classmethod
    def create_keypair(cls, key_name, key_pub=None):
        os_conn = cls.get_conn()
        if key_pub:
            ssh_key = os_conn.compute.create_keypair(name=key_name, public_key=key_pub)
        else:
            ssh_key = os_conn.compute.create_keypair(name=key_name)
        return ssh_key

    def destroy_keypair(self):
        os_conn = self.get_conn()
        os_conn.compute.delete_keypair(self.name, ignore_missing=False)
