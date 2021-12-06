from django.contrib.postgres.indexes import BrinIndex
from django.db import models

# Create your models here.
from django.utils.translation import gettext_lazy as _


class Inform(models.Model):
    name = models.CharField(max_length=255, null=True, verbose_name=_('Inform name'))
    inform_object_type = models.CharField(max_length=100, null=True)
    inform_tenant = models.CharField(max_length=100, null=True, blank=True)
    inform_user = models.JSONField(default=list)
    details = models.CharField(max_length=255, null=True, blank=True)
    sms_way = models.IntegerField(null=True, blank=True)
    email_way = models.IntegerField(null=True, blank=True)
    wecom_way = models.IntegerField(null=True, blank=True)
    inside_way = models.IntegerField(null=True, blank=True)
    initiator_id = models.CharField(null=True, blank=True, max_length=100)
    initiator_name = models.CharField(null=True, blank=True, max_length=100)
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created time'))

    class Meta:
        indexes = (BrinIndex(fields=['created']),)
        ordering = ('-created',)


class InformUser(models.Model):
    user_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100, null=True, verbose_name=_('User name'))
    phone = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    wecom = models.CharField(max_length=100, null=True, blank=True)
    employeeNo = models.CharField(max_length=100, null=True, blank=True)
    informs = models.ForeignKey(Inform, max_length=100, related_name="info",
                                on_delete=models.CASCADE)

    class Meta:
        indexes = (BrinIndex(fields=['name']),)
