from django.contrib import admin
from .models import OperationLog


@admin.register(OperationLog)
class OperationLogApplicationAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'user_id',
                    'user_name',
                    'type',
                    'type_id',
                    'type_name',
                    'status',
                    'operation_ip',
                    'operation_address',
                    'created_at')
