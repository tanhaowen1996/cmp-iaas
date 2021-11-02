from django.contrib.postgres.indexes import BrinIndex
from django.db import models
from django.utils.translation import gettext_lazy as _
from netfields import CidrAddressField
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
        default=uuid.uuid1)
    os_network_id = models.UUIDField(
        editable=False)
    os_subnet_id = models.UUIDField(
        editable=False)
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('network name'))
    cidr = CidrAddressField(
        unique=True)
    total_interface = models.PositiveIntegerField()
    category = models.CharField(
        choices=CATEGORY_CHOICES,
        max_length=255)
    is_shared = models.BooleanField()
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

    def destory_os_network_subnet(self):
        os_conn = self.get_conn()
        os_conn.network.delete_subnet(self.subnet_id, ignore_missing=False)
        os_conn.network.delete_network(self.network_id, ignore_missing=False)
