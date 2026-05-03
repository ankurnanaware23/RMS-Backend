from django.contrib import admin
from .models import Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('id', 'table_number', 'seats', 'status', 'customer_name', 'booking_time')
    list_filter = ('status',)
    search_fields = ('table_number', 'customer_name')
    ordering = ('table_number',)
