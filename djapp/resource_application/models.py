from django.conf import settings
from django.contrib.postgres.indexes import BrinIndex
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class ResourceApplication(models.Model):
    CATEGORY_QUOTA = 'quota'
    CATEGORY_PRIVATE_NETWORK = 'private_network'
    CATEGORY_EXTRANET = 'extranet'
    CATEGORY_LAUNCH_PRODUCT = 'launch_product'
    CATEGORY_VOLUMN_FLAVOR = 'volumn_flavor'
    CATEGORY_BACKUP_FILE = 'backup_file'
    CATEGORY_CHOICES = (
        (CATEGORY_QUOTA, 'quota'),
        (CATEGORY_PRIVATE_NETWORK, 'private network'),
        (CATEGORY_EXTRANET, 'extranet'),
        (CATEGORY_LAUNCH_PRODUCT, 'launch product'),
        (CATEGORY_VOLUMN_FLAVOR, 'volumn flavor'),
        (CATEGORY_BACKUP_FILE, 'backup file'),
    )
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_DENIED = 'denied'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'pending'),
        (STATUS_APPROVED, 'approved'),
        (STATUS_DENIED, 'denied'),
    )
    id = models.UUIDField(
        editable=False,
        primary_key=True,
        default=uuid.uuid1,
        verbose_name=_('resource application id'))
    category = models.CharField(
        choices=CATEGORY_CHOICES,
        max_length=50,
        verbose_name=_('resource application name'))
    creater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT)
    tenant = models.JSONField(
        default=dict,
        verbose_name=_('tenant obj with id & name'))
    content = models.JSONField(
        default=dict,
        verbose_name=_('content body'))
    status = models.CharField(
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        max_length=20)
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created time'))
    modified = models.DateTimeField(
        auto_now=True,
        verbose_name=_('updated time'))

    class Meta:
        indexes = (BrinIndex(fields=['modified', 'created']),)
        ordering = ('-modified',)

    @property
    def creater_name(self):
        return self.creater.get_full_name()
