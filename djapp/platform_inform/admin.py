from django.contrib import admin
from .models import Inform


@admin.register(Inform)
class ResourceApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'inform_object_type', 'inform_tenant', 'inform_user',
                    'details', 'sms_way', 'email_way', 'wecom_way', 'inside_way',
                    'initiator_id', 'initiator_name', 'created')
